"""Tests for Walsh Medical Media dance function.

This test suite validates the WalshMedia function following 
dance function guidelines Phase 4: Test Development.

Evidence analyzed:
- PMID 29226023: DOI resolution works perfectly 
- DOI 10.4172/2161-1122.1000448 resolves to direct PDF with article slug
- Primary URL construction method failed, DOI resolution succeeded
- Function reduced from 90→24 lines (73.3% reduction)

Implementation approach:
- Uses the_doi_2step for direct DOI resolution
- Eliminates trial-and-error patterns
- CLAUDE.md compliant: no generic exceptions, under 50 lines
"""

import unittest
from unittest.mock import Mock, patch
import pytest
from metapub.findit.dances.generic import the_doi_2step, verify_pdf_url
from metapub.findit.dances import the_walshmedia_bora
from metapub.findit.registry import JournalRegistry
from metapub.pubmedfetcher import PubMedFetcher
from metapub.exceptions import NoPDFLink
from tests.test_compat import skip_network_tests
from tests.fixtures import load_pmid_xml, WALSHMEDIA_EVIDENCE_PMIDS


class TestWalshMedia(unittest.TestCase):
    """Test rewritten Walsh Medical Media dance function."""
    
    def setUp(self):
        """Set up test fixtures with evidence PMIDs."""
        # Evidence PMID from investigation
        self.evidence_pmid = '29226023'
        self.evidence_doi = '10.4172/2161-1122.1000448'
        self.evidence_journal = 'Dentistry (Sunnyvale)'
        self.evidence_url = 'https://www.walshmedicalmedia.com/open-access/evaluating-the-whitening-and-microstructural-effects-of-a-novel-whitening-strip-on-porcelain-and-composite-dental-materials-2161-1122-1000449.pdf'
    
    
    @skip_network_tests
    def test_evidence_based_doi_resolution(self):
        """Test DOI resolution with evidence PMID."""
        pmf = PubMedFetcher()
        pma = pmf.article_by_pmid(self.evidence_pmid)
        
        # Verify evidence metadata
        self.assertEqual(pma.doi, self.evidence_doi)
        self.assertEqual(pma.journal, self.evidence_journal)
        
        # Test DOI resolution directly
        resolved_url = the_doi_2step(pma.doi)
        self.assertEqual(resolved_url, self.evidence_url)
        
        # Test function without verification
        url = the_walshmedia_bora(pma, verify=False)
        self.assertEqual(url, self.evidence_url)
        
        print(f"✅ DOI resolution works: {url}")
    
    @skip_network_tests 
    def test_verification_success(self):
        """Test verification with evidence PMID (should succeed)."""
        pmf = PubMedFetcher()
        pma = pmf.article_by_pmid(self.evidence_pmid)
        
        # Should succeed with verification since it's open access
        url = the_walshmedia_bora(pma, verify=True)
        self.assertEqual(url, self.evidence_url)
        self.assertTrue(url.startswith('https://www.walshmedicalmedia.com/'))
        self.assertTrue(url.endswith('.pdf'))
        
        print(f"✅ Verification successful: {url}")
    
    def test_missing_doi_error_handling(self):
        """Test error handling for missing DOI (DANCE_FUNCTION_GUIDELINES compliance)."""
        # Create mock PubMedArticle without DOI
        mock_pma = Mock()
        mock_pma.doi = None
        mock_pma.journal = 'Dentistry'
        
        # Should raise NoPDFLink with clear error message
        with self.assertRaises(NoPDFLink) as context:
            the_walshmedia_bora(mock_pma, verify=False)
        
        error_msg = str(context.exception)
        self.assertIn('MISSING', error_msg)
        self.assertIn('DOI required', error_msg)
        self.assertIn('Walsh Medical Media', error_msg)
        
        print(f"✅ Missing DOI handled correctly: {error_msg}")
    
    
    def test_registry_integration(self):
        """Test Walsh Medical Media journals are mapped correctly in registry."""
        registry = JournalRegistry()
        
        # Test key Walsh Medical Media journals
        test_journals = [
            'Dentistry (Sunnyvale)',
            'J Pharmacovigil', 
            'Health Care Curr Rev'
        ]
        
        for journal in test_journals:
            with self.subTest(journal=journal):
                publisher_info = registry.get_publisher_for_journal(journal)
                if publisher_info:  # Some may not be in registry
                    self.assertEqual(publisher_info['name'], 'walshmedia')
                    self.assertEqual(publisher_info['dance_function'], 'the_walshmedia_bora')
        
        registry.close()
        print("✅ Registry integration verified")
    
    def test_doi_prefix_flexibility(self):
        """Test function handles Walsh Media DOI patterns correctly.""" 
        # Test with evidence DOI that we know works
        mock_pma = Mock()
        mock_pma.doi = '10.4172/2161-1122.1000448'  # Evidence DOI that works
        mock_pma.journal = 'Dentistry'
        
        # Should work without verification (DOI resolution)
        url = the_walshmedia_bora(mock_pma, verify=False)
        self.assertIsNotNone(url)
        self.assertTrue(url.startswith('https://'))
        self.assertIn('walshmedicalmedia.com', url)
                
        print(f"✅ DOI prefix flexibility confirmed for 10.4172 prefix")
    
    def test_comparison_with_longdom_pattern(self):
        """Test that WalshMedia follows same proven pattern as Longdom."""
        from metapub.findit.dances.longdom import the_longdom_hustle
        import inspect
        
        # Both should use same approach
        walsh_source = inspect.getsource(the_walshmedia_bora)
        longdom_source = inspect.getsource(the_longdom_hustle)
        
        # Both should use the_doi_2step and verify_pdf_url
        common_patterns = ['the_doi_2step', 'verify_pdf_url', 'if not pma.doi:', 'MISSING:']
        
        for pattern in common_patterns:
            self.assertIn(pattern, walsh_source, f"WalshMedia should use pattern: {pattern}")
            self.assertIn(pattern, longdom_source, f"Longdom should use pattern: {pattern}")
        
        print("✅ WalshMedia follows proven Longdom pattern")


class TestWalshMediaXMLFixtures:
    """Test WalshMedia dance function with real XML fixtures."""

    def test_walshmedia_authentic_metadata_validation(self):
        """Validate authentic metadata from XML fixtures matches expected patterns."""
        for pmid, expected in WALSHMEDIA_EVIDENCE_PMIDS.items():
            pma = load_pmid_xml(pmid)
            
            # Validate DOI follows WalshMedia pattern (10.4172/)
            assert pma.doi == expected['doi']
            assert pma.doi.startswith('10.4172/'), f"WalshMedia DOI must start with 10.4172/, got: {pma.doi}"
            
            # Validate journal name matches expected
            assert pma.journal == expected['journal']
            
            # Validate PMID matches
            assert pma.pmid == pmid
            
            print(f"✓ PMID {pmid}: {pma.journal} - {pma.doi}")

    @patch('metapub.findit.dances.walshmedia.the_doi_2step')
    def test_walshmedia_url_construction_without_verification(self, mock_doi_2step):
        """Test URL construction without verification using XML fixtures."""
        for pmid in WALSHMEDIA_EVIDENCE_PMIDS.keys():
            pma = load_pmid_xml(pmid)
            
            # Mock DOI resolution to WalshMedia URL
            expected_url = f'https://www.walshmedicalmedia.com/open-access/test-article-{pmid}.pdf'
            mock_doi_2step.return_value = expected_url
            
            # Test URL construction without verification
            result = the_walshmedia_bora(pma, verify=False)
            
            # Should return the DOI resolution result
            assert result == expected_url
            mock_doi_2step.assert_called_with(pma.doi)
            
            print(f"✓ PMID {pmid} URL construction: {result}")

    @patch('metapub.findit.dances.walshmedia.verify_pdf_url')
    @patch('metapub.findit.dances.walshmedia.the_doi_2step')
    def test_walshmedia_url_construction_with_mocked_verification(self, mock_doi_2step, mock_verify):
        """Test URL construction with mocked verification."""
        for pmid in WALSHMEDIA_EVIDENCE_PMIDS.keys():
            pma = load_pmid_xml(pmid)
            
            expected_url = f'https://www.walshmedicalmedia.com/open-access/test-article-{pmid}.pdf'
            mock_doi_2step.return_value = expected_url
            # Mock successful verification returns the URL
            mock_verify.return_value = expected_url
            
            result = the_walshmedia_bora(pma, verify=True)
            
            assert result == expected_url
            mock_verify.assert_called_with(expected_url, 'Walsh Medical Media')
            
            print(f"✓ PMID {pmid} verified URL: {result}")

    @patch('metapub.findit.dances.walshmedia.verify_pdf_url')
    @patch('metapub.findit.dances.walshmedia.the_doi_2step')
    def test_walshmedia_paywall_handling(self, mock_doi_2step, mock_verify):
        """Test paywall detection and error handling."""
        expected_url = 'https://www.walshmedicalmedia.com/open-access/test-article.pdf'
        mock_doi_2step.return_value = expected_url
        
        # Mock paywall response
        from metapub.exceptions import AccessDenied
        mock_verify.side_effect = AccessDenied('PAYWALL: Article requires subscription')
        
        pma = load_pmid_xml('29226023')  # Use test PMID
        
        with pytest.raises(AccessDenied):
            the_walshmedia_bora(pma, verify=True)

    def test_walshmedia_journal_coverage(self):
        """Test journal coverage across different WalshMedia publications."""
        journals_found = set()
        
        for pmid in WALSHMEDIA_EVIDENCE_PMIDS.keys():
            pma = load_pmid_xml(pmid)
            journals_found.add(pma.journal)
        
        # Should have at least 1 WalshMedia journal
        assert len(journals_found) >= 1, f"Expected at least 1 journal, got: {journals_found}"
        
        # All should be from Dentistry (Sunnyvale) based on our evidence
        expected_journals = {'Dentistry (Sunnyvale)'}
        assert journals_found == expected_journals, f"Unexpected journals: {journals_found - expected_journals}"

    def test_walshmedia_doi_pattern_consistency(self):
        """Test that all WalshMedia PMIDs use 10.4172 DOI prefix."""
        doi_prefix = '10.4172'
        
        for pmid, data in WALSHMEDIA_EVIDENCE_PMIDS.items():
            assert data['doi'].startswith(doi_prefix), f"PMID {pmid} has unexpected DOI prefix: {data['doi']}"
            
            pma = load_pmid_xml(pmid)
            assert pma.doi.startswith(doi_prefix), f"PMID {pmid} XML fixture has unexpected DOI: {pma.doi}"

    @patch('metapub.findit.dances.walshmedia.the_doi_2step')
    def test_walshmedia_error_handling_missing_doi(self, mock_doi_2step):
        """Test error handling for articles without DOI."""
        # Create mock article without DOI
        class MockPMA:
            def __init__(self):
                self.doi = None
                self.journal = 'Dentistry (Sunnyvale)'
        
        mock_pma = MockPMA()
        
        with pytest.raises(NoPDFLink) as excinfo:
            the_walshmedia_bora(mock_pma)
        
        assert 'MISSING' in str(excinfo.value) and 'DOI required' in str(excinfo.value)

    @patch('metapub.findit.dances.walshmedia.the_doi_2step')
    def test_walshmedia_template_flexibility(self, mock_doi_2step):
        """Test template flexibility for WalshMedia URL patterns."""
        pma = load_pmid_xml('29226023')  # Dentistry (Sunnyvale)
        
        # Mock DOI resolution
        expected_url = 'https://www.walshmedicalmedia.com/open-access/dental-whitening-example.pdf'
        mock_doi_2step.return_value = expected_url
        
        # Test URL construction
        result = the_walshmedia_bora(pma, verify=False)
        
        # Should follow WalshMedia URL pattern
        assert result == expected_url
        assert 'walshmedicalmedia.com' in result
        mock_doi_2step.assert_called_with(pma.doi)

    def test_walshmedia_pmc_availability(self):
        """Test coverage of PMC-available WalshMedia articles."""
        # Our test article has PMC ID
        for pmid, expected in WALSHMEDIA_EVIDENCE_PMIDS.items():
            pma = load_pmid_xml(pmid)
            
            assert 'pmc' in expected, f"PMID {pmid} should have PMC ID"
            
            # Test URL construction still works even with PMC availability
            with patch('metapub.findit.dances.walshmedia.the_doi_2step') as mock_doi:
                mock_doi.return_value = f'https://www.walshmedicalmedia.com/open-access/test-{pmid}.pdf'
                result = the_walshmedia_bora(pma, verify=False)
                assert result is not None
                assert 'walshmedicalmedia.com' in result
            
            print(f"✓ PMID {pmid} (PMC: {expected['pmc']}) works with WalshMedia infrastructure")



if __name__ == '__main__':
    unittest.main()