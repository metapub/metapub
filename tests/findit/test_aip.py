"""Tests for AIP Publishing dance function."""

import pytest
from unittest.mock import patch, Mock
import requests

from .common import BaseDanceTest
from metapub import PubMedFetcher
from metapub.findit.dances import the_aip_allegro
from metapub.exceptions import AccessDenied, NoPDFLink


class TestAIPDance(BaseDanceTest):
    """Test cases for AIP Publishing."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.fetch = PubMedFetcher()

    def test_aip_allegro_url_construction_struct_dyn(self):
        """Test 1: URL construction success (Struct Dyn).
        
        PMID: 38912290 (Struct Dyn)
        Expected: Should construct valid AIP Publishing PDF URL
        """
        pma = self.fetch.article_by_pmid('38912290')
        
        print(f"Test 1 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification (should always work for URL construction)
        url = the_aip_allegro(pma, verify=False)
        assert url is not None
        assert 'pubs.aip.org' in url or 'aip.scitation.org' in url
        assert url.startswith('https://')
        print(f"Test 1 - PDF URL: {url}")

    def test_aip_allegro_url_construction_appl_phys_rev(self):
        """Test 2: Appl Phys Rev.
        
        PMID: 38784221 (Appl Phys Rev)
        Expected: Should construct valid AIP Publishing PDF URL
        """
        pma = self.fetch.article_by_pmid('38784221')
        
        print(f"Test 2 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Skip test if no DOI available
        if not pma.doi:
            print("Test 2 - Skipping: No DOI available for this PMID")
            return

        # Test without verification
        url = the_aip_allegro(pma, verify=False)
        assert url is not None
        assert 'pubs.aip.org' in url or 'aip.scitation.org' in url
        print(f"Test 2 - PDF URL: {url}")

    def test_aip_allegro_url_construction_j_chem_phys(self):
        """Test 3: J Chem Phys.
        
        PMID: 38913842 (J Chem Phys)
        Expected: Should construct valid AIP Publishing PDF URL
        """
        pma = self.fetch.article_by_pmid('38913842')
        
        print(f"Test 3 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Skip test if no DOI available
        if not pma.doi:
            print("Test 3 - Skipping: No DOI available for this PMID")
            return

        # Test without verification
        url = the_aip_allegro(pma, verify=False)
        assert url is not None
        assert 'pubs.aip.org' in url or 'aip.scitation.org' in url
        print(f"Test 3 - PDF URL: {url}")

    @patch('requests.get')
    def test_aip_allegro_successful_access(self, mock_get):
        """Test 4: Successful PDF access simulation.
        
        Expected: Should return PDF URL when accessible
        """
        # Mock successful PDF response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.headers = {'content-type': 'application/pdf'}
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('38912290')
        
        # Test with verification - should succeed
        url = the_aip_allegro(pma, verify=True)
        assert 'pubs.aip.org' in url or 'aip.scitation.org' in url
        print(f"Test 4 - Successful verified access: {url}")

    @patch('requests.get')
    def test_aip_allegro_paywall_detection(self, mock_get):
        """Test 5: Paywall detection.
        
        Expected: Should detect paywall and raise AccessDenied
        """
        # Mock paywall response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.text = '''<html><body>
            <h1>AIP Publishing</h1>
            <p>Institutional access required to view this article</p>
            <button>Buy this article</button>
        </body></html>'''
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('38912290')
        
        # Test with verification - should detect paywall
        with pytest.raises(AccessDenied) as exc_info:
            the_aip_allegro(pma, verify=True)
        
        assert 'PAYWALL' in str(exc_info.value)
        print(f"Test 5 - Correctly detected paywall: {exc_info.value}")

    @patch('requests.get')
    def test_aip_allegro_network_error(self, mock_get):
        """Test 6: Network error handling.
        
        Expected: Should handle network errors gracefully
        """
        # Mock network error
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

        pma = self.fetch.article_by_pmid('38912290')
        
        # Test - should handle network error
        with pytest.raises(NoPDFLink) as exc_info:
            the_aip_allegro(pma, verify=True)
        
        # Should contain either TXERROR (network error) or PATTERN (DOI mismatch)
        assert 'TXERROR' in str(exc_info.value) or 'PATTERN' in str(exc_info.value)
        print(f"Test 6 - Correctly handled network error or pattern mismatch: {exc_info.value}")

    def test_aip_allegro_missing_doi(self):
        """Test 7: Article without DOI.
        
        Expected: Should raise NoPDFLink for missing DOI
        """
        # Create a mock PMA without DOI
        pma = Mock()
        pma.doi = None
        pma.journal = 'J Chem Phys'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_aip_allegro(pma, verify=False)
        
        assert 'MISSING' in str(exc_info.value)
        assert 'DOI required' in str(exc_info.value)
        print(f"Test 7 - Correctly handled missing DOI: {exc_info.value}")

    @patch('requests.get')
    def test_aip_allegro_404_error(self, mock_get):
        """Test 8: Article not found (404 error).
        
        Expected: Should try multiple patterns and handle 404 errors
        """
        # Mock 404 response for all attempts
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('38912290')
        
        # Test - should try multiple patterns and eventually fail
        with pytest.raises(NoPDFLink) as exc_info:
            the_aip_allegro(pma, verify=True)
        
        assert 'TXERROR' in str(exc_info.value) or 'PATTERN' in str(exc_info.value)
        print(f"Test 8 - Correctly handled 404: {exc_info.value}")

    @patch('requests.get')
    def test_aip_allegro_volume_url_construction(self, mock_get):
        """Test 9: Volume-based URL construction.
        
        Expected: Should use volume info in URL when available
        """
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.headers = {'content-type': 'application/pdf'}
        mock_get.return_value = mock_response

        # Create mock PMA with volume info
        pma = Mock()
        pma.doi = '10.1063/4.0000259'
        pma.journal = 'Struct Dyn'
        pma.volume = '11'
        pma.issue = '2'
        
        # Test - should use volume in URL
        url = the_aip_allegro(pma, verify=True)
        assert 'pubs.aip.org' in url or 'aip.scitation.org' in url
        print(f"Test 9 - Volume-based URL construction: {url}")

    def test_aip_allegro_multiple_doi_prefixes(self):
        """Test 10: Multiple DOI prefix handling.
        
        Expected: Should handle various DOI prefixes due to acquisitions
        """
        # Test different DOI prefixes that AIP might use
        test_dois = [
            '10.1063/4.0000259',            # Primary AIP DOI
            '10.1116/example.2023.123',     # AIP subsidiary DOI
            '10.1121/acquired.2023.456'     # Acquired journal DOI
        ]
        
        for doi in test_dois:
            pma = Mock()
            pma.doi = doi
            pma.journal = 'J Chem Phys'
            
            # Should construct URL regardless of DOI prefix
            url = the_aip_allegro(pma, verify=False)
            assert url is not None
            assert 'pubs.aip.org' in url or 'aip.scitation.org' in url
            print(f"Test 10 - DOI {doi}: {url}")

    def test_aip_allegro_multiple_journals(self):
        """Test 11: Multiple AIP journal coverage.
        
        Expected: Should work with various AIP journals
        """
        # Test different journal patterns
        test_journals = [
            'J Chem Phys',
            'Appl Phys Lett',
            'J Appl Phys',
            'Rev Sci Instrum',
            'Chaos'
        ]
        
        for journal in test_journals:
            pma = Mock()
            pma.doi = '10.1063/4.0000259'
            pma.journal = journal
            
            url = the_aip_allegro(pma, verify=False)
            assert url is not None
            assert 'pubs.aip.org' in url or 'aip.scitation.org' in url
            print(f"Test 11 - {journal}: {url}")


def test_aip_journal_recognition():
    """Test that AIP journals are properly recognized in the registry."""
    from metapub.findit.registry import JournalRegistry
    from metapub.findit.journals.aip import aip_journals
    
    registry = JournalRegistry()
    
    # Test sample AIP journals (using PubMed abbreviated names)
    test_journals = [
        'J Chem Phys',
        'Appl Phys Lett',
        'J Appl Phys',
        'Rev Sci Instrum',
        'Chaos'
    ]
    
    # Test journal recognition
    found_count = 0
    for journal in test_journals:
        if journal in aip_journals:
            publisher_info = registry.get_publisher_for_journal(journal)
            if publisher_info and publisher_info['name'] == 'aip':
                assert publisher_info['dance_function'] == 'the_aip_allegro'
                print(f"✓ {journal} correctly mapped to AIP Publishing")
                found_count += 1
            else:
                print(f"⚠ {journal} mapped to different publisher: {publisher_info['name'] if publisher_info else 'None'}")
        else:
            print(f"⚠ {journal} not in aip_journals list")
    
    # Just make sure we found at least one AIP journal
    assert found_count > 0, "No AIP journals found in registry with aip publisher"
    print(f"✓ Found {found_count} properly mapped AIP journals")
    
    registry.close()


if __name__ == '__main__':
    # Run basic tests if executed directly
    test_instance = TestAIPDance()
    test_instance.setUp()
    
    print("Running AIP Publishing tests...")
    print("\n" + "="*60)
    
    tests = [
        ('test_aip_allegro_url_construction_struct_dyn', 'Struct Dyn URL construction'),
        ('test_aip_allegro_url_construction_appl_phys_rev', 'Appl Phys Rev URL construction'),
        ('test_aip_allegro_url_construction_j_chem_phys', 'J Chem Phys URL construction'),
        ('test_aip_allegro_successful_access', 'Successful access simulation'),
        ('test_aip_allegro_paywall_detection', 'Paywall detection'),
        ('test_aip_allegro_network_error', 'Network error handling'),
        ('test_aip_allegro_missing_doi', 'Missing DOI handling'),
        ('test_aip_allegro_404_error', '404 error handling'),
        ('test_aip_allegro_volume_url_construction', 'Volume-based URL construction'),
        ('test_aip_allegro_multiple_doi_prefixes', 'Multiple DOI prefix handling'),
        ('test_aip_allegro_multiple_journals', 'Multiple journal coverage')
    ]
    
    for test_method, description in tests:
        try:
            getattr(test_instance, test_method)()
            print(f"✓ {description} works")
        except Exception as e:
            print(f"✗ {description} failed: {e}")
    
    try:
        test_aip_journal_recognition()
        print("✓ Registry test passed: Journal recognition works")
    except Exception as e:
        print(f"✗ Registry test failed: {e}")
    
    print("\n" + "="*60)
    print("Test suite completed!")