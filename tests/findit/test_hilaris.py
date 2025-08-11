#!/usr/bin/env python3
"""
Test suite for Hilaris Publisher dance function.
Uses DOI resolution approach - no HTML samples required.

Test approach:
- Tests DOI resolution instead of HTML parsing
- Uses real DOI from evidence: 10.4172/2161-0525.1000551
- Validates dance function guidelines compliance
"""

import unittest
from unittest.mock import patch, Mock
import requests
import pytest

from metapub.findit.dances.hilaris import the_hilaris_hop
from metapub.exceptions import NoPDFLink, AccessDenied
from metapub import PubMedFetcher
from tests.fixtures import load_pmid_xml, HILARIS_EVIDENCE_PMIDS


class TestHilarisDanceEvidenceDriven(unittest.TestCase):
    """Evidence-driven test suite for Hilaris Publisher dance function"""

    def setUp(self):
        """Set up test fixtures with real evidence DOI"""
        self.fetch = PubMedFetcher()
        
        # Real evidence DOI from PMID 34094707
        self.evidence_doi = '10.4172/2161-0525.1000551'
        self.evidence_pmid = '34094707'
        
        # Create mock PMA with evidence data
        self.mock_pma = Mock()
        self.mock_pma.doi = self.evidence_doi
        self.mock_pma.journal = 'J Environ Anal Toxicol'
        self.mock_pma.pmid = self.evidence_pmid


    @patch('metapub.findit.dances.hilaris.the_doi_2step')
    def test_doi_resolution_success_without_verification(self, mock_doi_2step):
        """Test successful DOI resolution without verification"""
        expected_url = 'https://www.hilarispublisher.com/open-access/environmental-toxins-example.pdf'
        mock_doi_2step.return_value = expected_url
        
        result = the_hilaris_hop(self.mock_pma, verify=False)
        
        self.assertEqual(result, expected_url)
        mock_doi_2step.assert_called_once_with(self.evidence_doi)

    @patch('metapub.findit.dances.hilaris.verify_pdf_url')
    @patch('metapub.findit.dances.hilaris.the_doi_2step')
    def test_doi_resolution_with_verification_success(self, mock_doi_2step, mock_verify):
        """Test successful DOI resolution with verification"""
        expected_url = 'https://www.hilarispublisher.com/open-access/environmental-toxins-example.pdf'
        mock_doi_2step.return_value = expected_url
        mock_verify.return_value = expected_url
        
        result = the_hilaris_hop(self.mock_pma, verify=True)
        
        self.assertEqual(result, expected_url)
        mock_doi_2step.assert_called_once_with(self.evidence_doi)
        mock_verify.assert_called_once_with(expected_url, 'Hilaris Publisher')

    @patch('metapub.findit.dances.hilaris.verify_pdf_url')
    @patch('metapub.findit.dances.hilaris.the_doi_2step')
    def test_verification_access_denied(self, mock_doi_2step, mock_verify):
        """Test that AccessDenied from verification bubbles up correctly"""
        expected_url = 'https://www.hilarispublisher.com/open-access/environmental-toxins-example.pdf'
        mock_doi_2step.return_value = expected_url
        mock_verify.side_effect = AccessDenied('PAYWALL: Article requires subscription')
        
        with self.assertRaises(AccessDenied):
            the_hilaris_hop(self.mock_pma, verify=True)

    @patch('metapub.findit.dances.hilaris.the_doi_2step')
    def test_non_hilaris_domain_raises_invalid(self, mock_doi_2step):
        """Test that DOI resolving to non-Hilaris domain raises NoPDFLink"""
        mock_doi_2step.return_value = 'https://other-publisher.com/article.pdf'
        
        with self.assertRaises(NoPDFLink) as context:
            the_hilaris_hop(self.mock_pma, verify=False)
        
        self.assertIn('INVALID:', str(context.exception))
        self.assertIn('did not resolve to Hilaris Publisher domain', str(context.exception))

    @patch('metapub.findit.dances.hilaris.the_doi_2step')
    def test_doi_resolution_txerror_bubbles_up(self, mock_doi_2step):
        """Test that TXERROR from the_doi_2step bubbles up correctly"""
        mock_doi_2step.side_effect = NoPDFLink('TXERROR: dx.doi.org lookup failed (Network timeout) - attempted: https://dx.doi.org/10.4172/2161-0525.1000551')
        
        with self.assertRaises(NoPDFLink) as context:
            the_hilaris_hop(self.mock_pma, verify=False)
        
        self.assertIn('TXERROR:', str(context.exception))
        self.assertIn('dx.doi.org lookup failed', str(context.exception))

    def test_real_pmid_metadata_validation(self):
        """Test with real PMID metadata to validate approach"""
        try:
            pma = self.fetch.article_by_pmid(self.evidence_pmid)
            
            # Validate we have expected data
            self.assertEqual(pma.doi, self.evidence_doi)
            self.assertEqual(pma.journal, 'J Environ Anal Toxicol')
            self.assertIsNotNone(pma.title)
            
            print(f"Real PMID validation: DOI={pma.doi}, Journal={pma.journal}")
            
        except Exception as e:
            self.skipTest(f"Could not fetch real PMID data: {e}")

    @patch('metapub.findit.dances.hilaris.the_doi_2step')
    def test_doi_prefix_pattern_validation(self, mock_doi_2step):
        """Test that function works with Hilaris DOI prefix pattern"""
        # Test primary Hilaris DOI pattern
        hilaris_dois = [
            '10.4172/2161-0525.1000551',  # Evidence DOI
            '10.4172/1234-5678.1000123',  # Pattern variation
            '10.4172/0987-6543.1000999'   # Another variation
        ]
        
        for doi in hilaris_dois:
            pma = Mock()
            pma.doi = doi
            pma.journal = 'J Environ Anal Toxicol'
            
            expected_url = f'https://www.hilarispublisher.com/open-access/test-article-{doi.split("/")[-1]}.pdf'
            mock_doi_2step.return_value = expected_url
            
            result = the_hilaris_hop(pma, verify=False)
            self.assertEqual(result, expected_url)


    def test_no_html_sample_dependency(self):
        """Test that function works without any HTML sample requirements"""
        # This test validates that the DOI resolution approach 
        # completely bypasses the need for HTML samples
        
        with patch('metapub.findit.dances.hilaris.the_doi_2step') as mock_doi:
            expected_url = 'https://www.hilarispublisher.com/open-access/test-article.pdf'
            mock_doi.return_value = expected_url
            
            # Function should work purely from DOI resolution
            result = the_hilaris_hop(self.mock_pma, verify=False)
            
            self.assertEqual(result, expected_url)
            # Verify only DOI resolution was called, no HTML operations
            mock_doi.assert_called_once_with(self.evidence_doi)
            
        print("✓ No HTML sample dependency - function uses pure DOI resolution")


class TestHilarisXMLFixtures:
    """Test Hilaris dance function with real XML fixtures."""

    def test_hilaris_authentic_metadata_validation(self):
        """Validate authentic metadata from XML fixtures matches expected patterns."""
        for pmid, expected in HILARIS_EVIDENCE_PMIDS.items():
            pma = load_pmid_xml(pmid)
            
            # Validate DOI follows Hilaris pattern (10.4172/)
            assert pma.doi == expected['doi']
            assert pma.doi.startswith('10.4172/'), f"Hilaris DOI must start with 10.4172/, got: {pma.doi}"
            
            # Validate journal name matches expected
            assert pma.journal == expected['journal']
            
            # Validate PMID matches
            assert pma.pmid == pmid
            
            print(f"✓ PMID {pmid}: {pma.journal} - {pma.doi}")

    @patch('metapub.findit.dances.hilaris.the_doi_2step')
    def test_hilaris_url_construction_without_verification(self, mock_doi_2step):
        """Test URL construction without verification using XML fixtures."""
        for pmid in HILARIS_EVIDENCE_PMIDS.keys():
            pma = load_pmid_xml(pmid)
            
            # Mock DOI resolution to Hilaris URL
            expected_url = f'https://www.hilarispublisher.com/open-access/test-article-{pmid}.pdf'
            mock_doi_2step.return_value = expected_url
            
            # Test URL construction without verification
            result = the_hilaris_hop(pma, verify=False)
            
            # Should return the DOI resolution result
            assert result == expected_url
            mock_doi_2step.assert_called_with(pma.doi)
            
            print(f"✓ PMID {pmid} URL construction: {result}")

    @patch('metapub.findit.dances.hilaris.verify_pdf_url')
    @patch('metapub.findit.dances.hilaris.the_doi_2step')
    def test_hilaris_url_construction_with_mocked_verification(self, mock_doi_2step, mock_verify):
        """Test URL construction with mocked verification."""
        for pmid in HILARIS_EVIDENCE_PMIDS.keys():
            pma = load_pmid_xml(pmid)
            
            expected_url = f'https://www.hilarispublisher.com/open-access/test-article-{pmid}.pdf'
            mock_doi_2step.return_value = expected_url
            # Mock successful verification returns the URL
            mock_verify.return_value = expected_url
            
            result = the_hilaris_hop(pma, verify=True)
            
            assert result == expected_url
            mock_verify.assert_called_with(expected_url, 'Hilaris Publisher')
            
            print(f"✓ PMID {pmid} verified URL: {result}")

    @patch('metapub.findit.dances.hilaris.verify_pdf_url')
    @patch('metapub.findit.dances.hilaris.the_doi_2step')
    def test_hilaris_paywall_handling(self, mock_doi_2step, mock_verify):
        """Test paywall detection and error handling."""
        expected_url = 'https://www.hilarispublisher.com/open-access/test-article.pdf'
        mock_doi_2step.return_value = expected_url
        
        # Mock paywall response
        mock_verify.side_effect = AccessDenied('PAYWALL: Article requires subscription')
        
        pma = load_pmid_xml('34094707')  # Use first test PMID
        
        with pytest.raises(AccessDenied):
            the_hilaris_hop(pma, verify=True)

    def test_hilaris_journal_coverage(self):
        """Test journal coverage across different Hilaris publications."""
        journals_found = set()
        
        for pmid in HILARIS_EVIDENCE_PMIDS.keys():
            pma = load_pmid_xml(pmid)
            journals_found.add(pma.journal)
        
        # Should have at least 1 Hilaris journal
        assert len(journals_found) >= 1, f"Expected at least 1 journal, got: {journals_found}"
        
        # All should be from J Environ Anal Toxicol based on our evidence
        expected_journals = {'J Environ Anal Toxicol'}
        assert journals_found == expected_journals, f"Unexpected journals: {journals_found - expected_journals}"

    def test_hilaris_doi_pattern_consistency(self):
        """Test that all Hilaris PMIDs use 10.4172 DOI prefix."""
        doi_prefix = '10.4172'
        
        for pmid, data in HILARIS_EVIDENCE_PMIDS.items():
            assert data['doi'].startswith(doi_prefix), f"PMID {pmid} has unexpected DOI prefix: {data['doi']}"
            
            pma = load_pmid_xml(pmid)
            assert pma.doi.startswith(doi_prefix), f"PMID {pmid} XML fixture has unexpected DOI: {pma.doi}"


    @patch('metapub.findit.dances.hilaris.the_doi_2step')
    def test_hilaris_template_flexibility(self, mock_doi_2step):
        """Test template flexibility for Hilaris URL patterns."""
        pma = load_pmid_xml('34094707')  # J Environ Anal Toxicol
        
        # Mock DOI resolution
        expected_url = 'https://www.hilarispublisher.com/open-access/environmental-toxins-example.pdf'
        mock_doi_2step.return_value = expected_url
        
        # Test URL construction
        result = the_hilaris_hop(pma, verify=False)
        
        # Should follow Hilaris URL pattern
        assert result == expected_url
        assert 'hilarispublisher.com' in result
        mock_doi_2step.assert_called_with(pma.doi)

    def test_hilaris_pmc_availability(self):
        """Test coverage of PMC-available Hilaris articles."""
        # Both our test articles have PMC IDs
        for pmid, expected in HILARIS_EVIDENCE_PMIDS.items():
            pma = load_pmid_xml(pmid)
            
            assert 'pmc' in expected, f"PMID {pmid} should have PMC ID"
            
            # Test URL construction still works even with PMC availability
            with patch('metapub.findit.dances.hilaris.the_doi_2step') as mock_doi:
                mock_doi.return_value = f'https://www.hilarispublisher.com/open-access/test-{pmid}.pdf'
                result = the_hilaris_hop(pma, verify=False)
                assert result is not None
                assert 'hilarispublisher.com' in result
            
            print(f"✓ PMID {pmid} (PMC: {expected['pmc']}) works with Hilaris infrastructure")


if __name__ == '__main__':
    # Run comprehensive test suite
    unittest.main(verbosity=2)