"""Tests for Inderscience Publishers dance function."""

import pytest
from unittest.mock import patch, Mock
import requests

from .common import BaseDanceTest
from metapub import PubMedFetcher
from metapub.findit.dances import the_inderscience_ula
from metapub.exceptions import AccessDenied, NoPDFLink


class TestInderscienceDance(BaseDanceTest):
    """Test cases for Inderscience Publishers."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.fetch = PubMedFetcher()

    def test_inderscience_ula_url_construction_biomed_eng(self):
        """Test 1: URL construction success (Int J Biomed Eng Technol).
        
        PMID: 23565122 (Int J Biomed Eng Technol)
        Expected: Should construct valid Inderscience PDF URL
        """
        pma = self.fetch.article_by_pmid('23565122')
        
        print(f"Test 1 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification (should always work for URL construction)
        url = the_inderscience_ula(pma, verify=False)
        assert url is not None
        assert 'inderscienceonline.com' in url
        assert '/doi/pdf/' in url
        assert url.startswith('https://')
        print(f"Test 1 - PDF URL: {url}")

    def test_inderscience_ula_url_construction_bioinform(self):
        """Test 2: Bioinformatics Research and Applications.
        
        PMID: 26642363 (Int J Bioinform Res Appl)
        Expected: Should construct valid Inderscience PDF URL
        """
        pma = self.fetch.article_by_pmid('26642363')
        
        print(f"Test 2 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Skip test if no DOI available
        if not pma.doi:
            print("Test 2 - Skipping: No DOI available for this PMID")
            return

        # Test without verification
        url = the_inderscience_ula(pma, verify=False)
        assert url is not None
        assert 'inderscienceonline.com' in url
        print(f"Test 2 - PDF URL: {url}")

    def test_inderscience_ula_url_construction_environ_pollut(self):
        """Test 3: Environmental Pollution.
        
        PMID: 31534305 (Int J Environ Pollut)
        Expected: Should construct valid Inderscience PDF URL
        """
        pma = self.fetch.article_by_pmid('31534305')
        
        print(f"Test 3 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Skip test if no DOI available
        if not pma.doi:
            print("Test 3 - Skipping: No DOI available for this PMID")
            return

        # Test without verification
        url = the_inderscience_ula(pma, verify=False)
        assert url is not None
        assert 'inderscienceonline.com' in url
        print(f"Test 3 - PDF URL: {url}")

    @patch('requests.get')
    def test_inderscience_ula_successful_access(self, mock_get):
        """Test 4: Successful PDF access simulation.
        
        Expected: Should return PDF URL when accessible
        """
        # Mock successful PDF response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.headers = {'content-type': 'application/pdf'}
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('23565122')
        
        # Test with verification - should succeed
        url = the_inderscience_ula(pma, verify=True)
        assert 'inderscienceonline.com' in url
        assert '/doi/pdf/' in url
        print(f"Test 4 - Successful verified access: {url}")

    @patch('requests.get')
    def test_inderscience_ula_paywall_detection(self, mock_get):
        """Test 5: Paywall detection.
        
        Expected: Should detect paywall and raise AccessDenied
        """
        # Mock paywall response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.text = '''<html><body>
            <h1>Subscription Required</h1>
            <p>Login required for institutional access</p>
            <button>Subscribe now</button>
        </body></html>'''
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('23565122')
        
        # Test with verification - should detect paywall
        with pytest.raises(AccessDenied) as exc_info:
            the_inderscience_ula(pma, verify=True)
        
        assert 'PAYWALL' in str(exc_info.value)
        print(f"Test 5 - Correctly detected paywall: {exc_info.value}")

    @patch('requests.get')
    def test_inderscience_ula_network_error(self, mock_get):
        """Test 6: Network error handling.
        
        Expected: Should handle network errors gracefully
        """
        # Mock network error
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

        pma = self.fetch.article_by_pmid('23565122')
        
        # Test - should handle network error
        with pytest.raises(NoPDFLink) as exc_info:
            the_inderscience_ula(pma, verify=True)
        
        assert 'TXERROR' in str(exc_info.value)
        print(f"Test 6 - Correctly handled network error: {exc_info.value}")

    def test_inderscience_ula_missing_doi(self):
        """Test 7: Article without DOI.
        
        Expected: Should raise NoPDFLink for missing DOI
        """
        # Create a mock PMA without DOI
        pma = Mock()
        pma.doi = None
        pma.journal = 'Int J Biomed Eng Technol'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_inderscience_ula(pma, verify=False)
        
        assert 'MISSING' in str(exc_info.value)
        assert 'DOI required' in str(exc_info.value)
        print(f"Test 7 - Correctly handled missing DOI: {exc_info.value}")

    @patch('requests.get')
    def test_inderscience_ula_404_error(self, mock_get):
        """Test 8: Article not found (404 error).
        
        Expected: Should try multiple patterns and handle 404 errors
        """
        # Mock 404 response for all attempts
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('23565122')
        
        # Test - should try multiple patterns and eventually fail
        with pytest.raises(NoPDFLink) as exc_info:
            the_inderscience_ula(pma, verify=True)
        
        assert 'TXERROR' in str(exc_info.value) or 'PATTERN' in str(exc_info.value)
        print(f"Test 8 - Correctly handled 404: {exc_info.value}")

    @patch('requests.get')
    def test_inderscience_ula_url_fallback(self, mock_get):
        """Test 9: URL pattern fallback.
        
        Expected: Should try different URL patterns until one works
        """
        # Mock responses: first fails, second succeeds
        responses = [
            Mock(ok=False, status_code=404),  # First URL fails
            Mock(ok=True, status_code=200, headers={'content-type': 'application/pdf'})  # Second succeeds
        ]
        mock_get.side_effect = responses

        pma = self.fetch.article_by_pmid('23565122')
        
        # Test - should succeed on second attempt
        url = the_inderscience_ula(pma, verify=True)
        assert 'inderscienceonline.com' in url
        print(f"Test 9 - URL fallback success: {url}")

    def test_inderscience_ula_doi_pattern_warning(self):
        """Test 10: Non-standard DOI pattern handling.
        
        Expected: Should handle non-10.1504 DOI patterns but may warn
        """
        # Create a mock PMA with non-Inderscience DOI pattern
        pma = Mock()
        pma.doi = '10.1016/j.example.2023.123456'  # Non-Inderscience DOI
        pma.journal = 'Int J Biomed Eng Technol'
        
        # Should still construct URL without verification
        url = the_inderscience_ula(pma, verify=False)
        assert url is not None
        assert 'inderscienceonline.com' in url
        print(f"Test 10 - Non-standard DOI pattern handled: {url}")


def test_inderscience_journal_recognition():
    """Test that Inderscience journals are properly recognized in the registry."""
    from metapub.findit.registry import JournalRegistry
    from metapub.findit.journals.inderscience import inderscience_journals
    
    registry = JournalRegistry()
    
    # Test sample Inderscience journals (using PubMed abbreviated names)
    test_journals = [
        'Int J Biomed Eng Technol',
        'Int J Bioinform Res Appl',
        'Int J Environ Pollut',
        'Int J Nanotechnol',
        'Botulinum J'
    ]
    
    # Test journal recognition
    found_count = 0
    for journal in test_journals:
        if journal in inderscience_journals:
            publisher_info = registry.get_publisher_for_journal(journal)
            if publisher_info and publisher_info['name'] == 'inderscience':
                assert publisher_info['dance_function'] == 'the_inderscience_ula'
                print(f"✓ {journal} correctly mapped to Inderscience Publishers")
                found_count += 1
            else:
                print(f"⚠ {journal} mapped to different publisher: {publisher_info['name'] if publisher_info else 'None'}")
        else:
            print(f"⚠ {journal} not in inderscience_journals list")
    
    # Just make sure we found at least one Inderscience journal
    assert found_count > 0, "No Inderscience journals found in registry with inderscience publisher"
    print(f"✓ Found {found_count} properly mapped Inderscience journals")
    
    registry.close()


if __name__ == '__main__':
    # Run basic tests if executed directly
    test_instance = TestInderscienceDance()
    test_instance.setUp()
    
    print("Running Inderscience Publishers tests...")
    print("\n" + "="*60)
    
    tests = [
        ('test_inderscience_ula_url_construction_biomed_eng', 'Biomed Eng Technol URL construction'),
        ('test_inderscience_ula_url_construction_bioinform', 'Bioinform Res Appl URL construction'),
        ('test_inderscience_ula_url_construction_environ_pollut', 'Environ Pollut URL construction'),
        ('test_inderscience_ula_successful_access', 'Successful access simulation'),
        ('test_inderscience_ula_paywall_detection', 'Paywall detection'),
        ('test_inderscience_ula_network_error', 'Network error handling'),
        ('test_inderscience_ula_missing_doi', 'Missing DOI handling'),
        ('test_inderscience_ula_404_error', '404 error handling'),
        ('test_inderscience_ula_url_fallback', 'URL pattern fallback'),
        ('test_inderscience_ula_doi_pattern_warning', 'Non-standard DOI pattern handling')
    ]
    
    for test_method, description in tests:
        try:
            getattr(test_instance, test_method)()
            print(f"✓ {description} works")
        except Exception as e:
            print(f"✗ {description} failed: {e}")
    
    try:
        test_inderscience_journal_recognition()
        print("✓ Registry test passed: Journal recognition works")
    except Exception as e:
        print(f"✗ Registry test failed: {e}")
    
    print("\n" + "="*60)
    print("Test suite completed!")