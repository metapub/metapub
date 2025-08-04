"""Tests for Emerald Publishing dance function."""

import pytest
from unittest.mock import patch, Mock
import requests

from .common import BaseDanceTest
from metapub import PubMedFetcher
from metapub.findit.dances import the_emerald_ceili
from metapub.exceptions import AccessDenied, NoPDFLink


class TestEmeraldDance(BaseDanceTest):
    """Test cases for Emerald Publishing."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.fetch = PubMedFetcher()

    def test_emerald_ceili_url_construction_library_review(self):
        """Test 1: URL construction success (Library Review).
        
        PMID: 11617596 (Libr Rev (Lond))
        Expected: Should construct valid Emerald PDF URL
        """
        pma = self.fetch.article_by_pmid('11617596')
        
        print(f"Test 1 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification (should always work for URL construction)
        url = the_emerald_ceili(pma, verify=False)
        assert url is not None
        assert 'emerald.com' in url
        assert '/insight/content/doi/' in url
        assert url.startswith('https://')
        print(f"Test 1 - PDF URL: {url}")

    def test_emerald_ceili_url_construction_clinical_governance(self):
        """Test 2: Clinical Governance article.
        
        PMID: 26855615 (Clin Gov)
        Expected: Should construct valid Emerald PDF URL
        """
        pma = self.fetch.article_by_pmid('26855615')
        
        print(f"Test 2 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification
        url = the_emerald_ceili(pma, verify=False)
        assert url is not None
        assert 'emerald.com' in url
        assert '/insight/content/doi/' in url
        print(f"Test 2 - PDF URL: {url}")

    def test_emerald_ceili_url_construction_mental_health(self):
        """Test 3: Mental Health article.
        
        PMID: 27066217 (Adv Ment Health Intellect Disabil)
        Expected: Should construct valid Emerald PDF URL
        """
        pma = self.fetch.article_by_pmid('27066217')
        
        print(f"Test 3 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification
        url = the_emerald_ceili(pma, verify=False)
        assert url is not None
        assert 'emerald.com' in url
        assert '/insight/content/doi/' in url
        print(f"Test 3 - PDF URL: {url}")

    @patch('requests.get')
    def test_emerald_ceili_successful_access(self, mock_get):
        """Test 4: Successful PDF access simulation.
        
        Expected: Should return PDF URL when accessible
        """
        # Mock successful PDF response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.headers = {'content-type': 'application/pdf'}
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('11617596')
        
        # Test with verification - should succeed
        url = the_emerald_ceili(pma, verify=True)
        assert 'emerald.com' in url
        assert '/insight/content/doi/' in url
        print(f"Test 4 - Successful verified access: {url}")

    @patch('requests.get')
    def test_emerald_ceili_paywall_detection(self, mock_get):
        """Test 5: Paywall detection.
        
        Expected: Should detect paywall and raise AccessDenied
        """
        # Mock paywall response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.text = '''<html><body>
            <h1>Subscribe to access this article</h1>
            <p>Institutional access required</p>
        </body></html>'''
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('11617596')
        
        # Test with verification - should detect paywall
        with pytest.raises(AccessDenied) as exc_info:
            the_emerald_ceili(pma, verify=True)
        
        assert 'PAYWALL' in str(exc_info.value)
        print(f"Test 5 - Correctly detected paywall: {exc_info.value}")

    @patch('requests.get')
    def test_emerald_ceili_network_error(self, mock_get):
        """Test 6: Network error handling.
        
        Expected: Should handle network errors gracefully
        """
        # Mock network error
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

        pma = self.fetch.article_by_pmid('11617596')
        
        # Test - should handle network error
        with pytest.raises(NoPDFLink) as exc_info:
            the_emerald_ceili(pma, verify=True)
        
        assert 'TXERROR' in str(exc_info.value)
        print(f"Test 6 - Correctly handled network error: {exc_info.value}")

    def test_emerald_ceili_missing_doi(self):
        """Test 7: Article without DOI.
        
        Expected: Should raise NoPDFLink for missing DOI
        """
        # Create a mock PMA without DOI
        pma = Mock()
        pma.doi = None
        pma.journal = 'Libr Rev (Lond)'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_emerald_ceili(pma, verify=False)
        
        assert 'MISSING' in str(exc_info.value)
        assert 'DOI required' in str(exc_info.value)
        print(f"Test 7 - Correctly handled missing DOI: {exc_info.value}")

    def test_emerald_ceili_wrong_doi_pattern(self):
        """Test 8: Article with non-Emerald DOI pattern.
        
        Expected: Should raise NoPDFLink for wrong DOI pattern
        """
        # Create a mock PMA with non-Emerald DOI
        pma = Mock()
        pma.doi = '10.1016/j.example.2023.123456'  # Elsevier DOI
        pma.journal = 'Libr Rev (Lond)'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_emerald_ceili(pma, verify=False)
        
        assert 'PATTERN' in str(exc_info.value)
        assert '10.1108' in str(exc_info.value)
        print(f"Test 8 - Correctly handled wrong DOI pattern: {exc_info.value}")

    @patch('requests.get')
    def test_emerald_ceili_404_error(self, mock_get):
        """Test 9: Article not found (404 error).
        
        Expected: Should handle 404 errors properly
        """
        # Mock 404 response
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('11617596')
        
        # Test - should handle 404
        with pytest.raises(NoPDFLink) as exc_info:
            the_emerald_ceili(pma, verify=True)
        
        assert 'TXERROR' in str(exc_info.value)
        assert '404' in str(exc_info.value)
        print(f"Test 9 - Correctly handled 404: {exc_info.value}")


def test_emerald_journal_recognition():
    """Test that Emerald journals are properly recognized in the registry."""
    from metapub.findit.registry import JournalRegistry
    from metapub.findit.journals.emerald import emerald_journals
    
    registry = JournalRegistry()
    
    # Test sample Emerald journals (using PubMed abbreviated names)
    test_journals = [
        'Libr Rev (Lond)',
        'Clin Gov',
        'Adv Ment Health Intellect Disabil',
        'J Financ Crime'
    ]
    
    # Test journal recognition
    found_count = 0
    for journal in test_journals:
        if journal in emerald_journals:
            publisher_info = registry.get_publisher_for_journal(journal)
            if publisher_info and publisher_info['name'] == 'emerald':
                assert publisher_info['dance_function'] == 'the_emerald_ceili'
                print(f"✓ {journal} correctly mapped to Emerald")
                found_count += 1
            else:
                print(f"⚠ {journal} mapped to different publisher: {publisher_info['name'] if publisher_info else 'None'}")
        else:
            print(f"⚠ {journal} not in emerald_journals list")
    
    # Just make sure we found at least one Emerald journal
    assert found_count > 0, "No Emerald journals found in registry with emerald publisher"
    print(f"✓ Found {found_count} properly mapped Emerald journals")
    
    registry.close()


if __name__ == '__main__':
    # Run basic tests if executed directly
    test_instance = TestEmeraldDance()
    test_instance.setUp()
    
    print("Running Emerald Publishing tests...")
    print("\n" + "="*60)
    
    tests = [
        ('test_emerald_ceili_url_construction_library_review', 'Library Review URL construction'),
        ('test_emerald_ceili_url_construction_clinical_governance', 'Clinical Governance URL construction'),
        ('test_emerald_ceili_url_construction_mental_health', 'Mental Health URL construction'),
        ('test_emerald_ceili_successful_access', 'Successful access simulation'),
        ('test_emerald_ceili_paywall_detection', 'Paywall detection'),
        ('test_emerald_ceili_network_error', 'Network error handling'),
        ('test_emerald_ceili_missing_doi', 'Missing DOI handling'),
        ('test_emerald_ceili_wrong_doi_pattern', 'Wrong DOI pattern handling'),
        ('test_emerald_ceili_404_error', '404 error handling')
    ]
    
    for test_method, description in tests:
        try:
            getattr(test_instance, test_method)()
            print(f"✓ {description} works")
        except Exception as e:
            print(f"✗ {description} failed: {e}")
    
    try:
        test_emerald_journal_recognition()
        print("✓ Registry test passed: Journal recognition works")
    except Exception as e:
        print(f"✗ Registry test failed: {e}")
    
    print("\n" + "="*60)
    print("Test suite completed!")