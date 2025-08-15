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
        print(f"Test 3 - Mock PDF URL: {url}")

    @patch('metapub.findit.dances.jci.verify_pdf_url')
    def test_jci_jig_successful_pdf_access(self, mock_verify):
        """Test 4: Successful PDF access simulation.
        
        PMID: 26030226 (J Clin Invest)
        Expected: Should return PDF URL when accessible
        """
        # Mock successful PDF verification
        mock_verify.return_value = True

        pma = self.fetch.article_by_pmid('26030226')
        
        # Test with verification - should succeed
        url = the_jci_jig(pma, verify=True)
        assert 'jci.org' in url
        assert '/articles/view/' in url
        print(f"Test 4 - Successful verified access: {url}")

    @patch('metapub.findit.dances.jci.unified_uri_get')
    def test_jci_jig_html_response_handling(self, mock_get):
        """Test 5: JCI returning HTML instead of PDF (common case).
        
        Expected: Should handle HTML response gracefully and return URL
        """
        # Mock HTML response (JCI often returns HTML even for PDF URLs)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.headers = {'content-type': 'text/html; charset=utf-8'}
        mock_response.url = 'http://www.jci.org/articles/view/82041/files/pdf'
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('26030226')
        
        # Test with verification - should handle HTML response gracefully
        url = the_jci_jig(pma, verify=True)
        assert url == 'http://www.jci.org/articles/view/82041/files/pdf'
        print(f"Test 5 - HTML response handled gracefully: {url}")

    @patch('metapub.findit.dances.jci.verify_pdf_url')
    def test_jci_jig_access_denied(self, mock_verify):
        """Test 6: Access forbidden (403 error).
        
        Expected: Should handle 403 errors properly
        """
        # Mock access denied
        mock_verify.side_effect = NoPDFLink("DENIED: access forbidden")

        pma = self.fetch.article_by_pmid('26030226')
        
        # Test with verification - should handle 403
        with pytest.raises(NoPDFLink) as exc_info:
            the_jci_jig(pma, verify=True)
        
        assert 'DENIED' in str(exc_info.value) or 'TXERROR' in str(exc_info.value)
        print(f"Test 6 - Correctly handled 403: {exc_info.value}")

    @patch('metapub.findit.dances.jci.verify_pdf_url')
    def test_jci_jig_network_error(self, mock_verify):
        """Test 7: Network error handling.
        
        Expected: Should handle network errors gracefully
        """
        # Mock network error
        mock_verify.side_effect = requests.exceptions.ConnectionError("Network error")

        pma = self.fetch.article_by_pmid('26030226')
        
        # Test - should handle network error
        with pytest.raises(requests.exceptions.ConnectionError):
            the_jci_jig(pma, verify=True)
        print("Test 7 - Correctly handled network error")

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
        print(f"Test 9 - DOI fallback with redirect: {url}")


def test_jci_journal_recognition():
    """Test that JCI journals are properly recognized in the registry."""
    from metapub.findit.registry import JournalRegistry
    from metapub.findit.journals.jci import jci_journals
    
    registry = JournalRegistry()
    
    # Test JCI journal
    test_journals = [
        'J Clin Invest'
    ]
    
    # Test journal recognition
    found_count = 0
    for journal in test_journals:
        publisher_info = registry.get_publisher_for_journal(journal)
        if publisher_info and publisher_info['name'] == 'jci':
            assert publisher_info['dance_function'] == 'the_jci_jig'
            print(f"✓ {journal} correctly mapped to JCI")
            found_count += 1
        else:
            print(f"⚠ {journal} mapped to different publisher: {publisher_info['name'] if publisher_info else 'None'}")
    
    # Just make sure we found at least one JCI journal
    assert found_count > 0, "No JCI journals found in registry with jci publisher"
    print(f"✓ Found {found_count} properly mapped JCI journals")
    
    registry.close()


if __name__ == '__main__':
    # Run basic tests if executed directly
    test_instance = TestJCIDance()
    test_instance.setUp()
    
    print("Running JCI (Journal of Clinical Investigation) tests...")
    print("\n" + "="*60)
    
    tests = [
        ('test_jci_jig_url_construction_with_pii', 'URL construction with PII'),
        ('test_jci_jig_url_construction_with_doi_fallback', 'URL construction with DOI fallback'),
        ('test_jci_jig_different_article_pattern', 'Different article patterns'),
        ('test_jci_jig_successful_pdf_access', 'Successful access simulation'),
        ('test_jci_jig_html_response_handling', 'HTML response handling'),
        ('test_jci_jig_access_denied', 'Access denied handling'),
        ('test_jci_jig_network_error', 'Network error handling'),
        ('test_jci_jig_missing_data', 'Missing data handling'),
        ('test_jci_jig_doi_fallback_with_redirect', 'DOI fallback with redirect')
    ]
    
    for test_method, description in tests:
        try:
            getattr(test_instance, test_method)()
            print(f"✓ {description} works")
        except Exception as e:
            print(f"✗ {description} failed: {e}")
    
    try:
        test_jci_journal_recognition()
        print("✓ Registry test passed: Journal recognition works")
    except Exception as e:
        print(f"✗ Registry test failed: {e}")
    
    print("\n" + "="*60)
    print("Test suite completed!")


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