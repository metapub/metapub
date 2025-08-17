"""Tests for ASME (American Society of Mechanical Engineers) dance function."""

import pytest
from unittest.mock import patch, Mock
import requests

from .common import BaseDanceTest
from metapub import PubMedFetcher
from metapub.findit.dances import the_asme_animal
from metapub.exceptions import AccessDenied, NoPDFLink
from tests.fixtures import load_pmid_xml, ASME_EVIDENCE_PMIDS

class TestASMEDance(BaseDanceTest):
    """Test cases for ASME (American Society of Mechanical Engineers)."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.fetch = PubMedFetcher()

    def test_asme_assembly_url_construction_appl_mech(self):
        """Test 1: URL construction success (J Appl Mech).
        
        PMID: 38449742 (J Appl Mech)
        Expected: Should construct valid ASME PDF URL
        """
        pma = self.fetch.article_by_pmid('38449742')
        
        print(f"Test 1 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification (should always work for URL construction)
        url = the_asme_animal(pma, verify=False)
        assert url is not None
        assert 'asmedigitalcollection.asme.org' in url
        assert url.startswith('https://')
        print(f"Test 1 - PDF URL: {url}")

    def test_asme_assembly_url_construction_biomech_eng(self):
        """Test 2: Biomechanical Engineering.
        
        PMID: 38913074 (J Biomech Eng)
        Expected: Should construct valid ASME PDF URL
        """
        pma = self.fetch.article_by_pmid('38913074')
        
        print(f"Test 2 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Skip test if no DOI available
        if not pma.doi:
            print("Test 2 - Skipping: No DOI available for this PMID")
            return

        # Test without verification
        url = the_asme_animal(pma, verify=False)
        assert url is not None
        assert 'asmedigitalcollection.asme.org' in url
        print(f"Test 2 - PDF URL: {url}")
        
    # Test removed: URL construction and journal code mapping tests - functionality now handled by verify_pdf_url

    def test_asme_assembly_doi_pattern_warning(self):
        """Test 10: Non-standard DOI pattern handling.
        
        Expected: Should handle non-10.1115 DOI patterns but may warn
        """
        # Create a mock PMA with non-ASME DOI pattern
        pma = Mock()
        pma.doi = '10.1016/j.example.2023.123456'  # Non-ASME DOI
        pma.journal = 'J Appl Mech'
        
        # Should still construct URL without verification
        url = the_asme_animal(pma, verify=False)
        assert url is not None
        assert 'asmedigitalcollection.asme.org' in url
        print(f"Test 10 - Non-standard DOI pattern handled: {url}")
        
    # Test removed: Journal recognition test - functionality now handled by verify_pdf_url

class TestASMEXMLFixtures:
    """Test ASME dance function with real XML fixtures."""

    def test_asme_authentic_metadata_validation(self):
        """Validate authentic metadata from XML fixtures matches expected patterns."""
        for pmid, expected in ASME_EVIDENCE_PMIDS.items():
            pma = load_pmid_xml(pmid)
            
            # Validate DOI follows ASME pattern (10.1115/)
            assert pma.doi == expected['doi']
            assert pma.doi.startswith('10.1115/'), f"ASME DOI must start with 10.1115/, got: {pma.doi}"
            
            # Validate journal name matches expected
            assert pma.journal == expected['journal']
            
            # Validate PMID matches
            assert pma.pmid == pmid
            
            print(f"✓ PMID {pmid}: {pma.journal} - {pma.doi}")

    def test_asme_url_construction_without_verification(self):
        """Test URL construction without verification using XML fixtures."""
        for pmid in ASME_EVIDENCE_PMIDS.keys():
            pma = load_pmid_xml(pmid)
            
            # Test URL construction without verification
            result = the_asme_animal(pma, verify=False)
            
            # Should be ASME URL pattern
            assert result is not None
            assert 'asmedigitalcollection.asme.org' in result
            assert result.startswith('https://')
            
            print(f"✓ PMID {pmid} URL: {result}")    # Test removed: test_asme_url_construction_with_mocked_verification - functionality now handled by verify_pdf_url

    def test_asme_journal_coverage(self):
        """Test journal coverage across different ASME publications."""
        journals_found = set()
        
        for pmid in ASME_EVIDENCE_PMIDS.keys():
            pma = load_pmid_xml(pmid)
            journals_found.add(pma.journal)
        
        # Should have multiple different ASME journals
        assert len(journals_found) >= 3, f"Expected at least 3 different journals, got: {journals_found}"
        
        # All should be known ASME journals
        expected_journals = {'J Appl Mech', 'J Biomech Eng', 'J Heat Transfer'}
        assert journals_found == expected_journals, f"Unexpected journals: {journals_found - expected_journals}"

    def test_asme_doi_pattern_consistency(self):
        """Test that all ASME PMIDs use 10.1115 DOI prefix."""
        doi_prefix = '10.1115'
        
        for pmid, data in ASME_EVIDENCE_PMIDS.items():
            assert data['doi'].startswith(doi_prefix), f"PMID {pmid} has unexpected DOI prefix: {data['doi']}"
            
            pma = load_pmid_xml(pmid)
            assert pma.doi.startswith(doi_prefix), f"PMID {pmid} XML fixture has unexpected DOI: {pma.doi}"

    def test_asme_template_flexibility(self):
        """Test template flexibility for ASME URL patterns."""
        pma = load_pmid_xml('38449742')  # J Appl Mech
        
        # Test URL construction 
        result = the_asme_animal(pma, verify=False)
        
        # Should follow ASME URL pattern (may be CrossRef or direct URL)
        assert result is not None
        assert 'asmedigitalcollection.asme.org' in result
        assert result.startswith('https://')
        # Note: DOI may not be directly in URL if CrossRef returns alternative URL

    def test_asme_pmc_availability(self):
        """Test coverage of PMC-available ASME articles."""
        # All our test articles have PMC IDs
        for pmid, expected in ASME_EVIDENCE_PMIDS.items():
            pma = load_pmid_xml(pmid)
            
            assert 'pmc' in expected, f"PMID {pmid} should have PMC ID"
            
            # Test URL construction still works even with PMC availability
            result = the_asme_animal(pma, verify=False)
            assert result is not None
            assert 'asmedigitalcollection.asme.org' in result
            
            print(f"✓ PMID {pmid} (PMC: {expected['pmc']}) works with ASME infrastructure: {result}")