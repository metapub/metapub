"""Tests for DovePress (Dove Medical Press) dance function."""

import pytest
from unittest.mock import patch, Mock
import requests

from .common import BaseDanceTest
from metapub import PubMedFetcher
from metapub.findit.dances import the_dovepress_peacock
from metapub.exceptions import AccessDenied, NoPDFLink
from tests.fixtures import load_pmid_xml, DOVEPRESS_EVIDENCE_PMIDS

class TestDovePressTest(BaseDanceTest):
    """Test cases for DovePress (Dove Medical Press)."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.fetch = PubMedFetcher()

    def test_dovepress_waltz_ijin_article(self):
        """Test 1: URL construction success (International Journal of Nanomedicine).
        
        PMID: 37693885 (Int J Nanomedicine)
        Expected: Should construct valid DovePress PDF URL
        """
        pma = self.fetch.article_by_pmid('37693885')
        
        assert pma.journal == 'Int J Nanomedicine'
        assert pma.doi == '10.2147/IJN.S420748'
        print(f"Test 1 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification (should always work for URL construction)
        url = the_dovepress_peacock(pma, verify=False)
        assert url is not None
        assert 'dovepress.com' in url
        assert '/article/download/' in url
        assert url.startswith('https://')
        print(f"Test 1 - PDF URL: {url}")

    def test_dovepress_waltz_opth_article(self):
        """Test 2: Clinical Ophthalmology article.
        
        PMID: 37736107 (Clin Ophthalmol)
        Expected: Should construct valid DovePress PDF URL
        """
        pma = self.fetch.article_by_pmid('37736107')
        
        assert pma.journal == 'Clin Ophthalmol'
        assert pma.doi == '10.2147/OPTH.S392665'
        print(f"Test 2 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification
        url = the_dovepress_peacock(pma, verify=False)
        assert url is not None
        assert 'dovepress.com' in url
        assert '/article/download/' in url
        print(f"Test 2 - PDF URL: {url}")

    def test_dovepress_waltz_cmar_article(self):
        """Test 3: Cancer Management and Research article.
        
        PMID: 36873252 (Cancer Manag Res)
        Expected: Should construct valid DovePress PDF URL
        """
        pma = self.fetch.article_by_pmid('36873252')
        
        assert pma.journal == 'Cancer Manag Res'
        assert pma.doi == '10.2147/CMAR.S400013'
        print(f"Test 3 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification
        url = the_dovepress_peacock(pma, verify=False)
        assert url is not None
        assert 'dovepress.com' in url
        assert '/article/download/' in url
        print(f"Test 3 - PDF URL: {url}")

    # Test removed: Multiple tests - successful PDF access, paywall detection, network error, article not found, HTML parsing error, no PDF link found, journal recognition - functionality now handled by verify_pdf_url


class TestDovepressXMLFixtures:
    """Test Dovepress XML fixtures for evidence-driven testing."""

    @patch('metapub.findit.dances.dovepress.verify_pdf_url')
    def test_dovepress_xml_37822558_adolesc_health_med_ther(self, mock_verify):
        """Test PMID 37822558 - Adolesc Health Med Ther with DOI 10.2147/AHMT.S429238."""
        mock_verify.return_value = None
        pma = load_pmid_xml('37822558')
        
        assert pma.pmid == '37822558'
        assert pma.doi == '10.2147/AHMT.S429238'
        assert 'Adolesc Health Med Ther' in pma.journal
        
        result = the_dovepress_peacock(pma, verify=True)
        expected_url = 'https://www.dovepress.com/article/download/87183'
        assert result == expected_url
        mock_verify.assert_called_once_with(expected_url, 'DovePress', request_timeout=10, max_redirects=3)

    @patch('metapub.findit.dances.dovepress.verify_pdf_url')
    def test_dovepress_xml_35592492_adolesc_health_med_ther(self, mock_verify):
        """Test PMID 35592492 - Adolesc Health Med Ther with DOI 10.2147/AHMT.S358140."""
        mock_verify.return_value = None
        pma = load_pmid_xml('35592492')
        
        assert pma.pmid == '35592492'
        assert pma.doi == '10.2147/AHMT.S358140'
        assert 'Adolesc Health Med Ther' in pma.journal
        
        result = the_dovepress_peacock(pma, verify=True)
        expected_url = 'https://www.dovepress.com/article/download/75287'
        assert result == expected_url
        mock_verify.assert_called_once_with(expected_url, 'DovePress', request_timeout=10, max_redirects=3)