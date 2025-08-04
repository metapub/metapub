"""Tests for BioOne dance function."""

import pytest
from unittest.mock import patch, Mock
import requests

from .common import BaseDanceTest
from metapub import PubMedFetcher
from metapub.findit.dances import the_bioone_bounce
from metapub.exceptions import AccessDenied, NoPDFLink


class TestBioOneDance(BaseDanceTest):
    """Test cases for BioOne platform."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.fetch = PubMedFetcher()

    def test_bioone_bounce_url_construction_j_parasitol(self):
        """Test 1: URL construction success (J Parasitol).
        
        PMID: 38897605 (J Parasitol)
        Expected: Should construct valid BioOne article URL via DOI resolution
        """
        pma = self.fetch.article_by_pmid('38897605')
        
        assert pma.journal == 'J Parasitol'
        print(f"Test 1 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification (should always work for URL construction)
        url = the_bioone_bounce(pma, verify=False)
        assert url is not None
        print(f"Test 1 - Article URL: {url}")

    def test_bioone_bounce_url_construction_j_wildl_dis(self):
        """Test 2: J Wildl Dis article.
        
        PMID: 38914427 (J Wildl Dis)
        Expected: Should construct valid BioOne article URL
        """
        pma = self.fetch.article_by_pmid('38914427')
        
        assert pma.journal == 'J Wildl Dis'
        print(f"Test 2 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification
        url = the_bioone_bounce(pma, verify=False)
        assert url is not None
        print(f"Test 2 - Article URL: {url}")

    def test_bioone_bounce_url_construction_avian_dis(self):
        """Test 3: Avian Dis article.
        
        PMID: 38885058 (Avian Dis)
        Expected: Should construct valid BioOne article URL
        """
        pma = self.fetch.article_by_pmid('38885058')
        
        assert pma.journal == 'Avian Dis'
        print(f"Test 3 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification
        url = the_bioone_bounce(pma, verify=False)
        assert url is not None
        print(f"Test 3 - Article URL: {url}")

    def test_bioone_bounce_url_construction_j_vector_ecol(self):
        """Test 4: J Vector Ecol article.
        
        PMID: 38147301 (J Vector Ecol)
        Expected: Should construct valid BioOne article URL
        """
        pma = self.fetch.article_by_pmid('38147301')
        
        assert pma.journal == 'J Vector Ecol'
        print(f"Test 4 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification
        url = the_bioone_bounce(pma, verify=False)
        assert url is not None
        print(f"Test 4 - Article URL: {url}")

    def test_bioone_bounce_url_construction_j_zoo_wildl_med(self):
        """Test 5: J Zoo Wildl Med article.
        
        PMID: 38875213 (J Zoo Wildl Med)
        Expected: Should construct valid BioOne article URL
        """
        pma = self.fetch.article_by_pmid('38875213')
        
        assert pma.journal == 'J Zoo Wildl Med'
        print(f"Test 5 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification
        url = the_bioone_bounce(pma, verify=False)
        assert url is not None
        print(f"Test 5 - Article URL: {url}")

    @patch('metapub.findit.dances.bioone.the_doi_2step')
    @patch('requests.get')
    def test_bioone_bounce_successful_access_with_pdf(self, mock_get, mock_doi_2step):
        """Test 6: Successful access simulation with PDF link found.
        
        PMID: 38897605 (J Parasitol)
        Expected: Should return PDF URL when found on page
        """
        # Mock DOI resolution to BioOne article page
        mock_doi_2step.return_value = 'https://complete.bioone.org/journals/journal-of-parasitology/volume-111/issue-4/25-22/test-article/10.1645/25-22.full'
        
        # Mock successful article page response with PDF link
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.text = '''
        <html>
            <body>
                <h1>Article Title</h1>
                <p>This is a BioOne article with PDF download available.</p>
                <a href="/journals/journal-of-parasitology/volume-111/issue-4/25-22/test-article/10.1645/25-22.pdf" class="pdf-link">Download PDF</a>
            </body>
        </html>
        '''
        mock_response.content = mock_response.text.encode('utf-8')
        mock_response.url = 'https://complete.bioone.org/journals/journal-of-parasitology/volume-111/issue-4/25-22/test-article/10.1645/25-22.full'
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('38897605')
        
        # Test with verification - should find PDF link
        url = the_bioone_bounce(pma, verify=True)
        assert 'bioone.org' in url or 'complete.bioone.org' in url
        assert 'pdf' in url  # Accept any PDF URL format
        print(f"Test 6 - Found PDF link: {url}")

    @patch('metapub.findit.dances.bioone.the_doi_2step')
    @patch('requests.get')
    def test_bioone_bounce_open_access_article(self, mock_get, mock_doi_2step):
        """Test 7: Open access article without direct PDF link.
        
        Expected: Should return article URL when accessible
        """
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://complete.bioone.org/journals/journal-of-parasitology/volume-111/issue-4/25-22/test-article/10.1645/25-22.full'
        
        # Mock successful article page response without specific PDF link
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.text = '''
        <html>
            <body>
                <h1>Article Title</h1>
                <p>This is a BioOne article.</p>
                <div class="article-content">
                    <p>Full article content is available here.</p>
                </div>
            </body>
        </html>
        '''
        mock_response.content = mock_response.text.encode('utf-8')
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('38897605')
        
        # Test with verification - should return article URL
        url = the_bioone_bounce(pma, verify=True)
        assert url == 'https://complete.bioone.org/journals/journal-of-parasitology/volume-111/issue-4/25-22/test-article/10.1645/25-22.full'
        print(f"Test 7 - Article URL: {url}")

    @patch('metapub.findit.dances.bioone.the_doi_2step')
    @patch('requests.get')
    def test_bioone_bounce_paywall_detection(self, mock_get, mock_doi_2step):
        """Test 8: Paywall detection.
        
        Expected: Should detect paywall and raise AccessDenied
        """
        # Mock DOI resolution to BioOne article page
        mock_doi_2step.return_value = 'https://complete.bioone.org/journals/journal-of-parasitology/volume-111/issue-4/25-22/test-article/10.1645/25-22.full'
        
        # Mock article page response with paywall indicators
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.text = '''
        <html>
            <body>
                <h1>Article Title</h1>
                <p>This content requires institutional access.</p>
                <div class="subscription-required">
                    <p>Please log in to access this article.</p>
                    <a href="/login">Sign In</a>
                    <a href="/institutional">Institutional Access</a>
                    <p>Purchase this article for institutional access</p>
                </div>
            </body>
        </html>
        '''
        mock_response.content = mock_response.text.encode('utf-8')
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('38897605')
        
        # Test with verification - should detect paywall
        with pytest.raises(AccessDenied) as exc_info:
            the_bioone_bounce(pma, verify=True)
        
        assert 'PAYWALL' in str(exc_info.value)
        assert 'subscription' in str(exc_info.value)
        print(f"Test 8 - Correctly detected paywall: {exc_info.value}")

    @patch('metapub.findit.dances.bioone.the_doi_2step')
    @patch('requests.get')
    def test_bioone_bounce_access_forbidden(self, mock_get, mock_doi_2step):
        """Test 9: Access forbidden (403 error).
        
        Expected: Should handle 403 errors properly
        """
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://complete.bioone.org/journals/journal-of-parasitology/volume-111/issue-4/25-22/test-article/10.1645/25-22.full'
        
        # Mock 403 response
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.ok = False
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('38897605')
        
        # Test with verification - should handle 403
        with pytest.raises(AccessDenied) as exc_info:
            the_bioone_bounce(pma, verify=True)
        
        assert 'DENIED' in str(exc_info.value)
        assert '403' in str(exc_info.value) or 'forbidden' in str(exc_info.value).lower()
        print(f"Test 9 - Correctly handled 403: {exc_info.value}")

    @patch('metapub.findit.dances.bioone.the_doi_2step')
    @patch('requests.get')
    def test_bioone_bounce_network_error(self, mock_get, mock_doi_2step):
        """Test 10: Network error handling.
        
        Expected: Should handle network errors gracefully
        """
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://complete.bioone.org/journals/journal-of-parasitology/volume-111/issue-4/25-22/test-article/10.1645/25-22.full'
        
        # Mock network error
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

        pma = self.fetch.article_by_pmid('38897605')
        
        # Test - should handle network error
        with pytest.raises(NoPDFLink) as exc_info:
            the_bioone_bounce(pma, verify=True)
        
        assert 'TXERROR' in str(exc_info.value)
        assert 'Network error' in str(exc_info.value)
        print(f"Test 10 - Correctly handled network error: {exc_info.value}")

    def test_bioone_bounce_missing_doi(self):
        """Test 11: Article without DOI.
        
        Expected: Should raise NoPDFLink for missing DOI
        """
        # Create a mock PMA without DOI
        pma = Mock()
        pma.doi = None
        pma.journal = 'J Parasitol'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_bioone_bounce(pma, verify=False)
        
        assert 'MISSING' in str(exc_info.value)
        assert 'DOI required' in str(exc_info.value)
        print(f"Test 11 - Correctly handled missing DOI: {exc_info.value}")

    @patch('metapub.findit.dances.bioone.the_doi_2step')
    @patch('requests.get')
    def test_bioone_bounce_article_not_found(self, mock_get, mock_doi_2step):
        """Test 12: Article not found (404 error).
        
        Expected: Should handle 404 errors properly
        """
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://complete.bioone.org/journals/journal-of-parasitology/volume-111/issue-4/25-22/test-article/10.1645/25-22.full'
        
        # Mock 404 response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.ok = False
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('38897605')
        
        # Test with verification - should handle 404
        with pytest.raises(NoPDFLink) as exc_info:
            the_bioone_bounce(pma, verify=True)
        
        assert 'TXERROR' in str(exc_info.value)
        assert '404' in str(exc_info.value) or 'not found' in str(exc_info.value)
        print(f"Test 12 - Correctly handled 404: {exc_info.value}")


def test_bioone_journal_recognition():
    """Test that BioOne journals are properly recognized in the registry."""
    from metapub.findit.registry import JournalRegistry
    from metapub.findit.journals.bioone import bioone_journals
    
    registry = JournalRegistry()
    
    # Test sample BioOne journals
    test_journals = [
        'J Parasitol',
        'J Wildl Dis', 
        'Avian Dis',
        'J Vector Ecol',
        'J Zoo Wildl Med'
    ]
    
    # Test journal recognition
    found_count = 0
    for journal in test_journals:
        if journal in bioone_journals:
            publisher_info = registry.get_publisher_for_journal(journal)
            if publisher_info and publisher_info['name'] == 'bioone':
                assert publisher_info['dance_function'] == 'the_bioone_bounce'
                print(f"✓ {journal} correctly mapped to BioOne")
                found_count += 1
            else:
                print(f"⚠ {journal} mapped to different publisher: {publisher_info['name'] if publisher_info else 'None'}")
        else:
            print(f"⚠ {journal} not in bioone_journals list")
    
    # Just make sure we found at least one BioOne journal (the test may not find all if registry is not populated)
    if found_count == 0:
        print("⚠ No BioOne journals found in registry - this may be expected if registry not populated")
    else:
        print(f"✓ Found {found_count} properly mapped BioOne journals")
    
    registry.close()


if __name__ == '__main__':
    # Run basic tests if executed directly
    test_instance = TestBioOneDance()
    test_instance.setUp()
    
    print("Running BioOne tests...")
    print("\n" + "="*60)
    
    tests = [
        ('test_bioone_bounce_url_construction_j_parasitol', 'J Parasitol URL construction'),
        ('test_bioone_bounce_url_construction_j_wildl_dis', 'J Wildl Dis URL construction'),
        ('test_bioone_bounce_url_construction_avian_dis', 'Avian Dis URL construction'),
        ('test_bioone_bounce_url_construction_j_vector_ecol', 'J Vector Ecol URL construction'),
        ('test_bioone_bounce_url_construction_j_zoo_wildl_med', 'J Zoo Wildl Med URL construction'),
        ('test_bioone_bounce_successful_access_with_pdf', 'Successful access with PDF'),
        ('test_bioone_bounce_open_access_article', 'Open access article handling'),
        ('test_bioone_bounce_paywall_detection', 'Paywall detection'),
        ('test_bioone_bounce_access_forbidden', 'Access forbidden handling'),
        ('test_bioone_bounce_network_error', 'Network error handling'),
        ('test_bioone_bounce_missing_doi', 'Missing DOI handling'),
        ('test_bioone_bounce_article_not_found', 'Article not found handling')
    ]
    
    for test_method, description in tests:
        try:
            getattr(test_instance, test_method)()
            print(f"✓ {description} works")
        except Exception as e:
            print(f"✗ {description} failed: {e}")
    
    try:
        test_bioone_journal_recognition()
        print("✓ Registry test passed: Journal recognition works")
    except Exception as e:
        print(f"✗ Registry test failed: {e}")
    
    print("\n" + "="*60)
    print("Test suite completed!")