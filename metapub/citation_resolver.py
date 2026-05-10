"""
citation_resolver — resolve messy citation text to PubMed IDs.

Takes freeform citation strings like "Bienvenu et al 1993" or
"Cukier HN et al. (2016)" and resolves them to PMIDs by searching
the local pubmed.article table first, then CrossRef as a backup.

Designed for bulk resolution of LOVD-style citation text, which is
notoriously messy: mixed formats, tooltip HTML fragments, multiple
citations per field, full author lists, missing years, etc.

Usage::

    from metapub.citation_resolver import CitationResolver

    resolver = CitationResolver(db_url="postgresql://medgen:medgen@loki.local/medgen")

    # Single citation
    pmid = resolver.resolve("Bienvenu et al 1993", gene="CFTR")
    # → 7691353

    # Batch
    results = resolver.resolve_batch([
        {"text": "Cukier HN et al. (2016)", "gene": "ABCA7"},
        {"text": "Abou-Sleiman PM, 2003", "gene": "PINK1"},
    ])
    # → [{"text": ..., "pmid": 12345, "method": "local_db", "confidence": 0.95}, ...]
"""

import logging
import re

log = logging.getLogger(__name__)


def parse_citation_text(raw: str) -> list[dict]:
    """
    Parse messy LOVD citation text into structured citation(s).

    Handles:
      - "Author et al. (YEAR)" → {"author": "Author", "year": 2016}
      - "Author1, YEAR;Author2, YEAR" → multiple citations
      - "Author1 A1, Author2 B2, ... (YEAR)" → first author + year
      - Strips LOVD tooltip HTML fragments

    Returns a list of {"author": str, "year": int|None} dicts.
    """
    if not raw or raw.strip() in ("-", ""):
        return []

    # Strip LOVD tooltip HTML fragments
    # Pattern: "Author et al 1993 ', this);">Author et al 1993"
    # Keep only the first occurrence (before the tooltip repeat)
    text = re.split(r"',\s*this\);", raw)[0].strip()
    text = re.sub(r"<[^>]+>", " ", text)       # remove any HTML tags
    text = re.sub(r"\\+'", "", text)            # remove escaped quotes
    text = text.strip().strip("'\"").strip()

    if not text or text in ("-", ""):
        return []

    # Split multiple citations separated by semicolons
    # "Abou-Sleiman PM, 2003;Lockhart PJ, 2004" → two citations
    parts = re.split(r"\s*;\s*", text)

    results = []
    for part in parts:
        part = part.strip()
        if not part or part in ("-", "dbSNP", "ClinVar", "link"):
            continue

        citation = _parse_single_citation(part)
        if citation:
            results.append(citation)

    return results


# Patterns for extracting author + year from a single citation string
_RE_AUTHOR_ET_AL_YEAR = re.compile(
    r"^([A-Z][A-Za-zÀ-ÿ\-'\s]+?)\s+(?:et|at)\s+al\.?\s*\(?(\d{4})\)?",
    re.IGNORECASE,
)
_RE_AUTHOR_COMMA_YEAR = re.compile(
    r"^([A-Z][A-Za-zÀ-ÿ\-']+(?:\s+[A-Z]{1,2})?)\s*,\s*(\d{4})",
)
_RE_FULL_AUTHORS_YEAR = re.compile(
    r"^([A-Z][A-Za-zÀ-ÿ\-']+)\s+\w{1,3}[\d]?\s*,.*?\(?(\d{4})\)?$",
)
_RE_YEAR_ONLY = re.compile(r"\((\d{4})\)$")
_RE_BARE_PMID = re.compile(r"^(\d{7,8})\s")


def _parse_single_citation(text: str) -> dict | None:
    """Parse a single citation string into {"author": str, "year": int|None}."""

    # "26176978 et al. (2015)" — starts with a PMID-like number (garbage)
    m = _RE_BARE_PMID.match(text)
    if m:
        return None

    # "Author et al. (YEAR)" or "Author et al YEAR"
    m = _RE_AUTHOR_ET_AL_YEAR.match(text)
    if m:
        author = m.group(1).strip().rstrip(",")
        # Take the last substantial word as surname
        # "Polin Haghvirdizadeh et al" → "Haghvirdizadeh"
        # "Cukier HN et al" → "Cukier" (HN is initials)
        words = author.split()
        surname = words[0]  # default to first word
        for w in reversed(words):
            if len(w) > 2 and not re.match(r"^[A-Z]{1,3}\d?$", w):
                surname = w
                break
        return {"author": surname, "year": int(m.group(2))}

    # "Author, YEAR" (simple format)
    m = _RE_AUTHOR_COMMA_YEAR.match(text)
    if m:
        author = m.group(1).strip()
        author = author.split()[0] if " " in author else author
        return {"author": author, "year": int(m.group(2))}

    # "Firstname Lastname, Firstname Lastname, ... (YEAR)" (full author list)
    m = _RE_FULL_AUTHORS_YEAR.match(text)
    if m:
        author = m.group(1).strip()
        return {"author": author, "year": int(m.group(2))}

    # Last resort: find any 4-digit year and grab the first substantial word
    m = _RE_YEAR_ONLY.search(text)
    if not m:
        # Also try year without parens at end
        m = re.search(r"\b(\d{4})\s*$", text)
    if m:
        year = int(m.group(1))
        surname = _extract_surname(text)
        if surname:
            return {"author": surname, "year": year}

    # No year found — try to get at least an author
    surname = _extract_surname(text)
    if surname:
        return {"author": surname, "year": None}

    return None


def _extract_surname(text: str) -> str | None:
    """Extract the most likely surname from the beginning of a citation string.

    Skips single-letter initials ("A Del Grande" → "Del Grande" → "Grande").
    Takes the first word longer than 2 chars that isn't all-caps initials.
    """
    words = re.findall(r"[A-ZÀ-ÿ][A-Za-zÀ-ÿ\-']+", text)
    for w in words:
        # Skip initials (A, AB, JC1) and very short words
        if len(w) <= 2 or re.match(r"^[A-Z]{1,3}\d?$", w):
            continue
        return w
    return None


class CitationResolver:
    """
    Resolve citation text to PMIDs using local DB + CrossRef.

    Resolution order:
      1. Local pubmed.article (author + year + optional gene)
      2. CrossRef bibliographic search (if local misses)
    """

    def __init__(self, db_url: str = None):
        self._db_url = db_url
        self._conn = None

    def _get_conn(self):
        if self._conn is not None and not self._conn.closed:
            return self._conn
        if not self._db_url:
            return None
        try:
            import psycopg2
            self._conn = psycopg2.connect(self._db_url)
            self._conn.set_session(readonly=True, autocommit=True)
            return self._conn
        except Exception as e:
            log.warning("CitationResolver: DB connect failed: %s", e)
            return None

    def resolve(self, text: str, gene: str = None) -> dict | None:
        """
        Resolve a single citation string to a PMID.

        Returns {"pmid": int, "method": str, "confidence": float} or None.
        """
        citations = parse_citation_text(text)
        if not citations:
            return None

        # Try each parsed citation
        for cite in citations:
            result = self._resolve_one(cite, gene)
            if result:
                return result

        return None

    def _resolve_one(self, cite: dict, gene: str = None,
                     use_crossref: bool = False) -> dict | None:
        """Try to resolve a single parsed citation.

        If use_crossref is True, queries CrossRef in addition to local DB.
        When both find a result, agreement boosts confidence; disagreement
        flags ambiguity.
        """
        author = cite.get("author")
        year = cite.get("year")

        if not author:
            return None

        local = self._search_local(author, year, gene)

        if not use_crossref:
            return local

        cr = self._search_crossref(author, year, gene)

        if local and cr:
            if local["pmid"] == cr["pmid"]:
                # Both agree — high confidence
                local["confidence"] = min(local["confidence"] + 0.1, 1.0)
                local["method"] = "local_db+crossref"
                local["crossref_doi"] = cr.get("doi")
                return local
            else:
                # Disagreement — trust local but note it
                local["note"] = f"CrossRef disagrees (PMID {cr['pmid']})"
                return local
        elif local:
            return local
        elif cr:
            return cr

        return None

    def _search_local(self, author: str, year: int = None,
                      gene: str = None) -> dict | None:
        """Search pubmed.article by author + year, optionally filtered by gene in title/abstract."""
        conn = self._get_conn()
        if conn is None:
            return None

        # Build query — use lower(first_author) with text_pattern_ops index
        conditions = ["lower(first_author) LIKE %s"]
        params = [f"{author.lower()}%"]

        if year:
            conditions.append("year = %s")
            params.append(year)

        # If we have a gene name, require it in title or abstract
        if gene:
            conditions.append("(title ILIKE %s OR abstract ILIKE %s)")
            params.extend([f"%{gene}%", f"%{gene}%"])

        sql = f"""
            SELECT pmid, title, first_author, year
            FROM pubmed.article
            WHERE {' AND '.join(conditions)}
            ORDER BY year DESC
            LIMIT 10
        """

        try:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                rows = cur.fetchall()
        except Exception as e:
            log.warning("CitationResolver local search error: %s", e)
            self._conn = None
            return None

        if not rows:
            # Try without gene filter
            if gene:
                return self._search_local(author, year, gene=None)
            return None

        if len(rows) == 1:
            pmid, title, first_author, yr = rows[0]
            return {"pmid": int(pmid), "method": "local_db", "confidence": 0.95,
                    "title": title, "matched_author": first_author}

        # Multiple results — if we had a gene filter and got exactly one, that's high confidence
        # Otherwise, return the first with lower confidence
        pmid, title, first_author, yr = rows[0]
        confidence = 0.7 if len(rows) <= 3 else 0.5
        return {"pmid": int(pmid), "method": "local_db", "confidence": confidence,
                "title": title, "matched_author": first_author,
                "note": f"{len(rows)} candidates"}

    def _search_crossref(self, author: str, year: int = None,
                         gene: str = None) -> dict | None:
        """Search CrossRef by author + year, resolve to PMID."""
        try:
            from .crossref import CrossRefFetcher
            from .pubmedfetcher import PubMedFetcher
        except ImportError:
            return None

        query = f"{author} {year}" if year else author
        if gene:
            query = f"{query} {gene}"

        try:
            cr = CrossRefFetcher()
            work = cr.article_by_title(query)
            if work and work.doi:
                # Resolve DOI → PMID
                try:
                    fetch = PubMedFetcher()
                    pma = fetch.article_by_doi(work.doi)
                    if pma and pma.pmid:
                        return {"pmid": int(pma.pmid), "method": "crossref",
                                "confidence": 0.8, "doi": work.doi,
                                "title": work.title[0] if work.title else None}
                except Exception:
                    pass
        except Exception as e:
            log.debug("CrossRef search failed for '%s': %s", query, e)

        return None

    def resolve_batch(self, items: list[dict]) -> list[dict]:
        """
        Resolve a batch of citations.

        Each item should have {"text": str, "gene": str (optional)}.
        Returns list with added "pmid", "method", "confidence" fields.
        """
        results = []
        for item in items:
            text = item.get("text", "")
            gene = item.get("gene")
            result = self.resolve(text, gene=gene)
            out = dict(item)
            if result:
                out.update(result)
            results.append(out)
        return results
