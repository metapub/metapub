"""
Tests for the_sage_hula dance function (SAGE Publications).

Tests cover three different scenarios:
1. SAGE paywall access (should raise AccessDenied)
2. PMC availability (FindIt should prefer PMC over SAGE paywall)
3. Missing DOI (should raise NoPDFLink)
"""

import unittest
import pytest
import os
from unittest.mock import Mock, patch

from metapub import FindIt, PubMedFetcher
from metapub.findit.dances import the_sage_hula
from metapub.exceptions import AccessDenied, NoPDFLink


class TestSageHula(unittest.TestCase):
    """Test the_sage_hula dance function for SAGE Publications."""

    def setUp(self):
        """Set up test fixtures."""
        self.fetcher = PubMedFetcher()

    @pytest.mark.skipif(os.getenv('SKIP_NETWORK_TESTS'), reason="Network tests disabled")
    def test_sage_paywall_access_denied(self):
        """Test SAGE journal behind paywall (should raise AccessDenied)."""
        # PMID 22295291 - South Asia Research - typical paywalled SAGE article
        pmid = "22295291"
        pma = self.fetcher.article_by_pmid(pmid)
        
        # Verify this is a SAGE journal with DOI
        self.assertEqual(pma.journal, "South Asia Res")
        self.assertTrue(pma.doi.startswith("10.1177/"))
        
        # the_sage_hula should detect paywall and raise AccessDenied
        with self.assertRaises(AccessDenied) as context:
            the_sage_hula(pma, verify=True)
        
        # Should contain SAGE-specific error message
        error_msg = str(context.exception)
        self.assertIn("SAGE", error_msg)
        self.assertTrue(
            "Access forbidden" in error_msg or "DENIED" in error_msg,
            f"Expected access denial message, got: {error_msg}"
        )

    @pytest.mark.skipif(os.getenv('SKIP_NETWORK_TESTS'), reason="Network tests disabled") 
    def test_sage_with_pmc_availability(self):
        """Test SAGE journal available in PMC (FindIt should prefer PMC)."""
        # PMID 30369646 - Urban Studies - available in both SAGE and PMC
        pmid = "30369646"
        
        # Test full FindIt flow (should prefer PMC over SAGE paywall)
        finder = FindIt(pmid=pmid)
        
        # Verify journal info
        self.assertEqual(finder.pma.journal, "Urban Stud")
        self.assertTrue(finder.pma.doi.startswith("10.1177/"))
        
        # FindIt should find PMC URL instead of hitting SAGE paywall
        self.assertIsNotNone(finder.url)
        self.assertIn("europepmc.org", finder.url)
        self.assertIn("pdf", finder.url.lower())
        
        # But the_sage_hula directly should still raise AccessDenied
        with self.assertRaises(AccessDenied):
            the_sage_hula(finder.pma, verify=True)

    def test_sage_missing_doi(self):
        """Test SAGE journal without DOI (should raise NoPDFLink)."""
        # Create mock PMA without DOI
        mock_pma = Mock()
        mock_pma.doi = None
        mock_pma.journal = "Test SAGE Journal"
        
        # Should raise NoPDFLink for missing DOI
        with self.assertRaises(NoPDFLink) as context:
            the_sage_hula(mock_pma, verify=True)
        
        error_msg = str(context.exception)
        self.assertIn("DOI required", error_msg)
        self.assertIn("SAGE", error_msg)

    def test_sage_url_construction_no_verify(self):
        """Test SAGE URL construction without verification."""
        # Create mock PMA with SAGE DOI
        mock_pma = Mock()
        mock_pma.doi = "10.1177/1234567890123456"
        mock_pma.journal = "Test SAGE Journal"
        
        # Should construct correct SAGE PDF URL without verification
        url = the_sage_hula(mock_pma, verify=False)
        
        expected_url = "https://journals.sagepub.com/doi/pdf/10.1177/1234567890123456"
        self.assertEqual(url, expected_url)

    @pytest.mark.skipif(os.getenv('SKIP_NETWORK_TESTS'), reason="Network tests disabled")
    def test_sage_integration_with_registry(self):
        """Test that SAGE journals are properly handled through registry system."""
        # Test different SAGE journals to ensure registry integration
        test_cases = [
            ("22295291", "South Asia Res"),      # Political science journal
            ("38863277", "Med Sci Law"),         # Medical-legal journal  
            ("37972566", "Sex Abuse"),           # Psychology journal
        ]
        
        for pmid, expected_journal in test_cases:
            with self.subTest(pmid=pmid, journal=expected_journal):
                finder = FindIt(pmid=pmid)
                
                # Verify journal identification
                self.assertEqual(finder.pma.journal, expected_journal)
                self.assertTrue(finder.pma.doi.startswith("10.1177/"))
                
                # Should either get PMC URL or SAGE access denial
                if finder.url:
                    # If URL found, should be PMC (not SAGE paywall)
                    self.assertIn("europepmc.org", finder.url)
                else:
                    # If no URL, should be SAGE access denial
                    self.assertIsNotNone(finder.reason)
                    self.assertIn("SAGE", finder.reason)
                    self.assertTrue(
                        "Access forbidden" in finder.reason or "DENIED" in finder.reason
                    )

    def test_sage_network_error_handling(self):
        """Test network error handling in the_sage_hula."""
        import requests
        
        mock_pma = Mock()
        mock_pma.doi = "10.1177/1234567890123456"
        mock_pma.journal = "Test Journal"
        
        # Use a proper requests exception that will be caught
        with patch('metapub.findit.dances.requests.get', side_effect=requests.exceptions.Timeout("Network timeout")):
            with self.assertRaises(NoPDFLink) as context:
                the_sage_hula(mock_pma, verify=True)
            
            error_msg = str(context.exception)
            self.assertIn("TXERROR", error_msg)
            self.assertIn("Network timeout", error_msg)

    def test_sage_404_handling(self):
        """Test 404 response handling in the_sage_hula."""
        # Mock 404 response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.headers = {'content-type': 'text/html'}
        
        mock_pma = Mock()
        mock_pma.doi = "10.1177/1234567890123456"
        mock_pma.journal = "Test Journal"
        
        with patch('metapub.findit.dances.requests.get', return_value=mock_response):
            with self.assertRaises(NoPDFLink) as context:
                the_sage_hula(mock_pma, verify=True)
            
            error_msg = str(context.exception)
            self.assertIn("NOTFOUND", error_msg)
            self.assertIn("not found", error_msg.lower())


class TestSageHulaIntegration(unittest.TestCase):
    """Integration tests for SAGE journals in FindIt system."""

    @pytest.mark.skipif(os.getenv('SKIP_NETWORK_TESTS'), reason="Network tests disabled")
    def test_sage_registry_coverage(self):
        """Test that SAGE journals are properly registered."""
        from metapub.findit.registry import JournalRegistry
        
        registry = JournalRegistry()
        
        # Test some known SAGE journals
        sage_journals = [
            "South Asia Res",
            "Med Sci Law", 
            "Sex Abuse",
            "Urban Stud",
            "Med Decis Making"
        ]
        
        for journal in sage_journals:
            with self.subTest(journal=journal):
                publisher_data = registry.get_publisher_for_journal(journal)
                
                self.assertIsNotNone(publisher_data, f"Journal '{journal}' not found in registry")
                self.assertEqual(publisher_data['name'], "SAGE Publications")
                self.assertEqual(publisher_data['dance_function'], "the_sage_hula")
                self.assertEqual(publisher_data['base_url'], "https://journals.sagepub.com")
        
        registry.close()

    @pytest.mark.skipif(os.getenv('SKIP_NETWORK_TESTS'), reason="Network tests disabled")
    def test_no_noformat_errors_for_sage(self):
        """Test that SAGE journals no longer return NOFORMAT errors."""
        # Test a variety of SAGE PMIDs
        sage_pmids = ["22295291", "38863277", "37972566", "30369646", "38827578"]
        
        for pmid in sage_pmids:
            with self.subTest(pmid=pmid):
                finder = FindIt(pmid=pmid)
                
                # Should never get NOFORMAT for SAGE journals
                if finder.reason:
                    self.assertNotIn("NOFORMAT", finder.reason, 
                                   f"PMID {pmid} still returning NOFORMAT")
                
                # Should either get URL or SAGE-specific error
                if not finder.url:
                    self.assertTrue(
                        "SAGE" in finder.reason or "DENIED" in finder.reason,
                        f"PMID {pmid} returned unexpected reason: {finder.reason}"
                    )


if __name__ == '__main__':
    unittest.main()