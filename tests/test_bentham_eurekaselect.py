"""Tests for Bentham Science Publishers (EurekaSelect.com) dance function.

This module tests the_eureka_frug dance function with different PMIDs
to verify various access scenarios and error handling.
"""

import pytest
from unittest.mock import patch, Mock
import requests

from metapub import PubMedFetcher
from metapub.findit.dances import the_eureka_frug
from metapub.exceptions import AccessDenied, NoPDFLink


class TestBenthamEurekaSelect:
    """Test cases for Bentham Science Publishers journal access."""

    def setup_method(self):
        """Set up test fixtures."""
        self.fetch = PubMedFetcher()

    def test_eureka_frug_available_article(self):
        """Test 1: Article potentially available (optimistic case).
        
        PMID: 38751602 (Current Genomics)
        Expected: Should construct valid URL without verification errors
        """
        pma = self.fetch.article_by_pmid('38751602')
        
        assert pma.journal == 'Curr Genomics'
        assert pma.doi == '10.2174/0113892029284920240212091903'
        
        # Test without verification (should always work for URL construction)
        url = the_eureka_frug(pma, verify=False)
        assert url is not None
        assert 'eurekaselect.com' in url
        assert '/pdf' in url or 'openurl.php' in url
        print(f"Test 1 - Constructed URL: {url}")

    @patch('requests.get')
    def test_eureka_frug_paywall_detected(self, mock_get):
        """Test 2: Article behind paywall (typical case).
        
        PMID: 38867537 (Current Molecular Medicine)
        Expected: Should detect paywall and raise AccessDenied
        """
        # Mock paywall response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.text = '<html><body>Please sign in to access this article. Subscribe now for full access.</body></html>'
        mock_response.url = 'https://www.eurekaselect.com/article/140986'
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('38867537')
        
        assert pma.journal == 'Curr Mol Med'
        assert pma.doi == '10.2174/0115665240310818240531080353'
        
        # Test with verification - should detect paywall
        with pytest.raises(AccessDenied) as exc_info:
            the_eureka_frug(pma, verify=True)
        
        assert 'PAYWALL' in str(exc_info.value)
        assert 'Bentham Science' in str(exc_info.value)
        print(f"Test 2 - Correctly detected paywall: {exc_info.value}")

    @patch('requests.get')
    def test_eureka_frug_server_error(self, mock_get):
        """Test 3: Server error or article not found.
        
        PMID: 38318823 (Current Topics in Medicinal Chemistry)
        Expected: Should handle server errors gracefully
        """
        # Mock server error response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.headers = {'content-type': 'text/html'}
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('38318823')
        
        assert pma.journal == 'Curr Top Med Chem'
        assert pma.doi is not None  # DOI may vary, just check it exists
        
        # Test with verification - should handle server error
        with pytest.raises(NoPDFLink) as exc_info:
            the_eureka_frug(pma, verify=True)
        
        assert 'TXERROR' in str(exc_info.value)
        assert 'status 500' in str(exc_info.value)
        print(f"Test 3 - Correctly handled server error: {exc_info.value}")

    def test_eureka_frug_no_doi(self):
        """Test edge case: Article without DOI.
        
        Expected: Should raise NoPDFLink for missing DOI
        """
        # Create a mock PMA without DOI
        pma = Mock()
        pma.doi = None
        pma.journal = 'Test Journal'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_eureka_frug(pma, verify=False)
        
        assert 'MISSING: DOI required' in str(exc_info.value)
        print(f"Test 4 - Correctly handled missing DOI: {exc_info.value}")

    @patch('requests.get')
    def test_eureka_frug_successful_pdf_access(self, mock_get):
        """Test optimistic case: Successful PDF access.
        
        This simulates the rare case where a Bentham article is freely accessible.
        """
        # Mock successful PDF response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'application/pdf'}
        mock_response.url = 'https://www.eurekaselect.com/article/123456/pdf'
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('38751602')
        
        # Test with verification - should succeed
        url = the_eureka_frug(pma, verify=True)
        assert url == 'https://www.eurekaselect.com/article/123456/pdf'
        print(f"Test 5 - Successful PDF access: {url}")


def test_bentham_journal_recognition():
    """Test that Bentham journals are properly recognized in the registry."""
    from metapub.findit.registry import JournalRegistry
    from metapub.findit.journals.eurekaselect import eurekaselect_journals, eurekaselect_template
    
    registry = JournalRegistry()
    
    # Ensure Bentham publisher exists in registry
    publisher_id = registry.add_publisher(
        name='Bentham Science Publishers',
        dance_function='the_eureka_frug', 
        format_template=eurekaselect_template
    )
    
    # Add test journals to registry
    test_journals = [
        'Curr Genomics',
        'Curr Mol Med', 
        'Curr Top Med Chem',
        'Antiinfect Agents',
        'Recent Pat Biotechnol'
    ]
    
    for journal in test_journals:
        if journal in eurekaselect_journals:
            registry.add_journal(journal, publisher_id)
    
    # Test journal recognition
    for journal in test_journals:
        if journal in eurekaselect_journals:
            publisher_info = registry.get_publisher_for_journal(journal)
            assert publisher_info is not None, f"Journal {journal} not found in registry"
            assert publisher_info['name'] == 'Bentham Science Publishers'
            assert publisher_info['dance_function'] == 'the_eureka_frug'
            print(f"✓ {journal} correctly mapped to Bentham Science Publishers")
        else:
            print(f"⚠ {journal} not in eurekaselect_journals list - skipping")
    
    registry.close()


if __name__ == '__main__':
    # Run basic tests if executed directly
    test_instance = TestBenthamEurekaSelect()
    test_instance.setup_method()
    
    print("Running Bentham Science Publishers tests...")
    print("\n" + "="*60)
    
    try:
        test_instance.test_eureka_frug_available_article()
        print("✓ Test 1 passed: URL construction works")
    except Exception as e:
        print(f"✗ Test 1 failed: {e}")
    
    try:
        test_instance.test_eureka_frug_paywall_detected()
        print("✓ Test 2 passed: Paywall detection works")
    except Exception as e:
        print(f"✗ Test 2 failed: {e}")
    
    try:
        test_instance.test_eureka_frug_server_error()
        print("✓ Test 3 passed: Server error handling works")
    except Exception as e:
        print(f"✗ Test 3 failed: {e}")
    
    try:
        test_instance.test_eureka_frug_no_doi()
        print("✓ Test 4 passed: Missing DOI handling works")
    except Exception as e:
        print(f"✗ Test 4 failed: {e}")
    
    try:
        test_instance.test_eureka_frug_successful_pdf_access()
        print("✓ Test 5 passed: Successful access simulation works")
    except Exception as e:
        print(f"✗ Test 5 failed: {e}")
    
    try:
        test_bentham_journal_recognition()
        print("✓ Registry test passed: Journal recognition works")
    except Exception as e:
        print(f"✗ Registry test failed: {e}")
    
    print("\n" + "="*60)
    print("Test suite completed!")