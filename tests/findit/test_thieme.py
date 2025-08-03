"""Tests for Thieme Medical Publishers dance function."""

import pytest
from unittest.mock import patch, Mock
import requests

from .common import BaseDanceTest
from metapub import PubMedFetcher
from metapub.findit.dances import the_thieme_tap
from metapub.exceptions import AccessDenied, NoPDFLink


class TestThiemeTap(BaseDanceTest):
    """Test cases for Thieme Medical Publishers journal access."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.fetch = PubMedFetcher()

    def test_thieme_tap_url_construction(self):
        """Test 1: URL construction success (recent article).
        
        PMID: 38740374 (Methods Inf Med)
        Expected: Should construct valid Thieme PDF URL
        """
        pma = self.fetch.article_by_pmid('38740374')
        
        assert pma.journal == 'Methods Inf Med'
        assert pma.doi == '10.1055/s-0044-1786839'
        
        # Test without verification (should always work for URL construction)
        url = the_thieme_tap(pma, verify=False)
        assert url is not None
        assert 'thieme-connect.de' in url
        assert '/products/ejournals/pdf/' in url
        assert pma.doi in url
        assert url.endswith('.pdf')
        
        expected_url = f"https://www.thieme-connect.de/products/ejournals/pdf/{pma.doi}.pdf"
        assert url == expected_url
        print(f"Test 1 - Constructed URL: {url}")

    def test_thieme_tap_older_article(self):
        """Test 2: Older article URL construction.
        
        PMID: 8309498 (Neurochirurgia (Stuttg))
        Expected: Should construct valid URL for older Thieme article
        """
        pma = self.fetch.article_by_pmid('8309498')
        
        assert pma.journal == 'Neurochirurgia (Stuttg)'
        assert pma.doi == '10.1055/s-2008-1053830'
        
        # Test URL construction for older article
        url = the_thieme_tap(pma, verify=False)
        assert url is not None
        assert 'thieme-connect.de' in url
        assert pma.doi in url
        assert url.endswith('.pdf')
        print(f"Test 2 - Older article URL: {url}")

    @patch('requests.get')
    def test_thieme_tap_successful_access(self, mock_get):
        """Test 3: Successful PDF access simulation.
        
        PMID: 38740374 (Methods Inf Med)
        Expected: Should return PDF URL when accessible
        """
        # Mock successful PDF response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'application/pdf'}
        mock_response.url = 'https://www.thieme-connect.de/products/ejournals/pdf/10.1055/s-0044-1786839.pdf'
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('38740374')
        
        # Test with verification - should succeed
        url = the_thieme_tap(pma, verify=True)
        assert url == mock_response.url
        assert 'thieme-connect.de' in url
        print(f"Test 3 - Successful access: {url}")

    @patch('requests.get')
    def test_thieme_tap_paywall_detection(self, mock_get):
        """Test 4: Paywall detection.
        
        PMID: 8309498 (Neurochirurgia (Stuttg))
        Expected: Should detect paywall and raise AccessDenied
        """
        # Mock paywall response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.text = '<html><body>Please log in to access this article. Subscribe for full access.</body></html>'
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('8309498')
        
        # Test with verification - should detect paywall
        with pytest.raises(AccessDenied) as exc_info:
            the_thieme_tap(pma, verify=True)
        
        assert 'PAYWALL' in str(exc_info.value)
        assert 'Thieme' in str(exc_info.value)
        print(f"Test 4 - Correctly detected paywall: {exc_info.value}")

    @patch('requests.get')
    def test_thieme_tap_not_found(self, mock_get):
        """Test 5: Article not found (404 error).
        
        PMID: 219391 (Neuropadiatrie - very old article)
        Expected: Should handle 404 errors gracefully
        """
        # Mock 404 response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.headers = {'content-type': 'text/html'}
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('219391')
        
        # Test with verification - should handle 404
        with pytest.raises(NoPDFLink) as exc_info:
            the_thieme_tap(pma, verify=True)
        
        assert 'TXERROR' in str(exc_info.value)
        assert 'not found' in str(exc_info.value)
        print(f"Test 5 - Correctly handled 404: {exc_info.value}")

    def test_thieme_tap_no_doi(self):
        """Test 6: Article without DOI.
        
        Expected: Should raise NoPDFLink for missing DOI
        """
        # Create a mock PMA without DOI
        pma = Mock()
        pma.doi = None
        pma.journal = 'Test Thieme Journal'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_thieme_tap(pma, verify=False)
        
        assert 'MISSING: DOI required' in str(exc_info.value)
        print(f"Test 6 - Correctly handled missing DOI: {exc_info.value}")

    @patch('requests.get')
    def test_thieme_tap_network_error(self, mock_get):
        """Test 7: Network error handling.
        
        Expected: Should handle network errors gracefully
        """
        # Mock network error
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

        pma = self.fetch.article_by_pmid('38740374')
        
        # Test with verification - should handle network error
        with pytest.raises(NoPDFLink) as exc_info:
            the_thieme_tap(pma, verify=True)
        
        assert 'TXERROR' in str(exc_info.value)
        assert 'Network error' in str(exc_info.value)
        print(f"Test 7 - Correctly handled network error: {exc_info.value}")


def test_thieme_journal_recognition():
    """Test that Thieme journals are properly recognized in the registry."""
    from metapub.findit.registry import JournalRegistry
    from metapub.findit.journals.thieme import thieme_journals, thieme_template
    
    registry = JournalRegistry()
    
    # Ensure Thieme publisher exists in registry
    publisher_id = registry.add_publisher(
        name='Thieme Medical Publishers',
        dance_function='the_thieme_tap',
        format_template=thieme_template
    )
    
    # Add test journals to registry
    test_journals = [
        'Methods Inf Med',
        'Neurochirurgia (Stuttg)',
        'Endoscopy',
        'Planta Med',
        'Semin Thromb Hemost'
    ]
    
    for journal in test_journals:
        if journal in thieme_journals:
            registry.add_journal(journal, publisher_id)
    
    # Test journal recognition
    for journal in test_journals:
        if journal in thieme_journals:
            publisher_info = registry.get_publisher_for_journal(journal)
            assert publisher_info is not None, f"Journal {journal} not found in registry"
            assert publisher_info['name'] == 'Thieme Medical Publishers'
            assert publisher_info['dance_function'] == 'the_thieme_tap'
            assert 'thieme-connect.de' in publisher_info['format_template']
            print(f"✓ {journal} correctly mapped to Thieme Medical Publishers")
        else:
            print(f"⚠ {journal} not in thieme_journals list - skipping")
    
    registry.close()


if __name__ == '__main__':
    # Run basic tests if executed directly
    test_instance = TestThiemeTap()
    test_instance.setUp()
    
    print("Running Thieme Medical Publishers tests...")
    print("\n" + "="*60)
    
    try:
        test_instance.test_thieme_tap_url_construction()
        print("✓ Test 1 passed: URL construction works")
    except Exception as e:
        print(f"✗ Test 1 failed: {e}")
    
    try:
        test_instance.test_thieme_tap_older_article()
        print("✓ Test 2 passed: Older article URL construction works")
    except Exception as e:
        print(f"✗ Test 2 failed: {e}")
    
    try:
        test_instance.test_thieme_tap_successful_access()
        print("✓ Test 3 passed: Successful access simulation works")
    except Exception as e:
        print(f"✗ Test 3 failed: {e}")
    
    try:
        test_instance.test_thieme_tap_paywall_detection()
        print("✓ Test 4 passed: Paywall detection works")
    except Exception as e:
        print(f"✗ Test 4 failed: {e}")
    
    try:
        test_instance.test_thieme_tap_not_found()
        print("✓ Test 5 passed: 404 error handling works")
    except Exception as e:
        print(f"✗ Test 5 failed: {e}")
    
    try:
        test_instance.test_thieme_tap_no_doi()
        print("✓ Test 6 passed: Missing DOI handling works")
    except Exception as e:
        print(f"✗ Test 6 failed: {e}")
    
    try:
        test_instance.test_thieme_tap_network_error()
        print("✓ Test 7 passed: Network error handling works")
    except Exception as e:
        print(f"✗ Test 7 failed: {e}")
    
    try:
        test_thieme_journal_recognition()
        print("✓ Registry test passed: Journal recognition works")
    except Exception as e:
        print(f"✗ Registry test failed: {e}")
    
    print("\n" + "="*60)
    print("Test suite completed!")