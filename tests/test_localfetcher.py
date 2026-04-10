"""
Tests for metapub.localfetcher — all offline, no DB or NCBI required.

Tests cover:
  - LocalPubMedBackend.fetch_xml: DB hit, DB miss, DB error
  - LocalPubMedBackend.fetch_xml_many: partial hits, empty list, DB error
  - LocalPubMedBackend.store_xml: success, error (silent)
  - make_local_fetcher_methods: hit path, miss+fallback, miss+write-through,
    miss+no-write-through, bulk fetch
  - PubMedFetcher with METAPUB_DB_URL env var wires up local backend
"""

import os
import threading
import unittest
from unittest.mock import MagicMock, patch, call


class _Psycopg2Error(Exception):
    """Stub for psycopg2.Error used when psycopg2 is fully mocked."""

# Minimal NLM XML fixture — enough for PubMedArticle to parse
_NLM_XML = """\
<?xml version="1.0" ?>
<!DOCTYPE PubmedArticleSet PUBLIC "-//NLM//DTD PubMedArticle, 1st January 2025//EN"
  "https://dtd.nlm.nih.gov/ncbi/pubmed/out/pubmed_250101.dtd">
<PubmedArticleSet>
<PubmedArticle>
  <MedlineCitation Status="MEDLINE" Owner="NLM">
    <PMID Version="1">27022295</PMID>
    <Article PubModel="Print">
      <Journal>
        <JournalIssue CitedMedium="Print">
          <PubDate><Year>2016</Year></PubDate>
        </JournalIssue>
        <Title>Test Journal</Title>
        <ISOAbbreviation>Test J</ISOAbbreviation>
      </Journal>
      <ArticleTitle>Test article title</ArticleTitle>
      <Abstract><AbstractText>Test abstract.</AbstractText></Abstract>
      <AuthorList CompleteYN="Y">
        <Author ValidYN="Y">
          <LastName>Smith</LastName>
          <ForeName>Jane</ForeName>
          <Initials>J</Initials>
        </Author>
      </AuthorList>
      <Language>eng</Language>
      <PublicationTypeList>
        <PublicationType UI="D016428">Journal Article</PublicationType>
      </PublicationTypeList>
    </Article>
  </MedlineCitation>
  <PubmedData>
    <ArticleIdList>
      <ArticleId IdType="pubmed">27022295</ArticleId>
    </ArticleIdList>
  </PubmedData>
</PubmedArticle>
</PubmedArticleSet>
"""


def _make_backend(fetch_xml_return=None, fetch_xml_many_return=None):
    """Return a LocalPubMedBackend with mocked DB methods."""
    from metapub.localfetcher import LocalPubMedBackend
    backend = LocalPubMedBackend.__new__(LocalPubMedBackend)
    backend._db_url = "postgresql://mock/mock"
    backend._local = threading.local()
    backend.fetch_xml = MagicMock(return_value=fetch_xml_return)
    backend.fetch_xml_many = MagicMock(return_value=fetch_xml_many_return or {})
    backend.store_xml = MagicMock()
    return backend


class TestLocalPubMedBackend(unittest.TestCase):
    """Unit tests for LocalPubMedBackend DB methods (psycopg2 mocked)."""

    def _make_conn(self, fetchone=None, fetchall=None):
        """Build a mock psycopg2 connection/cursor."""
        cur = MagicMock()
        cur.__enter__ = lambda s: s
        cur.__exit__ = MagicMock(return_value=False)
        cur.fetchone.return_value = fetchone
        cur.fetchall.return_value = fetchall or []
        conn = MagicMock()
        conn.closed = False
        conn.cursor.return_value = cur
        return conn, cur

    @patch("metapub.localfetcher.HAS_PSYCOPG2", True)
    @patch("metapub.localfetcher.psycopg2")
    def test_fetch_xml_hit(self, mock_psycopg2):
        from metapub.localfetcher import LocalPubMedBackend
        conn, _ = self._make_conn(fetchone=(_NLM_XML,))
        mock_psycopg2.connect.return_value = conn
        b = LocalPubMedBackend("postgresql://mock/mock")
        result = b.fetch_xml(27022295)
        self.assertEqual(result, _NLM_XML)

    @patch("metapub.localfetcher.HAS_PSYCOPG2", True)
    @patch("metapub.localfetcher.psycopg2")
    def test_fetch_xml_miss(self, mock_psycopg2):
        from metapub.localfetcher import LocalPubMedBackend
        conn, _ = self._make_conn(fetchone=None)
        mock_psycopg2.connect.return_value = conn
        b = LocalPubMedBackend("postgresql://mock/mock")
        result = b.fetch_xml(99999999)
        self.assertIsNone(result)

    @patch("metapub.localfetcher.HAS_PSYCOPG2", True)
    @patch("metapub.localfetcher.psycopg2")
    def test_fetch_xml_db_error_returns_none(self, mock_psycopg2):
        from metapub.localfetcher import LocalPubMedBackend
        mock_psycopg2.Error = _Psycopg2Error
        conn = MagicMock()
        conn.closed = False
        conn.cursor.side_effect = _Psycopg2Error("DB connection failed")
        mock_psycopg2.connect.return_value = conn
        b = LocalPubMedBackend("postgresql://mock/mock")
        result = b.fetch_xml(27022295)
        self.assertIsNone(result)

    @patch("metapub.localfetcher.HAS_PSYCOPG2", True)
    @patch("metapub.localfetcher.psycopg2")
    def test_fetch_xml_many_partial(self, mock_psycopg2):
        from metapub.localfetcher import LocalPubMedBackend
        conn, _ = self._make_conn(fetchall=[(27022295, _NLM_XML)])
        mock_psycopg2.connect.return_value = conn
        b = LocalPubMedBackend("postgresql://mock/mock")
        result = b.fetch_xml_many([27022295, 99999999])
        self.assertIn(27022295, result)
        self.assertNotIn(99999999, result)
        self.assertEqual(result[27022295], _NLM_XML)

    @patch("metapub.localfetcher.HAS_PSYCOPG2", True)
    @patch("metapub.localfetcher.psycopg2")
    def test_fetch_xml_many_empty_list(self, mock_psycopg2):
        from metapub.localfetcher import LocalPubMedBackend
        mock_psycopg2.connect.return_value = MagicMock()
        b = LocalPubMedBackend("postgresql://mock/mock")
        result = b.fetch_xml_many([])
        self.assertEqual(result, {})
        mock_psycopg2.connect.assert_not_called()

    @patch("metapub.localfetcher.HAS_PSYCOPG2", True)
    @patch("metapub.localfetcher.psycopg2")
    def test_store_xml_success(self, mock_psycopg2):
        from metapub.localfetcher import LocalPubMedBackend
        conn, cur = self._make_conn()
        mock_psycopg2.connect.return_value = conn
        b = LocalPubMedBackend("postgresql://mock/mock")
        b.store_xml(27022295, _NLM_XML)
        cur.execute.assert_called_once()
        args = cur.execute.call_args[0]
        self.assertIn(27022295, args[1])

    @patch("metapub.localfetcher.HAS_PSYCOPG2", True)
    @patch("metapub.localfetcher.psycopg2")
    def test_store_xml_error_is_silent(self, mock_psycopg2):
        from metapub.localfetcher import LocalPubMedBackend
        mock_psycopg2.Error = _Psycopg2Error
        conn = MagicMock()
        conn.closed = False
        conn.cursor.side_effect = _Psycopg2Error("write error")
        mock_psycopg2.connect.return_value = conn
        b = LocalPubMedBackend("postgresql://mock/mock")
        # Must not raise
        b.store_xml(27022295, _NLM_XML)

    def test_requires_psycopg2(self):
        with patch("metapub.localfetcher.HAS_PSYCOPG2", False):
            from metapub.localfetcher import LocalPubMedBackend
            with self.assertRaises(ImportError):
                LocalPubMedBackend("postgresql://mock/mock")


class TestMakeLocalFetcherMethods(unittest.TestCase):
    """Tests for the article_by_pmid / articles_by_pmids closures."""

    def _make_article(self, pmid="27022295"):
        from metapub.pubmedarticle import PubMedArticle
        art = PubMedArticle(_NLM_XML)
        art.xml = _NLM_XML
        return art

    def test_article_by_pmid_db_hit(self):
        from metapub.localfetcher import make_local_fetcher_methods
        backend = _make_backend(fetch_xml_return=_NLM_XML)
        eutils = MagicMock()
        article_by_pmid, _ = make_local_fetcher_methods(backend, eutils)
        art = article_by_pmid("27022295")
        self.assertIsNotNone(art)
        self.assertEqual(str(art.pmid), "27022295")
        eutils.assert_not_called()
        backend.store_xml.assert_not_called()

    def test_article_by_pmid_db_miss_falls_back_to_ncbi(self):
        from metapub.localfetcher import make_local_fetcher_methods
        backend = _make_backend(fetch_xml_return=None)
        ncbi_art = self._make_article()
        eutils = MagicMock(return_value=ncbi_art)
        article_by_pmid, _ = make_local_fetcher_methods(backend, eutils)
        art = article_by_pmid("27022295")
        self.assertIs(art, ncbi_art)
        eutils.assert_called_once_with("27022295")

    def test_article_by_pmid_miss_write_through(self):
        from metapub.localfetcher import make_local_fetcher_methods
        backend = _make_backend(fetch_xml_return=None)
        ncbi_art = self._make_article()
        eutils = MagicMock(return_value=ncbi_art)
        article_by_pmid, _ = make_local_fetcher_methods(backend, eutils, write_through=True)
        article_by_pmid("27022295")
        backend.store_xml.assert_called_once_with("27022295", _NLM_XML)

    def test_article_by_pmid_miss_no_write_through(self):
        from metapub.localfetcher import make_local_fetcher_methods
        backend = _make_backend(fetch_xml_return=None)
        ncbi_art = self._make_article()
        eutils = MagicMock(return_value=ncbi_art)
        article_by_pmid, _ = make_local_fetcher_methods(backend, eutils, write_through=False)
        article_by_pmid("27022295")
        backend.store_xml.assert_not_called()

    def test_article_by_pmid_ncbi_returns_none(self):
        from metapub.localfetcher import make_local_fetcher_methods
        backend = _make_backend(fetch_xml_return=None)
        eutils = MagicMock(return_value=None)
        article_by_pmid, _ = make_local_fetcher_methods(backend, eutils)
        art = article_by_pmid("99999999")
        self.assertIsNone(art)
        backend.store_xml.assert_not_called()

    def test_articles_by_pmids_all_local(self):
        from metapub.localfetcher import make_local_fetcher_methods
        backend = _make_backend(fetch_xml_many_return={27022295: _NLM_XML})
        eutils = MagicMock()
        _, articles_by_pmids = make_local_fetcher_methods(backend, eutils)
        results = articles_by_pmids(["27022295"])
        self.assertIn("27022295", results)
        eutils.assert_not_called()

    def test_articles_by_pmids_partial_ncbi_fallback(self):
        from metapub.localfetcher import make_local_fetcher_methods
        ncbi_art = self._make_article("99999999")
        backend = _make_backend(fetch_xml_many_return={27022295: _NLM_XML})
        eutils = MagicMock(return_value=ncbi_art)
        _, articles_by_pmids = make_local_fetcher_methods(backend, eutils)
        results = articles_by_pmids(["27022295", "99999999"])
        self.assertIn("27022295", results)
        self.assertIn("99999999", results)
        eutils.assert_called_once_with(99999999)

    def test_articles_by_pmids_invalid_pmid_raises(self):
        from metapub.localfetcher import make_local_fetcher_methods
        backend = _make_backend()
        eutils = MagicMock()
        _, articles_by_pmids = make_local_fetcher_methods(backend, eutils)
        with self.assertRaises(ValueError):
            articles_by_pmids(["not-a-number"])

    def test_articles_by_pmids_cached_xml_parse_error_falls_back_to_ncbi(self):
        """Corrupt XML in local cache triggers NCBI fallback for that PMID."""
        from metapub.localfetcher import make_local_fetcher_methods
        ncbi_art = self._make_article("27022295")
        backend = _make_backend(fetch_xml_many_return={27022295: "<<corrupt xml>>"})
        eutils = MagicMock(return_value=ncbi_art)
        _, articles_by_pmids = make_local_fetcher_methods(backend, eutils)
        results = articles_by_pmids(["27022295"])
        self.assertIn("27022295", results)
        eutils.assert_called_once_with(27022295)

    def test_article_by_pmid_empty_xml_falls_back_to_ncbi(self):
        """Empty string XML from DB (raises MetaPubError) triggers eutils fallback."""
        from metapub.localfetcher import make_local_fetcher_methods
        ncbi_art = self._make_article()
        backend = _make_backend(fetch_xml_return="")
        eutils = MagicMock(return_value=ncbi_art)
        article_by_pmid, _ = make_local_fetcher_methods(backend, eutils)
        art = article_by_pmid("27022295")
        self.assertIs(art, ncbi_art)
        eutils.assert_called_once_with("27022295")

    def test_articles_by_pmids_empty_xml_falls_back_to_ncbi(self):
        """Empty string XML in bulk DB result (raises MetaPubError) triggers eutils fallback."""
        from metapub.localfetcher import make_local_fetcher_methods
        ncbi_art = self._make_article("27022295")
        backend = _make_backend(fetch_xml_many_return={27022295: ""})
        eutils = MagicMock(return_value=ncbi_art)
        _, articles_by_pmids = make_local_fetcher_methods(backend, eutils)
        results = articles_by_pmids(["27022295"])
        self.assertIn("27022295", results)
        eutils.assert_called_once_with(27022295)

    def test_articles_by_pmids_ncbi_error_returns_partial_results(self):
        """An NCBI service error for one PMID does not abort the whole batch."""
        from metapub.exceptions import MetaPubError
        from metapub.localfetcher import make_local_fetcher_methods
        ncbi_art = self._make_article("27022295")
        backend = _make_backend(fetch_xml_many_return={})
        eutils = MagicMock(side_effect=[ncbi_art, MetaPubError("NCBI unavailable")])
        _, articles_by_pmids = make_local_fetcher_methods(backend, eutils)
        results = articles_by_pmids(["27022295", "99999999"])
        self.assertIn("27022295", results)
        self.assertNotIn("99999999", results)

    def test_articles_by_pmids_ncbi_service_error_returns_partial_results(self):
        """An NCBIServiceError for one PMID does not abort the whole batch."""
        from metapub.localfetcher import make_local_fetcher_methods
        from metapub.ncbi_errors import NCBIServiceError
        ncbi_art = self._make_article("27022295")
        backend = _make_backend(fetch_xml_many_return={})
        eutils = MagicMock(side_effect=[ncbi_art, NCBIServiceError("timeout")])
        _, articles_by_pmids = make_local_fetcher_methods(backend, eutils)
        results = articles_by_pmids(["27022295", "99999999"])
        self.assertIn("27022295", results)
        self.assertNotIn("99999999", results)

    def test_article_by_pmid_cached_xml_parse_error_falls_back_to_ncbi(self):
        """Corrupt XML in local cache for single-article path triggers NCBI fallback."""
        from metapub.localfetcher import make_local_fetcher_methods
        ncbi_art = self._make_article()
        backend = _make_backend(fetch_xml_return="<<corrupt xml>>")
        eutils = MagicMock(return_value=ncbi_art)
        article_by_pmid, _ = make_local_fetcher_methods(backend, eutils)
        art = article_by_pmid("27022295")
        self.assertIs(art, ncbi_art)
        eutils.assert_called_once_with("27022295")

    def test_articles_by_pmids_thread_safety(self):
        """Each thread gets its own result set; no cross-thread contamination."""
        from metapub.localfetcher import make_local_fetcher_methods
        backend = _make_backend(fetch_xml_many_return={27022295: _NLM_XML})
        eutils = MagicMock(return_value=None)
        _, articles_by_pmids = make_local_fetcher_methods(backend, eutils)

        results = {}
        errors = []

        def fetch(pmids, key):
            try:
                results[key] = articles_by_pmids(pmids)
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=fetch, args=(["27022295"], "t1")),
            threading.Thread(target=fetch, args=(["27022295"], "t2")),
            threading.Thread(target=fetch, args=(["27022295"], "t3")),
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertFalse(errors, f"Threads raised: {errors}")
        for key in ("t1", "t2", "t3"):
            self.assertIn("27022295", results[key])


class TestPubMedFetcherLocalWiring(unittest.TestCase):
    """PubMedFetcher picks up METAPUB_DB_URL and switches to local method."""

    @patch("metapub.localfetcher.HAS_PSYCOPG2", True)
    @patch("metapub.localfetcher.psycopg2")
    def test_env_var_activates_local_backend(self, mock_psycopg2):
        mock_psycopg2.Error = _Psycopg2Error
        mock_psycopg2.connect.return_value = MagicMock(closed=False)
        with patch.dict(os.environ, {"METAPUB_DB_URL": "postgresql://mock/mock"}):
            # Reset Borg state so a fresh instance is created
            from metapub.pubmedfetcher import PubMedFetcher
            PubMedFetcher._shared_state = {}
            f = PubMedFetcher()
            self.assertEqual(f.method, "local")
            self.assertTrue(callable(f.article_by_pmid))

    def test_no_env_var_stays_eutils(self):
        env = {k: v for k, v in os.environ.items() if k != "METAPUB_DB_URL"}
        with patch.dict(os.environ, env, clear=True):
            from metapub.pubmedfetcher import PubMedFetcher
            PubMedFetcher._shared_state = {}
            f = PubMedFetcher()
            self.assertEqual(f.method, "eutils")


if __name__ == "__main__":
    unittest.main()
