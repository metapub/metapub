"""Tests for OAText Publishing dance function."""

import pytest
from unittest.mock import patch, Mock
import requests

from .common import BaseDanceTest
from metapub import PubMedFetcher
from metapub.findit.dances import the_oatext_orbit
from metapub.exceptions import AccessDenied, NoPDFLink


class TestOATextDance(BaseDanceTest):
    """Test cases for OAText Publishing."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.fetch = PubMedFetcher()

    def test_oatext_orbit_url_construction_syst_integr_neurosci(self):
        """Test 1: URL construction success (Journal of Systems and Integrative Neuroscience).
        
        PMID: 34707891 (J Syst Integr Neurosci)
        Expected: Should construct valid OAText PDF URL
        """
        pma = self.fetch.article_by_pmid('34707891')
        
        print(f"Test 1 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification (should always work for URL construction)
        url = the_oatext_orbit(pma, verify=False)
        assert url is not None
        assert 'oatext.com' in url
        assert '/pdf/' in url
        assert url.startswith('https://')
        print(f"Test 1 - PDF URL: {url}")

    def test_oatext_orbit_url_construction_clin_case_rep(self):
        """Test 2: Clinical Case Reports and Reviews.
        
        PMID: 36203911 (Clin Case Rep Rev) - alternative PMID with DOI
        Expected: Should construct valid OAText PDF URL
        """
        pma = self.fetch.article_by_pmid('36203911')
        
        print(f"Test 2 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Skip test if no DOI available
        if not pma.doi:
            print("Test 2 - Skipping: No DOI available for this PMID")
            return

        # Test without verification
        url = the_oatext_orbit(pma, verify=False)
        assert url is not None
        assert 'oatext.com' in url
        print(f"Test 2 - PDF URL: {url}")

    def test_oatext_orbit_url_construction_integr_cancer(self):
        """Test 3: Integrative Cancer Science and Therapy.
        
        PMID: 31832233 (Integr Cancer Sci Ther)
        Expected: Should construct valid OAText PDF URL
        """
        pma = self.fetch.article_by_pmid('31832233')
        
        print(f"Test 3 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification
        url = the_oatext_orbit(pma, verify=False)
        assert url is not None
        assert 'oatext.com' in url
        print(f"Test 3 - PDF URL: {url}")

    @patch('requests.get')
    def test_oatext_orbit_successful_access(self, mock_get):
        """Test 4: Successful PDF access simulation.
        
        Expected: Should return PDF URL when accessible
        """
        # Mock successful PDF response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.headers = {'content-type': 'application/pdf'}
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('34707891')
        
        # Test with verification - should succeed
        url = the_oatext_orbit(pma, verify=True)
        assert 'oatext.com' in url
        assert '/pdf/' in url
        print(f"Test 4 - Successful verified access: {url}")

    @patch('requests.get')
    def test_oatext_orbit_html_article_page(self, mock_get):
        """Test 5: HTML article page access.
        
        Expected: Should return article page URL when PDF not directly available
        """
        # Mock HTML article page response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.text = '''<html><body>
            <h1>Article Title</h1>
            <p>This is an article on OAText</p>
            <div class="content">Article content here</div>
        </body></html>'''
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('34707891')
        
        # Test with verification - should return article page
        url = the_oatext_orbit(pma, verify=True)
        assert 'oatext.com' in url
        print(f"Test 5 - HTML article page: {url}")

    @patch('requests.get')
    def test_oatext_orbit_network_error(self, mock_get):
        """Test 6: Network error handling.
        
        Expected: Should handle network errors gracefully
        """
        # Mock network error
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

        pma = self.fetch.article_by_pmid('34707891')
        
        # Test - should handle network error
        with pytest.raises(NoPDFLink) as exc_info:
            the_oatext_orbit(pma, verify=True)
        
        assert 'TXERROR' in str(exc_info.value)
        print(f"Test 6 - Correctly handled network error: {exc_info.value}")

    def test_oatext_orbit_missing_doi(self):
        """Test 7: Article without DOI.
        
        Expected: Should raise NoPDFLink for missing DOI
        """
        # Create a mock PMA without DOI
        pma = Mock()
        pma.doi = None
        pma.journal = 'J Syst Integr Neurosci'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_oatext_orbit(pma, verify=False)
        
        assert 'MISSING' in str(exc_info.value)
        assert 'DOI required' in str(exc_info.value)
        print(f"Test 7 - Correctly handled missing DOI: {exc_info.value}")

    @patch('requests.get')
    def test_oatext_orbit_404_error(self, mock_get):
        """Test 8: Article not found (404 error).
        
        Expected: Should try multiple patterns and handle 404 errors
        """
        # Mock 404 response for all attempts
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('34707891')
        
        # Test - should try multiple patterns and eventually fail
        with pytest.raises(NoPDFLink) as exc_info:
            the_oatext_orbit(pma, verify=True)
        
        assert 'TXERROR' in str(exc_info.value)
        print(f"Test 8 - Correctly handled 404: {exc_info.value}")

    @patch('requests.get')
    def test_oatext_orbit_multiple_url_patterns(self, mock_get):
        """Test 9: Multiple URL pattern attempts.
        
        Expected: Should try different URL patterns until one works
        """
        # Mock responses: first few fail, last one succeeds
        responses = [
            Mock(ok=False, status_code=404),  # First URL fails
            Mock(ok=False, status_code=404),  # Second URL fails
            Mock(ok=True, status_code=200, headers={'content-type': 'application/pdf'})  # Third succeeds
        ]
        mock_get.side_effect = responses

        pma = self.fetch.article_by_pmid('34707891')
        
        # Test - should succeed on third attempt
        url = the_oatext_orbit(pma, verify=True)
        assert 'oatext.com' in url
        print(f"Test 9 - Multiple pattern success: {url}")

    @patch('requests.get')
    def test_oatext_orbit_title_based_url(self, mock_get):
        """Test 10: Title-based URL construction.
        
        Expected: Should try title-based URLs when DOI-based ones fail
        """
        # Mock DOI-based URLs failing, title-based succeeding
        responses = [
            Mock(ok=False, status_code=404),  # PDF pattern 1 fails
            Mock(ok=False, status_code=404),  # PDF pattern 2 fails
            Mock(ok=False, status_code=404),  # PDF pattern 3 fails
            Mock(ok=False, status_code=404),  # PDF pattern 4 fails
            Mock(ok=True, status_code=200, headers={'content-type': 'text/html'}, text='<html><body>Article content</body></html>')  # Title-based succeeds
        ]
        mock_get.side_effect = responses

        pma = self.fetch.article_by_pmid('34707891')
        # Add a mock title for testing
        pma.title = "Test Article Title"
        
        # Test - should succeed with title-based URL
        url = the_oatext_orbit(pma, verify=True)
        assert 'oatext.com' in url
        assert 'test-article-title' in url or '.php' in url
        print(f"Test 10 - Title-based URL success: {url}")


def test_oatext_journal_recognition():
    """Test that OAText journals are properly recognized in the registry."""
    from metapub.findit.registry import JournalRegistry
    from metapub.findit.journals.oatext import oatext_journals
    
    registry = JournalRegistry()
    
    # Test sample OAText journals (using PubMed abbreviated names)
    test_journals = [
        'J Syst Integr Neurosci',
        'Clin Case Rep Rev',
        'Integr Cancer Sci Ther',
        'Health Educ Care',
        'Biomed Res Rev'
    ]
    
    # Test journal recognition
    found_count = 0
    for journal in test_journals:
        if journal in oatext_journals:
            publisher_info = registry.get_publisher_for_journal(journal)
            if publisher_info and publisher_info['name'] == 'oatext':
                assert publisher_info['dance_function'] == 'the_oatext_orbit'
                print(f"✓ {journal} correctly mapped to OAText Publishing")
                found_count += 1
            else:
                print(f"⚠ {journal} mapped to different publisher: {publisher_info['name'] if publisher_info else 'None'}")
        else:
            print(f"⚠ {journal} not in oatext_journals list")
    
    # Just make sure we found at least one OAText journal
    assert found_count > 0, "No OAText journals found in registry with oatext publisher"
    print(f"✓ Found {found_count} properly mapped OAText journals")
    
    registry.close()


if __name__ == '__main__':
    # Run basic tests if executed directly
    test_instance = TestOATextDance()
    test_instance.setUp()
    
    print("Running OAText Publishing tests...")
    print("\n" + "="*60)
    
    tests = [
        ('test_oatext_orbit_url_construction_syst_integr_neurosci', 'Syst Integr Neurosci URL construction'),
        ('test_oatext_orbit_url_construction_clin_case_rep', 'Clin Case Rep URL construction'),
        ('test_oatext_orbit_url_construction_integr_cancer', 'Integr Cancer URL construction'),
        ('test_oatext_orbit_successful_access', 'Successful access simulation'),
        ('test_oatext_orbit_html_article_page', 'HTML article page access'),
        ('test_oatext_orbit_network_error', 'Network error handling'),
        ('test_oatext_orbit_missing_doi', 'Missing DOI handling'),
        ('test_oatext_orbit_404_error', '404 error handling'),
        ('test_oatext_orbit_multiple_url_patterns', 'Multiple URL patterns'),
        ('test_oatext_orbit_title_based_url', 'Title-based URL construction')
    ]
    
    for test_method, description in tests:
        try:
            getattr(test_instance, test_method)()
            print(f"✓ {description} works")
        except Exception as e:
            print(f"✗ {description} failed: {e}")
    
    try:
        test_oatext_journal_recognition()
        print("✓ Registry test passed: Journal recognition works")
    except Exception as e:
        print(f"✗ Registry test failed: {e}")
    
    print("\n" + "="*60)
    print("Test suite completed!")