"""Tests for Cambridge University Press dance function."""

from .common import BaseDanceTest
from metapub import FindIt
from tests.fixtures import load_pmid_xml, CAMBRIDGE_EVIDENCE_PMIDS


class TestCambridgeDance(BaseDanceTest):
    """Test cases for Cambridge University Press."""

    def test_cambridge_foxtrot(self):
        """Test Cambridge University Press dance function across different eras."""
        # Test PMIDs from different decades to ensure Cambridge dance works across time periods
        
        # 1990s era - Journal of Mental Science  
        pmid_1990s = '14021516'  # 1992 - DOI: 10.1192/bjp.108.457.811
        source = FindIt(pmid=pmid_1990s)
        # Cambridge journals should either get PDF URL or fall back to PMC
        self.assertUrlOrReason(source)
        
        # 2010s era - Trans R Hist Soc  
        pmid_2010s = '26633910'  # 2015 - DOI: 10.1017/S008044011500002X
        source = FindIt(pmid=pmid_2010s)
        self.assertUrlOrReason(source)
        
        # 2020s era - Philosophy
        pmid_2020s = '38481934'  # 2023 - DOI: 10.1017/S0031819123000049
        source = FindIt(pmid=pmid_2020s)
        self.assertUrlOrReason(source)


class TestCambridgeXMLFixtures:
    """Test Cambridge University Press with real XML fixtures."""

    def test_cambridge_authentic_metadata_validation(self):
        """Validate authentic metadata from XML fixtures matches expected patterns."""
        for pmid, expected in CAMBRIDGE_EVIDENCE_PMIDS.items():
            pma = load_pmid_xml(pmid)
            assert pma.doi == expected['doi']
            assert pma.journal == expected['journal']
            assert pma.pmid == pmid
            print(f"✓ PMID {pmid}: {pma.journal} - {pma.doi}")

    def test_cambridge_doi_pattern_consistency(self):
        """Test Cambridge DOI patterns (10.1017/)."""
        for pmid, data in CAMBRIDGE_EVIDENCE_PMIDS.items():
            pma = load_pmid_xml(pmid)
            assert pma.doi.startswith('10.1017/'), f"Cambridge DOI must start with 10.1017/, got: {pma.doi}"
            print(f"✓ PMID {pmid} DOI pattern: {pma.doi}")