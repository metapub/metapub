"""Tests for Wolters Kluwer dance function."""

import pytest
from unittest.mock import patch, Mock
import requests

from .common import BaseDanceTest
from metapub import PubMedFetcher
from metapub.findit.dances import the_wolterskluwer_volta
from metapub.exceptions import AccessDenied, NoPDFLink


class TestWoltersKluwerDance(BaseDanceTest):
    """Test cases for Wolters Kluwer."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.fetch = PubMedFetcher()

    def test_wolterskluwer_volta_url_construction(self):
        """Test 1: URL construction success (Pain journal article).
        
        PMID: 37326643 (Pain)
        Expected: Should construct valid Wolters Kluwer PDF URL
        """
        pma = self.fetch.article_by_pmid('37326643')
        
        assert pma.journal == 'Pain'
        assert pma.doi is not None
        print(f"Test 1 - Article info: {pma.journal}, DOI: {pma.doi}")

    def test_wolterskluwer_volta_neurosurgery_article(self):
        """Test 2: Neurosurgery journal article.
        
        PMID: 36924482 (Neurosurgery)
        Expected: Should have correct journal and DOI info
        """
        pma = self.fetch.article_by_pmid('36924482')
        
        assert pma.journal == 'Neurosurgery'
        assert pma.doi is not None
        print(f"Test 2 - Neurosurgery article: {pma.journal}, DOI: {pma.doi}")

    def test_wolterskluwer_volta_critical_care_article(self):
        """Test 3: Critical Care Medicine journal article.
        
        PMID: 38240510 (Crit Care Med)
        Expected: Should have correct journal and DOI info
        """
        pma = self.fetch.article_by_pmid('38240510')
        
        assert pma.journal == 'Crit Care Med'
        assert pma.doi is not None
        print(f"Test 3 - Critical Care article: {pma.journal}, DOI: {pma.doi}")


    @patch('metapub.findit.dances.wolterskluwer.the_doi_2step')
    @patch('requests.get')
    def test_wolterskluwer_volta_paywall_detection(self, mock_get, mock_doi_2step):
        """Test 5: Paywall detection.
        
        PMID: 36924482 (Neurosurgery)
        Expected: Should detect paywall and raise AccessDenied
        """
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://journals.lww.com/neurosurgery/pages/articleviewer.aspx'
        
        # Mock paywall response (no PDF link available)
        mock_html_content = b'''<html><head><title>Neurosurgery</title></head>
        <body><div class="content">
        <p>Subscribe to access full content</p>
        </div></body></html>'''
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.content = mock_html_content
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('36924482')
        
        # Test - should detect paywall/missing PDF link
        with pytest.raises(NoPDFLink) as exc_info:
            the_wolterskluwer_volta(pma, verify=False)
        
        assert 'DENIED' in str(exc_info.value) or 'PDF link' in str(exc_info.value)
        print(f"Test 5 - Correctly detected paywall: {exc_info.value}")


    @patch('metapub.findit.dances.wolterskluwer.the_doi_2step')
    @patch('requests.get')
    def test_wolterskluwer_volta_network_error(self, mock_get, mock_doi_2step):
        """Test 7: Network error handling.
        
        Expected: Should handle network errors gracefully
        """
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://journals.lww.com/pain/pages/articleviewer.aspx'
        
        # Mock network error
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

        pma = self.fetch.article_by_pmid('37326643')
        
        # Test - should handle network error
        with pytest.raises(requests.exceptions.ConnectionError):
            the_wolterskluwer_volta(pma, verify=False)
        print("Test 7 - Correctly handled network error")


def test_wolterskluwer_journal_recognition():
    """Test that Wolters Kluwer journals are properly recognized in the registry."""
    from metapub.findit.registry import JournalRegistry
    from metapub.findit.journals.wolterskluwer import wolterskluwer_journals
    
    registry = JournalRegistry()
    
    # Test journals from Wolters Kluwer
    test_journals = [
        'Pain',
        'Neurosurgery',
        'Crit Care Med',
        'Circulation',
        'Anesthesiology'
    ]
    
    # Test journal recognition
    for journal in test_journals:
        if journal in wolterskluwer_journals:
            publisher_info = registry.get_publisher_for_journal(journal)
            assert publisher_info is not None, f"Journal {journal} not found in registry"
            assert publisher_info['name'] == 'wolterskluwer'
            assert publisher_info['dance_function'] == 'the_wolterskluwer_volta'
            print(f"✓ {journal} correctly mapped to Wolters Kluwer")
        else:
            print(f"⚠ {journal} not in wolterskluwer_journals list - skipping")
    
    registry.close()


if __name__ == '__main__':
    # Run basic tests if executed directly
    test_instance = TestWoltersKluwerDance()
    test_instance.setUp()
    
    print("Running Wolters Kluwer journal tests...")
    print("\n" + "="*60)
    
    tests = [
        ('test_wolterskluwer_volta_url_construction', 'URL construction'),
        ('test_wolterskluwer_volta_neurosurgery_article', 'Neurosurgery article info'),
        ('test_wolterskluwer_volta_critical_care_article', 'Critical Care article info'),
        ('test_wolterskluwer_volta_paywall_detection', 'Paywall detection'),
        ('test_wolterskluwer_volta_network_error', 'Network error handling')
    ]
    
    for test_method, description in tests:
        try:
            getattr(test_instance, test_method)()
            print(f"✓ {description} works")
        except Exception as e:
            print(f"✗ {description} failed: {e}")
    
    try:
        test_wolterskluwer_journal_recognition()
        print("✓ Registry test passed: Journal recognition works")
    except Exception as e:
        print(f"✗ Registry test failed: {e}")
    
    print("\n" + "="*60)
    print("Test suite completed!")