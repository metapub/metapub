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
    fetch = PubMedFetcher(db_url="postgresql://user:pass@host/dbname")
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

from lxml import etree

from .exceptions import MetaPubError

log = logging.getLogger(__name__)

try:
    import psycopg2
    import psycopg2.extras
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False

def _ensure_article_set_wrapper(xml: str) -> str:
    """Wrap bare <PubmedArticle> XML in <PubmedArticleSet> if the wrapper is missing.

    PubMedArticle.parse_xml searches for a 'PubmedArticle' child of the root
    element.  If the DB stores bare <PubmedArticle> XML (no <PubmedArticleSet>
    parent), that search returns None and every attribute ends up None.
    eutils always returns the full set wrapper, so this only matters for
    pre-existing DB rows written by other tools (e.g. medgen-stacks).
    """
    if isinstance(xml, bytes):
        xml = xml.decode('utf-8')
    if '<PubmedArticleSet>' not in xml and '<PubmedArticle>' in xml:
        return f'<PubmedArticleSet>{xml}</PubmedArticleSet>'
    return xml


_SELECT_ONE  = "SELECT xml FROM pubmed.article WHERE pmid = %s"
_SELECT_MANY = "SELECT pmid, xml FROM pubmed.article WHERE pmid = ANY(%s)"
_UPSERT_XML  = """
INSERT INTO pubmed.article (pmid, xml)
VALUES (%s, %s)
ON CONFLICT (pmid) DO UPDATE SET xml = EXCLUDED.xml, updated_at = NOW()
"""


class LocalPubMedBackend:
    """PostgreSQL connection to the medgen-stacks pubmed schema."""

    def __init__(self, db_url: str):
        if not HAS_PSYCOPG2:
            raise ImportError(
                "psycopg2 is required for the local backend. "
                "Install it with: pip install psycopg2-binary"
            )
        self._db_url = db_url
        self._ro_conn = None   # read-only connection (reads)
        self._rw_conn = None   # read-write connection (write-through stores)

    def _connection(self):
        """Return a read-only connection, reconnecting if needed."""
        if self._ro_conn is not None and not self._ro_conn.closed:
            try:
                self._ro_conn.cursor().execute("SELECT 1")
            except psycopg2.OperationalError:
                self._ro_conn = None
        if self._ro_conn is None:
            self._ro_conn = psycopg2.connect(self._db_url)
            self._ro_conn.set_session(readonly=True, autocommit=True)
        return self._ro_conn

    def _rw_connection(self):
        """Return a read-write connection for write-through stores."""
        if self._rw_conn is not None and not self._rw_conn.closed:
            try:
                self._rw_conn.cursor().execute("SELECT 1")
            except psycopg2.OperationalError:
                self._rw_conn = None
        if self._rw_conn is None:
            self._rw_conn = psycopg2.connect(self._db_url)
            self._rw_conn.autocommit = True
        return self._rw_conn

    def fetch_xml(self, pmid: int | str) -> str | None:
        """Return raw NLM XML for a single PMID, or None if not in the local DB."""
        try:
            with self._connection().cursor() as cur:
                cur.execute(_SELECT_ONE, (int(pmid),))
                row = cur.fetchone()
                return row[0] if row else None
        except psycopg2.OperationalError as e:
            log.error("localfetcher: DB connection error for PMID %s: %s", pmid, e)
            self._ro_conn = None
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
        except psycopg2.OperationalError as e:
            log.error("localfetcher: DB connection error for batch of %d PMIDs: %s", len(pmids), e)
            self._ro_conn = None
            return {}

    def store_xml(self, pmid: int | str, xml: str) -> None:
        """
        Write-through: persist NLM XML for a PMID fetched from NCBI.
        Structured columns (title, authors, etc.) are left NULL; only the
        raw XML needed by metapub is stored. Silently ignored on error.
        """
        try:
            with self._rw_connection().cursor() as cur:
                cur.execute(_UPSERT_XML, (int(pmid), xml))
            log.debug("localfetcher: stored PMID %s in local DB", pmid)
        except Exception as e:
            log.warning("localfetcher: write-through store failed for PMID %s: %s", pmid, e)
            self._rw_conn = None


def make_local_fetcher_methods(backend: LocalPubMedBackend, eutils_fetcher,
                               write_through: bool = True):
    """
    Return (article_by_pmid, articles_by_pmids) methods that use the local
    backend first and fall back to eutils for misses.

    `eutils_fetcher` is a bound method: the existing PubMedFetcher instance's
    `_eutils_article_by_pmid`.

    When `write_through=True` (default), articles fetched from NCBI are stored
    in the local DB so future lookups are served locally.
    """
    from .pubmedarticle import PubMedArticle

    def article_by_pmid(pmid):
        xml = backend.fetch_xml(pmid)
        if xml:
            log.debug("localfetcher: hit for PMID %s", pmid)
            try:
                art = PubMedArticle(_ensure_article_set_wrapper(xml))
            except (etree.XMLSyntaxError, etree.ParserError, MetaPubError) as e:
                log.warning("localfetcher: XML parse error for PMID %s: %s — falling back", pmid, e)
            else:
                if art.pmid is None:
                    log.warning("localfetcher: DB XML for PMID %s parsed but yielded no PMID — falling back", pmid)
                else:
                    return art
        log.debug("localfetcher: miss for PMID %s — falling back to eutils", pmid)
        art = eutils_fetcher(pmid)
        if write_through and art is not None:
            backend.store_xml(pmid, art.xml)
        return art

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
                    art = PubMedArticle(_ensure_article_set_wrapper(xml))
                except (etree.XMLSyntaxError, etree.ParserError, MetaPubError) as e:
                    log.warning("localfetcher: XML parse error for PMID %s: %s", pmid, e)
                else:
                    if art.pmid is None:
                        log.warning("localfetcher: DB XML for PMID %s parsed but yielded no PMID — falling back", pmid)
                    else:
                        results[pmid] = art
                        continue
            ncbi_needed.append(pmid)

        if ncbi_needed:
            log.debug("localfetcher: fetching %d PMIDs from NCBI", len(ncbi_needed))
            for pmid in ncbi_needed:
                try:
                    art = eutils_fetcher(pmid)
                    if art:
                        results[pmid] = art
                        if write_through:
                            backend.store_xml(pmid, art.xml)
                except Exception as e:
                    log.warning("localfetcher: NCBI error for PMID %s: %s", pmid, e)

        return results

    return article_by_pmid, articles_by_pmids
