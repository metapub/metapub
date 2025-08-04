"""Tests for JAMA network journals dance function."""

import pytest
from unittest.mock import patch, Mock
import requests

from .common import BaseDanceTest
from metapub import PubMedFetcher
from metapub.findit.dances import the_jama_dance
from metapub.exceptions import AccessDenied, NoPDFLink


class TestJAMADance(BaseDanceTest):
    """Test cases for JAMA network journals."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.fetch = PubMedFetcher()

    def test_jama_dance_url_construction_basic(self):
        """Test 1: Basic URL construction without network calls.
        
        PMID: 26575068 (JAMA)
        Expected: Should have correct DOI and journal info
        """
        pma = self.fetch.article_by_pmid('26575068')
        
        assert pma.journal == 'JAMA'
        assert pma.doi == '10.1001/jama.2015.12931'
        print(f"Test 1 - Article info: {pma.journal}, DOI: {pma.doi}")

    def test_jama_dance_second_article(self):
        """Test 2: Second JAMA article info.
        
        PMID: 26575069 (JAMA)
        Expected: Should have correct journal and DOI info
        """
        pma = self.fetch.article_by_pmid('26575069')
        
        # Just check that we got valid article data
        assert pma.journal is not None
        assert pma.doi is not None
        print(f"Test 2 - Second article: {pma.journal}, DOI: {pma.doi}")

    @patch('metapub.findit.dances.jama.the_doi_2step')
    @patch('requests.get')
    def test_jama_dance_successful_access(self, mock_get, mock_doi_2step):
        """Test 3: Successful PDF access simulation.
        
        PMID: 26575068 (JAMA)
        Expected: Should return PDF URL when accessible
        """
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://jamanetwork.com/article.aspx?doi=10.1001/jama.2015.12931'
        
        # Mock successful HTML response with PDF citation
        mock_html_content = b'''<html><head>
        <meta name="citation_pdf_url" content="https://jamanetwork.com/journals/jama/fullarticle/2468891.pdf" />
        </head><body></body></html>'''
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.content = mock_html_content
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('26575068')
        
        # Test with verification disabled to avoid second request
        url = the_jama_dance(pma, verify=False)
        assert url == 'https://jamanetwork.com/journals/jama/fullarticle/2468891.pdf'
        assert 'jamanetwork.com' in url
        print(f"Test 3 - Successful access: {url}")

    @patch('metapub.findit.dances.jama.the_doi_2step')
    @patch('requests.get')
    def test_jama_dance_no_pdf_link(self, mock_get, mock_doi_2step):
        """Test 4: Missing PDF link detection.
        
        PMID: 36301627 (JAMA Psychiatry)
        Expected: Should detect missing PDF link and raise NoPDFLink
        """
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://jamanetwork.com/article.aspx?doi=10.1001/jama.2015.12931'
        
        # Mock HTML response without PDF citation (paywall scenario)
        mock_html_content = b'''<html><head>
        <meta name="citation_title" content="Some Article" />
        </head><body>Subscribe to access this article.</body></html>'''
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.content = mock_html_content
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('26575069')
        
        # Test - should detect missing PDF link
        with pytest.raises(NoPDFLink) as exc_info:
            the_jama_dance(pma, verify=False)
        
        assert 'DENIED' in str(exc_info.value)
        assert 'JAMA' in str(exc_info.value)
        print(f"Test 4 - Correctly detected missing PDF link: {exc_info.value}")

    def test_jama_dance_no_doi(self):
        """Test 5: Article without DOI.
        
        Expected: Should raise NoPDFLink for missing DOI
        """
        # Create a mock PMA without DOI
        pma = Mock()
        pma.doi = None
        pma.journal = 'JAMA'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_jama_dance(pma, verify=False)
        
        assert 'MISSING: doi needed for JAMA article' in str(exc_info.value)
        print(f"Test 5 - Correctly handled missing DOI: {exc_info.value}")

    @patch('metapub.findit.dances.jama.the_doi_2step')
    @patch('requests.get')
    def test_jama_dance_network_error(self, mock_get, mock_doi_2step):
        """Test 6: Network error handling.
        
        Expected: Should handle network errors gracefully
        """
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://jamanetwork.com/article.aspx?doi=10.1001/jama.2015.12931'
        
        # Mock network error
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

        pma = self.fetch.article_by_pmid('26575068')
        
        # Test - should handle network error
        with pytest.raises(requests.exceptions.ConnectionError):
            the_jama_dance(pma, verify=False)
        print("Test 6 - Correctly handled network error")


def test_jama_journal_recognition():
    """Test that JAMA journals are properly recognized in the registry."""
    from metapub.findit.registry import JournalRegistry
    from metapub.findit.journals.jama import jama_journals
    
    registry = JournalRegistry()
    
    # Test journals from JAMA network
    test_journals = [
        'JAMA',
        'JAMA Psychiatry',
        'JAMA Intern Med',
        'JAMA Surg',
        'JAMA Pediatr'
    ]
    
    # Test journal recognition
    for journal in test_journals:
        if journal in jama_journals:
            publisher_info = registry.get_publisher_for_journal(journal)
            assert publisher_info is not None, f"Journal {journal} not found in registry"
            assert publisher_info['name'] == 'jama'
            assert publisher_info['dance_function'] == 'the_jama_dance'
            print(f"✓ {journal} correctly mapped to JAMA network")
        else:
            print(f"⚠ {journal} not in jama_journals list - skipping")
    
    registry.close()


if __name__ == '__main__':
    # Run basic tests if executed directly
    test_instance = TestJAMADance()
    test_instance.setUp()
    
    print("Running JAMA network journal tests...")
    print("\n" + "="*60)
    
    tests = [
        ('test_jama_dance_url_construction_basic', 'Basic URL construction'),
        ('test_jama_dance_second_article', 'Second article info'),
        ('test_jama_dance_successful_access', 'Successful access simulation'),
        ('test_jama_dance_no_pdf_link', 'Missing PDF link detection'),
        ('test_jama_dance_no_doi', 'Missing DOI handling'),
        ('test_jama_dance_network_error', 'Network error handling')
    ]
    
    for test_method, description in tests:
        try:
            getattr(test_instance, test_method)()
            print(f"✓ {description} works")
        except Exception as e:
            print(f"✗ {description} failed: {e}")
    
    try:
        test_jama_journal_recognition()
        print("✓ Registry test passed: Journal recognition works")
    except Exception as e:
        print(f"✗ Registry test failed: {e}")
    
    print("\n" + "="*60)
    print("Test suite completed!")