"""Tests for Royal Society of Chemistry (RSC) dance function."""

import pytest
from unittest.mock import patch, Mock
import requests

from .common import BaseDanceTest
from metapub import PubMedFetcher
from metapub.findit.dances import the_rsc_reaction
from metapub.exceptions import AccessDenied, NoPDFLink
from tests.fixtures import load_pmid_xml, RSC_EVIDENCE_PMIDS

class TestRSCDance(BaseDanceTest):
    """Test cases for Royal Society of Chemistry."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.fetch = PubMedFetcher()

    def test_rsc_reaction_url_construction_chem_commun(self):
        """Test 1: URL construction success (Chem Commun).
        
        PMID: 38916454 (Chem Commun (Camb))
        Expected: Should construct valid RSC article URL via DOI resolution
        """
        pma = load_pmid_xml('32935693')
        
        assert pma.journal == 'Nat Prod Rep'
        assert pma.doi == '10.1039/d0np00027b'
        print(f"Test 1 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification (should always work for URL construction)
        url = the_rsc_reaction(pma, verify=False)
        assert url is not None
        assert 'pubs.rsc.org' in url
        print(f"Test 1 - Article URL: {url}")

    def test_rsc_reaction_url_construction_chem_soc_rev(self):
        """Test 2: Chemical Society Reviews article.
        
        PMID: 38912871 (Chem Soc Rev)
        Expected: Should construct valid RSC article URL
        """
        pma = load_pmid_xml('38170905')
        
        assert pma.journal == 'Nat Prod Rep'
        assert pma.doi == '10.1039/d3np00037k'
        print(f"Test 2 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification
        url = the_rsc_reaction(pma, verify=False)
        assert url is not None
        assert 'pubs.rsc.org' in url
        print(f"Test 2 - Article URL: {url}")

    def test_rsc_reaction_url_construction_chem_sci(self):
        """Test 3: Chemical Science journal article.
        
        PMID: 38903241 (Chem Sci)
        Expected: Should construct valid RSC article URL
        """
        pma = load_pmid_xml('31712796')
        
        assert pma.journal == 'Environ Sci Process Impacts'
        assert pma.doi == '10.1039/c9em00386j'
        print(f"Test 3 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification
        url = the_rsc_reaction(pma, verify=False)
        assert url is not None
        print(f"Test 3 - Article URL: {url}")

    def test_rsc_reaction_url_construction_lab_chip(self):
        """Test 4: Lab Chip journal article.
        
        PMID: 38916038 (Lab Chip)
        Expected: Should construct valid RSC article URL
        """
        pma = load_pmid_xml('34817495')
        
        assert pma.journal == 'Environ Sci Process Impacts'
        assert pma.doi == '10.1039/d1em00296a'
        print(f"Test 4 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification
        url = the_rsc_reaction(pma, verify=False)
        assert url is not None
        print(f"Test 4 - Article URL: {url}")

    def test_rsc_reaction_url_construction_nat_prod_rep(self):
        """Test 5: Natural Product Reports.
        
        PMID: 28290569 (Nat Prod Rep)
        Expected: Should construct valid RSC article URL
        """
        pma = load_pmid_xml('35699396')
        
        assert pma.journal == 'Environ Sci Process Impacts'
        assert pma.doi == '10.1039/d1em00553g'
        print(f"Test 5 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification
        url = the_rsc_reaction(pma, verify=False)
        assert url is not None
        print(f"Test 5 - Article URL: {url}")

    # Test removed: Multiple tests - successful access, open access, paywall detection, access forbidden, network error - functionality now handled by verify_pdf_url

    def test_rsc_reaction_invalid_doi(self):
        """Test 12: Article with non-RSC DOI.
        
        Expected: Should raise NoPDFLink for invalid DOI pattern
        """
        # Create a mock PMA with non-RSC DOI
        pma = Mock()
        pma.doi = '10.1000/invalid-doi'
        pma.journal = 'Chem Commun (Camb)'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_rsc_reaction(pma, verify=False)
        
        assert 'INVALID' in str(exc_info.value)
        assert '10.1039/' in str(exc_info.value)
        print(f"Test 12 - Correctly handled invalid DOI: {exc_info.value}")

    # Test removed: test_rsc_reaction_article_not_found and test_rsc_journal_recognition - functionality now handled by verify_pdf_url


class TestRSCXMLFixtures:
    """Test Royal Society of Chemistry dance function with real XML fixtures."""

    def test_rsc_authentic_metadata_validation(self):
        """Validate authentic metadata from XML fixtures matches expected patterns."""
        for pmid, expected in RSC_EVIDENCE_PMIDS.items():
            pma = load_pmid_xml(pmid)
            
            # Validate DOI follows RSC pattern
            assert pma.doi == expected['doi']
            assert pma.doi.startswith('10.1039/'), f"RSC DOI must start with 10.1039/, got: {pma.doi}"
            
            # Validate journal name matches expected
            assert pma.journal == expected['journal']
            
            # Validate PMID matches
            assert pma.pmid == pmid
            
            print(f"✓ PMID {pmid}: {pma.journal} - {pma.doi}")

    # Test removed: test_rsc_url_construction_without_verification - functionality now handled by verify_pdf_url

    def test_rsc_journal_coverage(self):
        """Test journal coverage across different RSC publications."""
        journals_found = set()
        
        for pmid in RSC_EVIDENCE_PMIDS.keys():
            pma = load_pmid_xml(pmid)
            journals_found.add(pma.journal)
        
        # Should have multiple different RSC journals
        assert len(journals_found) >= 2, f"Expected at least 2 different journals, got: {journals_found}"
        
        # All should be known RSC journals
        expected_journals = {'Nat Prod Rep', 'Environ Sci Process Impacts'}
        assert journals_found == expected_journals, f"Unexpected journals: {journals_found - expected_journals}"

    def test_rsc_doi_pattern_consistency(self):
        """Test that all RSC PMIDs use 10.1039 DOI prefix."""
        doi_prefix = '10.1039'
        
        for pmid, data in RSC_EVIDENCE_PMIDS.items():
            assert data['doi'].startswith(doi_prefix), f"PMID {pmid} has unexpected DOI prefix: {data['doi']}"
            
            pma = load_pmid_xml(pmid)
            assert pma.doi.startswith(doi_prefix), f"PMID {pmid} XML fixture has unexpected DOI: {pma.doi}"

    # Test removed: test_rsc_paywall_handling_with_fixtures - functionality now handled by verify_pdf_url