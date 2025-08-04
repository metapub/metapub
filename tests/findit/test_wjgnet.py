"""Tests for WJG Net (Baishideng Publishing Group) dance function."""

import pytest
from unittest.mock import patch, Mock
import requests

from .common import BaseDanceTest
from metapub import PubMedFetcher
from metapub.findit.dances import the_wjgnet_wave
from metapub.exceptions import AccessDenied, NoPDFLink


class TestWJGNetDance(BaseDanceTest):
    """Test cases for WJG Net (Baishideng Publishing Group)."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.fetch = PubMedFetcher()

    def test_wjgnet_wave_url_construction_gastroenterol(self):
        """Test 1: URL construction success (World J Gastroenterol).
        
        PMID: 38899335 (World J Gastroenterol)
        Expected: Should construct valid WJG Net PDF URL
        """
        pma = self.fetch.article_by_pmid('38899335')
        
        print(f"Test 1 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification (should always work for URL construction)
        url = the_wjgnet_wave(pma, verify=False)
        assert url is not None
        assert 'wjgnet.com' in url
        assert url.startswith('https://')
        print(f"Test 1 - PDF URL: {url}")

    def test_wjgnet_wave_url_construction_cardiol(self):
        """Test 2: World J Cardiol.
        
        PMID: 38817651 (World J Cardiol)
        Expected: Should construct valid WJG Net PDF URL
        """
        pma = self.fetch.article_by_pmid('38817651')
        
        print(f"Test 2 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Skip test if no DOI available
        if not pma.doi:
            print("Test 2 - Skipping: No DOI available for this PMID")
            return

        # Test without verification
        url = the_wjgnet_wave(pma, verify=False)
        assert url is not None
        assert 'wjgnet.com' in url
        print(f"Test 2 - PDF URL: {url}")

    def test_wjgnet_wave_url_construction_hepatol(self):
        """Test 3: World J Hepatol.
        
        PMID: 38818301 (World J Hepatol)
        Expected: Should construct valid WJG Net PDF URL
        """
        pma = self.fetch.article_by_pmid('38818301')
        
        print(f"Test 3 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Skip test if no DOI available
        if not pma.doi:
            print("Test 3 - Skipping: No DOI available for this PMID")
            return

        # Test without verification
        url = the_wjgnet_wave(pma, verify=False)
        assert url is not None
        assert 'wjgnet.com' in url
        print(f"Test 3 - PDF URL: {url}")

    @patch('requests.get')
    def test_wjgnet_wave_successful_access(self, mock_get):
        """Test 4: Successful PDF access simulation.
        
        Expected: Should return PDF URL when accessible
        """
        # Mock successful PDF response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.headers = {'content-type': 'application/pdf'}
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('38899335')
        
        # Test with verification - should succeed
        url = the_wjgnet_wave(pma, verify=True)
        assert 'wjgnet.com' in url
        print(f"Test 4 - Successful verified access: {url}")

    @patch('requests.get')
    def test_wjgnet_wave_paywall_detection(self, mock_get):
        """Test 5: Paywall detection.
        
        Expected: Should detect paywall and raise AccessDenied
        """
        # Mock paywall response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.text = '''<html><body>
            <h1>WJG Net</h1>
            <p>Login required for institutional access</p>
            <button>Subscribe to access</button>
        </body></html>'''
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('38899335')
        
        # Test with verification - should detect paywall
        with pytest.raises(AccessDenied) as exc_info:
            the_wjgnet_wave(pma, verify=True)
        
        assert 'PAYWALL' in str(exc_info.value)
        print(f"Test 5 - Correctly detected paywall: {exc_info.value}")

    @patch('requests.get')
    def test_wjgnet_wave_network_error(self, mock_get):
        """Test 6: Network error handling.
        
        Expected: Should handle network errors gracefully
        """
        # Mock network error
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

        pma = self.fetch.article_by_pmid('38899335')
        
        # Test - should handle network error
        with pytest.raises(NoPDFLink) as exc_info:
            the_wjgnet_wave(pma, verify=True)
        
        assert 'TXERROR' in str(exc_info.value)
        print(f"Test 6 - Correctly handled network error: {exc_info.value}")

    def test_wjgnet_wave_missing_doi(self):
        """Test 7: Article without DOI.
        
        Expected: Should raise NoPDFLink for missing DOI
        """
        # Create a mock PMA without DOI
        pma = Mock()
        pma.doi = None
        pma.journal = 'World J Gastroenterol'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_wjgnet_wave(pma, verify=False)
        
        assert 'MISSING' in str(exc_info.value)
        assert 'DOI required' in str(exc_info.value)
        print(f"Test 7 - Correctly handled missing DOI: {exc_info.value}")

    @patch('requests.get')
    def test_wjgnet_wave_404_error(self, mock_get):
        """Test 8: Article not found (404 error).
        
        Expected: Should try multiple patterns and handle 404 errors
        """
        # Mock 404 response for all attempts
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('38899335')
        
        # Test - should try multiple patterns and eventually fail
        with pytest.raises(NoPDFLink) as exc_info:
            the_wjgnet_wave(pma, verify=True)
        
        assert 'TXERROR' in str(exc_info.value) or 'PATTERN' in str(exc_info.value)
        print(f"Test 8 - Correctly handled 404: {exc_info.value}")

    @patch('requests.get')
    def test_wjgnet_wave_volume_issue_construction(self, mock_get):
        """Test 9: Volume/issue URL construction.
        
        Expected: Should use volume/issue in URL when available
        """
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.headers = {'content-type': 'application/pdf'}
        mock_get.return_value = mock_response

        # Create mock PMA with volume/issue data
        pma = Mock()
        pma.doi = '10.3748/wjg.v30.i1.123'
        pma.journal = 'World J Gastroenterol'
        pma.volume = '30'
        pma.issue = '1'
        
        # Test - should use volume/issue in URL
        url = the_wjgnet_wave(pma, verify=True)
        assert 'wjgnet.com' in url
        print(f"Test 9 - Volume/issue URL construction: {url}")

    def test_wjgnet_wave_multiple_doi_prefixes(self):
        """Test 10: Multiple DOI prefix handling.
        
        Expected: Should handle various DOI prefixes due to acquisitions
        """
        # Test different DOI prefixes that WJG Net might use
        test_dois = [
            '10.3748/wjg.v30.i1.123',      # Primary WJG Net DOI
            '10.1016/j.example.2023.123',   # Acquired journal DOI
            '10.1186/example-2023-456'      # Partnership DOI
        ]
        
        for doi in test_dois:
            pma = Mock()
            pma.doi = doi
            pma.journal = 'World J Gastroenterol'
            
            # Should construct URL regardless of DOI prefix
            url = the_wjgnet_wave(pma, verify=False)
            assert url is not None
            assert 'wjgnet.com' in url
            print(f"Test 10 - DOI {doi}: {url}")

    def test_wjgnet_wave_multiple_journals(self):
        """Test 11: Multiple WJG Net journal coverage.
        
        Expected: Should work with various World J ... journals
        """
        # Test different journal patterns
        test_journals = [
            'World J Gastroenterol',
            'World J Cardiol', 
            'World J Hepatol',
            'World J Diabetes',
            'World J Clin Cases'
        ]
        
        for journal in test_journals:
            pma = Mock()
            pma.doi = '10.3748/wjg.v30.i1.123'
            pma.journal = journal
            
            url = the_wjgnet_wave(pma, verify=False)
            assert url is not None
            assert 'wjgnet.com' in url
            print(f"Test 11 - {journal}: {url}")


def test_wjgnet_journal_recognition():
    """Test that WJG Net journals are properly recognized in the registry."""
    from metapub.findit.registry import JournalRegistry
    from metapub.findit.journals.wjgnet import wjgnet_journals
    
    registry = JournalRegistry()
    
    # Test sample WJG Net journals (using PubMed abbreviated names)
    test_journals = [
        'World J Gastroenterol',
        'World J Cardiol',
        'World J Hepatol',
        'World J Diabetes',
        'World J Clin Cases'
    ]
    
    # Test journal recognition
    found_count = 0
    for journal in test_journals:
        if journal in wjgnet_journals:
            publisher_info = registry.get_publisher_for_journal(journal)
            if publisher_info and publisher_info['name'] == 'wjgnet':
                assert publisher_info['dance_function'] == 'the_wjgnet_wave'
                print(f"✓ {journal} correctly mapped to WJG Net")
                found_count += 1
            else:
                print(f"⚠ {journal} mapped to different publisher: {publisher_info['name'] if publisher_info else 'None'}")
        else:
            print(f"⚠ {journal} not in wjgnet_journals list")
    
    # Just make sure we found at least one WJG Net journal
    assert found_count > 0, "No WJG Net journals found in registry with wjgnet publisher"
    print(f"✓ Found {found_count} properly mapped WJG Net journals")
    
    registry.close()


if __name__ == '__main__':
    # Run basic tests if executed directly
    test_instance = TestWJGNetDance()
    test_instance.setUp()
    
    print("Running WJG Net tests...")
    print("\n" + "="*60)
    
    tests = [
        ('test_wjgnet_wave_url_construction_gastroenterol', 'Gastroenterol URL construction'),
        ('test_wjgnet_wave_url_construction_cardiol', 'Cardiol URL construction'),
        ('test_wjgnet_wave_url_construction_hepatol', 'Hepatol URL construction'),
        ('test_wjgnet_wave_successful_access', 'Successful access simulation'),
        ('test_wjgnet_wave_paywall_detection', 'Paywall detection'),
        ('test_wjgnet_wave_network_error', 'Network error handling'),
        ('test_wjgnet_wave_missing_doi', 'Missing DOI handling'),
        ('test_wjgnet_wave_404_error', '404 error handling'),
        ('test_wjgnet_wave_volume_issue_construction', 'Volume/issue URL construction'),
        ('test_wjgnet_wave_doi_pattern_warning', 'Non-standard DOI pattern handling'),
        ('test_wjgnet_wave_multiple_journals', 'Multiple journal coverage')
    ]
    
    for test_method, description in tests:
        try:
            getattr(test_instance, test_method)()
            print(f"✓ {description} works")
        except Exception as e:
            print(f"✗ {description} failed: {e}")
    
    try:
        test_wjgnet_journal_recognition()
        print("✓ Registry test passed: Journal recognition works")
    except Exception as e:
        print(f"✗ Registry test failed: {e}")
    
    print("\n" + "="*60)
    print("Test suite completed!")