"""
metapub.localfetcher — PostgreSQL-backed PubMed article fetcher.

Looks up articles from a local medgen-stacks `pubmed.article` table first,
falling back to NCBI eutils for any PMID not found locally.  Returns the
same `PubMedArticle` objects as the standard fetcher — fully transparent to
callers.

The local table stores raw NLM XML (identical to efetch output), so
PubMedArticle is instantiated exactly as it is in the normal path.

Usage::

    from metapub import PubMedFetcher

    # Local-first with NCBI fallback
    fetch = PubMedFetcher(db_url="postgresql://medgen:medgen@loki.local/medgen")
    article = fetch.article_by_pmid("27022295")

    # Bulk lookup (new — not available in eutils-only mode)
    articles = fetch.articles_by_pmids(["27022295", "18319072", "32404922"])
    # returns {pmid_str: PubMedArticle, ...}

Configuration via environment variables (read automatically)::

    METAPUB_DB_URL   postgresql://user:pass@host/dbname

Requires psycopg2::

    pip install psycopg2-binary
"""

import logging
import os

log = logging.getLogger(__name__)

try:
    import psycopg2
    import psycopg2.extras
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False

_SELECT_ONE  = "SELECT xml FROM pubmed.article WHERE pmid = %s"
_SELECT_MANY = "SELECT pmid, xml FROM pubmed.article WHERE pmid = ANY(%s)"


class LocalPubMedBackend:
    """PostgreSQL connection to the medgen-stacks pubmed schema."""

    def __init__(self, db_url: str):
        if not HAS_PSYCOPG2:
            raise ImportError(
                "psycopg2 is required for the local backend. "
                "Install it with: pip install psycopg2-binary"
            )
        self._db_url = db_url
        self._conn = None

    def _connection(self):
        """Return an open connection, reconnecting if needed."""
        if self._conn is None or self._conn.closed:
            self._conn = psycopg2.connect(self._db_url)
            self._conn.set_session(readonly=True, autocommit=True)
        return self._conn

    def fetch_xml(self, pmid: int | str) -> str | None:
        """Return raw NLM XML for a single PMID, or None if not in the local DB."""
        try:
            with self._connection().cursor() as cur:
                cur.execute(_SELECT_ONE, (int(pmid),))
                row = cur.fetchone()
                return row[0] if row else None
        except Exception as e:
            log.warning("localfetcher: DB error for PMID %s: %s", pmid, e)
            self._conn = None   # force reconnect next time
            return None

    def fetch_xml_many(self, pmids: list[int | str]) -> dict[int, str]:
        """
        Return {pmid: xml} for all PMIDs found in the local DB.
        Missing PMIDs are simply absent from the returned dict.
        """
        int_pmids = [int(p) for p in pmids]
        if not int_pmids:
            return {}
        try:
            with self._connection().cursor() as cur:
                cur.execute(_SELECT_MANY, (int_pmids,))
                return {row[0]: row[1] for row in cur.fetchall()}
        except Exception as e:
            log.warning("localfetcher: DB error for batch of %d PMIDs: %s", len(pmids), e)
            self._conn = None
            return {}


def make_local_fetcher_methods(backend: LocalPubMedBackend, eutils_fetcher):
    """
    Return (article_by_pmid, articles_by_pmids) methods that use the local
    backend first and fall back to eutils for misses.

    `eutils_fetcher` is a bound method: the existing PubMedFetcher instance's
    `_eutils_article_by_pmid`.
    """
    from .pubmedarticle import PubMedArticle

    def article_by_pmid(pmid):
        xml = backend.fetch_xml(pmid)
        if xml:
            log.debug("localfetcher: hit for PMID %s", pmid)
            try:
                return PubMedArticle(xml)
            except Exception as e:
                log.warning("localfetcher: XML parse error for PMID %s: %s — falling back", pmid, e)
        log.debug("localfetcher: miss for PMID %s — falling back to eutils", pmid)
        return eutils_fetcher(pmid)

    def articles_by_pmids(pmids: list) -> dict:
        """
        Bulk fetch articles for a list of PMIDs.
        Returns {str(pmid): PubMedArticle} for all PMIDs that resolve.
        PMIDs not found in the local DB are fetched from NCBI individually.
        """
        pmids = [str(p) for p in pmids]
        local_xml = backend.fetch_xml_many(pmids)

        results: dict[str, PubMedArticle] = {}
        ncbi_needed = []

        for pmid in pmids:
            xml = local_xml.get(int(pmid))
            if xml:
                try:
                    results[pmid] = PubMedArticle(xml)
                    continue
                except Exception as e:
                    log.warning("localfetcher: XML parse error for PMID %s: %s", pmid, e)
            ncbi_needed.append(pmid)

        if ncbi_needed:
            log.debug("localfetcher: fetching %d PMIDs from NCBI", len(ncbi_needed))
            for pmid in ncbi_needed:
                try:
                    art = eutils_fetcher(pmid)
                    if art:
                        results[pmid] = art
                except Exception as e:
                    log.warning("localfetcher: NCBI error for PMID %s: %s", pmid, e)

        return results

    return article_by_pmid, articles_by_pmids
