"""Tests for JCI (Journal of Clinical Investigation) dance function."""

import pytest
from unittest.mock import patch, Mock
import requests

from .common import BaseDanceTest
from metapub import PubMedFetcher
from metapub.findit.dances import the_jci_jig
from metapub.exceptions import AccessDenied, NoPDFLink
from tests.fixtures import load_pmid_xml, JCI_EVIDENCE_PMIDS

class TestJCIDance(BaseDanceTest):
    """Test cases for JCI (Journal of Clinical Investigation)."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.fetch = PubMedFetcher()

    def test_jci_jig_url_construction_with_pii(self):
        """Test 1: URL construction success using PII (recent article).
        
        PMID: 26030226 (J Clin Invest)
        Expected: Should construct valid JCI PDF URL using PII
        """
        pma = self.fetch.article_by_pmid('26030226')
        
        assert pma.journal == 'J Clin Invest'
        assert pma.doi == '10.1172/JCI82041'
        assert pma.pii == '82041'
        print(f"Test 1 - Article info: {pma.journal}, PII: {pma.pii}, DOI: {pma.doi}")

        # Test without verification (should always work for URL construction)
        url = the_jci_jig(pma, verify=False)
        assert url is not None
        assert url == 'http://www.jci.org/articles/view/82041/files/pdf'
        assert 'jci.org' in url
        assert '/articles/view/' in url
        assert '/files/pdf' in url
        print(f"Test 1 - PDF URL: {url}")

    def test_jci_jig_url_construction_with_doi_fallback(self):
        """Test 2: URL construction using DOI fallback (older article without PII).
        
        PMID: 15902306 (J Clin Invest, 2005)
        Expected: Should construct valid JCI PDF URL using DOI fallback
        """
        pma = self.fetch.article_by_pmid('15902306')
        
        assert pma.journal == 'J Clin Invest'
        assert pma.doi == '10.1172/JCI23606'
        assert pma.pii is None  # This older article doesn't have PII
        print(f"Test 2 - Article info: {pma.journal}, PII: {pma.pii}, DOI: {pma.doi}")

        # Test without verification
        url = the_jci_jig(pma, verify=False)
        assert url is not None
        assert 'jci.org' in url
        assert '/articles/view/' in url
        assert '/files/pdf' in url
        print(f"Test 2 - PDF URL: {url}")

    def test_jci_jig_different_article_pattern(self):
        """Test 3: Test with a mock article to ensure different patterns work.
        
        Expected: Should handle different JCI article patterns
        """
        # Create a mock PMA with different JCI data
        pma = Mock()
        pma.pii = '12345'
        pma.doi = '10.1172/JCI12345'
        pma.journal = 'J Clin Invest'
        
        url = the_jci_jig(pma, verify=False)
        assert url == 'http://www.jci.org/articles/view/12345/files/pdf'
        print(f"Test 3 - Mock PDF URL: {url}")    # Test removed: test_jci_jig_successful_pdf_access - functionality now handled by verify_pdf_url    # Test removed: test_jci_jig_html_response_handling - functionality now handled by verify_pdf_url    # Test removed: test_jci_jig_access_denied - functionality now handled by verify_pdf_url    # Test removed: test_jci_jig_network_error - functionality now handled by verify_pdf_url

    def test_jci_jig_missing_data(self):
        """Test 8: Article without PII or DOI.
        
        Expected: Should raise NoPDFLink for missing data
        """
        # Create a mock PMA without PII or DOI
        pma = Mock()
        pma.pii = None
        pma.doi = None
        pma.journal = 'J Clin Invest'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_jci_jig(pma, verify=False)
        
        assert 'MISSING' in str(exc_info.value)
        assert 'pii or doi needed' in str(exc_info.value)
        print(f"Test 8 - Correctly handled missing data: {exc_info.value}")

    @patch('metapub.findit.dances.jci.the_doi_2step')
    def test_jci_jig_doi_fallback_with_redirect(self, mock_doi_2step):
        """Test 9: DOI fallback with redirect handling.
        
        Expected: Should handle DOI redirect to JCI article page properly
        """
        # Mock DOI resolution to JCI article page
        mock_doi_2step.return_value = 'http://www.jci.org/articles/view/23606'
        
        pma = Mock()
        pma.pii = None
        pma.doi = '10.1172/JCI23606'
        pma.journal = 'J Clin Invest'
        
        url = the_jci_jig(pma, verify=False)
        assert url == 'http://www.jci.org/articles/view/23606/files/pdf'
        print(f"Test 9 - DOI fallback with redirect: {url}")    # Test removed: test_jci_journal_recognition - functionality now handled by verify_pdf_url

class TestJCIXMLFixtures:
    """Test JCI XML fixtures for evidence-driven testing."""

    @patch('metapub.findit.dances.jci.verify_pdf_url')
    def test_jci_xml_37966116_j_clin_invest(self, mock_verify):
        """Test PMID 37966116 - J Clin Invest with DOI 10.1172/JCI170500."""
        mock_verify.return_value = None
        pma = load_pmid_xml('37966116')
        
        assert pma.pmid == '37966116'
        assert pma.doi == '10.1172/JCI170500'
        assert 'J Clin Invest' in pma.journal
        
        result = the_jci_jig(pma, verify=True)
        expected_url = 'http://www.jci.org/articles/view/170500/files/pdf'
        assert result == expected_url
        mock_verify.assert_called_once_with(expected_url, 'JCI', request_timeout=10, max_redirects=3)

    @patch('metapub.findit.dances.jci.verify_pdf_url')
    def test_jci_xml_35358095_j_clin_invest(self, mock_verify):
        """Test PMID 35358095 - J Clin Invest with DOI 10.1172/JCI154225."""
        mock_verify.return_value = None
        pma = load_pmid_xml('35358095')
        
        assert pma.pmid == '35358095'
        assert pma.doi == '10.1172/JCI154225'
        assert 'J Clin Invest' in pma.journal
        
        result = the_jci_jig(pma, verify=True)
        expected_url = 'http://www.jci.org/articles/view/154225/files/pdf'
        assert result == expected_url
        mock_verify.assert_called_once_with(expected_url, 'JCI', request_timeout=10, max_redirects=3)