"""Tests for IOP Publishing (Institute of Physics) dance function."""

import pytest
from unittest.mock import patch, Mock
import requests

from .common import BaseDanceTest
from metapub import PubMedFetcher
from metapub.findit.dances import the_iop_fusion
from metapub.exceptions import AccessDenied, NoPDFLink
from tests.fixtures import load_pmid_xml, IOP_EVIDENCE_PMIDS

class TestIOPDance(BaseDanceTest):
    """Test cases for IOP Publishing (Institute of Physics)."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.fetch = PubMedFetcher()

    def test_iop_fusion_url_construction_phys_med_biol(self):
        """Test 1: URL construction success (Physics in Medicine & Biology).
        
        PMID: 38914107 (Phys Med Biol)
        Expected: Should construct valid IOP PDF URL
        """
        pma = self.fetch.article_by_pmid('38914107')
        
        print(f"Test 1 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification (should always work for URL construction)
        url = the_iop_fusion(pma, verify=False)
        assert url is not None
        assert 'iopscience.iop.org' in url
        assert '/article/' in url
        assert '/pdf' in url
        assert url.startswith('https://')
        print(f"Test 1 - PDF URL: {url}")

    def test_iop_fusion_url_construction_nanotechnology(self):
        """Test 2: Nanotechnology journal.
        
        PMID: 38914053 (Nanotechnology)
        Expected: Should construct valid IOP PDF URL
        """
        pma = self.fetch.article_by_pmid('38914053')
        
        print(f"Test 2 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification
        url = the_iop_fusion(pma, verify=False)
        assert url is not None
        assert 'iopscience.iop.org' in url
        print(f"Test 2 - PDF URL: {url}")

    def test_iop_fusion_url_construction_astrophys_j(self):
        """Test 3: Astrophysical Journal.
        
        PMID: 38799617 (Astrophys J)
        Expected: Should construct valid IOP PDF URL
        """
        pma = self.fetch.article_by_pmid('38799617')
        
        print(f"Test 3 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification
        url = the_iop_fusion(pma, verify=False)
        assert url is not None
        assert 'iopscience.iop.org' in url
        print(f"Test 3 - PDF URL: {url}")

    # Test removed: Multiple tests - successful access, paywall detection, network error - functionality now handled by verify_pdf_url

    def test_iop_fusion_missing_doi(self):
        """Test 7: Article without DOI.
        
        Expected: Should raise NoPDFLink for missing DOI
        """
        # Create a mock PMA without DOI
        pma = Mock()
        pma.doi = None
        pma.journal = 'Phys Med Biol'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_iop_fusion(pma, verify=False)
        
        assert 'MISSING' in str(exc_info.value)
        assert 'doi needed' in str(exc_info.value)
        print(f"Test 7 - Correctly handled missing DOI: {exc_info.value}")

    # Test removed: 404 error and domain fallback testing - functionality now handled by verify_pdf_url

    def test_iop_fusion_uncommon_doi_pattern(self):
        """Test 10: Article with uncommon DOI pattern.
        
        Expected: Should handle uncommon DOI patterns but warn
        """
        # Create a mock PMA with uncommon DOI pattern
        pma = Mock()
        pma.doi = '10.1016/j.example.2023.123456'  # Non-IOP DOI
        pma.journal = 'Phys Med Biol'
        
        # Should still construct URL but may warn about pattern
        url = the_iop_fusion(pma, verify=False)
        assert url is not None
        assert 'iopscience.iop.org' in url
        print(f"Test 10 - Uncommon DOI pattern handled: {url}")    # Test removed: test_iop_journal_recognition - functionality now handled by verify_pdf_url

class TestIOPXMLFixtures:
    """Test IOP XML fixtures for evidence-driven testing."""

    def test_iop_xml_36096127_phys_med_biol(self):
        """Test PMID 36096127 - Phys Med Biol with DOI 10.1088/1361-6560/ac9174."""
        pma = load_pmid_xml('36096127')
        
        assert pma.pmid == '36096127'
        assert pma.doi == '10.1088/1361-6560/ac9174'
        assert 'Phys Med Biol' in pma.journal
        
        result = the_iop_fusion(pma, verify=False)
        # IOP constructs URLs using iopscience.iop.org
        assert result.startswith('https://iopscience.iop.org/article/')
        assert result.endswith('/pdf')
        assert '10.1088/1361-6560/ac9174' in result

    def test_iop_xml_39159658_phys_med_biol(self):
        """Test PMID 39159658 - Phys Med Biol with DOI 10.1088/1361-6560/ad70f0."""
        pma = load_pmid_xml('39159658')
        
        assert pma.pmid == '39159658'
        assert pma.doi == '10.1088/1361-6560/ad70f0'
        assert 'Phys Med Biol' in pma.journal
        
        result = the_iop_fusion(pma, verify=False)
        # IOP constructs URLs using iopscience.iop.org
        assert result.startswith('https://iopscience.iop.org/article/')
        assert result.endswith('/pdf')
        assert '10.1088/1361-6560/ad70f0' in result

    def test_iop_xml_37167981_phys_med_biol(self):
        """Test PMID 37167981 - Phys Med Biol with DOI 10.1088/1361-6560/acd48e."""
        pma = load_pmid_xml('37167981')
        
        assert pma.pmid == '37167981'
        assert pma.doi == '10.1088/1361-6560/acd48e'
        assert 'Phys Med Biol' in pma.journal
        
        result = the_iop_fusion(pma, verify=False)
        # IOP constructs URLs using iopscience.iop.org
        assert result.startswith('https://iopscience.iop.org/article/')
        assert result.endswith('/pdf')
        assert '10.1088/1361-6560/acd48e' in result