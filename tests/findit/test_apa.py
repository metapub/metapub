"""Tests for APA (American Psychological Association) dance function."""

import pytest
from unittest.mock import patch, Mock
import requests

from .common import BaseDanceTest
from metapub import PubMedFetcher
from metapub.findit.dances import the_apa_dab
from metapub.exceptions import AccessDenied, NoPDFLink


class TestAPADance(BaseDanceTest):
    """Test cases for APA (American Psychological Association)."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.fetch = PubMedFetcher()

    def test_apa_dab_url_construction_health_psych(self):
        """Test 1: URL construction success (Health Psychology).
        
        PMID: 38884978 (Health Psychol)
        Expected: Should construct valid APA article URL via DOI resolution
        """
        pma = self.fetch.article_by_pmid('38884978')
        
        assert pma.journal == 'Health Psychol'
        assert pma.doi == '10.1037/hea0001386'
        assert pma.doi.startswith('10.1037/')
        print(f"Test 1 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification (should always work for URL construction)
        url = the_apa_dab(pma, verify=False)
        assert url is not None
        assert 'doi.apa.org' in url or 'psycnet.apa.org' in url
        print(f"Test 1 - Article URL: {url}")

    def test_apa_dab_url_construction_dev_psych(self):
        """Test 2: Developmental Psychology article.
        
        PMID: 38913760 (Dev Psychol)
        Expected: Should construct valid APA article URL
        """
        pma = self.fetch.article_by_pmid('38913760')
        
        assert pma.journal == 'Dev Psychol'
        assert pma.doi == '10.1037/dev0001772'
        assert pma.doi.startswith('10.1037/')
        print(f"Test 2 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification
        url = the_apa_dab(pma, verify=False)
        assert url is not None
        assert 'doi.apa.org' in url or 'psycnet.apa.org' in url
        print(f"Test 2 - Article URL: {url}")

    def test_apa_dab_url_construction_pers_soc_psych(self):
        """Test 3: Journal of Personality and Social Psychology article.
        
        PMID: 38900533 (J Pers Soc Psychol)
        Expected: Should construct valid APA article URL
        """
        pma = self.fetch.article_by_pmid('38900533')
        
        assert pma.journal == 'J Pers Soc Psychol'
        assert pma.doi == '10.1037/pspp0000508'
        assert pma.doi.startswith('10.1037/')
        print(f"Test 3 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification
        url = the_apa_dab(pma, verify=False)
        assert url is not None
        assert 'doi.apa.org' in url or 'psycnet.apa.org' in url
        print(f"Test 3 - Article URL: {url}")

    @patch('metapub.findit.dances.the_doi_2step')
    @patch('requests.get')
    def test_apa_dab_successful_access_with_pdf(self, mock_get, mock_doi_2step):
        """Test 4: Successful access simulation with PDF link found.
        
        PMID: 38884978 (Health Psychol)
        Expected: Should return PDF URL when found on page
        """
        # Mock DOI resolution to APA article page
        mock_doi_2step.return_value = 'https://doi.apa.org/doi/10.1037/hea0001386'
        
        # Mock successful article page response with PDF link
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.text = '''
        <html>
            <body>
                <h1>Article Title</h1>
                <p>This is an article page with PDF download available.</p>
                <a href="/fulltext/2024-12345-001.pdf" class="pdf-link">Download PDF</a>
            </body>
        </html>
        '''
        mock_response.content = mock_response.text.encode('utf-8')
        mock_response.url = 'https://doi.apa.org/doi/10.1037/hea0001386'
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('38884978')
        
        # Test with verification - should find PDF link
        url = the_apa_dab(pma, verify=True)
        assert 'doi.apa.org' in url
        assert '.pdf' in url
        print(f"Test 4 - Found PDF link: {url}")

    @patch('metapub.findit.dances.the_doi_2step')
    @patch('requests.get')
    def test_apa_dab_paywall_detection(self, mock_get, mock_doi_2step):
        """Test 5: Paywall detection.
        
        Expected: Should detect paywall and raise AccessDenied
        """
        # Mock DOI resolution to APA article page
        mock_doi_2step.return_value = 'https://doi.apa.org/doi/10.1037/hea0001386'
        
        # Mock article page response with paywall indicators
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.text = '''
        <html>
            <body>
                <h1>Article Title</h1>
                <p>This content requires a subscription to access.</p>
                <div class="paywall">
                    <p>Please sign in to access this article.</p>
                    <a href="/login">Log In</a>
                    <a href="/subscribe">Subscribe</a>
                </div>
            </body>
        </html>
        '''
        mock_response.content = mock_response.text.encode('utf-8')
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('38884978')
        
        # Test with verification - should detect paywall
        with pytest.raises(AccessDenied) as exc_info:
            the_apa_dab(pma, verify=True)
        
        assert 'PAYWALL' in str(exc_info.value)
        assert 'subscription' in str(exc_info.value)
        print(f"Test 5 - Correctly detected paywall: {exc_info.value}")

    @patch('metapub.findit.dances.the_doi_2step')
    @patch('requests.get')
    def test_apa_dab_access_forbidden(self, mock_get, mock_doi_2step):
        """Test 6: Access forbidden (403 error).
        
        Expected: Should handle 403 errors properly
        """
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://doi.apa.org/doi/10.1037/hea0001386'
        
        # Mock 403 response
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.ok = False
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('38884978')
        
        # Test with verification - should handle 403
        with pytest.raises(AccessDenied) as exc_info:
            the_apa_dab(pma, verify=True)
        
        assert 'DENIED' in str(exc_info.value)
        assert '403' in str(exc_info.value) or 'forbidden' in str(exc_info.value).lower()
        print(f"Test 6 - Correctly handled 403: {exc_info.value}")

    @patch('metapub.findit.dances.the_doi_2step')
    @patch('requests.get')
    def test_apa_dab_network_error(self, mock_get, mock_doi_2step):
        """Test 7: Network error handling.
        
        Expected: Should handle network errors gracefully
        """
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://doi.apa.org/doi/10.1037/hea0001386'
        
        # Mock network error
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

        pma = self.fetch.article_by_pmid('38884978')
        
        # Test - should handle network error
        with pytest.raises(NoPDFLink) as exc_info:
            the_apa_dab(pma, verify=True)
        
        assert 'TXERROR' in str(exc_info.value)
        assert 'Network error' in str(exc_info.value)
        print(f"Test 7 - Correctly handled network error: {exc_info.value}")

    def test_apa_dab_missing_doi(self):
        """Test 8: Article without DOI.
        
        Expected: Should raise NoPDFLink for missing DOI
        """
        # Create a mock PMA without DOI
        pma = Mock()
        pma.doi = None
        pma.journal = 'Health Psychol'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_apa_dab(pma, verify=False)
        
        assert 'MISSING' in str(exc_info.value)
        assert 'DOI required' in str(exc_info.value)
        print(f"Test 8 - Correctly handled missing DOI: {exc_info.value}")

    def test_apa_dab_invalid_doi_pattern(self):
        """Test 9: Article with non-APA DOI pattern.
        
        Expected: Should raise NoPDFLink for invalid DOI pattern
        """
        # Create a mock PMA with non-APA DOI
        pma = Mock()
        pma.doi = '10.1016/j.example.2024.01.001'  # Elsevier DOI, not APA
        pma.journal = 'Health Psychol'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_apa_dab(pma, verify=False)
        
        assert 'INVALID' in str(exc_info.value)
        assert '10.1037' in str(exc_info.value)
        print(f"Test 9 - Correctly handled invalid DOI pattern: {exc_info.value}")

    @patch('metapub.findit.dances.the_doi_2step')
    @patch('requests.get') 
    def test_apa_dab_open_access_article(self, mock_get, mock_doi_2step):
        """Test 10: Open access article without paywall.
        
        Expected: Should return article URL for open access content
        """
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://doi.apa.org/doi/10.1037/hea0001386'
        
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

        pma = self.fetch.article_by_pmid('38884978')
        
        # Test with verification - should return article URL
        url = the_apa_dab(pma, verify=True)
        assert url == 'https://doi.apa.org/doi/10.1037/hea0001386'
        print(f"Test 10 - Open access article URL: {url}")


def test_apa_journal_recognition():
    """Test that APA journals are properly recognized in the registry."""
    from metapub.findit.registry import JournalRegistry
    from metapub.findit.journals.apa import apa_journals
    
    registry = JournalRegistry()
    
    # Test sample APA journals
    test_journals = [
        'Health Psychol',
        'Dev Psychol',
        'J Pers Soc Psychol',
        'Psychol Rev'
    ]
    
    # Test journal recognition
    found_count = 0
    for journal in test_journals:
        if journal in apa_journals:
            publisher_info = registry.get_publisher_for_journal(journal)
            if publisher_info and publisher_info['name'] == 'apa':
                assert publisher_info['dance_function'] == 'the_apa_dab'
                print(f"✓ {journal} correctly mapped to APA")
                found_count += 1
            else:
                print(f"⚠ {journal} mapped to different publisher: {publisher_info['name'] if publisher_info else 'None'}")
        else:
            print(f"⚠ {journal} not in apa_journals list")
    
    # Just make sure we found at least one APA journal
    assert found_count > 0, "No APA journals found in registry with apa publisher"
    print(f"✓ Found {found_count} properly mapped APA journals")
    
    registry.close()


if __name__ == '__main__':
    # Run basic tests if executed directly
    test_instance = TestAPADance()
    test_instance.setUp()
    
    print("Running APA (American Psychological Association) tests...")
    print("\n" + "="*60)
    
    tests = [
        ('test_apa_dab_url_construction_health_psych', 'Health Psychology URL construction'),
        ('test_apa_dab_url_construction_dev_psych', 'Developmental Psychology URL construction'),
        ('test_apa_dab_url_construction_pers_soc_psych', 'Personality & Social Psychology URL construction'),
        ('test_apa_dab_successful_access_with_pdf', 'Successful access with PDF'),
        ('test_apa_dab_paywall_detection', 'Paywall detection'),
        ('test_apa_dab_access_forbidden', 'Access forbidden handling'),
        ('test_apa_dab_network_error', 'Network error handling'),
        ('test_apa_dab_missing_doi', 'Missing DOI handling'),
        ('test_apa_dab_invalid_doi_pattern', 'Invalid DOI pattern handling'),
        ('test_apa_dab_open_access_article', 'Open access article handling')
    ]
    
    for test_method, description in tests:
        try:
            getattr(test_instance, test_method)()
            print(f"✓ {description} works")
        except Exception as e:
            print(f"✗ {description} failed: {e}")
    
    try:
        test_apa_journal_recognition()
        print("✓ Registry test passed: Journal recognition works")
    except Exception as e:
        print(f"✗ Registry test failed: {e}")
    
    print("\n" + "="*60)
    print("Test suite completed!")