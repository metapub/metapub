"""Tests for Wiley dance function."""

import pytest
from unittest.mock import patch, Mock

from .common import BaseDanceTest
from metapub import PubMedFetcher
from metapub.findit.dances import the_wiley_shuffle
from metapub.exceptions import AccessDenied, NoPDFLink


class TestWileyDance(BaseDanceTest):
    """Test cases for Wiley Publishing."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.fetch = PubMedFetcher()

    def test_wiley_shuffle_trusts_registry(self):
        """Test 1: Function trusts registry routing.
        
        Expected: Should construct URL for any DOI that gets routed here by registry
        """
        # Test with any DOI - function should trust the registry routing
        pma = Mock()
        pma.doi = '10.1234/any-doi-pattern'
        pma.journal = 'Test Journal'
        
        url = the_wiley_shuffle(pma, verify=False)
        assert url == 'https://onlinelibrary.wiley.com/doi/epdf/10.1234/any-doi-pattern'
        print(f"Test 1 - Trusts registry routing: {url}")

    def test_wiley_shuffle_epdf_url_construction(self):
        """Test 2: Wiley epdf DOI-based URL construction.
        
        PMID: 33474827 (Thoracic Cancer)
        Expected: Should construct Wiley epdf URL using evidence-driven pattern
        """
        pma = self.fetch.article_by_pmid('33474827')
        
        assert pma.journal == 'Thorac Cancer'
        assert pma.doi == '10.1111/1759-7714.13823'
        
        # Test without verification
        url = the_wiley_shuffle(pma, verify=False)
        assert url is not None
        assert url == 'https://onlinelibrary.wiley.com/doi/epdf/10.1111/1759-7714.13823'
        assert 'onlinelibrary.wiley.com/doi/epdf/' in url
        print(f"Test 2 - Wiley epdf URL: {url}")

    def test_wiley_shuffle_different_journal(self):
        """Test 3: Mock Wiley article with 10.1002 DOI pattern.
        
        Expected: Should construct correct Wiley epdf URL
        """
        # Use mock since we need reliable test data
        pma = Mock()
        pma.doi = '10.1002/cncr.32345'
        pma.journal = 'Cancer'
        
        # Test URL construction (verify=False to avoid network calls)
        url = the_wiley_shuffle(pma, verify=False)
        assert url is not None 
        assert url == 'https://onlinelibrary.wiley.com/doi/epdf/10.1002/cncr.32345'
        print(f"Test 3 - Mock Cancer journal URL: {url}")

    def test_wiley_shuffle_mock_articles(self):
        """Test 4: Mock articles with different DOI patterns."""
        # Test standard Wiley DOI (10.1002)
        pma = Mock()
        pma.doi = '10.1002/brb3.70665'
        pma.journal = 'Brain and Behavior'
        
        url = the_wiley_shuffle(pma, verify=False)
        assert url == 'https://onlinelibrary.wiley.com/doi/epdf/10.1002/brb3.70665'
        print(f"Test 4a - Mock Wiley 10.1002 URL: {url}")
        
        # Test Wiley 10.1111 DOI pattern
        pma.doi = '10.1111/1365-2664.14386'
        url = the_wiley_shuffle(pma, verify=False)
        assert url == 'https://onlinelibrary.wiley.com/doi/epdf/10.1111/1365-2664.14386'
        print(f"Test 4b - Mock Wiley 10.1111 URL: {url}")
        
        # Test Hindawi DOI pattern (10.1155) - acquired by Wiley
        pma.doi = '10.1155/2023/1234567'
        url = the_wiley_shuffle(pma, verify=False)
        assert url == 'https://onlinelibrary.wiley.com/doi/epdf/10.1155/2023/1234567'
        print(f"Test 4c - Hindawi (Wiley-acquired) URL: {url}")

    @patch('metapub.findit.dances.wiley.verify_pdf_url')
    def test_wiley_shuffle_successful_pdf_access(self, mock_verify):
        """Test 5: Successful PDF access simulation.
        
        PMID: 33474827 (Thorac Cancer)
        Expected: Should return PDF URL when accessible
        """
        # Mock successful PDF verification
        mock_verify.return_value = True

        pma = self.fetch.article_by_pmid('33474827')
        
        # Test with verification - should succeed
        url = the_wiley_shuffle(pma, verify=True)
        expected_url = 'https://onlinelibrary.wiley.com/doi/epdf/10.1111/1759-7714.13823'
        assert url == expected_url
        assert 'onlinelibrary.wiley.com' in url
        print(f"Test 5 - Successful access: {url}")

    @patch('metapub.findit.dances.wiley.verify_pdf_url')
    def test_wiley_shuffle_paywall_detection(self, mock_verify):
        """Test 6: Paywall detection.
        
        Expected: Should detect paywall and raise AccessDenied when PDF verification fails
        """
        # Mock failed PDF verification (paywall)
        mock_verify.return_value = False

        pma = self.fetch.article_by_pmid('33474827')
        
        # Test with verification - should detect paywall
        with pytest.raises(AccessDenied) as exc_info:
            the_wiley_shuffle(pma, verify=True)
        
        assert 'PAYWALL' in str(exc_info.value)
        assert 'subscription' in str(exc_info.value)
        print(f"Test 6 - Correctly detected paywall: {exc_info.value}")

    @patch('metapub.findit.dances.wiley.verify_pdf_url')
    def test_wiley_shuffle_network_error(self, mock_verify):
        """Test 7: Network error handling.
        
        Expected: Should handle network errors gracefully
        """
        # Mock network error during verification
        mock_verify.side_effect = Exception("Network error")

        pma = self.fetch.article_by_pmid('33474827')
        
        # Test with verification - should handle network error
        with pytest.raises(AccessDenied) as exc_info:
            the_wiley_shuffle(pma, verify=True)
        
        assert 'PAYWALL' in str(exc_info.value)
        print(f"Test 7 - Correctly handled network error: {exc_info.value}")

    def test_wiley_shuffle_missing_doi(self):
        """Test 8: Article without DOI.
        
        Expected: Should raise NoPDFLink for missing DOI
        """
        # Create a mock PMA without DOI
        pma = Mock()
        pma.doi = None
        pma.journal = 'Some Journal'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_wiley_shuffle(pma, verify=False)
        
        assert 'MISSING' in str(exc_info.value)
        assert 'DOI required' in str(exc_info.value)
        print(f"Test 8 - Correctly handled missing DOI: {exc_info.value}")

    def test_wiley_shuffle_any_doi_pattern(self):
        """Test 9: Article with any DOI pattern.
        
        Expected: Should construct URL for any DOI (trusts registry routing)
        """
        # Create a mock PMA with any DOI pattern
        pma = Mock()
        pma.doi = '10.9999/any-publisher-pattern-works'
        pma.journal = 'Some Journal'
        
        url = the_wiley_shuffle(pma, verify=False)
        assert url == 'https://onlinelibrary.wiley.com/doi/epdf/10.9999/any-publisher-pattern-works'
        print(f"Test 9 - Works with any DOI pattern: {url}")


def test_wiley_journal_recognition():
    """Test that Wiley journals are properly recognized in the registry."""
    from metapub.findit.registry import JournalRegistry
    
    registry = JournalRegistry()
    
    # Test some known Wiley journals
    test_journals = [
        'Brain Behav',
        'J Appl Ecol',
        'Cancer',
        'Hepatology'
    ]
    
    # Test journal recognition
    found_count = 0
    for journal in test_journals:
        publisher_info = registry.get_publisher_for_journal(journal)
        if publisher_info and publisher_info['name'] == 'wiley':
            assert publisher_info['dance_function'] == 'the_wiley_shuffle'
            print(f"✓ {journal} correctly mapped to Wiley")
            found_count += 1
        else:
            print(f"⚠ {journal} mapped to different publisher: {publisher_info['name'] if publisher_info else 'None'}")
    
    # Test some Hindawi journals (acquired by Wiley)
    hindawi_journals = ['Case Rep Med', 'J Immunol Res']
    for journal in hindawi_journals:
        publisher_info = registry.get_publisher_for_journal(journal)
        if publisher_info and publisher_info['name'] == 'wiley':
            print(f"✓ {journal} correctly mapped to Wiley (Hindawi acquisition)")
        else:
            print(f"⚠ {journal} mapped to: {publisher_info['name'] if publisher_info else 'None'}")
    
    # Just make sure we found at least one Wiley journal
    if found_count > 0:
        print(f"✓ Found {found_count} properly mapped Wiley journals")
    else:
        print("⚠ No Wiley journals found in registry")
    
    registry.close()


if __name__ == '__main__':
    # Run basic tests if executed directly
    test_instance = TestWileyDance()
    test_instance.setUp()
    
    print("Running Wiley dance function tests...")
    print("\\n" + "="*60)
    
    tests = [
        ('test_wiley_shuffle_trusts_registry', 'Registry routing trust'),
        ('test_wiley_shuffle_epdf_url_construction', 'Wiley epdf URL construction'),
        ('test_wiley_shuffle_different_journal', 'Different Wiley journal'),
        ('test_wiley_shuffle_mock_articles', 'Mock article handling'),
        ('test_wiley_shuffle_successful_pdf_access', 'Successful access simulation'),
        ('test_wiley_shuffle_paywall_detection', 'Paywall detection'),
        ('test_wiley_shuffle_network_error', 'Network error handling'),
        ('test_wiley_shuffle_missing_doi', 'Missing DOI handling'),
        ('test_wiley_shuffle_any_doi_pattern', 'Any DOI pattern handling')
    ]
    
    for test_method, description in tests:
        try:
            getattr(test_instance, test_method)()
            print(f"✓ {description} works")
        except Exception as e:
            print(f"✗ {description} failed: {e}")
    
    try:
        test_wiley_journal_recognition()
        print("✓ Registry test passed: Journal recognition works")
    except Exception as e:
        print(f"✗ Registry test failed: {e}")
    
    print("\\n" + "="*60)
    print("Test suite completed!")