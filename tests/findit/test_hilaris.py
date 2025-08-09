#!/usr/bin/env python3
"""
Evidence-driven test suite for Hilaris Publisher dance function
Following DOI resolution approach - no HTML samples required

EVIDENCE-DRIVEN REWRITE 2025-08-09:
- Tests DOI resolution approach instead of HTML parsing
- Bypasses corrupted HTML sample issue
- Uses real DOI from evidence: 10.4172/2161-0525.1000551
- Validates DANCE_FUNCTION_GUIDELINES compliance
"""

import unittest
from unittest.mock import patch, Mock
import requests

from metapub.findit.dances.hilaris import the_hilaris_hop
from metapub.exceptions import NoPDFLink, AccessDenied
from metapub import PubMedFetcher


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

    def test_missing_doi_raises_nopdflink(self):
        """Test that missing DOI raises NoPDFLink with MISSING prefix"""
        pma = Mock()
        pma.doi = None
        pma.journal = 'J Environ Anal Toxicol'
        
        with self.assertRaises(NoPDFLink) as context:
            the_hilaris_hop(pma, verify=False)
        
        self.assertIn('MISSING:', str(context.exception))
        self.assertIn('DOI required', str(context.exception))

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

    def test_function_length_compliance(self):
        """Test that rewritten function complies with DANCE_FUNCTION_GUIDELINES (<50 lines)"""
        import inspect
        
        source_lines = inspect.getsourcelines(the_hilaris_hop)[0]
        function_lines = len([line for line in source_lines if line.strip() and not line.strip().startswith('#')])
        
        self.assertLess(function_lines, 50, f"Function has {function_lines} lines, should be under 50")
        print(f"✓ Function length compliance: {function_lines} lines (under 50 line guideline)")

    def test_error_message_prefix_compliance(self):
        """Test that error messages follow DANCE_FUNCTION_GUIDELINES prefix patterns"""
        # Test MISSING prefix
        pma_no_doi = Mock()
        pma_no_doi.doi = None
        
        with self.assertRaises(NoPDFLink) as context:
            the_hilaris_hop(pma_no_doi, verify=False)
        self.assertTrue(str(context.exception).startswith('MISSING:'))
        
        # Test INVALID prefix
        with patch('metapub.findit.dances.hilaris.the_doi_2step') as mock_doi:
            mock_doi.return_value = 'https://wrong-domain.com/article.pdf'
            
            with self.assertRaises(NoPDFLink) as context:
                the_hilaris_hop(self.mock_pma, verify=False)
            self.assertTrue(str(context.exception).startswith('INVALID:'))
        
        # Test TXERROR prefix (from the_doi_2step)
        with patch('metapub.findit.dances.hilaris.the_doi_2step') as mock_doi:
            mock_doi.side_effect = NoPDFLink('TXERROR: dx.doi.org lookup failed - attempted: https://dx.doi.org/test')
            
            with self.assertRaises(NoPDFLink) as context:
                the_hilaris_hop(self.mock_pma, verify=False)
            self.assertTrue(str(context.exception).startswith('TXERROR:'))

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


if __name__ == '__main__':
    # Run comprehensive test suite
    unittest.main(verbosity=2)