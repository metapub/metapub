"""Tests for ACM Digital Library dance function."""

import pytest
from unittest.mock import patch, Mock
import requests

from .common import BaseDanceTest
from metapub import PubMedFetcher
from metapub.findit.dances import the_acm_reel
from metapub.findit.registry import JournalRegistry
from metapub.exceptions import AccessDenied, NoPDFLink


class TestACMDance(BaseDanceTest):
    """Test cases for ACM Digital Library."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.fetch = PubMedFetcher()

    def test_acm_reel_url_construction_wireless_health(self):
        """Test 1: URL construction success (Wireless Health).
        
        PMID: 26949753 (Proc Wirel Health)
        Expected: Should construct valid ACM PDF URL
        """
        pma = self.fetch.article_by_pmid('26949753')
        
        print(f"Test 1 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification (should always work for URL construction)
        url = the_acm_reel(pma, verify=False)
        assert url is not None
        assert 'dl.acm.org' in url
        assert '/doi/pdf/' in url
        assert url.startswith('https://')
        print(f"Test 1 - PDF URL: {url}")

    def test_acm_reel_url_construction_mobile_computing(self):
        """Test 2: Mobile Computing article.
        
        PMID: 34262408 (Proc Annu Int Conf Mob Comput Netw)
        Expected: Should construct valid ACM PDF URL
        """
        pma = self.fetch.article_by_pmid('34262408')
        
        print(f"Test 2 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification
        url = the_acm_reel(pma, verify=False)
        assert url is not None
        assert 'dl.acm.org' in url
        assert '/doi/pdf/' in url
        print(f"Test 2 - PDF URL: {url}")

    def test_acm_reel_url_construction_interactive_systems(self):
        """Test 3: Interactive Systems article.
        
        PMID: 29515937 (ACM Trans Interact Intell Syst)
        Expected: Should construct valid ACM PDF URL
        """
        pma = self.fetch.article_by_pmid('29515937')
        
        print(f"Test 3 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification
        url = the_acm_reel(pma, verify=False)
        assert url is not None
        assert 'dl.acm.org' in url
        assert '/doi/pdf/' in url
        print(f"Test 3 - PDF URL: {url}")

    # Test removed: PDF access verification is now handled by verify_pdf_url

    # Test removed: Paywall detection is now handled by verify_pdf_url

    # Test removed: Network error handling is now handled by verify_pdf_url


    # Test removed: DOI pattern gating was explicitly removed per user requirements

    # Test removed: HTTP error handling is now handled by verify_pdf_url


def test_acm_journal_recognition():
    """Test that ACM journals are properly recognized in the registry."""
    registry = JournalRegistry()
    
    # Test sample ACM journals (using PubMed abbreviated names)
    test_journals = [
        'Proc Wirel Health',
        'ACM Trans Interact Intell Syst',
        'ACM BCB',
        'KDD'
    ]
    
    # Test journal recognition
    found_count = 0
    for journal in test_journals:
        publisher_info = registry.get_publisher_for_journal(journal)
        if publisher_info and publisher_info['name'] == 'acm':
            assert publisher_info['dance_function'] == 'the_doi_slide'
            print(f"✓ {journal} correctly mapped to ACM")
            found_count += 1
        else:
            print(f"⚠ {journal} mapped to different publisher: {publisher_info['name'] if publisher_info else 'None'}")
    
    # Just make sure we found at least one ACM journal
    assert found_count > 0, "No ACM journals found in registry with acm publisher"
    print(f"✓ Found {found_count} properly mapped ACM journals")
    
    registry.close()


if __name__ == '__main__':
    # Run basic tests if executed directly
    test_instance = TestACMDance()
    test_instance.setUp()
    
    print("Running ACM Digital Library tests...")
    print("\n" + "="*60)
    
    tests = [
        ('test_acm_reel_url_construction_wireless_health', 'Wireless Health URL construction'),
        ('test_acm_reel_url_construction_mobile_computing', 'Mobile Computing URL construction'),
        ('test_acm_reel_url_construction_interactive_systems', 'Interactive Systems URL construction'),
        ('test_acm_reel_successful_access', 'Successful access simulation'),
        ('test_acm_reel_paywall_detection', 'Paywall detection'),
        ('test_acm_reel_network_error', 'Network error handling'),
        ('test_acm_reel_missing_doi', 'Missing DOI handling'),
        ('test_acm_reel_wrong_doi_pattern', 'Wrong DOI pattern handling'),
        ('test_acm_reel_404_error', '404 error handling')
    ]
    
    for test_method, description in tests:
        try:
            getattr(test_instance, test_method)()
            print(f"✓ {description} works")
        except Exception as e:
            print(f"✗ {description} failed: {e}")
    
    try:
        test_acm_journal_recognition()
        print("✓ Registry test passed: Journal recognition works")
    except Exception as e:
        print(f"✗ Registry test failed: {e}")
    
    print("\n" + "="*60)
    print("Test suite completed!")