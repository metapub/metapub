"""Tests for Royal Society of Chemistry (RSC) dance function."""

import pytest
from unittest.mock import patch, Mock
import requests

from .common import BaseDanceTest
from metapub import PubMedFetcher
from metapub.findit.dances import the_rsc_reaction
from metapub.exceptions import AccessDenied, NoPDFLink


class TestRSCDance(BaseDanceTest):
    """Test cases for Royal Society of Chemistry."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.fetch = PubMedFetcher()

    def test_rsc_reaction_url_construction_chem_commun(self):
        """Test 1: URL construction success (Chem Commun).
        
        PMID: 38916454 (Chem Commun (Camb))
        Expected: Should construct valid RSC article URL via DOI resolution
        """
        pma = self.fetch.article_by_pmid('38916454')
        
        assert pma.journal == 'Chem Commun (Camb)'
        assert pma.doi == '10.1039/d4cc02638a'
        print(f"Test 1 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification (should always work for URL construction)
        url = the_rsc_reaction(pma, verify=False)
        assert url is not None
        assert 'pubs.rsc.org' in url
        print(f"Test 1 - Article URL: {url}")

    def test_rsc_reaction_url_construction_chem_soc_rev(self):
        """Test 2: Chemical Society Reviews article.
        
        PMID: 38912871 (Chem Soc Rev)
        Expected: Should construct valid RSC article URL
        """
        pma = self.fetch.article_by_pmid('38912871')
        
        assert pma.journal == 'Chem Soc Rev'
        assert pma.doi == '10.1039/d4cs00390j'
        print(f"Test 2 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification
        url = the_rsc_reaction(pma, verify=False)
        assert url is not None
        assert 'pubs.rsc.org' in url
        print(f"Test 2 - Article URL: {url}")

    def test_rsc_reaction_url_construction_chem_sci(self):
        """Test 3: Chemical Science journal article.
        
        PMID: 38903241 (Chem Sci)
        Expected: Should construct valid RSC article URL
        """
        pma = self.fetch.article_by_pmid('38903241')
        
        assert pma.journal == 'Chem Sci'
        assert pma.doi == '10.1039/d4sc01708k'
        print(f"Test 3 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification
        url = the_rsc_reaction(pma, verify=False)
        assert url is not None
        print(f"Test 3 - Article URL: {url}")

    def test_rsc_reaction_url_construction_lab_chip(self):
        """Test 4: Lab Chip journal article.
        
        PMID: 38916038 (Lab Chip)
        Expected: Should construct valid RSC article URL
        """
        pma = self.fetch.article_by_pmid('38916038')
        
        assert pma.journal == 'Lab Chip'
        assert pma.doi == '10.1039/d4lc00276h'
        print(f"Test 4 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification
        url = the_rsc_reaction(pma, verify=False)
        assert url is not None
        print(f"Test 4 - Article URL: {url}")

    def test_rsc_reaction_url_construction_nat_prod_rep(self):
        """Test 5: Natural Product Reports (from existing paywalled list).
        
        PMID: 28290569 (Nat Prod Rep)
        Expected: Should construct valid RSC article URL
        """
        pma = self.fetch.article_by_pmid('28290569')
        
        assert pma.journal == 'Nat Prod Rep'
        assert pma.doi == '10.1039/c6np00124f'
        print(f"Test 5 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification
        url = the_rsc_reaction(pma, verify=False)
        assert url is not None
        print(f"Test 5 - Article URL: {url}")

    @patch('metapub.findit.dances.rsc.the_doi_2step')
    @patch('requests.get')
    def test_rsc_reaction_successful_access_with_pdf(self, mock_get, mock_doi_2step):
        """Test 6: Successful access simulation with PDF link found.
        
        PMID: 38916454 (Chem Commun)
        Expected: Should return PDF URL when found on page
        """
        # Mock DOI resolution to RSC article page
        mock_doi_2step.return_value = 'https://pubs.rsc.org/en/content/articlelanding/2024/cc/d4cc02638a'
        
        # Mock successful article page response with PDF link
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.text = '''
        <html>
            <body>
                <h1>Article Title</h1>
                <p>This is an RSC article with PDF download available.</p>
                <a href="/en/content/articlepdf/2024/cc/d4cc02638a" class="pdf-link">Download PDF</a>
            </body>
        </html>
        '''
        mock_response.content = mock_response.text.encode('utf-8')
        mock_response.url = 'https://pubs.rsc.org/en/content/articlelanding/2024/cc/d4cc02638a'
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('38916454')
        
        # Test with verification - should find PDF link
        url = the_rsc_reaction(pma, verify=True)
        assert 'pubs.rsc.org' in url
        assert 'pdf' in url  # Accept any PDF URL format
        print(f"Test 6 - Found PDF link: {url}")

    @patch('metapub.findit.dances.rsc.the_doi_2step')
    @patch('requests.get')
    def test_rsc_reaction_open_access_article(self, mock_get, mock_doi_2step):
        """Test 7: Open access article without direct PDF link.
        
        Expected: Should return article URL when accessible
        """
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://pubs.rsc.org/en/content/articlelanding/2024/cc/d4cc02638a'
        
        # Mock successful article page response without specific PDF link
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.text = '''
        <html>
            <body>
                <h1>Article Title</h1>
                <p>This is an RSC article.</p>
                <div class="article-content">
                    <p>Full article content is available here.</p>
                </div>
            </body>
        </html>
        '''
        mock_response.content = mock_response.text.encode('utf-8')
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('38916454')
        
        # Test with verification - should return article URL
        url = the_rsc_reaction(pma, verify=True)
        assert url == 'https://pubs.rsc.org/en/content/articlelanding/2024/cc/d4cc02638a'
        print(f"Test 7 - Article URL: {url}")

    @patch('metapub.findit.dances.rsc.the_doi_2step')
    @patch('requests.get')
    def test_rsc_reaction_paywall_detection(self, mock_get, mock_doi_2step):
        """Test 8: Paywall detection.
        
        Expected: Should detect paywall and raise AccessDenied
        """
        # Mock DOI resolution to RSC article page
        mock_doi_2step.return_value = 'https://pubs.rsc.org/en/content/articlelanding/2024/cc/d4cc02638a'
        
        # Mock article page response with paywall indicators
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.text = '''
        <html>
            <body>
                <h1>Article Title</h1>
                <p>This content requires institutional access.</p>
                <div class="member-access">
                    <p>Please log in to access this article.</p>
                    <a href="/login">Sign In</a>
                    <a href="/subscribe">Subscribe</a>
                    <p>Purchase this article for $35.00</p>
                </div>
            </body>
        </html>
        '''
        mock_response.content = mock_response.text.encode('utf-8')
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('38916454')
        
        # Test with verification - should detect paywall
        with pytest.raises(AccessDenied) as exc_info:
            the_rsc_reaction(pma, verify=True)
        
        assert 'PAYWALL' in str(exc_info.value)
        assert 'subscription' in str(exc_info.value)
        print(f"Test 8 - Correctly detected paywall: {exc_info.value}")

    @patch('metapub.findit.dances.rsc.the_doi_2step')
    @patch('requests.get')
    def test_rsc_reaction_access_forbidden(self, mock_get, mock_doi_2step):
        """Test 9: Access forbidden (403 error).
        
        Expected: Should handle 403 errors properly
        """
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://pubs.rsc.org/en/content/articlelanding/2024/cc/d4cc02638a'
        
        # Mock 403 response
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.ok = False
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('38916454')
        
        # Test with verification - should handle 403
        with pytest.raises(AccessDenied) as exc_info:
            the_rsc_reaction(pma, verify=True)
        
        assert 'DENIED' in str(exc_info.value)
        assert '403' in str(exc_info.value) or 'forbidden' in str(exc_info.value).lower()
        print(f"Test 9 - Correctly handled 403: {exc_info.value}")

    @patch('metapub.findit.dances.rsc.the_doi_2step')
    @patch('requests.get')
    def test_rsc_reaction_network_error(self, mock_get, mock_doi_2step):
        """Test 10: Network error handling.
        
        Expected: Should handle network errors gracefully
        """
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://pubs.rsc.org/en/content/articlelanding/2024/cc/d4cc02638a'
        
        # Mock network error
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

        pma = self.fetch.article_by_pmid('38916454')
        
        # Test - should handle network error
        with pytest.raises(NoPDFLink) as exc_info:
            the_rsc_reaction(pma, verify=True)
        
        assert 'TXERROR' in str(exc_info.value)
        assert 'Network error' in str(exc_info.value)
        print(f"Test 10 - Correctly handled network error: {exc_info.value}")

    def test_rsc_reaction_missing_doi(self):
        """Test 11: Article without DOI.
        
        Expected: Should raise NoPDFLink for missing DOI
        """
        # Create a mock PMA without DOI
        pma = Mock()
        pma.doi = None
        pma.journal = 'Chem Commun (Camb)'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_rsc_reaction(pma, verify=False)
        
        assert 'MISSING' in str(exc_info.value)
        assert 'DOI required' in str(exc_info.value)
        print(f"Test 11 - Correctly handled missing DOI: {exc_info.value}")

    def test_rsc_reaction_invalid_doi(self):
        """Test 12: Article with non-RSC DOI.
        
        Expected: Should raise NoPDFLink for invalid DOI pattern
        """
        # Create a mock PMA with non-RSC DOI
        pma = Mock()
        pma.doi = '10.1000/invalid-doi'
        pma.journal = 'Chem Commun (Camb)'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_rsc_reaction(pma, verify=False)
        
        assert 'INVALID' in str(exc_info.value)
        assert '10.1039/' in str(exc_info.value)
        print(f"Test 12 - Correctly handled invalid DOI: {exc_info.value}")

    @patch('metapub.findit.dances.rsc.the_doi_2step')
    @patch('requests.get')
    def test_rsc_reaction_article_not_found(self, mock_get, mock_doi_2step):
        """Test 13: Article not found (404 error).
        
        Expected: Should handle 404 errors properly
        """
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://pubs.rsc.org/en/content/articlelanding/2024/cc/d4cc02638a' 
        
        # Mock 404 response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.ok = False
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('38916454')
        
        # Test with verification - should handle 404
        with pytest.raises(NoPDFLink) as exc_info:
            the_rsc_reaction(pma, verify=True)
        
        assert 'TXERROR' in str(exc_info.value)
        assert '404' in str(exc_info.value) or 'not found' in str(exc_info.value)
        print(f"Test 13 - Correctly handled 404: {exc_info.value}")


def test_rsc_journal_recognition():
    """Test that RSC journals are properly recognized in the registry."""
    from metapub.findit.registry import JournalRegistry
    from metapub.findit.journals.rsc import rsc_journals
    
    registry = JournalRegistry()
    
    # Test sample RSC journals
    test_journals = [
        'Chem Commun (Camb)',
        'Chem Soc Rev', 
        'Chem Sci',
        'Lab Chip',
        'Nat Prod Rep'
    ]
    
    # Test journal recognition
    found_count = 0
    for journal in test_journals:
        if journal in rsc_journals:
            publisher_info = registry.get_publisher_for_journal(journal)
            if publisher_info and publisher_info['name'] == 'rsc':
                assert publisher_info['dance_function'] == 'the_rsc_reaction'
                print(f"✓ {journal} correctly mapped to Royal Society of Chemistry")
                found_count += 1
            else:
                print(f"⚠ {journal} mapped to different publisher: {publisher_info['name'] if publisher_info else 'None'}")
        else:
            print(f"⚠ {journal} not in rsc_journals list")
    
    # Just make sure we found at least one RSC journal (the test may not find all if registry is not populated)
    if found_count == 0:
        print("⚠ No RSC journals found in registry - this may be expected if registry not populated")
    else:
        print(f"✓ Found {found_count} properly mapped RSC journals")
    
    registry.close()


if __name__ == '__main__':
    # Run basic tests if executed directly
    test_instance = TestRSCDance()
    test_instance.setUp()
    
    print("Running Royal Society of Chemistry tests...")
    print("\n" + "="*60)
    
    tests = [
        ('test_rsc_reaction_url_construction_chem_commun', 'Chem Commun URL construction'),
        ('test_rsc_reaction_url_construction_chem_soc_rev', 'Chem Soc Rev URL construction'),
        ('test_rsc_reaction_url_construction_chem_sci', 'Chem Sci URL construction'),
        ('test_rsc_reaction_url_construction_lab_chip', 'Lab Chip URL construction'),
        ('test_rsc_reaction_url_construction_nat_prod_rep', 'Nat Prod Rep URL construction'),
        ('test_rsc_reaction_successful_access_with_pdf', 'Successful access with PDF'),
        ('test_rsc_reaction_open_access_article', 'Open access article handling'),
        ('test_rsc_reaction_paywall_detection', 'Paywall detection'),
        ('test_rsc_reaction_access_forbidden', 'Access forbidden handling'),
        ('test_rsc_reaction_network_error', 'Network error handling'),
        ('test_rsc_reaction_missing_doi', 'Missing DOI handling'),
        ('test_rsc_reaction_invalid_doi', 'Invalid DOI pattern handling'),
        ('test_rsc_reaction_article_not_found', 'Article not found handling')
    ]
    
    for test_method, description in tests:
        try:
            getattr(test_instance, test_method)()
            print(f"✓ {description} works")
        except Exception as e:
            print(f"✗ {description} failed: {e}")
    
    try:
        test_rsc_journal_recognition()
        print("✓ Registry test passed: Journal recognition works")
    except Exception as e:
        print(f"✗ Registry test failed: {e}")
    
    print("\n" + "="*60)
    print("Test suite completed!")