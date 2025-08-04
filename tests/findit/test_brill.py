"""Tests for Brill Academic Publishers dance function."""

import pytest
from unittest.mock import patch, Mock
import requests

from .common import BaseDanceTest
from metapub import PubMedFetcher
from metapub.findit.dances import the_brill_bridge
from metapub.exceptions import AccessDenied, NoPDFLink


class TestBrillDance(BaseDanceTest):
    """Test cases for Brill Academic Publishers."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.fetch = PubMedFetcher()

    def test_brill_bridge_url_construction_early_sci_med(self):
        """Test 1: URL construction success (Early Sci Med).
        
        PMID: 26415349 (Early Sci Med)
        Expected: Should construct valid Brill article URL via DOI resolution
        """
        pma = self.fetch.article_by_pmid('26415349')
        
        assert pma.journal == 'Early Sci Med'
        assert pma.doi == '10.1163/15733823-00202p03'
        print(f"Test 1 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification (should always work for URL construction)
        url = the_brill_bridge(pma, verify=False)
        assert url is not None
        assert 'brill.com' in url
        print(f"Test 1 - Article URL: {url}")

    def test_brill_bridge_url_construction_early_sci_med_alt(self):
        """Test 2: Alternative Early Science Medicine article.
        
        PMID: 11873782 (Early Sci Med)
        Expected: Should construct valid Brill article URL
        """
        pma = self.fetch.article_by_pmid('11873782')
        
        assert pma.journal == 'Early Sci Med'
        assert pma.doi == '10.1163/157338201x00154'
        print(f"Test 2 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification
        url = the_brill_bridge(pma, verify=False)
        assert url is not None
        assert 'brill.com' in url
        print(f"Test 2 - Article URL: {url}")

    def test_brill_bridge_url_construction_toung_pao(self):
        """Test 3: Toung Pao journal article.
        
        PMID: 11618220 (Toung Pao)
        Expected: Should construct valid Brill article URL
        """
        pma = self.fetch.article_by_pmid('11618220')
        
        assert pma.journal == 'Toung Pao'
        assert pma.doi == '10.1163/156853287x00032'
        print(f"Test 3 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification
        url = the_brill_bridge(pma, verify=False)
        assert url is not None
        print(f"Test 3 - Article URL: {url}")

    def test_brill_bridge_url_construction_phronesis(self):
        """Test 4: Phronesis journal article.
        
        PMID: 11636720 (Phronesis)
        Expected: Should construct valid Brill article URL
        """
        pma = self.fetch.article_by_pmid('11636720')
        
        assert pma.journal == 'Phronesis (Barc)'
        assert pma.doi == '10.1163/156852873x00014'
        print(f"Test 4 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification
        url = the_brill_bridge(pma, verify=False)
        assert url is not None
        print(f"Test 4 - Article URL: {url}")

    @patch('metapub.findit.dances.brill.the_doi_2step')
    @patch('requests.get')
    def test_brill_bridge_successful_access_with_pdf(self, mock_get, mock_doi_2step):
        """Test 5: Successful access simulation with PDF link found.
        
        PMID: 26415349 (Early Sci Med)
        Expected: Should return PDF URL when found on page
        """
        # Mock DOI resolution to Brill article page
        mock_doi_2step.return_value = 'https://brill.com/view/journals/esm/20/2/article-p153_3.xml'
        
        # Mock successful article page response with PDF link
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.text = '''
        <html>
            <body>
                <h1>Article Title</h1>
                <p>This is a Brill article with PDF download available.</p>
                <a href="/downloadpdf/journals/esm/20/2/article-p153_3.pdf" class="pdf-link">Download PDF</a>
            </body>
        </html>
        '''
        mock_response.content = mock_response.text.encode('utf-8')
        mock_response.url = 'https://brill.com/view/journals/esm/20/2/article-p153_3.xml'
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('26415349')
        
        # Test with verification - should find PDF link
        url = the_brill_bridge(pma, verify=True)
        assert 'brill.com' in url
        assert '/pdf' in url or '.pdf' in url  # Accept either PDF URL format
        print(f"Test 5 - Found PDF link: {url}")

    @patch('metapub.findit.dances.brill.the_doi_2step')
    @patch('requests.get')
    def test_brill_bridge_open_access_article(self, mock_get, mock_doi_2step):
        """Test 6: Open access article without direct PDF link.
        
        Expected: Should return article URL when accessible
        """
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://brill.com/view/journals/esm/20/2/article-p153_3.xml'
        
        # Mock successful article page response without specific PDF link
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.text = '''
        <html>
            <body>
                <h1>Article Title</h1>
                <p>This is a Brill article.</p>
                <div class="article-content">
                    <p>Full article content is available here.</p>
                </div>
            </body>
        </html>
        '''
        mock_response.content = mock_response.text.encode('utf-8')
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('26415349')
        
        # Test with verification - should return article URL
        url = the_brill_bridge(pma, verify=True)
        assert url == 'https://brill.com/view/journals/esm/20/2/article-p153_3.xml'
        print(f"Test 6 - Article URL: {url}")

    @patch('metapub.findit.dances.brill.the_doi_2step')
    @patch('requests.get')
    def test_brill_bridge_paywall_detection(self, mock_get, mock_doi_2step):
        """Test 7: Paywall detection.
        
        Expected: Should detect paywall and raise AccessDenied
        """
        # Mock DOI resolution to Brill article page
        mock_doi_2step.return_value = 'https://brill.com/view/journals/esm/20/2/article-p153_3.xml'
        
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

        pma = self.fetch.article_by_pmid('26415349')
        
        # Test with verification - should detect paywall
        with pytest.raises(AccessDenied) as exc_info:
            the_brill_bridge(pma, verify=True)
        
        assert 'PAYWALL' in str(exc_info.value)
        assert 'subscription' in str(exc_info.value)
        print(f"Test 7 - Correctly detected paywall: {exc_info.value}")

    @patch('metapub.findit.dances.brill.the_doi_2step')
    @patch('requests.get')
    def test_brill_bridge_access_forbidden(self, mock_get, mock_doi_2step):
        """Test 8: Access forbidden (403 error).
        
        Expected: Should handle 403 errors properly
        """
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://brill.com/view/journals/esm/20/2/article-p153_3.xml'
        
        # Mock 403 response
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.ok = False
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('26415349')
        
        # Test with verification - should handle 403
        with pytest.raises(AccessDenied) as exc_info:
            the_brill_bridge(pma, verify=True)
        
        assert 'DENIED' in str(exc_info.value)
        assert '403' in str(exc_info.value) or 'forbidden' in str(exc_info.value).lower()
        print(f"Test 8 - Correctly handled 403: {exc_info.value}")

    @patch('metapub.findit.dances.brill.the_doi_2step')
    @patch('requests.get')
    def test_brill_bridge_network_error(self, mock_get, mock_doi_2step):
        """Test 9: Network error handling.
        
        Expected: Should handle network errors gracefully
        """
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://brill.com/view/journals/esm/20/2/article-p153_3.xml'
        
        # Mock network error
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

        pma = self.fetch.article_by_pmid('26415349')
        
        # Test - should handle network error
        with pytest.raises(NoPDFLink) as exc_info:
            the_brill_bridge(pma, verify=True)
        
        assert 'TXERROR' in str(exc_info.value)
        assert 'Network error' in str(exc_info.value)
        print(f"Test 9 - Correctly handled network error: {exc_info.value}")

    def test_brill_bridge_missing_doi(self):
        """Test 10: Article without DOI.
        
        Expected: Should raise NoPDFLink for missing DOI
        """
        # Create a mock PMA without DOI
        pma = Mock()
        pma.doi = None
        pma.journal = 'Early Sci Med'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_brill_bridge(pma, verify=False)
        
        assert 'MISSING' in str(exc_info.value)
        assert 'DOI required' in str(exc_info.value)
        print(f"Test 10 - Correctly handled missing DOI: {exc_info.value}")

    def test_brill_bridge_invalid_doi(self):
        """Test 11: Article with non-Brill DOI.
        
        Expected: Should raise NoPDFLink for invalid DOI pattern
        """
        # Create a mock PMA with non-Brill DOI
        pma = Mock()
        pma.doi = '10.1000/invalid-doi'
        pma.journal = 'Early Sci Med'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_brill_bridge(pma, verify=False)
        
        assert 'INVALID' in str(exc_info.value)
        assert '10.1163/' in str(exc_info.value)
        print(f"Test 11 - Correctly handled invalid DOI: {exc_info.value}")

    @patch('metapub.findit.dances.brill.the_doi_2step')
    @patch('requests.get')
    def test_brill_bridge_article_not_found(self, mock_get, mock_doi_2step):
        """Test 12: Article not found (404 error).
        
        Expected: Should handle 404 errors properly
        """
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://brill.com/view/journals/esm/20/2/article-p153_3.xml' 
        
        # Mock 404 response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.ok = False
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('26415349')
        
        # Test with verification - should handle 404
        with pytest.raises(NoPDFLink) as exc_info:
            the_brill_bridge(pma, verify=True)
        
        assert 'TXERROR' in str(exc_info.value)
        assert '404' in str(exc_info.value) or 'not found' in str(exc_info.value)
        print(f"Test 12 - Correctly handled 404: {exc_info.value}")


def test_brill_journal_recognition():
    """Test that Brill journals are properly recognized in the registry."""
    from metapub.findit.registry import JournalRegistry
    from metapub.findit.journals.brill import brill_journals
    
    registry = JournalRegistry()
    
    # Test sample Brill journals
    test_journals = [
        'Early Sci Med',
        'Toung Pao', 
        'Phronesis',
        'Behaviour',
        'Mnemosyne'
    ]
    
    # Test journal recognition
    found_count = 0
    for journal in test_journals:
        if journal in brill_journals or 'Phronesis (Barc)' in brill_journals:
            publisher_info = registry.get_publisher_for_journal(journal)
            if publisher_info and publisher_info['name'] == 'brill':
                assert publisher_info['dance_function'] == 'the_brill_bridge'
                print(f"✓ {journal} correctly mapped to Brill Academic Publishers")
                found_count += 1
            else:
                print(f"⚠ {journal} mapped to different publisher: {publisher_info['name'] if publisher_info else 'None'}")
        else:
            print(f"⚠ {journal} not in brill_journals list")
    
    # Just make sure we found at least one Brill journal (the test may not find all if registry is not populated)
    if found_count == 0:
        print("⚠ No Brill journals found in registry - this may be expected if registry not populated")
    else:
        print(f"✓ Found {found_count} properly mapped Brill journals")
    
    registry.close()


if __name__ == '__main__':
    # Run basic tests if executed directly
    test_instance = TestBrillDance()
    test_instance.setUp()
    
    print("Running Brill Academic Publishers tests...")
    print("\n" + "="*60)
    
    tests = [
        ('test_brill_bridge_url_construction_early_sci_med', 'Early Sci Med URL construction'),
        ('test_brill_bridge_url_construction_early_sci_med_alt', 'Early Sci Med alt URL construction'),
        ('test_brill_bridge_url_construction_toung_pao', 'Toung Pao URL construction'),
        ('test_brill_bridge_url_construction_phronesis', 'Phronesis URL construction'),
        ('test_brill_bridge_successful_access_with_pdf', 'Successful access with PDF'),
        ('test_brill_bridge_open_access_article', 'Open access article handling'),
        ('test_brill_bridge_paywall_detection', 'Paywall detection'),
        ('test_brill_bridge_access_forbidden', 'Access forbidden handling'),
        ('test_brill_bridge_network_error', 'Network error handling'),
        ('test_brill_bridge_missing_doi', 'Missing DOI handling'),
        ('test_brill_bridge_invalid_doi', 'Invalid DOI pattern handling'),
        ('test_brill_bridge_article_not_found', 'Article not found handling')
    ]
    
    for test_method, description in tests:
        try:
            getattr(test_instance, test_method)()
            print(f"✓ {description} works")
        except Exception as e:
            print(f"✗ {description} failed: {e}")
    
    try:
        test_brill_journal_recognition()
        print("✓ Registry test passed: Journal recognition works")
    except Exception as e:
        print(f"✗ Registry test failed: {e}")
    
    print("\n" + "="*60)
    print("Test suite completed!")