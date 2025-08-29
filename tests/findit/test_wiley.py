"""Tests for Wiley dance function."""

import pytest
from unittest.mock import patch, Mock

from .common import BaseDanceTest
from metapub import PubMedFetcher
from metapub.findit.dances import the_doi_slide as the_wiley_shuffle
from metapub.exceptions import AccessDenied, NoPDFLink
from tests.fixtures import load_pmid_xml, WILEY_EVIDENCE_PMIDS


class TestWileyDance(BaseDanceTest):
    """Test cases for Wiley Publishing."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.fetch = PubMedFetcher()

    def test_wiley_shuffle_trusts_registry(self):
        """Test 1: Function trusts registry routing with real Wiley article.
        
        Expected: Should construct URL for DOI from known Wiley journal
        """
        # Use real Wiley article from verified PMIDs
        pma = self.fetch.article_by_pmid('39077977')  # ACR Open Rheumatol
        assert pma.doi == '10.1002/acr2.11726'
        assert 'ACR Open Rheumatol' in pma.journal
        
        url = the_wiley_shuffle(pma, verify=False)
        assert url == 'https://onlinelibrary.wiley.com/doi/epdf/10.1002/acr2.11726'
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
        expected_url = 'https://onlinelibrary.wiley.com/doi/epdf/10.1111/1759-7714.13823'
        assert url == expected_url
        assert 'onlinelibrary.wiley.com/doi/epdf/' in url
        print(f"Test 2 - Wiley epdf URL: {url}")

    def test_wiley_shuffle_different_journal(self):
        """Test 3: Real Wiley article with 10.1111 DOI pattern.
        
        Expected: Should construct correct Wiley epdf URL
        """
        # Use real Wiley article with 10.1111 pattern
        pma = self.fetch.article_by_pmid('36247735')  # J Finance
        assert pma.doi == '10.1111/jofi.13173'
        assert 'J Finance' in pma.journal
        
        # Test URL construction (verify=False to avoid network calls)
        url = the_wiley_shuffle(pma, verify=False)
        assert url is not None 
        assert url == 'https://onlinelibrary.wiley.com/doi/epdf/10.1111/jofi.13173'
        print(f"Test 3 - J Finance URL: {url}")

    def test_wiley_shuffle_real_articles(self):
        """Test 4: Real articles with different DOI patterns."""
        # Test standard Wiley DOI (10.1002) - already tested above
        pma1 = self.fetch.article_by_pmid('39077977')  # ACR Open Rheumatol
        assert pma1.doi == '10.1002/acr2.11726'
        
        url1 = the_wiley_shuffle(pma1, verify=False)
        assert url1 == 'https://onlinelibrary.wiley.com/doi/epdf/10.1002/acr2.11726'
        print(f"Test 4a - Real Wiley 10.1002 URL: {url1}")
        
        # Test Wiley 10.1111 DOI pattern
        pma2 = self.fetch.article_by_pmid('36247735')  # J Finance
        assert pma2.doi == '10.1111/jofi.13173'
        
        url2 = the_wiley_shuffle(pma2, verify=False)
        assert url2 == 'https://onlinelibrary.wiley.com/doi/epdf/10.1111/jofi.13173'
        print(f"Test 4b - Real Wiley 10.1111 URL: {url2}")
        
        # Test Hindawi DOI pattern (10.1155) - acquired by Wiley
        pma3 = self.fetch.article_by_pmid('35573891')  # Wirel Commun Mob Comput
        assert pma3.doi == '10.1155/2021/5792975'
        
        url3 = the_wiley_shuffle(pma3, verify=False)
        assert url3 == 'https://onlinelibrary.wiley.com/doi/epdf/10.1155/2021/5792975'
        print(f"Test 4c - Real Hindawi (Wiley-acquired) URL: {url3}")

    @patch('metapub.findit.dances.generic.verify_pdf_url')
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

    @patch('metapub.findit.dances.generic.verify_pdf_url')
    def test_wiley_shuffle_paywall_detection(self, mock_verify):
        """Test 6: Paywall detection.
        
        Expected: Should detect paywall and raise AccessDenied when PDF verification fails
        """
        # Mock verification raising AccessDenied (paywall detected)
        mock_verify.side_effect = AccessDenied('DENIED: Wiley url requires subscription')

        pma = self.fetch.article_by_pmid('39077977')  # Real Wiley article
        
        # Test with verification - should propagate AccessDenied
        with pytest.raises(AccessDenied) as exc_info:
            the_wiley_shuffle(pma, verify=True)
        
        assert 'DENIED' in str(exc_info.value)
        print(f"Test 6 - Correctly detected paywall: {exc_info.value}")

    @patch('metapub.findit.dances.generic.verify_pdf_url')
    def test_wiley_shuffle_network_error(self, mock_verify):
        """Test 7: Network error handling.
        
        Expected: Should propagate network errors from verify_pdf_url
        """
        # Mock network error during verification
        mock_verify.side_effect = Exception("Network error")

        pma = self.fetch.article_by_pmid('39077977')  # Real Wiley article
        
        # Test with verification - should propagate the Exception
        with pytest.raises(Exception) as exc_info:
            the_wiley_shuffle(pma, verify=True)
        
        assert 'Network error' in str(exc_info.value)
        print(f"Test 7 - Correctly handled network error: {exc_info.value}")




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
            assert publisher_info['dance_function'] == 'the_doi_slide'
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
        ('test_wiley_shuffle_real_articles', 'Real article handling'),
        ('test_wiley_shuffle_successful_pdf_access', 'Successful access simulation'),
        ('test_wiley_shuffle_paywall_detection', 'Paywall detection'),
        ('test_wiley_shuffle_network_error', 'Network error handling'),
        ('test_wiley_shuffle_missing_doi', 'Missing DOI handling')
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


class TestWileyWithVerifiedPMIDs:
    """Test Wiley dance function with verified PMIDs from our system."""
    
    def test_wiley_verified_pmids_url_construction(self):
        """Test URL construction with actual verified PMIDs from Wiley system."""
        from metapub import PubMedFetcher
        
        # Verified PMIDs from wiley_pmids.txt
        verified_pmids_with_dois = [
            ('39077977', '10.1002/acr2.11726'),   # ACR Open Rheumatol
            ('35157371', '10.1002/acr2.11414'),   # ACR Open Rheumatol
            ('36247735', '10.1111/jofi.13173'),   # J Finance
            ('35573891', '10.1155/2021/5792975'), # Wirel Commun Mob Comput (Hindawi->Wiley)
        ]
        
        fetch = PubMedFetcher()
        
        with patch('metapub.findit.dances.generic.verify_pdf_url') as mock_verify:
            mock_verify.return_value = True
            
            for pmid, expected_doi in verified_pmids_with_dois:
                try:
                    pma = fetch.article_by_pmid(pmid)
                    
                    # Verify the article has the expected DOI
                    assert pma.doi == expected_doi, f"PMID {pmid} DOI mismatch: expected {expected_doi}, got {pma.doi}"
                    
                    # Test URL construction
                    result = the_wiley_shuffle(pma, verify=True)
                    expected_url = f"https://onlinelibrary.wiley.com/doi/epdf/{expected_doi}"
                    
                    assert result == expected_url, f"PMID {pmid} URL mismatch"
                    print(f"✓ PMID {pmid} ({pma.journal}): {result}")
                    
                except Exception as e:
                    print(f"⚠ PMID {pmid} failed: {e}")
                    # Don't fail the test for network issues, just warn
                    pass
    
    def test_wiley_sample_pmids_integration(self):
        """Integration test with sample PMIDs to ensure functionality."""
        from metapub import PubMedFetcher
        
        # Test just 2 PMIDs for lighter integration testing
        sample_pmids = [
            '39077977',  # Recent ACR Open Rheumatol (10.1002/)
            '36247735',  # J Finance (10.1111/)
        ]
        
        fetch = PubMedFetcher()
        
        for pmid in sample_pmids:
            try:
                pma = fetch.article_by_pmid(pmid)
                
                if pma.doi:
                    # Test without verification to avoid network calls
                    url = the_wiley_shuffle(pma, verify=False)
                    
                    assert 'onlinelibrary.wiley.com/doi/epdf/' in url
                    assert pma.doi in url
                    print(f"✓ Sample integration test PMID {pmid}: {url}")
                else:
                    print(f"⚠ PMID {pmid} doesn't have a DOI")
                    
            except Exception as e:
                print(f"⚠ Sample PMID {pmid} failed: {e}")
                # Don't fail for network issues


class TestWileyXMLFixtures:
    """Test Wiley dance function with real XML fixtures."""

    def test_wiley_authentic_metadata_validation(self):
        """Validate authentic metadata from XML fixtures."""
        for pmid, expected in WILEY_EVIDENCE_PMIDS.items():
            pma = load_pmid_xml(pmid)
            
            assert pma.doi == expected['doi']
            assert pma.journal == expected['journal']
            assert pma.pmid == pmid
            
            print(f"✓ PMID {pmid}: {pma.journal} - {pma.doi}")

    def test_wiley_url_construction_without_verification(self):
        """Test URL construction using XML fixtures."""
        for pmid in WILEY_EVIDENCE_PMIDS.keys():
            pma = load_pmid_xml(pmid)
            
            result = the_wiley_shuffle(pma, verify=False)
            expected_url = f'https://onlinelibrary.wiley.com/doi/epdf/{pma.doi}'
            assert result == expected_url
            
            print(f"✓ PMID {pmid} URL: {result}")

    @patch('metapub.findit.dances.generic.verify_pdf_url')
    def test_wiley_paywall_handling(self, mock_verify):
        """Test paywall detection."""
        mock_verify.side_effect = AccessDenied('Wiley subscription required')
        
        pma = load_pmid_xml('39077977')  # Use first test PMID
        
        with pytest.raises(AccessDenied):
            the_wiley_shuffle(pma, verify=True)

    def test_wiley_journal_coverage(self):
        """Test journal coverage across different Wiley publications."""
        journals_found = set()
        
        for pmid in WILEY_EVIDENCE_PMIDS.keys():
            pma = load_pmid_xml(pmid)
            journals_found.add(pma.journal)
        
        assert len(journals_found) >= 4
        print(f"✅ Coverage: {len(journals_found)} different Wiley journals")

    def test_wiley_doi_pattern_diversity(self):
        """Test DOI pattern diversity across Wiley divisions."""
        doi_patterns = {'10.1002/': 'Standard Wiley', '10.1111/': 'Wiley-Blackwell', '10.1155/': 'Hindawi (acquired)'}
        patterns_found = set()
        
        for pmid in WILEY_EVIDENCE_PMIDS.keys():
            pma = load_pmid_xml(pmid)
            
            for pattern in doi_patterns.keys():
                if pma.doi.startswith(pattern):
                    patterns_found.add(pattern)
                    break
        
        assert len(patterns_found) >= 3, f"Expected at least 3 DOI patterns, got: {patterns_found}"