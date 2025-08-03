"""Tests for SCIRP dance function."""

import pytest
from unittest.mock import patch, Mock
import requests

from .common import BaseDanceTest
from metapub import PubMedFetcher
from metapub.findit.dances import the_scirp_timewarp
from metapub.exceptions import AccessDenied, NoPDFLink


class TestSCIRPDance(BaseDanceTest):
    """Test cases for SCIRP publisher."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.fetch = PubMedFetcher()

    def test_scirp_timewarp_url_construction_surg_sci(self):
        """Test 1: URL construction success (Surg Sci).
        
        PMID: 27213116 (Surg Sci)
        Expected: Should construct valid SCIRP article URL via DOI resolution
        """
        pma = self.fetch.article_by_pmid('27213116')
        
        assert pma.journal == 'Surg Sci'
        print(f"Test 1 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification (should always work for URL construction)
        url = the_scirp_timewarp(pma, verify=False)
        assert url is not None
        assert 'scirp' in url.lower()
        print(f"Test 1 - Article URL: {url}")

    def test_scirp_timewarp_url_construction_sens_technol(self):
        """Test 2: Journal of Sensor Technology article.
        
        PMID: 25019034 (J Sens Technol)
        Expected: Should construct valid SCIRP article URL
        """
        pma = self.fetch.article_by_pmid('25019034')
        
        assert pma.journal == 'J Sens Technol'
        print(f"Test 2 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification
        url = the_scirp_timewarp(pma, verify=False)
        assert url is not None
        assert 'scirp' in url.lower()
        print(f"Test 2 - Article URL: {url}")

    def test_scirp_timewarp_url_construction_world_neurosci(self):
        """Test 3: World Journal of Neuroscience article.
        
        PMID: 23837132 (World J Neurosci)
        Expected: Should construct valid SCIRP article URL
        """
        pma = self.fetch.article_by_pmid('23837132')
        
        assert pma.journal == 'World J Neurosci'
        print(f"Test 3 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification
        url = the_scirp_timewarp(pma, verify=False)
        assert url is not None
        print(f"Test 3 - Article URL: {url}")

    @patch('metapub.findit.dances.the_doi_2step')
    @patch('requests.get')
    def test_scirp_timewarp_successful_access_with_pdf(self, mock_get, mock_doi_2step):
        """Test 4: Successful access simulation with PDF link found.
        
        PMID: 27213116 (Surg Sci)
        Expected: Should return PDF URL when found on page
        """
        # Mock DOI resolution to SCIRP article page
        mock_doi_2step.return_value = 'https://www.scirp.org/journal/articleinformation.aspx?articleid=68734'
        
        # Mock successful article page response with PDF link
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.text = '''
        <html>
            <body>
                <h1>Article Title</h1>
                <p>This is an open access article with PDF download available.</p>
                <a href="/journal/paperpdf/68734.pdf" class="pdf-link">Download PDF</a>
            </body>
        </html>
        '''
        mock_response.content = mock_response.text.encode('utf-8')
        mock_response.url = 'https://www.scirp.org/journal/articleinformation.aspx?articleid=68734'
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('27213116')
        
        # Test with verification - should find PDF link
        url = the_scirp_timewarp(pma, verify=True)
        assert 'scirp.org' in url
        assert '.pdf' in url
        print(f"Test 4 - Found PDF link: {url}")

    @patch('metapub.findit.dances.the_doi_2step')
    @patch('requests.get')
    def test_scirp_timewarp_open_access_article(self, mock_get, mock_doi_2step):
        """Test 5: Open access article without direct PDF link.
        
        Expected: Should return article URL for open access content
        """
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://www.scirp.org/journal/articleinformation.aspx?articleid=68734'
        
        # Mock successful article page response without specific PDF link
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

        pma = self.fetch.article_by_pmid('27213116')
        
        # Test with verification - should return article URL
        url = the_scirp_timewarp(pma, verify=True)
        assert url == 'https://www.scirp.org/journal/articleinformation.aspx?articleid=68734'
        print(f"Test 5 - Open access article URL: {url}")

    @patch('metapub.findit.dances.the_doi_2step')
    @patch('requests.get')
    def test_scirp_timewarp_paywall_detection(self, mock_get, mock_doi_2step):
        """Test 6: Paywall detection (uncommon but possible).
        
        Expected: Should detect paywall and raise AccessDenied
        """
        # Mock DOI resolution to SCIRP article page
        mock_doi_2step.return_value = 'https://www.scirp.org/journal/articleinformation.aspx?articleid=68734'
        
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
                    <p>Purchase this article for $29.95</p>
                </div>
            </body>
        </html>
        '''
        mock_response.content = mock_response.text.encode('utf-8')
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('27213116')
        
        # Test with verification - should detect paywall
        with pytest.raises(AccessDenied) as exc_info:
            the_scirp_timewarp(pma, verify=True)
        
        assert 'PAYWALL' in str(exc_info.value)
        assert 'subscription' in str(exc_info.value)
        print(f"Test 6 - Correctly detected paywall: {exc_info.value}")

    @patch('metapub.findit.dances.the_doi_2step')
    @patch('requests.get')
    def test_scirp_timewarp_access_forbidden(self, mock_get, mock_doi_2step):
        """Test 7: Access forbidden (403 error).
        
        Expected: Should handle 403 errors properly
        """
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://www.scirp.org/journal/articleinformation.aspx?articleid=68734'
        
        # Mock 403 response
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.ok = False
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('27213116')
        
        # Test with verification - should handle 403
        with pytest.raises(AccessDenied) as exc_info:
            the_scirp_timewarp(pma, verify=True)
        
        assert 'DENIED' in str(exc_info.value)
        assert '403' in str(exc_info.value) or 'forbidden' in str(exc_info.value).lower()
        print(f"Test 7 - Correctly handled 403: {exc_info.value}")

    @patch('metapub.findit.dances.the_doi_2step')
    @patch('requests.get')
    def test_scirp_timewarp_network_error(self, mock_get, mock_doi_2step):
        """Test 8: Network error handling.
        
        Expected: Should handle network errors gracefully
        """
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://www.scirp.org/journal/articleinformation.aspx?articleid=68734'
        
        # Mock network error
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

        pma = self.fetch.article_by_pmid('27213116')
        
        # Test - should handle network error
        with pytest.raises(NoPDFLink) as exc_info:
            the_scirp_timewarp(pma, verify=True)
        
        assert 'TXERROR' in str(exc_info.value)
        assert 'Network error' in str(exc_info.value)
        print(f"Test 8 - Correctly handled network error: {exc_info.value}")

    def test_scirp_timewarp_missing_doi(self):
        """Test 9: Article without DOI.
        
        Expected: Should raise NoPDFLink for missing DOI
        """
        # Create a mock PMA without DOI
        pma = Mock()
        pma.doi = None
        pma.journal = 'Surg Sci'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_scirp_timewarp(pma, verify=False)
        
        assert 'MISSING' in str(exc_info.value)
        assert 'DOI required' in str(exc_info.value)
        print(f"Test 9 - Correctly handled missing DOI: {exc_info.value}")

    @patch('metapub.findit.dances.the_doi_2step')
    @patch('requests.get')
    def test_scirp_timewarp_article_not_found(self, mock_get, mock_doi_2step):
        """Test 10: Article not found (404 error).
        
        Expected: Should handle 404 errors properly
        """
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://www.scirp.org/journal/articleinformation.aspx?articleid=68734' 
        
        # Mock 404 response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.ok = False
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('27213116')
        
        # Test with verification - should handle 404
        with pytest.raises(NoPDFLink) as exc_info:
            the_scirp_timewarp(pma, verify=True)
        
        assert 'TXERROR' in str(exc_info.value)
        assert '404' in str(exc_info.value) or 'not found' in str(exc_info.value)
        print(f"Test 10 - Correctly handled 404: {exc_info.value}")

    @patch('metapub.findit.dances.the_doi_2step')
    @patch('requests.get') 
    def test_scirp_timewarp_pdf_with_view_pdf_text(self, mock_get, mock_doi_2step):
        """Test 11: PDF detection with 'view pdf' text.
        
        Expected: Should find PDF link when 'view pdf' appears in content
        """
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://www.scirp.org/journal/articleinformation.aspx?articleid=68734'
        
        # Mock successful article page response with 'view pdf' text
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.text = '''
        <html>
            <body>
                <h1>Article Title</h1>
                <p>Click to view pdf of this article.</p>
                <a href="/paper/68734.pdf" title="PDF Download">View PDF</a>
            </body>
        </html>
        '''
        mock_response.content = mock_response.text.encode('utf-8')
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('27213116')
        
        # Test with verification - should find PDF link
        url = the_scirp_timewarp(pma, verify=True)
        assert 'scirp.org' in url
        assert '.pdf' in url
        print(f"Test 11 - Found PDF with 'view pdf' text: {url}")


def test_scirp_journal_recognition():
    """Test that SCIRP journals are properly recognized in the registry."""
    from metapub.findit.registry import JournalRegistry
    from metapub.findit.journals.scirp import scirp_journals
    
    registry = JournalRegistry()
    
    # Test sample SCIRP journals
    test_journals = [
        'Surg Sci',
        'J Sens Technol', 
        'World J Neurosci',
        'Psychology'
    ]
    
    # Test journal recognition
    found_count = 0
    for journal in test_journals:
        if journal in scirp_journals:
            publisher_info = registry.get_publisher_for_journal(journal)
            if publisher_info and publisher_info['name'] == 'scirp':
                assert publisher_info['dance_function'] == 'the_scirp_timewarp'
                print(f"✓ {journal} correctly mapped to SCIRP")
                found_count += 1
            else:
                print(f"⚠ {journal} mapped to different publisher: {publisher_info['name'] if publisher_info else 'None'}")
        else:
            print(f"⚠ {journal} not in scirp_journals list")
    
    # Just make sure we found at least one SCIRP journal
    assert found_count > 0, "No SCIRP journals found in registry with scirp publisher"
    print(f"✓ Found {found_count} properly mapped SCIRP journals")
    
    registry.close()


if __name__ == '__main__':
    # Run basic tests if executed directly
    test_instance = TestSCIRPDance()
    test_instance.setUp()
    
    print("Running SCIRP tests...")
    print("\n" + "="*60)
    
    tests = [
        ('test_scirp_timewarp_url_construction_surg_sci', 'Surg Sci URL construction'),
        ('test_scirp_timewarp_url_construction_sens_technol', 'J Sens Technol URL construction'),
        ('test_scirp_timewarp_url_construction_world_neurosci', 'World J Neurosci URL construction'),
        ('test_scirp_timewarp_successful_access_with_pdf', 'Successful access with PDF'),
        ('test_scirp_timewarp_open_access_article', 'Open access article handling'),
        ('test_scirp_timewarp_paywall_detection', 'Paywall detection'),
        ('test_scirp_timewarp_access_forbidden', 'Access forbidden handling'),
        ('test_scirp_timewarp_network_error', 'Network error handling'),
        ('test_scirp_timewarp_missing_doi', 'Missing DOI handling'),
        ('test_scirp_timewarp_article_not_found', 'Article not found handling'),
        ('test_scirp_timewarp_pdf_with_view_pdf_text', 'PDF with view pdf text')
    ]
    
    for test_method, description in tests:
        try:
            getattr(test_instance, test_method)()
            print(f"✓ {description} works")
        except Exception as e:
            print(f"✗ {description} failed: {e}")
    
    try:
        test_scirp_journal_recognition()
        print("✓ Registry test passed: Journal recognition works")
    except Exception as e:
        print(f"✗ Registry test failed: {e}")
    
    print("\n" + "="*60)
    print("Test suite completed!")