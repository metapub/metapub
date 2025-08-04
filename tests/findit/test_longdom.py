"""Tests for Longdom Publishing dance function."""

import pytest
from unittest.mock import patch, Mock
import requests

from .common import BaseDanceTest
from metapub import PubMedFetcher
from metapub.findit.dances import the_longdom_hustle
from metapub.exceptions import AccessDenied, NoPDFLink


class TestLongdomDance(BaseDanceTest):
    """Test cases for Longdom Publishing."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.fetch = PubMedFetcher()

    def test_longdom_shuffle_url_construction_immunotherapy(self):
        """Test 1: URL construction success (Immunotherapy Los Angel).
        
        PMID: 28299372 (Immunotherapy (Los Angel))
        Expected: Should construct valid Longdom PDF URL
        """
        pma = self.fetch.article_by_pmid('28299372')
        
        print(f"Test 1 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification (should always work for URL construction)
        url = the_longdom_hustle(pma, verify=False)
        assert url is not None
        assert 'longdom.org' in url
        assert 'articles' in url or 'pdf' in url
        assert url.startswith('https://')
        print(f"Test 1 - PDF URL: {url}")

    def test_longdom_shuffle_url_construction_mycobact(self):
        """Test 2: Mycobacterial Diseases.
        
        PMID: 28856068 (Mycobact Dis)
        Expected: Should construct valid Longdom PDF URL
        """
        pma = self.fetch.article_by_pmid('28856068')
        
        print(f"Test 2 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification
        url = the_longdom_hustle(pma, verify=False)
        assert url is not None
        assert 'longdom.org' in url
        print(f"Test 2 - PDF URL: {url}")

    def test_longdom_shuffle_url_construction_angiology(self):
        """Test 3: Angiology Open Access.
        
        PMID: 24511556 (Angiol Open Access)
        Expected: Should construct valid Longdom PDF URL
        """
        pma = self.fetch.article_by_pmid('24511556')
        
        print(f"Test 3 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification
        url = the_longdom_hustle(pma, verify=False)
        assert url is not None
        assert 'longdom.org' in url
        print(f"Test 3 - PDF URL: {url}")

    @patch('requests.get')
    def test_longdom_shuffle_successful_access(self, mock_get):
        """Test 4: Successful PDF access simulation.
        
        Expected: Should return PDF URL when accessible
        """
        # Mock successful PDF response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.headers = {'content-type': 'application/pdf'}
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('28299372')
        
        # Test with verification - should succeed
        url = the_longdom_hustle(pma, verify=True)
        assert 'longdom.org' in url
        print(f"Test 4 - Successful verified access: {url}")

    @patch('requests.get')
    def test_longdom_shuffle_html_fallback(self, mock_get):
        """Test 5: HTML fallback when PDF not available.
        
        Expected: Should return article URL when PDF not available
        """
        # Mock HTML response (article page)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.text = '''<html><body>
            <h1>Article Title</h1>
            <p>Article content here</p>
        </body></html>'''
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('28299372')
        
        # Test with verification - should return article URL
        url = the_longdom_hustle(pma, verify=True)
        assert 'longdom.org' in url
        assert 'articles' in url
        print(f"Test 5 - HTML fallback: {url}")

    @patch('requests.get')
    def test_longdom_shuffle_network_error(self, mock_get):
        """Test 6: Network error handling.
        
        Expected: Should handle network errors gracefully
        """
        # Mock network error
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

        pma = self.fetch.article_by_pmid('28299372')
        
        # Test - should handle network error
        with pytest.raises(NoPDFLink) as exc_info:
            the_longdom_hustle(pma, verify=True)
        
        assert 'TXERROR' in str(exc_info.value)
        print(f"Test 6 - Correctly handled network error: {exc_info.value}")

    def test_longdom_shuffle_missing_doi(self):
        """Test 7: Article without DOI.
        
        Expected: Should raise NoPDFLink for missing DOI
        """
        # Create a mock PMA without DOI
        pma = Mock()
        pma.doi = None
        pma.journal = 'Immunotherapy (Los Angel)'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_longdom_hustle(pma, verify=False)
        
        assert 'MISSING' in str(exc_info.value)
        assert 'DOI required' in str(exc_info.value)
        print(f"Test 7 - Correctly handled missing DOI: {exc_info.value}")

    @patch('requests.get')
    def test_longdom_shuffle_404_error(self, mock_get):
        """Test 8: Article not found (404 error).
        
        Expected: Should try multiple URL patterns
        """
        # Mock 404 response for all attempts
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('28299372')
        
        # Test - should try multiple patterns and eventually fail
        with pytest.raises(NoPDFLink) as exc_info:
            the_longdom_hustle(pma, verify=True)
        
        assert 'TXERROR' in str(exc_info.value)
        print(f"Test 8 - Correctly handled 404: {exc_info.value}")

    @patch('requests.get')
    def test_longdom_shuffle_multiple_patterns(self, mock_get):
        """Test 9: Multiple URL pattern attempts.
        
        Expected: Should try different URL patterns until one works
        """
        # Mock responses: first fails, second succeeds
        responses = [
            Mock(ok=False, status_code=404),  # First URL fails
            Mock(ok=True, status_code=200, headers={'content-type': 'application/pdf'})  # Second succeeds
        ]
        mock_get.side_effect = responses

        pma = self.fetch.article_by_pmid('28299372')
        
        # Test - should succeed on second attempt
        url = the_longdom_hustle(pma, verify=True)
        assert 'longdom.org' in url
        print(f"Test 9 - Multiple pattern success: {url}")


def test_longdom_journal_recognition():
    """Test that Longdom journals are properly recognized in the registry."""
    from metapub.findit.registry import JournalRegistry
    from metapub.findit.journals.longdom import longdom_journals
    
    registry = JournalRegistry()
    
    # Test sample Longdom journals (using PubMed abbreviated names)
    test_journals = [
        'Immunotherapy (Los Angel)',
        'Mycobact Dis',
        'Angiol Open Access',
        'J Chromatogr Sep Tech'
    ]
    
    # Test journal recognition
    found_count = 0
    for journal in test_journals:
        if journal in longdom_journals:
            publisher_info = registry.get_publisher_for_journal(journal)
            if publisher_info and publisher_info['name'] == 'longdom':
                assert publisher_info['dance_function'] == 'the_longdom_hustle'
                print(f"✓ {journal} correctly mapped to Longdom")
                found_count += 1
            else:
                print(f"⚠ {journal} mapped to different publisher: {publisher_info['name'] if publisher_info else 'None'}")
        else:
            print(f"⚠ {journal} not in longdom_journals list")
    
    # Just make sure we found at least one Longdom journal
    assert found_count > 0, "No Longdom journals found in registry with longdom publisher"
    print(f"✓ Found {found_count} properly mapped Longdom journals")
    
    registry.close()


if __name__ == '__main__':
    # Run basic tests if executed directly
    test_instance = TestLongdomDance()
    test_instance.setUp()
    
    print("Running Longdom Publishing tests...")
    print("\n" + "="*60)
    
    tests = [
        ('test_longdom_hustle_url_construction_immunotherapy', 'Immunotherapy URL construction'),
        ('test_longdom_hustle_url_construction_mycobact', 'Mycobacterial URL construction'),
        ('test_longdom_hustle_url_construction_angiology', 'Angiology URL construction'),
        ('test_longdom_hustle_successful_access', 'Successful access simulation'),
        ('test_longdom_hustle_html_fallback', 'HTML fallback'),
        ('test_longdom_hustle_network_error', 'Network error handling'),
        ('test_longdom_hustle_missing_doi', 'Missing DOI handling'),
        ('test_longdom_hustle_404_error', '404 error handling'),
        ('test_longdom_hustle_multiple_patterns', 'Multiple pattern attempts')
    ]
    
    for test_method, description in tests:
        try:
            getattr(test_instance, test_method)()
            print(f"✓ {description} works")
        except Exception as e:
            print(f"✗ {description} failed: {e}")
    
    try:
        test_longdom_journal_recognition()
        print("✓ Registry test passed: Journal recognition works")
    except Exception as e:
        print(f"✗ Registry test failed: {e}")
    
    print("\n" + "="*60)
    print("Test suite completed!")