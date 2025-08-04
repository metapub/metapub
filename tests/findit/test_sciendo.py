"""Tests for Sciendo (De Gruyter) dance function."""

import pytest
from unittest.mock import patch, Mock
import requests

from .common import BaseDanceTest
from metapub import PubMedFetcher
from metapub.findit.dances import the_sciendo_spiral
from metapub.exceptions import AccessDenied, NoPDFLink


class TestSciendoDance(BaseDanceTest):
    """Test cases for Sciendo (De Gruyter)."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.fetch = PubMedFetcher()

    def test_sciendo_spiral_url_construction_pril(self):
        """Test 1: URL construction success (Pril).
        
        PMID: 38575384 (Pril (Makedon Akad Nauk Umet Odd Med Nauki))
        Expected: Should construct valid Sciendo PDF URL
        """
        pma = self.fetch.article_by_pmid('38575384')
        
        print(f"Test 1 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification (should always work for URL construction)
        url = the_sciendo_spiral(pma, verify=False)
        assert url is not None
        assert 'sciendo.com' in url
        assert url.startswith('https://')
        print(f"Test 1 - PDF URL: {url}")

    def test_sciendo_spiral_url_construction_j_soc_struct(self):
        """Test 2: J Soc Struct.
        
        PMID: 32855626 (J Soc Struct)
        Expected: Should construct valid Sciendo PDF URL
        """
        pma = self.fetch.article_by_pmid('32855626')
        
        print(f"Test 2 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Skip test if no DOI available
        if not pma.doi:
            print("Test 2 - Skipping: No DOI available for this PMID")
            return

        # Test without verification
        url = the_sciendo_spiral(pma, verify=False)
        assert url is not None
        assert 'sciendo.com' in url
        print(f"Test 2 - PDF URL: {url}")

    def test_sciendo_spiral_url_construction_j_nematol(self):
        """Test 3: J Nematol.
        
        PMID: 38855080 (J Nematol)
        Expected: Should construct valid Sciendo PDF URL
        """
        pma = self.fetch.article_by_pmid('38855080')
        
        print(f"Test 3 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Skip test if no DOI available
        if not pma.doi:
            print("Test 3 - Skipping: No DOI available for this PMID")
            return

        # Test without verification
        url = the_sciendo_spiral(pma, verify=False)
        assert url is not None
        assert 'sciendo.com' in url
        print(f"Test 3 - PDF URL: {url}")

    @patch('requests.get')
    def test_sciendo_spiral_successful_access(self, mock_get):
        """Test 4: Successful PDF access simulation.
        
        Expected: Should return PDF URL when accessible
        """
        # Mock successful PDF response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.headers = {'content-type': 'application/pdf'}
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('38575384')
        
        # Test with verification - should succeed
        url = the_sciendo_spiral(pma, verify=True)
        assert 'sciendo.com' in url
        print(f"Test 4 - Successful verified access: {url}")

    @patch('requests.get')
    def test_sciendo_spiral_open_access_article(self, mock_get):
        """Test 5: Open access article page detection.
        
        Expected: Should return article URL for open access content
        """
        # Mock HTML response (typical for Sciendo open access)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.text = '''<html><body>
            <h1>Sciendo</h1>
            <div class="article-content">Open access article content</div>
            <a href="/pdf" class="download-pdf">Download PDF</a>
        </body></html>'''
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('38575384')
        
        # Test with verification - should succeed (open access)
        url = the_sciendo_spiral(pma, verify=True)
        assert 'sciendo.com' in url
        print(f"Test 5 - Open access article detected: {url}")

    @patch('requests.get')
    def test_sciendo_spiral_paywall_detection(self, mock_get):
        """Test 6: Paywall detection.
        
        Expected: Should detect paywall and raise AccessDenied
        """
        # Mock paywall response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.text = '''<html><body>
            <h1>Sciendo</h1>
            <p>Login required for institutional access</p>
            <button>Subscribe to access</button>
        </body></html>'''
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('38575384')
        
        # Test with verification - should detect paywall
        with pytest.raises(AccessDenied) as exc_info:
            the_sciendo_spiral(pma, verify=True)
        
        assert 'PAYWALL' in str(exc_info.value)
        print(f"Test 6 - Correctly detected paywall: {exc_info.value}")

    @patch('requests.get')
    def test_sciendo_spiral_network_error(self, mock_get):
        """Test 7: Network error handling.
        
        Expected: Should handle network errors gracefully
        """
        # Mock network error
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

        pma = self.fetch.article_by_pmid('38575384')
        
        # Test - should handle network error
        with pytest.raises(NoPDFLink) as exc_info:
            the_sciendo_spiral(pma, verify=True)
        
        # Should contain either TXERROR (network error) or PATTERN (DOI mismatch)
        assert 'TXERROR' in str(exc_info.value) or 'PATTERN' in str(exc_info.value)
        print(f"Test 7 - Correctly handled network error or pattern mismatch: {exc_info.value}")

    def test_sciendo_spiral_missing_doi(self):
        """Test 8: Article without DOI.
        
        Expected: Should raise NoPDFLink for missing DOI
        """
        # Create a mock PMA without DOI
        pma = Mock()
        pma.doi = None
        pma.journal = 'Pril (Makedon Akad Nauk Umet Odd Med Nauki)'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_sciendo_spiral(pma, verify=False)
        
        assert 'MISSING' in str(exc_info.value)
        assert 'DOI required' in str(exc_info.value)
        print(f"Test 8 - Correctly handled missing DOI: {exc_info.value}")

    @patch('requests.get')
    def test_sciendo_spiral_404_error(self, mock_get):
        """Test 9: Article not found (404 error).
        
        Expected: Should try multiple patterns and handle 404 errors
        """
        # Mock 404 response for all attempts
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('38575384')
        
        # Test - should try multiple patterns and eventually fail
        with pytest.raises(NoPDFLink) as exc_info:
            the_sciendo_spiral(pma, verify=True)
        
        assert 'TXERROR' in str(exc_info.value) or 'PATTERN' in str(exc_info.value)
        print(f"Test 9 - Correctly handled 404: {exc_info.value}")

    @patch('requests.get')
    def test_sciendo_spiral_article_url_construction(self, mock_get):
        """Test 10: Article URL construction variations.
        
        Expected: Should use different URL patterns for Sciendo
        """
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.text = '<html>Open access article</html>'
        mock_get.return_value = mock_response

        # Create mock PMA with specific DOI pattern
        pma = Mock()
        pma.doi = '10.2478/prilozi-2024-0001'
        pma.journal = 'Pril (Makedon Akad Nauk Umet Odd Med Nauki)'
        
        # Test - should construct appropriate URL
        url = the_sciendo_spiral(pma, verify=True)
        assert 'sciendo.com' in url
        print(f"Test 10 - Article URL construction: {url}")

    def test_sciendo_spiral_multiple_doi_prefixes(self):
        """Test 11: Multiple DOI prefix handling.
        
        Expected: Should handle various DOI prefixes due to diverse publishers
        """
        # Test different DOI prefixes that Sciendo might use
        test_dois = [
            '10.2478/prilozi-2024-0001',        # Primary Sciendo DOI pattern
            '10.1515/example-2023-123',         # De Gruyter DOI pattern
            '10.3390/acquired-2023-456'         # Acquired journal DOI
        ]
        
        for doi in test_dois:
            pma = Mock()
            pma.doi = doi
            pma.journal = 'Pril (Makedon Akad Nauk Umet Odd Med Nauki)'
            
            # Should construct URL regardless of DOI prefix
            url = the_sciendo_spiral(pma, verify=False)
            assert url is not None
            assert 'sciendo.com' in url
            print(f"Test 11 - DOI {doi}: {url}")

    def test_sciendo_spiral_multiple_journals(self):
        """Test 12: Multiple Sciendo journal coverage.
        
        Expected: Should work with various Sciendo journals
        """
        # Test different journal patterns
        test_journals = [
            'Pril (Makedon Akad Nauk Umet Odd Med Nauki)',
            'J Soc Struct',
            'J Nematol',
            'Endocr Regul',
            'Rom J Intern Med'
        ]
        
        for journal in test_journals:
            pma = Mock()
            pma.doi = '10.2478/prilozi-2024-0001'
            pma.journal = journal
            
            url = the_sciendo_spiral(pma, verify=False)
            assert url is not None
            assert 'sciendo.com' in url
            print(f"Test 12 - {journal}: {url}")


def test_sciendo_journal_recognition():
    """Test that Sciendo journals are properly recognized in the registry."""
    from metapub.findit.registry import JournalRegistry
    from metapub.findit.journals.sciendo import sciendo_journals
    
    registry = JournalRegistry()
    
    # Test sample Sciendo journals (using PubMed abbreviated names)
    test_journals = [
        'Pril (Makedon Akad Nauk Umet Odd Med Nauki)',
        'J Soc Struct',
        'J Nematol',
        'Endocr Regul',
        'Rom J Intern Med'
    ]
    
    # Test journal recognition
    found_count = 0
    for journal in test_journals:
        if journal in sciendo_journals:
            publisher_info = registry.get_publisher_for_journal(journal)
            if publisher_info and publisher_info['name'] == 'sciendo':
                assert publisher_info['dance_function'] == 'the_sciendo_spiral'
                print(f"✓ {journal} correctly mapped to Sciendo")
                found_count += 1
            else:
                print(f"⚠ {journal} mapped to different publisher: {publisher_info['name'] if publisher_info else 'None'}")
        else:
            print(f"⚠ {journal} not in sciendo_journals list")
    
    # Just make sure we found at least one Sciendo journal
    assert found_count > 0, "No Sciendo journals found in registry with sciendo publisher"
    print(f"✓ Found {found_count} properly mapped Sciendo journals")
    
    registry.close()


if __name__ == '__main__':
    # Run basic tests if executed directly
    test_instance = TestSciendoDance()
    test_instance.setUp()
    
    print("Running Sciendo tests...")
    print("\n" + "="*60)
    
    tests = [
        ('test_sciendo_spiral_url_construction_pril', 'Pril URL construction'),
        ('test_sciendo_spiral_url_construction_j_soc_struct', 'J Soc Struct URL construction'),
        ('test_sciendo_spiral_url_construction_j_nematol', 'J Nematol URL construction'),
        ('test_sciendo_spiral_successful_access', 'Successful access simulation'),
        ('test_sciendo_spiral_open_access_article', 'Open access article detection'),
        ('test_sciendo_spiral_paywall_detection', 'Paywall detection'),
        ('test_sciendo_spiral_network_error', 'Network error handling'),
        ('test_sciendo_spiral_missing_doi', 'Missing DOI handling'),
        ('test_sciendo_spiral_404_error', '404 error handling'),
        ('test_sciendo_spiral_article_url_construction', 'Article URL construction'),
        ('test_sciendo_spiral_multiple_doi_prefixes', 'Multiple DOI prefix handling'),
        ('test_sciendo_spiral_multiple_journals', 'Multiple journal coverage')
    ]
    
    for test_method, description in tests:
        try:
            getattr(test_instance, test_method)()
            print(f"✓ {description} works")
        except Exception as e:
            print(f"✗ {description} failed: {e}")
    
    try:
        test_sciendo_journal_recognition()
        print("✓ Registry test passed: Journal recognition works")
    except Exception as e:
        print(f"✗ Registry test failed: {e}")
    
    print("\n" + "="*60)
    print("Test suite completed!")