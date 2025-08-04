"""Tests for Annual Reviews dance function."""

import pytest
from unittest.mock import patch, Mock
import requests

from .common import BaseDanceTest
from metapub import PubMedFetcher
from metapub.findit.dances import the_annualreviews_round
from metapub.exceptions import AccessDenied, NoPDFLink


class TestAnnualReviewsDance(BaseDanceTest):
    """Test cases for Annual Reviews Inc. publisher."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.fetch = PubMedFetcher()

    def test_annualreviews_round_url_construction_phytopathol(self):
        """Test 1: URL construction success (Annu Rev Phytopathol).
        
        PMID: 38885471 (Annu Rev Phytopathol)
        Expected: Should construct valid Annual Reviews article URL via DOI resolution
        """
        pma = self.fetch.article_by_pmid('38885471')
        
        assert pma.journal == 'Annu Rev Phytopathol'
        assert pma.doi == '10.1146/annurev-phyto-021722-034823'
        print(f"Test 1 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification (should always work for URL construction)
        url = the_annualreviews_round(pma, verify=False)
        assert url is not None
        assert 'annualreviews.org' in url
        print(f"Test 1 - Article URL: {url}")

    def test_annualreviews_round_url_construction_genomics(self):
        """Test 2: Annual Review of Genomics and Human Genetics article.
        
        PMID: 38724024 (Annu Rev Genomics Hum Genet)
        Expected: Should construct valid Annual Reviews article URL
        """
        pma = self.fetch.article_by_pmid('38724024')
        
        assert pma.journal == 'Annu Rev Genomics Hum Genet'
        assert pma.doi == '10.1146/annurev-genom-121222-105345'
        print(f"Test 2 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification
        url = the_annualreviews_round(pma, verify=False)
        assert url is not None
        assert 'annualreviews.org' in url
        print(f"Test 2 - Article URL: {url}")

    def test_annualreviews_round_url_construction_marine_sci(self):
        """Test 3: Annual Review of Marine Science article.
        
        PMID: 38896540 (Ann Rev Mar Sci)
        Expected: Should construct valid Annual Reviews article URL
        """
        pma = self.fetch.article_by_pmid('38896540')
        
        assert pma.journal == 'Ann Rev Mar Sci'
        assert pma.doi == '10.1146/annurev-marine-121422-015323'
        print(f"Test 3 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification
        url = the_annualreviews_round(pma, verify=False)
        assert url is not None
        print(f"Test 3 - Article URL: {url}")

    @patch('metapub.findit.dances.annualreviews.the_doi_2step')
    @patch('requests.get')
    def test_annualreviews_round_successful_access_with_pdf(self, mock_get, mock_doi_2step):
        """Test 4: Successful access simulation with PDF link found.
        
        PMID: 38885471 (Annu Rev Phytopathol)
        Expected: Should return PDF URL when found on page
        """
        # Mock DOI resolution to Annual Reviews article page
        mock_doi_2step.return_value = 'https://www.annualreviews.org/doi/10.1146/annurev-phyto-021722-034823'
        
        # Mock successful article page response with PDF link
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.text = '''
        <html>
            <body>
                <h1>Article Title</h1>
                <p>This is an Annual Reviews article with PDF download available.</p>
                <a href="/doi/pdf/10.1146/annurev-phyto-021722-034823" class="pdf-link">Download PDF</a>
            </body>
        </html>
        '''
        mock_response.content = mock_response.text.encode('utf-8')
        mock_response.url = 'https://www.annualreviews.org/doi/10.1146/annurev-phyto-021722-034823'
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('38885471')
        
        # Test with verification - should find PDF link
        url = the_annualreviews_round(pma, verify=True)
        assert 'annualreviews.org' in url
        assert '/pdf/' in url or '.pdf' in url  # Accept either PDF URL format
        print(f"Test 4 - Found PDF link: {url}")

    @patch('metapub.findit.dances.annualreviews.the_doi_2step')
    @patch('requests.get')
    def test_annualreviews_round_open_access_article(self, mock_get, mock_doi_2step):
        """Test 5: Open access article without direct PDF link.
        
        Expected: Should return article URL when accessible
        """
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://www.annualreviews.org/doi/10.1146/annurev-phyto-021722-034823'
        
        # Mock successful article page response without specific PDF link
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.text = '''
        <html>
            <body>
                <h1>Article Title</h1>
                <p>This is an Annual Reviews article.</p>
                <div class="article-content">
                    <p>Full article content is available here.</p>
                </div>
            </body>
        </html>
        '''
        mock_response.content = mock_response.text.encode('utf-8')
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('38885471')
        
        # Test with verification - should return article URL
        url = the_annualreviews_round(pma, verify=True)
        assert url == 'https://www.annualreviews.org/doi/10.1146/annurev-phyto-021722-034823'
        print(f"Test 5 - Article URL: {url}")

    @patch('metapub.findit.dances.annualreviews.the_doi_2step')
    @patch('requests.get')
    def test_annualreviews_round_paywall_detection(self, mock_get, mock_doi_2step):
        """Test 6: Paywall detection.
        
        Expected: Should detect paywall and raise AccessDenied
        """
        # Mock DOI resolution to Annual Reviews article page
        mock_doi_2step.return_value = 'https://www.annualreviews.org/doi/10.1146/annurev-phyto-021722-034823'
        
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
                    <p>Purchase this article for $49.95</p>
                </div>
            </body>
        </html>
        '''
        mock_response.content = mock_response.text.encode('utf-8')
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('38885471')
        
        # Test with verification - should detect paywall
        with pytest.raises(AccessDenied) as exc_info:
            the_annualreviews_round(pma, verify=True)
        
        assert 'PAYWALL' in str(exc_info.value)
        assert 'subscription' in str(exc_info.value)
        print(f"Test 6 - Correctly detected paywall: {exc_info.value}")

    @patch('metapub.findit.dances.annualreviews.the_doi_2step')
    @patch('requests.get')
    def test_annualreviews_round_access_forbidden(self, mock_get, mock_doi_2step):
        """Test 7: Access forbidden (403 error).
        
        Expected: Should handle 403 errors properly
        """
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://www.annualreviews.org/doi/10.1146/annurev-phyto-021722-034823'
        
        # Mock 403 response
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.ok = False
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('38885471')
        
        # Test with verification - should handle 403
        with pytest.raises(AccessDenied) as exc_info:
            the_annualreviews_round(pma, verify=True)
        
        assert 'DENIED' in str(exc_info.value)
        assert '403' in str(exc_info.value) or 'forbidden' in str(exc_info.value).lower()
        print(f"Test 7 - Correctly handled 403: {exc_info.value}")

    @patch('metapub.findit.dances.annualreviews.the_doi_2step')
    @patch('requests.get')
    def test_annualreviews_round_network_error(self, mock_get, mock_doi_2step):
        """Test 8: Network error handling.
        
        Expected: Should handle network errors gracefully
        """
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://www.annualreviews.org/doi/10.1146/annurev-phyto-021722-034823'
        
        # Mock network error
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

        pma = self.fetch.article_by_pmid('38885471')
        
        # Test - should handle network error
        with pytest.raises(NoPDFLink) as exc_info:
            the_annualreviews_round(pma, verify=True)
        
        assert 'TXERROR' in str(exc_info.value)
        assert 'Network error' in str(exc_info.value)
        print(f"Test 8 - Correctly handled network error: {exc_info.value}")

    def test_annualreviews_round_missing_doi(self):
        """Test 9: Article without DOI.
        
        Expected: Should raise NoPDFLink for missing DOI
        """
        # Create a mock PMA without DOI
        pma = Mock()
        pma.doi = None
        pma.journal = 'Annu Rev Phytopathol'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_annualreviews_round(pma, verify=False)
        
        assert 'MISSING' in str(exc_info.value)
        assert 'DOI required' in str(exc_info.value)
        print(f"Test 9 - Correctly handled missing DOI: {exc_info.value}")

    def test_annualreviews_round_invalid_doi(self):
        """Test 10: Article with non-Annual Reviews DOI.
        
        Expected: Should raise NoPDFLink for invalid DOI pattern
        """
        # Create a mock PMA with non-Annual Reviews DOI
        pma = Mock()
        pma.doi = '10.1000/invalid-doi'
        pma.journal = 'Annu Rev Phytopathol'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_annualreviews_round(pma, verify=False)
        
        assert 'INVALID' in str(exc_info.value)
        assert '10.1146/' in str(exc_info.value)
        print(f"Test 10 - Correctly handled invalid DOI: {exc_info.value}")

    @patch('metapub.findit.dances.annualreviews.the_doi_2step')
    @patch('requests.get')
    def test_annualreviews_round_article_not_found(self, mock_get, mock_doi_2step):
        """Test 11: Article not found (404 error).
        
        Expected: Should handle 404 errors properly
        """
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://www.annualreviews.org/doi/10.1146/annurev-phyto-021722-034823' 
        
        # Mock 404 response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.ok = False
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('38885471')
        
        # Test with verification - should handle 404
        with pytest.raises(NoPDFLink) as exc_info:
            the_annualreviews_round(pma, verify=True)
        
        assert 'TXERROR' in str(exc_info.value)
        assert '404' in str(exc_info.value) or 'not found' in str(exc_info.value)
        print(f"Test 11 - Correctly handled 404: {exc_info.value}")


def test_annualreviews_journal_recognition():
    """Test that Annual Reviews journals are properly recognized in the registry."""
    from metapub.findit.registry import JournalRegistry
    from metapub.findit.journals.annualreviews import annualreviews_journals
    
    registry = JournalRegistry()
    
    # Test sample Annual Reviews journals
    test_journals = [
        'Annu Rev Phytopathol',
        'Annu Rev Genomics Hum Genet',
        'Ann Rev Mar Sci',
        'Annu Rev Biochem',
        'Annu Rev Neurosci'
    ]
    
    # Test journal recognition
    found_count = 0
    for journal in test_journals:
        if journal in annualreviews_journals:
            publisher_info = registry.get_publisher_for_journal(journal)
            if publisher_info and publisher_info['name'] == 'annualreviews':
                assert publisher_info['dance_function'] == 'the_annualreviews_round'
                print(f"✓ {journal} correctly mapped to Annual Reviews")
                found_count += 1
            else:
                print(f"⚠ {journal} mapped to different publisher: {publisher_info['name'] if publisher_info else 'None'}")
        else:
            print(f"⚠ {journal} not in annualreviews_journals list")
    
    # Just make sure we found at least one Annual Reviews journal
    assert found_count > 0, "No Annual Reviews journals found in registry with annualreviews publisher"
    print(f"✓ Found {found_count} properly mapped Annual Reviews journals")
    
    registry.close()


if __name__ == '__main__':
    # Run basic tests if executed directly
    test_instance = TestAnnualReviewsDance()
    test_instance.setUp()
    
    print("Running Annual Reviews tests...")
    print("\n" + "="*60)
    
    tests = [
        ('test_annualreviews_round_url_construction_phytopathol', 'Annu Rev Phytopathol URL construction'),
        ('test_annualreviews_round_url_construction_genomics', 'Annu Rev Genomics Hum Genet URL construction'),
        ('test_annualreviews_round_url_construction_marine_sci', 'Ann Rev Mar Sci URL construction'),
        ('test_annualreviews_round_successful_access_with_pdf', 'Successful access with PDF'),
        ('test_annualreviews_round_open_access_article', 'Open access article handling'),
        ('test_annualreviews_round_paywall_detection', 'Paywall detection'),
        ('test_annualreviews_round_access_forbidden', 'Access forbidden handling'),
        ('test_annualreviews_round_network_error', 'Network error handling'),
        ('test_annualreviews_round_missing_doi', 'Missing DOI handling'),
        ('test_annualreviews_round_invalid_doi', 'Invalid DOI pattern handling'),
        ('test_annualreviews_round_article_not_found', 'Article not found handling')
    ]
    
    for test_method, description in tests:
        try:
            getattr(test_instance, test_method)()
            print(f"✓ {description} works")
        except Exception as e:
            print(f"✗ {description} failed: {e}")
    
    try:
        test_annualreviews_journal_recognition()
        print("✓ Registry test passed: Journal recognition works")
    except Exception as e:
        print(f"✗ Registry test failed: {e}")
    
    print("\n" + "="*60)
    print("Test suite completed!")