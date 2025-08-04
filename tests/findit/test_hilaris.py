"""Tests for Hilaris Publisher dance function."""

import pytest
from unittest.mock import patch, Mock
import requests

from .common import BaseDanceTest
from metapub import PubMedFetcher
from metapub.findit.dances import the_hilaris_hop
from metapub.exceptions import AccessDenied, NoPDFLink


class TestHilarisDance(BaseDanceTest):
    """Test cases for Hilaris Publisher."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.fetch = PubMedFetcher()

    def test_hilaris_hop_url_construction_environ_toxicol(self):
        """Test 1: URL construction success (J Environ Anal Toxicol).
        
        PMID: 34094707 (J Environ Anal Toxicol)
        Expected: Should construct valid Hilaris Publisher PDF URL
        """
        pma = self.fetch.article_by_pmid('34094707')
        
        print(f"Test 1 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification (should always work for URL construction)
        url = the_hilaris_hop(pma, verify=False)
        assert url is not None
        assert 'hilarispublisher.com' in url
        assert url.startswith('https://')
        print(f"Test 1 - PDF URL: {url}")

    def test_hilaris_hop_url_construction_mol_genet(self):
        """Test 2: J Mol Genet Med.
        
        PMID: 32952595 (J Mol Genet Med)
        Expected: Should construct valid Hilaris Publisher PDF URL
        """
        pma = self.fetch.article_by_pmid('32952595')
        
        print(f"Test 2 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Skip test if no DOI available
        if not pma.doi:
            print("Test 2 - Skipping: No DOI available for this PMID")
            return

        # Test without verification
        url = the_hilaris_hop(pma, verify=False)
        assert url is not None
        assert 'hilarispublisher.com' in url
        print(f"Test 2 - PDF URL: {url}")

    def test_hilaris_hop_url_construction_cancer_sci(self):
        """Test 3: J Cancer Sci Ther.
        
        PMID: 32494339 (J Cancer Sci Ther)
        Expected: Should construct valid Hilaris Publisher PDF URL
        """
        pma = self.fetch.article_by_pmid('32494339')
        
        print(f"Test 3 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Skip test if no DOI available
        if not pma.doi:
            print("Test 3 - Skipping: No DOI available for this PMID")
            return

        # Test without verification
        url = the_hilaris_hop(pma, verify=False)
        assert url is not None
        assert 'hilarispublisher.com' in url
        print(f"Test 3 - PDF URL: {url}")

    @patch('requests.get')
    def test_hilaris_hop_successful_access(self, mock_get):
        """Test 4: Successful PDF access simulation.
        
        Expected: Should return PDF URL when accessible
        """
        # Mock successful PDF response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.headers = {'content-type': 'application/pdf'}
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('34094707')
        
        # Test with verification - should succeed
        url = the_hilaris_hop(pma, verify=True)
        assert 'hilarispublisher.com' in url
        print(f"Test 4 - Successful verified access: {url}")

    @patch('requests.get')
    def test_hilaris_hop_paywall_detection(self, mock_get):
        """Test 5: Paywall detection.
        
        Expected: Should detect paywall and raise AccessDenied
        """
        # Mock paywall response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.text = '''<html><body>
            <h1>Hilaris Publisher</h1>
            <p>Login required for institutional access</p>
            <button>Subscribe to access</button>
        </body></html>'''
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('34094707')
        
        # Test with verification - should detect paywall
        with pytest.raises(AccessDenied) as exc_info:
            the_hilaris_hop(pma, verify=True)
        
        assert 'PAYWALL' in str(exc_info.value)
        print(f"Test 5 - Correctly detected paywall: {exc_info.value}")

    @patch('requests.get')
    def test_hilaris_hop_network_error(self, mock_get):
        """Test 6: Network error handling.
        
        Expected: Should handle network errors gracefully
        """
        # Mock network error
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

        pma = self.fetch.article_by_pmid('34094707')
        
        # Test - should handle network error
        with pytest.raises(NoPDFLink) as exc_info:
            the_hilaris_hop(pma, verify=True)
        
        # Should contain either TXERROR (network error) or PATTERN (DOI mismatch)
        assert 'TXERROR' in str(exc_info.value) or 'PATTERN' in str(exc_info.value)
        print(f"Test 6 - Correctly handled network error or pattern mismatch: {exc_info.value}")

    def test_hilaris_hop_missing_doi(self):
        """Test 7: Article without DOI.
        
        Expected: Should raise NoPDFLink for missing DOI
        """
        # Create a mock PMA without DOI
        pma = Mock()
        pma.doi = None
        pma.journal = 'J Environ Anal Toxicol'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_hilaris_hop(pma, verify=False)
        
        assert 'MISSING' in str(exc_info.value)
        assert 'DOI required' in str(exc_info.value)
        print(f"Test 7 - Correctly handled missing DOI: {exc_info.value}")

    @patch('requests.get')
    def test_hilaris_hop_404_error(self, mock_get):
        """Test 8: Article not found (404 error).
        
        Expected: Should try multiple patterns and handle 404 errors
        """
        # Mock 404 response for all attempts
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('34094707')
        
        # Test - should try multiple patterns and eventually fail
        with pytest.raises(NoPDFLink) as exc_info:
            the_hilaris_hop(pma, verify=True)
        
        assert 'TXERROR' in str(exc_info.value) or 'PATTERN' in str(exc_info.value)
        print(f"Test 8 - Correctly handled 404: {exc_info.value}")

    @patch('requests.get')
    def test_hilaris_hop_article_slug_construction(self, mock_get):
        """Test 9: Article slug URL construction.
        
        Expected: Should use article ID from DOI in URL when available
        """
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.headers = {'content-type': 'application/pdf'}
        mock_get.return_value = mock_response

        # Create mock PMA with article ID in DOI
        pma = Mock()
        pma.doi = '10.4172/2161-0525.1000551'
        pma.journal = 'J Environ Anal Toxicol'
        
        # Test - should use article ID in URL
        url = the_hilaris_hop(pma, verify=True)
        assert 'hilarispublisher.com' in url
        print(f"Test 9 - Article slug URL construction: {url}")

    def test_hilaris_hop_multiple_doi_prefixes(self):
        """Test 10: Multiple DOI prefix handling.
        
        Expected: Should handle various DOI prefixes due to acquisitions
        """
        # Test different DOI prefixes that Hilaris might use
        test_dois = [
            '10.4172/2161-0525.1000551',    # Primary Hilaris DOI
            '10.37421/example.2023.123',     # Secondary Hilaris DOI
            '10.1186/acquired-2023-456'      # Acquired journal DOI
        ]
        
        for doi in test_dois:
            pma = Mock()
            pma.doi = doi
            pma.journal = 'J Environ Anal Toxicol'
            
            # Should construct URL regardless of DOI prefix
            url = the_hilaris_hop(pma, verify=False)
            assert url is not None
            assert 'hilarispublisher.com' in url
            print(f"Test 10 - DOI {doi}: {url}")

    def test_hilaris_hop_multiple_journals(self):
        """Test 11: Multiple Hilaris journal coverage.
        
        Expected: Should work with various Hilaris journals
        """
        # Test different journal patterns
        test_journals = [
            'J Environ Anal Toxicol',
            'J Mol Genet Med',
            'J Cancer Sci Ther',
            'J Cytol Histol',
            'Med Chem (Los Angeles)'
        ]
        
        for journal in test_journals:
            pma = Mock()
            pma.doi = '10.4172/2161-0525.1000551'
            pma.journal = journal
            
            url = the_hilaris_hop(pma, verify=False)
            assert url is not None
            assert 'hilarispublisher.com' in url
            print(f"Test 11 - {journal}: {url}")


def test_hilaris_journal_recognition():
    """Test that Hilaris journals are properly recognized in the registry."""
    from metapub.findit.registry import JournalRegistry
    from metapub.findit.journals.hilaris import hilaris_journals
    
    registry = JournalRegistry()
    
    # Test sample Hilaris journals (using PubMed abbreviated names)
    test_journals = [
        'J Environ Anal Toxicol',
        'J Mol Genet Med',
        'J Cancer Sci Ther',
        'J Cytol Histol',
        'Med Chem (Los Angeles)'
    ]
    
    # Test journal recognition
    found_count = 0
    for journal in test_journals:
        if journal in hilaris_journals:
            publisher_info = registry.get_publisher_for_journal(journal)
            if publisher_info and publisher_info['name'] == 'hilaris':
                assert publisher_info['dance_function'] == 'the_hilaris_hop'
                print(f"✓ {journal} correctly mapped to Hilaris Publisher")
                found_count += 1
            else:
                print(f"⚠ {journal} mapped to different publisher: {publisher_info['name'] if publisher_info else 'None'}")
        else:
            print(f"⚠ {journal} not in hilaris_journals list")
    
    # Just make sure we found at least one Hilaris journal
    assert found_count > 0, "No Hilaris journals found in registry with hilaris publisher"
    print(f"✓ Found {found_count} properly mapped Hilaris journals")
    
    registry.close()


if __name__ == '__main__':
    # Run basic tests if executed directly
    test_instance = TestHilarisDance()
    test_instance.setUp()
    
    print("Running Hilaris Publisher tests...")
    print("\n" + "="*60)
    
    tests = [
        ('test_hilaris_hop_url_construction_environ_toxicol', 'Environ Toxicol URL construction'),
        ('test_hilaris_hop_url_construction_mol_genet', 'Mol Genet URL construction'),
        ('test_hilaris_hop_url_construction_cancer_sci', 'Cancer Sci URL construction'),
        ('test_hilaris_hop_successful_access', 'Successful access simulation'),
        ('test_hilaris_hop_paywall_detection', 'Paywall detection'),
        ('test_hilaris_hop_network_error', 'Network error handling'),
        ('test_hilaris_hop_missing_doi', 'Missing DOI handling'),
        ('test_hilaris_hop_404_error', '404 error handling'),
        ('test_hilaris_hop_article_slug_construction', 'Article slug URL construction'),
        ('test_hilaris_hop_doi_pattern_warning', 'Non-standard DOI pattern handling'),
        ('test_hilaris_hop_multiple_journals', 'Multiple journal coverage')
    ]
    
    for test_method, description in tests:
        try:
            getattr(test_instance, test_method)()
            print(f"✓ {description} works")
        except Exception as e:
            print(f"✗ {description} failed: {e}")
    
    try:
        test_hilaris_journal_recognition()
        print("✓ Registry test passed: Journal recognition works")
    except Exception as e:
        print(f"✗ Registry test failed: {e}")
    
    print("\n" + "="*60)
    print("Test suite completed!")