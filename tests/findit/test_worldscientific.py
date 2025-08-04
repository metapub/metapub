"""Tests for World Scientific Publishing dance function."""

import pytest
from unittest.mock import patch, Mock
import requests

from .common import BaseDanceTest
from metapub import PubMedFetcher
from metapub.findit.dances import the_worldscientific_robot
from metapub.exceptions import AccessDenied, NoPDFLink


class TestWorldScientificDance(BaseDanceTest):
    """Test cases for World Scientific Publishing."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.fetch = PubMedFetcher()

    def test_worldscientific_robot_url_construction_technology(self):
        """Test 1: URL construction success (Technology journal).
        
        PMID: 32292800 (Technology)
        Expected: Should construct valid World Scientific PDF URL
        """
        pma = self.fetch.article_by_pmid('32292800')
        
        print(f"Test 1 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification (should always work for URL construction)
        url = the_worldscientific_robot(pma, verify=False)
        assert url is not None
        assert 'worldscientific.com' in url
        assert '/doi/pdf/' in url
        assert url.startswith('https://')
        print(f"Test 1 - PDF URL: {url}")

    def test_worldscientific_robot_url_construction_ai_tools(self):
        """Test 2: AI Tools journal.
        
        PMID: 24808625 (Int J Artif Intell Tools)
        Expected: Should construct valid World Scientific PDF URL
        """
        pma = self.fetch.article_by_pmid('24808625')
        
        print(f"Test 2 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification
        url = the_worldscientific_robot(pma, verify=False)
        assert url is not None
        assert 'worldscientific.com' in url
        assert '/doi/pdf/' in url
        print(f"Test 2 - PDF URL: {url}")

    def test_worldscientific_robot_url_construction_porphyr(self):
        """Test 3: Porphyrins journal.
        
        PMID: 37868702 (J Porphyr Phthalocyanines)
        Expected: Should construct valid World Scientific PDF URL
        """
        pma = self.fetch.article_by_pmid('37868702')
        
        print(f"Test 3 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification
        url = the_worldscientific_robot(pma, verify=False)
        assert url is not None
        assert 'worldscientific.com' in url
        assert '/doi/pdf/' in url
        print(f"Test 3 - PDF URL: {url}")

    @patch('requests.get')
    def test_worldscientific_robot_successful_access(self, mock_get):
        """Test 4: Successful PDF access simulation.
        
        Expected: Should return PDF URL when accessible
        """
        # Mock successful PDF response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.headers = {'content-type': 'application/pdf'}
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('32292800')
        
        # Test with verification - should succeed
        url = the_worldscientific_robot(pma, verify=True)
        assert 'worldscientific.com' in url
        assert '/doi/pdf/' in url
        print(f"Test 4 - Successful verified access: {url}")

    @patch('requests.get')
    def test_worldscientific_robot_paywall_detection(self, mock_get):
        """Test 5: Paywall detection.
        
        Expected: Should detect paywall and raise AccessDenied
        """
        # Mock paywall response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.text = '''<html><body>
            <h1>Purchase this article</h1>
            <p>Subscription required for access</p>
            <button>Subscribe now</button>
        </body></html>'''
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('32292800')
        
        # Test with verification - should detect paywall
        with pytest.raises(AccessDenied) as exc_info:
            the_worldscientific_robot(pma, verify=True)
        
        assert 'PAYWALL' in str(exc_info.value)
        print(f"Test 5 - Correctly detected paywall: {exc_info.value}")

    @patch('requests.get')
    def test_worldscientific_robot_network_error(self, mock_get):
        """Test 6: Network error handling.
        
        Expected: Should handle network errors gracefully
        """
        # Mock network error
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

        pma = self.fetch.article_by_pmid('32292800')
        
        # Test - should handle network error
        with pytest.raises(NoPDFLink) as exc_info:
            the_worldscientific_robot(pma, verify=True)
        
        assert 'TXERROR' in str(exc_info.value)
        print(f"Test 6 - Correctly handled network error: {exc_info.value}")

    def test_worldscientific_robot_missing_doi(self):
        """Test 7: Article without DOI.
        
        Expected: Should raise NoPDFLink for missing DOI
        """
        # Create a mock PMA without DOI
        pma = Mock()
        pma.doi = None
        pma.journal = 'Technology'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_worldscientific_robot(pma, verify=False)
        
        assert 'MISSING' in str(exc_info.value)
        assert 'DOI required' in str(exc_info.value)
        print(f"Test 7 - Correctly handled missing DOI: {exc_info.value}")

    def test_worldscientific_robot_wrong_doi_pattern(self):
        """Test 8: Article with non-World Scientific DOI pattern.
        
        Expected: Should raise NoPDFLink for wrong DOI pattern
        """
        # Create a mock PMA with non-World Scientific DOI
        pma = Mock()
        pma.doi = '10.1016/j.example.2023.123456'  # Elsevier DOI
        pma.journal = 'Technology'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_worldscientific_robot(pma, verify=False)
        
        assert 'PATTERN' in str(exc_info.value)
        assert '10.1142' in str(exc_info.value)
        print(f"Test 8 - Correctly handled wrong DOI pattern: {exc_info.value}")

    @patch('requests.get')
    def test_worldscientific_robot_404_error(self, mock_get):
        """Test 9: Article not found (404 error).
        
        Expected: Should handle 404 errors properly
        """
        # Mock 404 response
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('32292800')
        
        # Test - should handle 404
        with pytest.raises(NoPDFLink) as exc_info:
            the_worldscientific_robot(pma, verify=True)
        
        assert 'TXERROR' in str(exc_info.value)
        assert '404' in str(exc_info.value)
        print(f"Test 9 - Correctly handled 404: {exc_info.value}")


def test_worldscientific_journal_recognition():
    """Test that World Scientific journals are properly recognized in the registry."""
    from metapub.findit.registry import JournalRegistry
    from metapub.findit.journals.worldscientific import worldscientific_journals
    
    registry = JournalRegistry()
    
    # Test sample World Scientific journals (using PubMed abbreviated names)
    test_journals = [
        'Technology',
        'Int J Artif Intell Tools',
        'J Porphyr Phthalocyanines',
        'Am J Chin Med'
    ]
    
    # Test journal recognition
    found_count = 0
    for journal in test_journals:
        if journal in worldscientific_journals:
            publisher_info = registry.get_publisher_for_journal(journal)
            if publisher_info and publisher_info['name'] == 'worldscientific':
                assert publisher_info['dance_function'] == 'the_worldscientific_robot'
                print(f"✓ {journal} correctly mapped to World Scientific")
                found_count += 1
            else:
                print(f"⚠ {journal} mapped to different publisher: {publisher_info['name'] if publisher_info else 'None'}")
        else:
            print(f"⚠ {journal} not in worldscientific_journals list")
    
    # Just make sure we found at least one World Scientific journal
    assert found_count > 0, "No World Scientific journals found in registry with worldscientific publisher"
    print(f"✓ Found {found_count} properly mapped World Scientific journals")
    
    registry.close()


if __name__ == '__main__':
    # Run basic tests if executed directly
    test_instance = TestWorldScientificDance()
    test_instance.setUp()
    
    print("Running World Scientific Publishing tests...")
    print("\n" + "="*60)
    
    tests = [
        ('test_worldscientific_robot_url_construction_technology', 'Technology URL construction'),
        ('test_worldscientific_robot_url_construction_ai_tools', 'AI Tools URL construction'),
        ('test_worldscientific_robot_url_construction_porphyr', 'Porphyrins URL construction'),
        ('test_worldscientific_robot_successful_access', 'Successful access simulation'),
        ('test_worldscientific_robot_paywall_detection', 'Paywall detection'),
        ('test_worldscientific_robot_network_error', 'Network error handling'),
        ('test_worldscientific_robot_missing_doi', 'Missing DOI handling'),
        ('test_worldscientific_robot_wrong_doi_pattern', 'Wrong DOI pattern handling'),
        ('test_worldscientific_robot_404_error', '404 error handling')
    ]
    
    for test_method, description in tests:
        try:
            getattr(test_instance, test_method)()
            print(f"✓ {description} works")
        except Exception as e:
            print(f"✗ {description} failed: {e}")
    
    try:
        test_worldscientific_journal_recognition()
        print("✓ Registry test passed: Journal recognition works")
    except Exception as e:
        print(f"✗ Registry test failed: {e}")
    
    print("\n" + "="*60)
    print("Test suite completed!")