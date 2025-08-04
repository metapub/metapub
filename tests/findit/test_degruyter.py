"""Tests for De Gruyter dance function."""

import pytest
from unittest.mock import patch, Mock
import requests

from .common import BaseDanceTest
from metapub import PubMedFetcher
from metapub.findit.dances import the_degruyter_danza
from metapub.exceptions import AccessDenied, NoPDFLink


class TestDeGruyterDance(BaseDanceTest):
    """Test cases for De Gruyter publisher."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.fetch = PubMedFetcher()

    def test_degruyter_dance_url_construction_phonetica(self):
        """Test 1: URL construction success (Phonetica).
        
        PMID: 38869142 (Phonetica)
        Expected: Should construct valid De Gruyter article URL via DOI resolution
        """
        pma = self.fetch.article_by_pmid('38869142')
        
        assert pma.journal == 'Phonetica'
        assert pma.doi == '10.1515/phon-2023-0049'
        print(f"Test 1 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification (should always work for URL construction)
        url = the_degruyter_danza(pma, verify=False)
        assert url is not None
        assert 'degruyter' in url.lower()
        print(f"Test 1 - Article URL: {url}")

    def test_degruyter_dance_url_construction_intl_soc_lang(self):
        """Test 2: International Journal of Sociology of Language article.
        
        PMID: 36701212 (Int J Soc Lang)
        Expected: Should construct valid De Gruyter article URL
        """
        pma = self.fetch.article_by_pmid('36701212')
        
        assert pma.journal == 'Int J Soc Lang'
        assert pma.doi == '10.1515/ijsl-2021-0099'
        print(f"Test 2 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification
        url = the_degruyter_danza(pma, verify=False)
        assert url is not None
        assert 'degruyter' in url.lower()
        print(f"Test 2 - Article URL: {url}")

    def test_degruyter_dance_url_construction_non_1515_doi(self):
        """Test 3: Article with non-10.1515 DOI (may not be De Gruyter).
        
        PMID: 33227128 (J Am Osteopath Assoc)
        Expected: Should still work via DOI resolution
        """
        pma = self.fetch.article_by_pmid('33227128')
        
        assert pma.journal == 'J Am Osteopath Assoc'
        assert pma.doi == '10.7556/jaoa.2020.157'
        print(f"Test 3 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification
        url = the_degruyter_danza(pma, verify=False)
        assert url is not None  
        print(f"Test 3 - Article URL: {url}")

    @patch('metapub.findit.dances.degruyter.the_doi_2step')
    @patch('requests.get')
    def test_degruyter_dance_successful_access_with_pdf(self, mock_get, mock_doi_2step):
        """Test 4: Successful access simulation with PDF link found.
        
        PMID: 38869142 (Phonetica)
        Expected: Should return PDF URL when found on page
        """
        # Mock DOI resolution to De Gruyter article page
        mock_doi_2step.return_value = 'https://www.degruyterbrill.com/document/doi/10.1515/phon-2023-0049/html'
        
        # Mock successful article page response with PDF link
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.text = '''
        <html>
            <body>
                <h1>Article Title</h1>
                <p>This is an article page with PDF download available.</p>
                <a href="/downloadpdf/journals/phon/81/4/article-p123.pdf" class="pdf-link">Download PDF</a>
            </body>
        </html>
        '''
        mock_response.content = mock_response.text.encode('utf-8')
        mock_response.url = 'https://www.degruyterbrill.com/document/doi/10.1515/phon-2023-0049/html'
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('38869142')
        
        # Test with verification - should find PDF link
        url = the_degruyter_danza(pma, verify=True)
        assert 'degruyterbrill.com' in url
        assert '.pdf' in url
        print(f"Test 4 - Found PDF link: {url}")

    @patch('metapub.findit.dances.degruyter.the_doi_2step')
    @patch('requests.get')
    def test_degruyter_dance_paywall_detection(self, mock_get, mock_doi_2step):
        """Test 5: Paywall detection.
        
        Expected: Should detect paywall and raise AccessDenied
        """
        # Mock DOI resolution to De Gruyter article page
        mock_doi_2step.return_value = 'https://www.degruyterbrill.com/document/doi/10.1515/phon-2023-0049/html'
        
        # Mock article page response with paywall indicators
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.text = '''
        <html>
            <body>
                <h1>Article Title</h1>
                <p>This content requires institutional access.</p>
                <div class="paywall">
                    <p>Please log in to access this article.</p>
                    <a href="/login">Sign In</a>
                    <a href="/subscribe">Subscribe</a>
                    <p>Purchase this article for $39.95</p>
                </div>
            </body>
        </html>
        '''
        mock_response.content = mock_response.text.encode('utf-8')
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('38869142')
        
        # Test with verification - should detect paywall
        with pytest.raises(AccessDenied) as exc_info:
            the_degruyter_danza(pma, verify=True)
        
        assert 'PAYWALL' in str(exc_info.value)
        assert 'subscription' in str(exc_info.value)
        print(f"Test 5 - Correctly detected paywall: {exc_info.value}")

    @patch('metapub.findit.dances.degruyter.the_doi_2step')
    @patch('requests.get')
    def test_degruyter_dance_access_forbidden(self, mock_get, mock_doi_2step):
        """Test 6: Access forbidden (403 error).
        
        Expected: Should handle 403 errors properly
        """
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://www.degruyterbrill.com/document/doi/10.1515/phon-2023-0049/html'
        
        # Mock 403 response
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.ok = False
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('38869142')
        
        # Test with verification - should handle 403
        with pytest.raises(AccessDenied) as exc_info:
            the_degruyter_danza(pma, verify=True)
        
        assert 'DENIED' in str(exc_info.value)
        assert '403' in str(exc_info.value) or 'forbidden' in str(exc_info.value).lower()
        print(f"Test 6 - Correctly handled 403: {exc_info.value}")

    @patch('metapub.findit.dances.degruyter.the_doi_2step')
    @patch('requests.get')
    def test_degruyter_dance_network_error(self, mock_get, mock_doi_2step):
        """Test 7: Network error handling.
        
        Expected: Should handle network errors gracefully
        """
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://www.degruyterbrill.com/document/doi/10.1515/phon-2023-0049/html'
        
        # Mock network error
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

        pma = self.fetch.article_by_pmid('38869142')
        
        # Test - should handle network error
        with pytest.raises(NoPDFLink) as exc_info:
            the_degruyter_danza(pma, verify=True)
        
        assert 'TXERROR' in str(exc_info.value)
        assert 'Network error' in str(exc_info.value)
        print(f"Test 7 - Correctly handled network error: {exc_info.value}")

    def test_degruyter_dance_missing_doi(self):
        """Test 8: Article without DOI.
        
        Expected: Should raise NoPDFLink for missing DOI
        """
        # Create a mock PMA without DOI
        pma = Mock()
        pma.doi = None
        pma.journal = 'Phonetica'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_degruyter_danza(pma, verify=False)
        
        assert 'MISSING' in str(exc_info.value)
        assert 'DOI required' in str(exc_info.value)
        print(f"Test 8 - Correctly handled missing DOI: {exc_info.value}")

    @patch('metapub.findit.dances.degruyter.the_doi_2step')
    @patch('requests.get')
    def test_degruyter_dance_article_not_found(self, mock_get, mock_doi_2step):
        """Test 9: Article not found (404 error).
        
        Expected: Should handle 404 errors properly
        """
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://www.degruyterbrill.com/document/doi/10.1515/phon-2023-0049/html' 
        
        # Mock 404 response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.ok = False
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('38869142')
        
        # Test with verification - should handle 404
        with pytest.raises(NoPDFLink) as exc_info:
            the_degruyter_danza(pma, verify=True)
        
        assert 'TXERROR' in str(exc_info.value)
        assert '404' in str(exc_info.value) or 'not found' in str(exc_info.value)
        print(f"Test 9 - Correctly handled 404: {exc_info.value}")

    @patch('metapub.findit.dances.degruyter.the_doi_2step')
    @patch('requests.get') 
    def test_degruyter_dance_open_access_article(self, mock_get, mock_doi_2step):
        """Test 10: Open access article without paywall.
        
        Expected: Should return article URL for open access content
        """
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://www.degruyterbrill.com/document/doi/10.1515/phon-2023-0049/html'
        
        # Mock successful article page response without paywall indicators
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.text = '''
        <html>
            <body>
                <h1>Article Title</h1>
                <p>This is an open access article.</p>
                <div class="article-content">
                    <p>Full article content is available here.</p>
                </div>
            </body>
        </html>
        '''
        mock_response.content = mock_response.text.encode('utf-8')
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('38869142')
        
        # Test with verification - should return article URL
        url = the_degruyter_danza(pma, verify=True)
        assert url == 'https://www.degruyterbrill.com/document/doi/10.1515/phon-2023-0049/html'
        print(f"Test 10 - Open access article URL: {url}")


def test_degruyter_journal_recognition():
    """Test that De Gruyter journals are properly recognized in the registry."""
    from metapub.findit.registry import JournalRegistry
    from metapub.findit.journals.degruyter import degruyter_journals
    
    registry = JournalRegistry()
    
    # Test sample De Gruyter journals
    test_journals = [
        'Phonetica',
        'Int J Soc Lang',
        'Biol Chem',
        'Pure Appl Chem'
    ]
    
    # Test journal recognition
    found_count = 0
    for journal in test_journals:
        if journal in degruyter_journals:
            publisher_info = registry.get_publisher_for_journal(journal)
            if publisher_info and publisher_info['name'] == 'degruyter':
                assert publisher_info['dance_function'] == 'the_degruyter_danza'
                print(f"✓ {journal} correctly mapped to De Gruyter")
                found_count += 1
            else:
                print(f"⚠ {journal} mapped to different publisher: {publisher_info['name'] if publisher_info else 'None'}")
        else:
            print(f"⚠ {journal} not in degruyter_journals list")
    
    # Just make sure we found at least one De Gruyter journal
    assert found_count > 0, "No De Gruyter journals found in registry with degruyter publisher"
    print(f"✓ Found {found_count} properly mapped De Gruyter journals")
    
    registry.close()


if __name__ == '__main__':
    # Run basic tests if executed directly
    test_instance = TestDeGruyterDance()
    test_instance.setUp()
    
    print("Running De Gruyter tests...")
    print("\n" + "="*60)
    
    tests = [
        ('test_degruyter_dance_url_construction_phonetica', 'Phonetica URL construction'),
        ('test_degruyter_dance_url_construction_intl_soc_lang', 'Int J Soc Lang URL construction'),
        ('test_degruyter_dance_url_construction_non_1515_doi', 'Non-10.1515 DOI handling'),
        ('test_degruyter_dance_successful_access_with_pdf', 'Successful access with PDF'),
        ('test_degruyter_dance_paywall_detection', 'Paywall detection'),
        ('test_degruyter_dance_access_forbidden', 'Access forbidden handling'),
        ('test_degruyter_dance_network_error', 'Network error handling'),
        ('test_degruyter_dance_missing_doi', 'Missing DOI handling'),
        ('test_degruyter_dance_article_not_found', 'Article not found handling'),
        ('test_degruyter_dance_open_access_article', 'Open access article handling')
    ]
    
    for test_method, description in tests:
        try:
            getattr(test_instance, test_method)()
            print(f"✓ {description} works")
        except Exception as e:
            print(f"✗ {description} failed: {e}")
    
    try:
        test_degruyter_journal_recognition()
        print("✓ Registry test passed: Journal recognition works")
    except Exception as e:
        print(f"✗ Registry test failed: {e}")
    
    print("\n" + "="*60)
    print("Test suite completed!")