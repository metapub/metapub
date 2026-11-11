"""Regression tests for metapub/metapub#60.

While processing ~90,000 PMIDs, FindIt crashed the caller's batch run with:

  * "cannot access local variable 'pdfurl' where it is not associated with
    a value" -- JAMA/Archives articles (PMIDs 23754160, 23143457, 22987178,
    23754081). In the pre-refactor code the JAMA dance assigned ``pdfurl``
    inside a loop over the article page's ``<meta>`` tags, so a page with
    no ``citation_pdf_url`` tag left the name unbound and the ``return
    pdfurl`` after the loop raised UnboundLocalError.
  * "argument of type 'NoneType' is not iterable" -- Optica journals
    (PMIDs 37378086, 29400356, 38249122, 34239948, 38741706, 31825017).

Both errors escaped because ``find_article_from_pma`` only caught
``MetaPubError`` around its lookup steps, so any other exception
propagated out of ``FindIt`` and killed the batch. The registry dances
were later protected by the catch-all in
``handlers._dispatch_dance_function``, and the JAMA dance was rewritten
to raise ``NoPDFLink`` when no PDF meta tag is found -- but the
pre-registry steps (PMC twist, PMID formats, BMC) still let unexpected
exceptions propagate. These tests lock in the fix: an unexpected
exception in any pre-registry lookup step is recorded as a TXERROR
reason and lookup falls through to the next step instead of crashing.

All tests are fully offline (mocked articles and HTTP); no live network.
"""

from unittest.mock import Mock, patch

import requests

from .common import BaseDanceTest
from metapub import FindIt
from metapub.exceptions import NoPDFLink
from metapub.findit.dances import the_jama_dance
from metapub.findit.logic import _try_lookup_step, find_article_from_pma


def _mock_pma(journal, pmc=None, doi=None, pmid='12345678'):
    pma = Mock()
    pma.journal = journal
    pma.pmc = pmc
    pma.doi = doi
    pma.pmid = pmid
    pma.pii = None
    return pma


def _noformat_lookup_system():
    """A lookup system whose find_pdf_url returns a realistic NOFORMAT
    reason, as the real registry does for an unregistered journal."""
    system = Mock()
    system.find_pdf_url.return_value = (
        None, "NOFORMAT: No handler found for journal 'Opt Contin'. "
              "Report with sample PMID at https://github.com/metapub/metapub/issues")
    return system


class TestTryLookupStep(BaseDanceTest):
    """_try_lookup_step converts unexpected failures to TXERROR reasons."""

    def test_type_error_becomes_txerror(self):
        pma = _mock_pma('Opt Contin', pmc='10299805', pmid='37378086')
        url, reason = _try_lookup_step(
            'the_pmc_twist',
            Mock(side_effect=TypeError(
                "argument of type 'NoneType' is not iterable")),
            pma)
        self.assertIsNone(url)
        self.assertTrue(reason.startswith('TXERROR:'),
                        'expected TXERROR reason, got %r' % reason)
        self.assertIn('NoneType', reason)

    def test_chunked_encoding_error_becomes_txerror(self):
        pma = _mock_pma('Opt Contin', pmc='10299805', pmid='37378086')
        url, reason = _try_lookup_step(
            'the_pmc_twist',
            Mock(side_effect=requests.exceptions.ChunkedEncodingError(
                'Response ended prematurely')),
            pma)
        self.assertIsNone(url)
        self.assertTrue(reason.startswith('TXERROR:'),
                        'expected TXERROR reason, got %r' % reason)

    def test_unbound_local_error_becomes_txerror(self):
        pma = _mock_pma('Photonics Res', pmc='5791906', pmid='29400356')
        url, reason = _try_lookup_step(
            'the_pmc_twist',
            Mock(side_effect=UnboundLocalError(
                "cannot access local variable 'pdfurl' where it is "
                "not associated with a value")),
            pma)
        self.assertIsNone(url)
        self.assertTrue(reason.startswith('TXERROR:'),
                        'expected TXERROR reason, got %r' % reason)

    def test_metapub_error_passes_through_unchanged(self):
        # Expected "no PDF here" signals keep their original reason.
        pma = _mock_pma('Opt Contin', pmc='10299805', pmid='37378086')
        url, reason = _try_lookup_step(
            'the_pmc_twist',
            Mock(side_effect=NoPDFLink(
                'TXERROR: could not get PDF from EuropePMC.org')),
            pma)
        self.assertIsNone(url)
        self.assertEqual(
            reason, 'TXERROR: could not get PDF from EuropePMC.org')

    def test_success_returns_url(self):
        pma = _mock_pma('Opt Contin', pmc='10299805', pmid='37378086')
        url, reason = _try_lookup_step(
            'the_pmc_twist',
            Mock(return_value='https://example.org/article.pdf'),
            pma)
        self.assertEqual(url, 'https://example.org/article.pdf')
        self.assertIsNone(reason)


class TestIssue60LookupSteps(BaseDanceTest):
    """Unexpected exceptions in pre-registry lookup steps must not crash
    find_article_from_pma / FindIt; lookup falls through to the registry."""

    def test_pmc_twist_type_error_returns_txerror(self):
        # PMID 37378086 (Opt Contin): the issue's "NoneType is not iterable".
        # The PMC step's TXERROR is superseded by the registry's NOFORMAT
        # for an unregistered journal (pre-existing reason precedence) --
        # the regression is that the call returns instead of raising.
        pma = _mock_pma('Opt Contin', pmc='10299805',
                        doi='10.1364/optcon.469219', pmid='37378086')
        with patch('metapub.findit.logic.the_pmc_twist',
                   side_effect=TypeError("argument of type 'NoneType' is not iterable")), \
             patch('metapub.findit.logic._get_lookup_system',
                   return_value=_noformat_lookup_system()):
            url, reason = find_article_from_pma(pma)
        self.assertIsNone(url)
        self.assertIn('NOFORMAT', reason)

    def test_pmc_twist_chunked_encoding_error_returns_txerror(self):
        # A truncated chunked response from EuropePMC must not kill the run.
        pma = _mock_pma('Opt Quantum', pmc='11089896',
                        doi='10.1364/opticaq.502464', pmid='38741706')
        with patch('metapub.findit.logic.the_pmc_twist',
                   side_effect=requests.exceptions.ChunkedEncodingError(
                       'Response ended prematurely')), \
             patch('metapub.findit.logic._get_lookup_system',
                   return_value=_noformat_lookup_system()):
            url, reason = find_article_from_pma(pma)
        self.assertIsNone(url)
        self.assertIn('NOFORMAT', reason)

    def test_pmc_twist_unbound_local_error_returns_txerror(self):
        pma = _mock_pma('Photonics Res', pmc='5791906',
                        doi='10.1364/PRJ.5.000176', pmid='29400356')
        with patch('metapub.findit.logic.the_pmc_twist',
                   side_effect=UnboundLocalError(
                       "cannot access local variable 'pdfurl' where it is "
                       "not associated with a value")), \
             patch('metapub.findit.logic._get_lookup_system',
                   return_value=_noformat_lookup_system()):
            url, reason = find_article_from_pma(pma)
        self.assertIsNone(url)
        self.assertIn('NOFORMAT', reason)

    def test_pmc_twist_failure_falls_through_to_registry(self):
        # Without the mocked lookup system, the real registry is consulted
        # and likewise returns NOFORMAT for the unregistered journal.
        pma = _mock_pma('Opt Contin', pmc='10299805',
                        doi='10.1364/optcon.469219', pmid='37378086')
        with patch('metapub.findit.logic.the_pmc_twist',
                   side_effect=TypeError("argument of type 'NoneType' is not iterable")):
            url, reason = find_article_from_pma(pma)
        self.assertIsNone(url)
        self.assertIn('NOFORMAT', reason)

    def test_pmid_pogo_unexpected_error_returns_txerror(self):
        # 'Medicina (B Aires)' is the only journal in simple_formats_pmid.
        pma = _mock_pma('Medicina (B Aires)', pmc=None, pmid='87654321')
        with patch('metapub.findit.logic.the_pmid_pogo',
                   side_effect=TypeError("argument of type 'NoneType' is not iterable")), \
             patch('metapub.findit.logic._get_lookup_system',
                   return_value=_noformat_lookup_system()):
            url, reason = find_article_from_pma(pma)
        self.assertIsNone(url)
        self.assertIn('NOFORMAT', reason)

    def test_bmc_boogie_unexpected_error_returns_txerror(self):
        pma = _mock_pma('BMC Genomics', pmc=None,
                        doi='10.1186/s12864-023-09123-4', pmid='11223344')
        with patch('metapub.findit.logic.the_bmc_boogie',
                   side_effect=TypeError("argument of type 'NoneType' is not iterable")), \
             patch('metapub.findit.logic._get_lookup_system',
                   return_value=_noformat_lookup_system()):
            url, reason = find_article_from_pma(pma)
        self.assertIsNone(url)
        self.assertIn('NOFORMAT', reason)

    def test_findit_survives_pmc_twist_type_error(self):
        # End-to-end through the public FindIt entry point: PMID 37378086
        # must come back with url=None and a reason, not raise.
        pma = _mock_pma('Opt Contin', pmc='10299805',
                        doi='10.1364/optcon.469219', pmid='37378086')
        # article_by_pmid is bound to _eutils_article_by_pmid at
        # PubMedFetcher.__init__ time, so patch the underlying method:
        # FindIt.__init__ builds a fresh fetcher inside the patch.
        with patch('metapub.pubmedfetcher.PubMedFetcher._eutils_article_by_pmid',
                   return_value=pma), \
             patch('metapub.findit.logic.the_pmc_twist',
                   side_effect=TypeError("argument of type 'NoneType' is not iterable")):
            source = FindIt(pmid='37378086', cachedir=None)
        self.assertIsNone(source.url)
        self.assertIsNotNone(source.reason)


class TestIssue60JamaDance(BaseDanceTest):
    """The JAMA dance must raise NoPDFLink -- never UnboundLocalError --
    when the article page has no citation_pdf_url meta tag (#60)."""

    _HTML_NO_PDF_META = (
        b'<html><head>'
        b'<meta name="citation_title" content="Some JAMA article">'
        b'<meta name="citation_author" content="Smith J">'
        b'</head><body><p>No PDF here.</p></body></html>'
    )
    _HTML_WITH_PDF_META = (
        b'<html><head>'
        b'<meta name="citation_title" content="Some JAMA article">'
        b'<meta name="citation_pdf_url" '
        b'content="https://jamanetwork.com/data/Journals/OFT/12345/test.pdf">'
        b'</head><body></body></html>'
    )

    def _run_jama_dance(self, html_content):
        # PMID 23754160: Arch Ophthalmol, 10.1001/archophthalmol.2012.1702.
        pma = _mock_pma('Arch Ophthalmol', pmc=None,
                        doi='10.1001/archophthalmol.2012.1702', pmid='23754160')
        response = Mock()
        response.content = html_content
        with patch('metapub.findit.dances.jama.get_crossref_pdf_links',
                   return_value=[]), \
             patch('metapub.findit.dances.jama.the_doi_2step',
                   return_value='https://jamanetwork.com/journals/'
                                'jamaophthalmology/fullarticle/123'), \
             patch('metapub.findit.dances.jama.unified_uri_get',
                   return_value=response):
            return the_jama_dance(pma, verify=False)

    def test_page_without_pdf_meta_raises_nopdflink(self):
        # The exact 2024 crash scenario: no citation_pdf_url tag in the
        # page. Old code raised UnboundLocalError('pdfurl'); current code
        # must raise NoPDFLink.
        with self.assertRaises(NoPDFLink) as ctx:
            self._run_jama_dance(self._HTML_NO_PDF_META)
        self.assertIn('did not provide PDF link', str(ctx.exception))

    def test_page_with_pdf_meta_returns_url(self):
        url = self._run_jama_dance(self._HTML_WITH_PDF_META)
        self.assertEqual(
            url, 'https://jamanetwork.com/data/Journals/OFT/12345/test.pdf')
