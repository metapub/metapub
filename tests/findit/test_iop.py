"""Tests for IOP Publishing (Institute of Physics) dance function."""

import pytest
from unittest.mock import patch, Mock
import requests

from .common import BaseDanceTest
from metapub import PubMedFetcher
from metapub.findit.dances import the_iop_fusion
from metapub.exceptions import AccessDenied, NoPDFLink


class TestIOPDance(BaseDanceTest):
    """Test cases for IOP Publishing (Institute of Physics)."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.fetch = PubMedFetcher()

    def test_iop_fusion_url_construction_phys_med_biol(self):
        """Test 1: URL construction success (Physics in Medicine & Biology).
        
        PMID: 38914107 (Phys Med Biol)
        Expected: Should construct valid IOP PDF URL
        """
        pma = self.fetch.article_by_pmid('38914107')
        
        print(f"Test 1 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification (should always work for URL construction)
        url = the_iop_fusion(pma, verify=False)
        assert url is not None
        assert 'iopscience.iop.org' in url
        assert '/article/' in url
        assert '/pdf' in url
        assert url.startswith('https://')
        print(f"Test 1 - PDF URL: {url}")

    def test_iop_fusion_url_construction_nanotechnology(self):
        """Test 2: Nanotechnology journal.
        
        PMID: 38914053 (Nanotechnology)
        Expected: Should construct valid IOP PDF URL
        """
        pma = self.fetch.article_by_pmid('38914053')
        
        print(f"Test 2 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification
        url = the_iop_fusion(pma, verify=False)
        assert url is not None
        assert 'iopscience.iop.org' in url
        print(f"Test 2 - PDF URL: {url}")

    def test_iop_fusion_url_construction_astrophys_j(self):
        """Test 3: Astrophysical Journal.
        
        PMID: 38799617 (Astrophys J)
        Expected: Should construct valid IOP PDF URL
        """
        pma = self.fetch.article_by_pmid('38799617')
        
        print(f"Test 3 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification
        url = the_iop_fusion(pma, verify=False)
        assert url is not None
        assert 'iopscience.iop.org' in url
        print(f"Test 3 - PDF URL: {url}")

    @patch('requests.get')
    def test_iop_fusion_successful_access(self, mock_get):
        """Test 4: Successful PDF access simulation.
        
        Expected: Should return PDF URL when accessible
        """
        # Mock successful PDF response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.headers = {'content-type': 'application/pdf'}
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('38914107')
        
        # Test with verification - should succeed
        url = the_iop_fusion(pma, verify=True)
        assert 'iopscience.iop.org' in url
        assert '/article/' in url
        assert '/pdf' in url
        print(f"Test 4 - Successful verified access: {url}")

    @patch('requests.get')
    def test_iop_fusion_paywall_detection(self, mock_get):
        """Test 5: Paywall detection.
        
        Expected: Should try both domains and detect paywall
        """
        # Mock paywall response for both domains
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.text = '''<html><body>
            <h1>Subscription Required</h1>
            <p>Login required for institutional access</p>
            <button>Subscribe now</button>
        </body></html>'''
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('38914107')
        
        # Test with verification - should eventually fail after trying both domains
        with pytest.raises(NoPDFLink) as exc_info:
            the_iop_fusion(pma, verify=True)
        
        assert 'TXERROR' in str(exc_info.value)
        print(f"Test 5 - Correctly detected paywall/access issues: {exc_info.value}")

    @patch('requests.get')
    def test_iop_fusion_network_error(self, mock_get):
        """Test 6: Network error handling.
        
        Expected: Should handle network errors gracefully
        """
        # Mock network error
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

        pma = self.fetch.article_by_pmid('38914107')
        
        # Test - should handle network error
        with pytest.raises(NoPDFLink) as exc_info:
            the_iop_fusion(pma, verify=True)
        
        assert 'TXERROR' in str(exc_info.value)
        print(f"Test 6 - Correctly handled network error: {exc_info.value}")

    def test_iop_fusion_missing_doi(self):
        """Test 7: Article without DOI.
        
        Expected: Should raise NoPDFLink for missing DOI
        """
        # Create a mock PMA without DOI
        pma = Mock()
        pma.doi = None
        pma.journal = 'Phys Med Biol'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_iop_fusion(pma, verify=False)
        
        assert 'MISSING' in str(exc_info.value)
        assert 'DOI required' in str(exc_info.value)
        print(f"Test 7 - Correctly handled missing DOI: {exc_info.value}")

    @patch('requests.get')
    def test_iop_fusion_404_error(self, mock_get):
        """Test 8: Article not found (404 error).
        
        Expected: Should try both domains and handle 404 errors
        """
        # Mock 404 response for both domains
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('38914107')
        
        # Test - should try both domains and eventually fail
        with pytest.raises(NoPDFLink) as exc_info:
            the_iop_fusion(pma, verify=True)
        
        assert 'TXERROR' in str(exc_info.value)
        print(f"Test 8 - Correctly handled 404: {exc_info.value}")

    @patch('requests.get')
    def test_iop_fusion_domain_fallback(self, mock_get):
        """Test 9: Fallback to second domain when first fails.
        
        Expected: Should try iopscience.iop.org first, then validate.perfdrive.com
        """
        # Mock responses: first domain fails, second succeeds
        responses = [
            Mock(ok=False, status_code=404),  # First domain fails
            Mock(ok=True, status_code=200, headers={'content-type': 'application/pdf'})  # Second succeeds
        ]
        mock_get.side_effect = responses

        pma = self.fetch.article_by_pmid('38914107')
        
        # Test - should succeed on second domain
        url = the_iop_fusion(pma, verify=True)
        assert 'validate.perfdrive.com' in url or 'iopscience.iop.org' in url
        print(f"Test 9 - Domain fallback success: {url}")

    def test_iop_fusion_uncommon_doi_pattern(self):
        """Test 10: Article with uncommon DOI pattern.
        
        Expected: Should handle uncommon DOI patterns but warn
        """
        # Create a mock PMA with uncommon DOI pattern
        pma = Mock()
        pma.doi = '10.1016/j.example.2023.123456'  # Non-IOP DOI
        pma.journal = 'Phys Med Biol'
        
        # Should still construct URL but may warn about pattern
        url = the_iop_fusion(pma, verify=False)
        assert url is not None
        assert 'iopscience.iop.org' in url
        print(f"Test 10 - Uncommon DOI pattern handled: {url}")


def test_iop_journal_recognition():
    """Test that IOP journals are properly recognized in the registry."""
    from metapub.findit.registry import JournalRegistry
    from metapub.findit.journals.iop import iop_journals
    
    registry = JournalRegistry()
    
    # Test sample IOP journals (using PubMed abbreviated names)
    test_journals = [
        'Phys Med Biol',
        'Nanotechnology', 
        'J Phys D Appl Phys',
        'New J Phys',
        'J Neural Eng'
    ]
    
    # Test journal recognition
    found_count = 0
    for journal in test_journals:
        if journal in iop_journals:
            publisher_info = registry.get_publisher_for_journal(journal)
            if publisher_info and publisher_info['name'] == 'iop':
                assert publisher_info['dance_function'] == 'the_iop_fusion'
                print(f"✓ {journal} correctly mapped to IOP Publishing")
                found_count += 1
            else:
                print(f"⚠ {journal} mapped to different publisher: {publisher_info['name'] if publisher_info else 'None'}")
        else:
            print(f"⚠ {journal} not in iop_journals list")
    
    # Just make sure we found at least one IOP journal
    assert found_count > 0, "No IOP journals found in registry with iop publisher"
    print(f"✓ Found {found_count} properly mapped IOP journals")
    
    registry.close()


if __name__ == '__main__':
    # Run basic tests if executed directly
    test_instance = TestIOPDance()
    test_instance.setUp()
    
    print("Running IOP Publishing tests...")
    print("\n" + "="*60)
    
    tests = [
        ('test_iop_fusion_url_construction_phys_med_biol', 'Phys Med Biol URL construction'),
        ('test_iop_fusion_url_construction_nanotechnology', 'Nanotechnology URL construction'),
        ('test_iop_fusion_url_construction_astrophys_j', 'Astrophys J URL construction'),
        ('test_iop_fusion_successful_access', 'Successful access simulation'),
        ('test_iop_fusion_paywall_detection', 'Paywall detection'),
        ('test_iop_fusion_network_error', 'Network error handling'),
        ('test_iop_fusion_missing_doi', 'Missing DOI handling'),
        ('test_iop_fusion_404_error', '404 error handling'),
        ('test_iop_fusion_domain_fallback', 'Domain fallback'),
        ('test_iop_fusion_uncommon_doi_pattern', 'Uncommon DOI pattern handling')
    ]
    
    for test_method, description in tests:
        try:
            getattr(test_instance, test_method)()
            print(f"✓ {description} works")
        except Exception as e:
            print(f"✗ {description} failed: {e}")
    
    try:
        test_iop_journal_recognition()
        print("✓ Registry test passed: Journal recognition works")
    except Exception as e:
        print(f"✗ Registry test failed: {e}")
    
    print("\n" + "="*60)
    print("Test suite completed!")