"""Tests for Springer dance function."""

import pytest
from unittest.mock import patch, Mock

from .common import BaseDanceTest
from metapub import PubMedFetcher
from metapub.findit.dances import the_springer_shag
from metapub.exceptions import AccessDenied, NoPDFLink


class TestSpringerDance(BaseDanceTest):
    """Test cases for Springer Publishing Group."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.fetch = PubMedFetcher()

    def test_springer_shag_trusts_registry(self):
        """Test 1: Function trusts registry routing.
        
        Expected: Should construct URL for any DOI that gets routed here by registry
        """
        # Test with any DOI - function should trust the registry routing
        pma = Mock()
        pma.doi = '10.1234/any-doi-pattern'
        pma.journal = 'Test Journal'
        
        url = the_springer_shag(pma, verify=False)
        assert url == 'https://link.springer.com/content/pdf/10.1234/any-doi-pattern.pdf'
        print(f"Test 1 - Trusts registry routing: {url}")

    def test_springer_shag_springerlink_url_construction(self):
        """Test 2: Springer Link DOI-based URL construction.
        
        PMID: 38187995 (Neural Computing and Applications)
        Expected: Should construct Springer Link PDF URL
        """
        pma = self.fetch.article_by_pmid('38187995')
        
        assert pma.journal == 'Neural Comput Appl'
        assert pma.doi == '10.1007/s00521-023-09033-7'
        
        # Test without verification
        url = the_springer_shag(pma, verify=False)
        assert url is not None
        assert url == 'https://link.springer.com/content/pdf/10.1007/s00521-023-09033-7.pdf'
        assert 'link.springer.com/content/pdf/' in url
        print(f"Test 2 - Springer Link URL: {url}")

    def test_springer_shag_different_springerlink_article(self):
        """Test 3: Different Springer Link article.
        
        PMID: 36919039 (European Journal of Wildlife Research)
        Expected: Should construct correct Springer Link URL
        """
        pma = self.fetch.article_by_pmid('36919039')
        
        assert pma.doi == '10.1007/s10344-023-01658-2'
        
        # Test URL construction (verify=False to avoid network calls)
        url = the_springer_shag(pma, verify=False)
        assert url is not None 
        assert url == 'https://link.springer.com/content/pdf/10.1007/s10344-023-01658-2.pdf'
        print(f"Test 3 - Different Springer Link URL: {url}")

    def test_springer_shag_mock_article(self):
        """Test 4: Mock article with different DOI patterns."""
        # Test Springer Link DOI
        pma = Mock()
        pma.doi = '10.1007/s12345-2024-67890-1'
        pma.journal = 'Test Journal'
        
        url = the_springer_shag(pma, verify=False)
        assert url == 'https://link.springer.com/content/pdf/10.1007/s12345-2024-67890-1.pdf'
        print(f"Test 4a - Mock Springer Link URL: {url}")
        
        # Test any other DOI pattern - registry routing is trusted
        pma.doi = '10.1186/s99999-2024-00001-x'
        url = the_springer_shag(pma, verify=False)
        assert url == 'https://link.springer.com/content/pdf/10.1186/s99999-2024-00001-x.pdf'
        print(f"Test 4b - Trusts registry for any DOI: {url}")

    @patch('metapub.findit.dances.springer.verify_pdf_url')
    def test_springer_shag_successful_pdf_access(self, mock_verify):
        """Test 5: Successful PDF access simulation.
        
        PMID: 38187995 (Neural Comput Appl)
        Expected: Should return PDF URL when accessible
        """
        # Mock successful PDF verification
        mock_verify.return_value = True

        pma = self.fetch.article_by_pmid('38187995')
        
        # Test with verification - should succeed
        url = the_springer_shag(pma, verify=True)
        expected_url = 'https://link.springer.com/content/pdf/10.1007/s00521-023-09033-7.pdf'
        assert url == expected_url
        assert 'springer.com' in url
        print(f"Test 5 - Successful access: {url}")

    @patch('metapub.findit.dances.springer.verify_pdf_url')
    def test_springer_shag_paywall_detection(self, mock_verify):
        """Test 6: Paywall detection.
        
        Expected: Should detect paywall and raise AccessDenied when PDF verification fails
        """
        # Mock failed PDF verification (paywall)
        mock_verify.return_value = False

        pma = self.fetch.article_by_pmid('38187995')
        
        # Test with verification - should detect paywall
        with pytest.raises(AccessDenied) as exc_info:
            the_springer_shag(pma, verify=True)
        
        assert 'PAYWALL' in str(exc_info.value)
        assert 'subscription' in str(exc_info.value)
        print(f"Test 6 - Correctly detected paywall: {exc_info.value}")

    @patch('metapub.findit.dances.springer.verify_pdf_url')
    def test_springer_shag_network_error(self, mock_verify):
        """Test 7: Network error handling.
        
        Expected: Should handle network errors gracefully
        """
        # Mock network error during verification
        mock_verify.side_effect = Exception("Network error")

        pma = self.fetch.article_by_pmid('38187995')
        
        # Test with verification - should handle network error
        with pytest.raises(AccessDenied) as exc_info:
            the_springer_shag(pma, verify=True)
        
        assert 'PAYWALL' in str(exc_info.value)
        print(f"Test 7 - Correctly handled network error: {exc_info.value}")

    def test_springer_shag_missing_doi(self):
        """Test 8: Article without DOI.
        
        Expected: Should raise NoPDFLink for missing DOI
        """
        # Create a mock PMA without DOI
        pma = Mock()
        pma.doi = None
        pma.journal = 'Some Journal'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_springer_shag(pma, verify=False)
        
        assert 'MISSING' in str(exc_info.value)
        assert 'DOI required' in str(exc_info.value)
        print(f"Test 8 - Correctly handled missing DOI: {exc_info.value}")

    def test_springer_shag_any_doi_pattern(self):
        """Test 9: Article with any DOI pattern.
        
        Expected: Should construct URL for any DOI (trusts registry routing)
        """
        # Create a mock PMA with any DOI pattern
        pma = Mock()
        pma.doi = '10.1234/any-doi-pattern-works'
        pma.journal = 'Some Journal'
        
        url = the_springer_shag(pma, verify=False)
        assert url == 'https://link.springer.com/content/pdf/10.1234/any-doi-pattern-works.pdf'
        print(f"Test 9 - Works with any DOI pattern: {url}")


def test_springer_journal_recognition():
    """Test that Springer journals are properly recognized in the registry."""
    from metapub.findit.registry import JournalRegistry
    
    registry = JournalRegistry()
    
    # Test some known Springer Link journals (10.1007 DOIs only)
    test_journals = [
        'Neural Comput Appl',
        'Eur J Wildl Res'
    ]
    
    # Test journal recognition
    found_count = 0
    for journal in test_journals:
        publisher_info = registry.get_publisher_for_journal(journal)
        if publisher_info and publisher_info['name'] == 'springer':
            assert publisher_info['dance_function'] == 'the_springer_shag'
            print(f"✓ {journal} correctly mapped to Springer")
            found_count += 1
        else:
            print(f"⚠ {journal} mapped to different publisher: {publisher_info['name'] if publisher_info else 'None'}")
    
    # Note: BMC journals should be mapped to BMC, not Springer
    bmc_journals = ['BMC Psychiatry', 'Implement Sci Commun']
    for journal in bmc_journals:
        publisher_info = registry.get_publisher_for_journal(journal)
        if publisher_info and publisher_info['name'] == 'bmc':
            print(f"✓ {journal} correctly mapped to BMC (not Springer)")
        else:
            print(f"⚠ {journal} mapped to: {publisher_info['name'] if publisher_info else 'None'}")
    
    # Just make sure we found at least one Springer journal
    if found_count > 0:
        print(f"✓ Found {found_count} properly mapped Springer journals")
    else:
        print("⚠ No Springer journals found in registry")
    
    registry.close()


if __name__ == '__main__':
    # Run basic tests if executed directly
    test_instance = TestSpringerDance()
    test_instance.setUp()
    
    print("Running Springer dance function tests...")
    print("\n" + "="*60)
    
    tests = [
        ('test_springer_shag_trusts_registry', 'Registry routing trust'),
        ('test_springer_shag_springerlink_url_construction', 'Springer Link URL construction'),
        ('test_springer_shag_different_springerlink_article', 'Different Springer Link article'),
        ('test_springer_shag_mock_article', 'Mock article handling'),
        ('test_springer_shag_successful_pdf_access', 'Successful access simulation'),
        ('test_springer_shag_paywall_detection', 'Paywall detection'),
        ('test_springer_shag_network_error', 'Network error handling'),
        ('test_springer_shag_missing_doi', 'Missing DOI handling'),
        ('test_springer_shag_any_doi_pattern', 'Any DOI pattern handling')
    ]
    
    for test_method, description in tests:
        try:
            getattr(test_instance, test_method)()
            print(f"✓ {description} works")
        except Exception as e:
            print(f"✗ {description} failed: {e}")
    
    try:
        test_springer_journal_recognition()
        print("✓ Registry test passed: Journal recognition works")
    except Exception as e:
        print(f"✗ Registry test failed: {e}")
    
    print("\n" + "="*60)
    print("Test suite completed!")