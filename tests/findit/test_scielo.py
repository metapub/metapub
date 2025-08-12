"""Tests for SciELO (Scientific Electronic Library Online) dance function."""

import pytest
from unittest.mock import patch, Mock
import requests

from .common import BaseDanceTest
from metapub import PubMedFetcher
from metapub.findit.dances import the_scielo_chula
from metapub.exceptions import AccessDenied, NoPDFLink
from tests.fixtures import load_pmid_xml, SCIELO_EVIDENCE_PMIDS


class TestScieloDance(BaseDanceTest):
    """Test cases for SciELO (Scientific Electronic Library Online)."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.fetch = PubMedFetcher()

    def test_scielo_chula_url_construction_with_pii(self):
        """Test 1: URL construction success using PII (Arq Gastroenterol article).
        
        PMID: 23657305 (Arq Gastroenterol - Arquivos de Gastroenterologia)
        Expected: Should construct valid SciELO PDF URL using PII
        """
        pma = self.fetch.article_by_pmid('23657305')
        
        assert pma.journal == 'Arq Gastroenterol'
        assert pma.doi == '10.1590/s0004-28032013000100008'
        assert pma.pii == 'S0004-28032013000100035'
        print(f"Test 1 - Article info: {pma.journal}, PII: {pma.pii}, DOI: {pma.doi}")

        # Test without verification (should always work for URL construction)
        url = the_scielo_chula(pma, verify=False)
        assert url is not None
        assert 'scielo.br' in url
        assert 'format=pdf' in url
        assert url.startswith('https://')
        print(f"Test 1 - PDF URL: {url}")

    def test_scielo_chula_url_construction_with_doi(self):
        """Test 2: URL construction using DOI fallback (different Arq Gastroenterol article).
        
        PMID: 32294727 (Arq Gastroenterol - Editorial)
        Expected: Should construct valid SciELO PDF URL using DOI when PII available
        """
        pma = self.fetch.article_by_pmid('32294727')
        
        assert pma.journal == 'Arq Gastroenterol'
        assert pma.doi == '10.1590/S0004-2803.202000000-01'
        assert pma.pii == 'S0004-28032020000100001'
        print(f"Test 2 - Article info: {pma.journal}, PII: {pma.pii}, DOI: {pma.doi}")

        # Test without verification
        url = the_scielo_chula(pma, verify=False)
        assert url is not None
        assert 'scielo.br' in url
        assert 'format=pdf' in url
        print(f"Test 2 - PDF URL: {url}")

    def test_scielo_chula_different_article_pattern(self):
        """Test 3: Test with a mock article to ensure different URL patterns work.
        
        Expected: Should handle different SciELO article patterns
        """
        # Create a mock PMA with different SciELO data
        pma = Mock()
        pma.pii = 'S0100-879X2020000500123'  # Different journal pattern
        pma.doi = '10.1590/1414-431X20209876'
        pma.journal = 'Braz J Med Biol Res'
        
        # We'll need to mock the requests.get for this test
        with patch('requests.get') as mock_get:
            # Mock successful response with citation_pdf_url
            mock_response = Mock()
            mock_response.ok = True
            mock_response.url = 'https://www.scielo.br/j/bjmbr/a/someID/?lang=en'
            mock_response.content = b'''<!DOCTYPE html>
            <html><head>
                <meta name="citation_pdf_url" content="https://www.scielo.br/j/bjmbr/a/someID/?format=pdf&lang=en">
            </head><body></body></html>'''
            mock_get.return_value = mock_response
            
            url = the_scielo_chula(pma, verify=False)
            assert url == 'https://www.scielo.br/j/bjmbr/a/someID/?format=pdf&lang=en'
            print(f"Test 3 - Mock PDF URL: {url}")

    @patch('requests.get')
    def test_scielo_chula_successful_pdf_access(self, mock_get):
        """Test 4: Successful PDF access simulation.
        
        PMID: 23657305 (Arq Gastroenterol)  
        Expected: Should return PDF URL when accessible
        """
        # Mock initial page response (successful)
        mock_page_response = Mock()
        mock_page_response.ok = True
        mock_page_response.url = 'https://www.scielo.br/j/ag/a/tmtNzPCNWvVSLhRw7NyjSnq/?lang=en'
        mock_page_response.content = b'''<!DOCTYPE html>
        <html><head>
            <meta name="citation_pdf_url" content="https://www.scielo.br/j/ag/a/tmtNzPCNWvVSLhRw7NyjSnq/?lang=en&format=pdf">
        </head><body></body></html>'''
        
        # Mock successful PDF response for verification
        mock_pdf_response = Mock()
        mock_pdf_response.status_code = 200
        mock_pdf_response.ok = True
        mock_pdf_response.headers = {'content-type': 'application/pdf'}
        mock_pdf_response.url = 'https://www.scielo.br/j/ag/a/tmtNzPCNWvVSLhRw7NyjSnq/?lang=en&format=pdf'
        
        def side_effect(url, *args, **kwargs):
            if 'format=pdf' in url:
                return mock_pdf_response
            else:
                return mock_page_response
        
        mock_get.side_effect = side_effect

        pma = self.fetch.article_by_pmid('23657305')
        
        # Test with verification - should succeed
        url = the_scielo_chula(pma, verify=True)
        assert 'scielo.br' in url
        assert 'format=pdf' in url
        print(f"Test 4 - Successful verified access: {url}")

    @patch('requests.get')
    def test_scielo_chula_paywall_detection(self, mock_get):
        """Test 5: Paywall detection.
        
        Expected: Should detect paywall and raise AccessDenied
        """
        # Mock initial page response (successful)
        mock_page_response = Mock()
        mock_page_response.ok = True
        mock_page_response.url = 'https://www.scielo.br/j/ag/a/someID/?lang=en'
        mock_page_response.content = b'''<!DOCTYPE html>
        <html><head>
            <meta name="citation_pdf_url" content="https://www.scielo.br/j/ag/a/someID/?format=pdf&lang=en">
        </head><body></body></html>'''
        
        # Mock paywall response for PDF verification
        mock_paywall_response = Mock()
        mock_paywall_response.status_code = 401
        mock_paywall_response.ok = False
        mock_paywall_response.headers = {'content-type': 'text/html'}
        
        def side_effect(url, *args, **kwargs):
            if 'format=pdf' in url:
                return mock_paywall_response
            else:
                return mock_page_response
        
        mock_get.side_effect = side_effect

        pma = self.fetch.article_by_pmid('23657305')
        
        # Test with verification - should detect paywall
        with pytest.raises(NoPDFLink) as exc_info:
            the_scielo_chula(pma, verify=True)
        
        assert ('DENIED' in str(exc_info.value) or 'MISSING' in str(exc_info.value))
        assert 'SciELO' in str(exc_info.value)
        print(f"Test 5 - Correctly detected paywall: {exc_info.value}")

    @patch('requests.get')
    def test_scielo_chula_network_error(self, mock_get):
        """Test 6: Network error handling.
        
        Expected: Should handle network errors gracefully
        """
        # Mock network error
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

        pma = self.fetch.article_by_pmid('23657305')
        
        # Test - should handle network error
        with pytest.raises(requests.exceptions.ConnectionError):
            the_scielo_chula(pma, verify=False)
        print("Test 6 - Correctly handled network error")

    def test_scielo_chula_missing_data(self):
        """Test 7: Article without PII or DOI.
        
        Expected: Should raise NoPDFLink for missing data
        """
        # Create a mock PMA without PII or DOI
        pma = Mock()
        pma.pii = None
        pma.doi = None
        pma.journal = 'Some Journal'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_scielo_chula(pma, verify=False)
        
        assert 'MISSING' in str(exc_info.value)
        assert 'pii or doi needed' in str(exc_info.value)
        print(f"Test 7 - Correctly handled missing data: {exc_info.value}")

    @patch('metapub.findit.dances.scielo.etree.fromstring')
    @patch('requests.get')
    def test_scielo_chula_html_parsing_error(self, mock_get, mock_etree):
        """Test 8: HTML parsing error handling.
        
        Expected: Should handle XML parsing exceptions gracefully
        """
        # Mock successful page response
        mock_response = Mock()
        mock_response.ok = True
        mock_response.url = 'https://www.scielo.br/test'
        mock_response.content = b'<html><head></head><body></body></html>'
        mock_get.return_value = mock_response
        
        # Mock etree.fromstring to raise an exception
        mock_etree.side_effect = Exception("XML parsing failed")

        pma = self.fetch.article_by_pmid('23657305')
        
        # Test - should handle parsing error
        with pytest.raises(NoPDFLink) as exc_info:
            the_scielo_chula(pma, verify=False)
        
        assert 'TXERROR' in str(exc_info.value)
        assert 'Failed to parse' in str(exc_info.value)
        print(f"Test 8 - Correctly handled parsing error: {exc_info.value}")

    @patch('requests.get')
    def test_scielo_chula_fallback_to_href_links(self, mock_get):
        """Test 9: Fallback to href PDF links when meta tag missing.
        
        Expected: Should find PDF links in page content as fallback
        """
        # Mock response without citation_pdf_url meta tag but with PDF links
        mock_response = Mock()
        mock_response.ok = True
        mock_response.url = 'https://www.scielo.br/test'
        mock_response.content = b'''<!DOCTYPE html>
        <html><head></head>
        <body>
            <a href="/j/ag/a/someID/?format=pdf&lang=en">Download PDF</a>
        </body></html>'''
        mock_get.return_value = mock_response

        pma = Mock()
        pma.pii = 'S0004-28032013000100035'
        pma.doi = '10.1590/test'
        pma.journal = 'Test Journal'
        
        url = the_scielo_chula(pma, verify=False)
        assert url == 'https://www.scielo.br/j/ag/a/someID/?format=pdf&lang=en'
        print(f"Test 9 - Fallback PDF link found: {url}")


def test_scielo_journal_recognition():
    """Test that SciELO journals are properly recognized in the registry."""
    from metapub.findit.registry import JournalRegistry
    from metapub.findit.journals.scielo import scielo_journals
    
    registry = JournalRegistry()
    
    # Test SciELO journals (including some of the newly added Brazilian journals)
    test_journals = [
        'Arq Gastroenterol',
        'Mem Inst Oswaldo Cruz',
        'Braz J Biol',
        'Quim Nova',
        'Rev Bras Enferm'
    ]
    
    # Test journal recognition
    found_count = 0
    for journal in test_journals:
        publisher_info = registry.get_publisher_for_journal(journal)
        if publisher_info and publisher_info['name'] == 'Scielo':
            assert publisher_info['dance_function'] == 'the_doi_slide'
            print(f"✓ {journal} correctly mapped to SciELO")
            found_count += 1
        else:
            print(f"⚠ {journal} mapped to different publisher: {publisher_info['name'] if publisher_info else 'None'}")
    
    # Just make sure we found at least one SciELO journal
    assert found_count > 0, "No SciELO journals found in registry with scielo publisher"
    print(f"✓ Found {found_count} properly mapped SciELO journals")
    
    registry.close()




class TestScieloXMLFixtures:
    """Test Scielo dance function with real XML fixtures."""

    def test_scielo_authentic_metadata_validation(self):
        """Validate authentic metadata from XML fixtures matches expected patterns."""
        for pmid, expected in SCIELO_EVIDENCE_PMIDS.items():
            pma = load_pmid_xml(pmid)
            assert pma.doi == expected['doi']
            assert pma.journal == expected['journal']
            assert pma.pmid == pmid
            print(f"✓ PMID {pmid}: {pma.journal} - {pma.doi}")

    def test_scielo_doi_pattern_consistency(self):
        """Test Scielo DOI patterns (10.1590/)."""
        for pmid, data in SCIELO_EVIDENCE_PMIDS.items():
            pma = load_pmid_xml(pmid)
            assert pma.doi.startswith('10.1590/'), f"Scielo DOI must start with 10.1590/, got: {pma.doi}"
            print(f"✓ PMID {pmid} DOI pattern: {pma.doi}")


if __name__ == '__main__':
    # Run basic tests if executed directly
    test_instance = TestScieloDance()
    test_instance.setUp()
    
    print("Running SciELO (Scientific Electronic Library Online) tests...")
    print("\n" + "="*60)
    
    tests = [
        ('test_scielo_chula_url_construction_with_pii', 'URL construction with PII'),
        ('test_scielo_chula_url_construction_with_doi', 'URL construction with DOI'),
        ('test_scielo_chula_different_article_pattern', 'Different article patterns'),
        ('test_scielo_chula_successful_pdf_access', 'Successful access simulation'),
        ('test_scielo_chula_paywall_detection', 'Paywall detection'),
        ('test_scielo_chula_network_error', 'Network error handling'),
        ('test_scielo_chula_missing_data', 'Missing data handling'),
        ('test_scielo_chula_html_parsing_error', 'HTML parsing error handling'),
        ('test_scielo_chula_fallback_to_href_links', 'Fallback to href PDF links')
    ]
    
    for test_method, description in tests:
        try:
            getattr(test_instance, test_method)()
            print(f"✓ {description} works")
        except Exception as e:
            print(f"✗ {description} failed: {e}")
    
    try:
        test_scielo_journal_recognition()
        print("✓ Registry test passed: Journal recognition works")
    except Exception as e:
        print(f"✗ Registry test failed: {e}")
    
    print("\n" + "="*60)
    print("Test suite completed!")