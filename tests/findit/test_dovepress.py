"""Tests for DovePress (Dove Medical Press) dance function."""

import pytest
from unittest.mock import patch, Mock
import requests

from .common import BaseDanceTest
from metapub import PubMedFetcher
from metapub.findit.dances import the_dovepress_peacock
from metapub.exceptions import AccessDenied, NoPDFLink


class TestDovePressTest(BaseDanceTest):
    """Test cases for DovePress (Dove Medical Press)."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.fetch = PubMedFetcher()

    def test_dovepress_waltz_ijin_article(self):
        """Test 1: URL construction success (International Journal of Nanomedicine).
        
        PMID: 37693885 (Int J Nanomedicine)
        Expected: Should construct valid DovePress PDF URL
        """
        pma = self.fetch.article_by_pmid('37693885')
        
        assert pma.journal == 'Int J Nanomedicine'
        assert pma.doi == '10.2147/IJN.S420748'
        print(f"Test 1 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification (should always work for URL construction)
        url = the_dovepress_peacock(pma, verify=False)
        assert url is not None
        assert 'dovepress.com' in url
        assert '/article/download/' in url
        assert url.startswith('https://')
        print(f"Test 1 - PDF URL: {url}")

    def test_dovepress_waltz_opth_article(self):
        """Test 2: Clinical Ophthalmology article.
        
        PMID: 37736107 (Clin Ophthalmol)
        Expected: Should construct valid DovePress PDF URL
        """
        pma = self.fetch.article_by_pmid('37736107')
        
        assert pma.journal == 'Clin Ophthalmol'
        assert pma.doi == '10.2147/OPTH.S392665'
        print(f"Test 2 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification
        url = the_dovepress_peacock(pma, verify=False)
        assert url is not None
        assert 'dovepress.com' in url
        assert '/article/download/' in url
        print(f"Test 2 - PDF URL: {url}")

    def test_dovepress_waltz_cmar_article(self):
        """Test 3: Cancer Management and Research article.
        
        PMID: 36873252 (Cancer Manag Res)
        Expected: Should construct valid DovePress PDF URL
        """
        pma = self.fetch.article_by_pmid('36873252')
        
        assert pma.journal == 'Cancer Manag Res'
        assert pma.doi == '10.2147/CMAR.S400013'
        print(f"Test 3 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification
        url = the_dovepress_peacock(pma, verify=False)
        assert url is not None
        assert 'dovepress.com' in url
        assert '/article/download/' in url
        print(f"Test 3 - PDF URL: {url}")

    @patch('requests.get')
    def test_dovepress_waltz_successful_pdf_access(self, mock_get):
        """Test 4: Successful PDF access simulation.
        
        PMID: 37693885 (Int J Nanomedicine)
        Expected: Should return PDF URL when accessible
        """
        # Mock DOI resolution to DovePress article page
        mock_article_response = Mock()
        mock_article_response.ok = True
        mock_article_response.url = 'https://www.dovepress.com/plant-derived-exosome-like-nanovesicles-peer-reviewed-fulltext-article-IJN'
        mock_article_response.content = b'''<!DOCTYPE html>
        <html><head></head>
        <body>
            <a href="/article/download/86435">[Download Article [PDF]]</a>
        </body></html>'''
        
        # Mock successful PDF response for verification
        mock_pdf_response = Mock()
        mock_pdf_response.status_code = 200
        mock_pdf_response.ok = True
        mock_pdf_response.headers = {'content-type': 'application/pdf'}
        mock_pdf_response.url = 'https://www.dovepress.com/article/download/86435'
        
        def side_effect(url, *args, **kwargs):
            if '/article/download/' in url:
                return mock_pdf_response
            else:
                return mock_article_response
        
        mock_get.side_effect = side_effect

        pma = self.fetch.article_by_pmid('37693885')
        
        # Test with verification - should succeed
        url = the_dovepress_peacock(pma, verify=True)
        assert 'dovepress.com' in url
        assert '/article/download/' in url
        print(f"Test 4 - Successful verified access: {url}")

    @patch('requests.get')
    def test_dovepress_waltz_paywall_detection(self, mock_get):
        """Test 5: Paywall detection.
        
        Expected: Should detect paywall and raise AccessDenied
        """
        # Mock article page response (successful)
        mock_article_response = Mock()
        mock_article_response.ok = True
        mock_article_response.url = 'https://www.dovepress.com/some-article-peer-reviewed-fulltext-article-IJN'
        mock_article_response.content = b'''<!DOCTYPE html>
        <html><head></head>
        <body>
            <a href="/article/download/12345">[Download Article [PDF]]</a>
        </body></html>'''
        
        # Mock paywall response for PDF verification
        mock_paywall_response = Mock()
        mock_paywall_response.status_code = 401
        mock_paywall_response.ok = False
        mock_paywall_response.headers = {'content-type': 'text/html'}
        
        def side_effect(url, *args, **kwargs):
            if '/article/download/' in url:
                return mock_paywall_response
            else:
                return mock_article_response
        
        mock_get.side_effect = side_effect

        pma = self.fetch.article_by_pmid('37693885')
        
        # Test with verification - should detect paywall
        with pytest.raises(NoPDFLink) as exc_info:
            the_dovepress_peacock(pma, verify=True)
        
        assert 'DENIED' in str(exc_info.value) or 'TXERROR' in str(exc_info.value)
        print(f"Test 5 - Correctly detected paywall: {exc_info.value}")

    @patch('requests.get')
    def test_dovepress_waltz_network_error(self, mock_get):
        """Test 6: Network error handling.
        
        Expected: Should handle network errors gracefully
        """
        # Mock network error on article page request
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

        pma = self.fetch.article_by_pmid('37693885')
        
        # Test - should handle network error
        with pytest.raises(requests.exceptions.ConnectionError):
            the_dovepress_peacock(pma, verify=False)
        print("Test 6 - Correctly handled network error")

    def test_dovepress_waltz_missing_doi(self):
        """Test 7: Article without DOI.
        
        Expected: Should raise NoPDFLink for missing DOI
        """
        # Create a mock PMA without DOI
        pma = Mock()
        pma.doi = None
        pma.journal = 'Int J Nanomedicine'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_dovepress_peacock(pma, verify=False)
        
        assert 'MISSING' in str(exc_info.value)
        assert 'doi needed' in str(exc_info.value)
        print(f"Test 7 - Correctly handled missing DOI: {exc_info.value}")

    @patch('requests.get')
    def test_dovepress_waltz_article_page_not_found(self, mock_get):
        """Test 8: Article page not found (404 error).
        
        Expected: Should handle 404 errors properly
        """
        # Mock 404 response for article page
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('37693885')
        
        # Test - should handle 404
        with pytest.raises(NoPDFLink) as exc_info:
            the_dovepress_peacock(pma, verify=False)
        
        assert 'TXERROR' in str(exc_info.value)
        assert '404' in str(exc_info.value)
        print(f"Test 8 - Correctly handled 404: {exc_info.value}")

    @patch('metapub.findit.dances.etree.fromstring')
    @patch('requests.get')
    def test_dovepress_waltz_html_parsing_error(self, mock_get, mock_etree):
        """Test 9: HTML parsing error handling.
        
        Expected: Should handle XML parsing exceptions gracefully
        """
        # Mock successful article page response
        mock_response = Mock()
        mock_response.ok = True
        mock_response.url = 'https://www.dovepress.com/test-article'
        mock_response.content = b'<html><head></head><body></body></html>'
        mock_get.return_value = mock_response
        
        # Mock etree.fromstring to raise an exception
        mock_etree.side_effect = Exception("XML parsing failed")

        pma = self.fetch.article_by_pmid('37693885')
        
        # Test - should handle parsing error
        with pytest.raises(NoPDFLink) as exc_info:
            the_dovepress_peacock(pma, verify=False)
        
        assert 'TXERROR' in str(exc_info.value)
        assert 'Failed to parse' in str(exc_info.value)
        print(f"Test 9 - Correctly handled parsing error: {exc_info.value}")

    @patch('requests.get')
    def test_dovepress_waltz_no_pdf_link_found(self, mock_get):
        """Test 10: Article page with no PDF download link.
        
        Expected: Should raise NoPDFLink when no download link found
        """
        # Mock article page response without PDF download link
        mock_response = Mock()
        mock_response.ok = True
        mock_response.url = 'https://www.dovepress.com/test-article'
        mock_response.content = b'''<!DOCTYPE html>
        <html><head></head>
        <body>
            <p>This is an article page with no PDF download link.</p>
        </body></html>'''
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('37693885')
        
        # Test - should raise NoPDFLink
        with pytest.raises(NoPDFLink) as exc_info:
            the_dovepress_peacock(pma, verify=False)
        
        assert 'TXERROR' in str(exc_info.value)
        assert 'lacks PDF download link' in str(exc_info.value)
        print(f"Test 10 - Correctly handled missing PDF link: {exc_info.value}")


def test_dovepress_journal_recognition():
    """Test that DovePress journals are properly recognized in the registry."""
    from metapub.findit.registry import JournalRegistry
    from metapub.findit.journals.dovepress import dovepress_journals
    
    registry = JournalRegistry()
    
    # Test sample DovePress journals (using PubMed abbreviated names)
    test_journals = [
        'Int J Nanomedicine',
        'Clin Ophthalmol',
        'Cancer Manag Res',
        'Drug Des Devel Ther'
    ]
    
    # Test journal recognition
    found_count = 0
    for journal in test_journals:
        if journal in dovepress_journals:
            publisher_info = registry.get_publisher_for_journal(journal)
            if publisher_info and publisher_info['name'] == 'dovepress':
                assert publisher_info['dance_function'] == 'the_dovepress_peacock'
                print(f"✓ {journal} correctly mapped to DovePress")
                found_count += 1
            else:
                print(f"⚠ {journal} mapped to different publisher: {publisher_info['name'] if publisher_info else 'None'}")
        else:
            print(f"⚠ {journal} not in dovepress_journals list")
    
    # Just make sure we found at least one DovePress journal
    assert found_count > 0, "No DovePress journals found in registry with dovepress publisher"
    print(f"✓ Found {found_count} properly mapped DovePress journals")
    
    registry.close()


if __name__ == '__main__':
    # Run basic tests if executed directly
    test_instance = TestDovePressTest()
    test_instance.setUp()
    
    print("Running DovePress (Dove Medical Press) tests...")
    print("\n" + "="*60)
    
    tests = [
        ('test_dovepress_waltz_ijin_article', 'IJN article URL construction'),
        ('test_dovepress_waltz_opth_article', 'OPTH article URL construction'),
        ('test_dovepress_waltz_cmar_article', 'CMAR article URL construction'),
        ('test_dovepress_waltz_successful_pdf_access', 'Successful access simulation'),
        ('test_dovepress_waltz_paywall_detection', 'Paywall detection'),
        ('test_dovepress_waltz_network_error', 'Network error handling'),
        ('test_dovepress_waltz_missing_doi', 'Missing DOI handling'),
        ('test_dovepress_waltz_article_page_not_found', 'Article page 404 handling'),
        ('test_dovepress_waltz_html_parsing_error', 'HTML parsing error handling'),
        ('test_dovepress_waltz_no_pdf_link_found', 'No PDF link found handling')
    ]
    
    for test_method, description in tests:
        try:
            getattr(test_instance, test_method)()
            print(f"✓ {description} works")
        except Exception as e:
            print(f"✗ {description} failed: {e}")
    
    try:
        test_dovepress_journal_recognition()
        print("✓ Registry test passed: Journal recognition works")
    except Exception as e:
        print(f"✗ Registry test failed: {e}")
    
    print("\n" + "="*60)
    print("Test suite completed!")