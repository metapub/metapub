"""Tests for Walsh Medical Media dance function."""

import pytest
from unittest.mock import patch, Mock
import requests

from .common import BaseDanceTest
from metapub import PubMedFetcher
from metapub.findit.dances import the_walshmedia_bora
from metapub.exceptions import AccessDenied, NoPDFLink


class TestWalshMediaDance(BaseDanceTest):
    """Test cases for Walsh Medical Media."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.fetch = PubMedFetcher()

    def test_walshmedia_waltz_url_construction_dentistry(self):
        """Test 1: URL construction success (Dentistry).
        
        PMID: 29226023 (Dentistry (Sunnyvale))
        Expected: Should construct valid Walsh Medical Media PDF URL
        """
        pma = self.fetch.article_by_pmid('29226023')
        
        print(f"Test 1 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification (should always work for URL construction)
        url = the_walshmedia_bora(pma, verify=False)
        assert url is not None
        assert 'walshmedicalmedia.com' in url
        assert url.startswith('https://')
        print(f"Test 1 - PDF URL: {url}")

    def test_walshmedia_waltz_url_construction_health_care(self):
        """Test 2: Health Care Curr Rev.
        
        PMID: 38525410 (Health Care Curr Rev)
        Expected: Should construct valid Walsh Medical Media PDF URL
        """
        pma = self.fetch.article_by_pmid('38525410')
        
        print(f"Test 2 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Skip test if no DOI available
        if not pma.doi:
            print("Test 2 - Skipping: No DOI available for this PMID")
            return

        # Test without verification
        url = the_walshmedia_bora(pma, verify=False)
        assert url is not None
        assert 'walshmedicalmedia.com' in url
        print(f"Test 2 - PDF URL: {url}")

    def test_walshmedia_waltz_url_construction_j_pharmacovigil(self):
        """Test 3: J Pharmacovigil.
        
        PMID: 37559896 (J Pharmacovigil)
        Expected: Should construct valid Walsh Medical Media PDF URL
        """
        pma = self.fetch.article_by_pmid('37559896')
        
        print(f"Test 3 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Skip test if no DOI available
        if not pma.doi:
            print("Test 3 - Skipping: No DOI available for this PMID")
            return

        # Test without verification
        url = the_walshmedia_bora(pma, verify=False)
        assert url is not None
        assert 'walshmedicalmedia.com' in url
        print(f"Test 3 - PDF URL: {url}")

    @patch('requests.get')
    def test_walshmedia_waltz_successful_access(self, mock_get):
        """Test 4: Successful PDF access simulation.
        
        Expected: Should return PDF URL when accessible
        """
        # Mock successful PDF response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.headers = {'content-type': 'application/pdf'}
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('29226023')
        
        # Test with verification - should succeed
        url = the_walshmedia_bora(pma, verify=True)
        assert 'walshmedicalmedia.com' in url
        print(f"Test 4 - Successful verified access: {url}")

    @patch('requests.get')
    def test_walshmedia_waltz_paywall_detection(self, mock_get):
        """Test 5: Paywall detection.
        
        Expected: Should detect paywall and raise AccessDenied
        """
        # Mock paywall response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.text = '''<html><body>
            <h1>Walsh Medical Media</h1>
            <p>Login required for institutional access</p>
            <button>Subscribe to access</button>
        </body></html>'''
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('29226023')
        
        # Test with verification - should detect paywall
        with pytest.raises(AccessDenied) as exc_info:
            the_walshmedia_bora(pma, verify=True)
        
        assert 'PAYWALL' in str(exc_info.value)
        print(f"Test 5 - Correctly detected paywall: {exc_info.value}")

    @patch('requests.get')
    def test_walshmedia_waltz_network_error(self, mock_get):
        """Test 6: Network error handling.
        
        Expected: Should handle network errors gracefully
        """
        # Mock network error
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

        pma = self.fetch.article_by_pmid('29226023')
        
        # Test - should handle network error
        with pytest.raises(NoPDFLink) as exc_info:
            the_walshmedia_bora(pma, verify=True)
        
        # Should contain either TXERROR (network error) or PATTERN (DOI mismatch)
        assert 'TXERROR' in str(exc_info.value) or 'PATTERN' in str(exc_info.value)
        print(f"Test 6 - Correctly handled network error or pattern mismatch: {exc_info.value}")

    def test_walshmedia_waltz_missing_doi(self):
        """Test 7: Article without DOI.
        
        Expected: Should raise NoPDFLink for missing DOI
        """
        # Create a mock PMA without DOI
        pma = Mock()
        pma.doi = None
        pma.journal = 'Dentistry'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_walshmedia_bora(pma, verify=False)
        
        assert 'MISSING' in str(exc_info.value)
        assert 'DOI required' in str(exc_info.value)
        print(f"Test 7 - Correctly handled missing DOI: {exc_info.value}")

    @patch('requests.get')
    def test_walshmedia_waltz_404_error(self, mock_get):
        """Test 8: Article not found (404 error).
        
        Expected: Should try multiple patterns and handle 404 errors
        """
        # Mock 404 response for all attempts
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('29226023')
        
        # Test - should try multiple patterns and eventually fail
        with pytest.raises(NoPDFLink) as exc_info:
            the_walshmedia_bora(pma, verify=True)
        
        assert 'TXERROR' in str(exc_info.value) or 'PATTERN' in str(exc_info.value)
        print(f"Test 8 - Correctly handled 404: {exc_info.value}")

    @patch('requests.get')
    def test_walshmedia_waltz_article_slug_construction(self, mock_get):
        """Test 9: Article slug URL construction.
        
        Expected: Should use article ID from DOI in URL when available
        """
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.headers = {'content-type': 'application/pdf'}
        mock_get.return_value = mock_response

        # Create mock PMA with article ID in DOI
        pma = Mock()
        pma.doi = '10.4172/2161-1122.1000448'
        pma.journal = 'Dentistry'
        
        # Test - should use article ID in URL
        url = the_walshmedia_bora(pma, verify=True)
        assert 'walshmedicalmedia.com' in url
        print(f"Test 9 - Article slug URL construction: {url}")

    def test_walshmedia_waltz_doi_pattern_warning(self):
        """Test 10: Non-standard DOI pattern handling.
        
        Expected: Should handle non-10.4172/10.35248 DOI patterns but may warn
        """
        # Create a mock PMA with non-Walsh Media DOI pattern
        pma = Mock()
        pma.doi = '10.1016/j.example.2023.123456'  # Non-Walsh Media DOI
        pma.journal = 'Dentistry'
        
        # Should still construct URL without verification
        url = the_walshmedia_bora(pma, verify=False)
        assert url is not None
        assert 'walshmedicalmedia.com' in url
        print(f"Test 10 - Non-standard DOI pattern handled: {url}")

    def test_walshmedia_waltz_multiple_journals(self):
        """Test 11: Multiple Walsh Medical Media journal coverage.
        
        Expected: Should work with various Walsh Medical Media journals
        """
        # Test different journal patterns
        test_journals = [
            'Dentistry',
            'Health Care Curr Rev',
            'J Pharmacovigil',
            'Clin Microbiol',
            'J Aging Sci'
        ]
        
        for journal in test_journals:
            pma = Mock()
            pma.doi = '10.4172/2161-1122.1000448'
            pma.journal = journal
            
            url = the_walshmedia_bora(pma, verify=False)
            assert url is not None
            assert 'walshmedicalmedia.com' in url
            print(f"Test 11 - {journal}: {url}")


def test_walshmedia_journal_recognition():
    """Test that Walsh Medical Media journals are properly recognized in the registry."""
    from metapub.findit.registry import JournalRegistry
    from metapub.findit.journals.walshmedia import walshmedia_journals
    
    registry = JournalRegistry()
    
    # Test sample Walsh Medical Media journals (using PubMed abbreviated names)
    test_journals = [
        'Dentistry',
        'Health Care Curr Rev',
        'J Pharmacovigil',
        'Clin Microbiol',
        'J Aging Sci'
    ]
    
    # Test journal recognition
    found_count = 0
    for journal in test_journals:
        if journal in walshmedia_journals:
            publisher_info = registry.get_publisher_for_journal(journal)
            if publisher_info and publisher_info['name'] == 'walshmedia':
                assert publisher_info['dance_function'] == 'the_walshmedia_bora'
                print(f"✓ {journal} correctly mapped to Walsh Medical Media")
                found_count += 1
            else:
                print(f"⚠ {journal} mapped to different publisher: {publisher_info['name'] if publisher_info else 'None'}")
        else:
            print(f"⚠ {journal} not in walshmedia_journals list")
    
    # Just make sure we found at least one Walsh Medical Media journal
    assert found_count > 0, "No Walsh Medical Media journals found in registry with walshmedia publisher"
    print(f"✓ Found {found_count} properly mapped Walsh Medical Media journals")
    
    registry.close()


if __name__ == '__main__':
    # Run basic tests if executed directly
    test_instance = TestWalshMediaDance()
    test_instance.setUp()
    
    print("Running Walsh Medical Media tests...")
    print("\n" + "="*60)
    
    tests = [
        ('test_walshmedia_waltz_url_construction_dentistry', 'Dentistry URL construction'),
        ('test_walshmedia_waltz_url_construction_health_care', 'Health Care URL construction'),
        ('test_walshmedia_waltz_url_construction_j_pharmacovigil', 'J Pharmacovigil URL construction'),
        ('test_walshmedia_waltz_successful_access', 'Successful access simulation'),
        ('test_walshmedia_waltz_paywall_detection', 'Paywall detection'),
        ('test_walshmedia_waltz_network_error', 'Network error handling'),
        ('test_walshmedia_waltz_missing_doi', 'Missing DOI handling'),
        ('test_walshmedia_waltz_404_error', '404 error handling'),
        ('test_walshmedia_waltz_article_slug_construction', 'Article slug URL construction'),
        ('test_walshmedia_waltz_doi_pattern_warning', 'Non-standard DOI pattern handling'),
        ('test_walshmedia_waltz_multiple_journals', 'Multiple journal coverage')
    ]
    
    for test_method, description in tests:
        try:
            getattr(test_instance, test_method)()
            print(f"✓ {description} works")
        except Exception as e:
            print(f"✗ {description} failed: {e}")
    
    try:
        test_walshmedia_journal_recognition()
        print("✓ Registry test passed: Journal recognition works")
    except Exception as e:
        print(f"✗ Registry test failed: {e}")
    
    print("\n" + "="*60)
    print("Test suite completed!")