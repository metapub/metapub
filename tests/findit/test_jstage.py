"""Tests for J-STAGE (Japan Science and Technology Information Aggregator, Electronic) dance function."""

from .common import BaseDanceTest
from metapub import FindIt
from tests.fixtures import load_pmid_xml, JSTAGE_EVIDENCE_PMIDS
from metapub.findit.dances.generic import the_doi_slide
from metapub.exceptions import NoPDFLink, AccessDenied
import pytest
from unittest.mock import patch


class TestJStageDance(BaseDanceTest):
    """Test cases for J-STAGE journals."""

    def test_jstage_dive(self):
        """Test Jstage dive function with expanded journal coverage."""
        # Test with a known working Jstage journal from our expansion
        pmid = '31902831'  # Okajimas Folia Anat Jpn - confirmed working
        source = FindIt(pmid=pmid)
        assert source.pma.journal == 'Okajimas Folia Anat Jpn'
        assert source.pma.doi == '10.2535/ofaj.96.49'
        # Should get Jstage URL via the_jstage_dive function
        assert source.url is not None
        assert 'jstage.jst.go.jp' in source.url
        assert source.url.endswith('_pdf')

    def test_jstage_expansion_coverage(self):
        """Test Jstage expansion with multiple Japanese journals."""
        # Test different types of Japanese journals from our expansion
        jstage_test_cases = [
            ('19037164', 'Nihon Hotetsu Shika Gakkai Zasshi'),  # Japanese dental journal
            ('1363467', 'Endocrinol Jpn'),                      # Japanese endocrinology
        ]
        
        for pmid, expected_journal in jstage_test_cases:
            source = FindIt(pmid=pmid)
            assert source.pma.journal == expected_journal
            # Should either get Jstage URL or proper reason (never NOFORMAT)
            if source.reason:
                assert 'NOFORMAT' not in source.reason
            if source.url:
                assert 'jstage.jst.go.jp' in source.url


class TestJSTAGEXMLFixtures:
    """Test J-STAGE dance function with real XML fixtures."""

    def test_jstage_authentic_metadata_validation(self):
        """Validate authentic metadata from XML fixtures."""
        for pmid, expected in JSTAGE_EVIDENCE_PMIDS.items():
            pma = load_pmid_xml(pmid)
            
            assert pma.doi == expected['doi']
            assert pma.journal == expected['journal']
            assert pma.pmid == pmid
            
            print(f"✓ PMID {pmid}: {pma.journal} - {pma.doi}")

    def test_jstage_url_construction_without_verification(self):
        """Test URL construction using XML fixtures."""
        for pmid in JSTAGE_EVIDENCE_PMIDS.keys():
            pma = load_pmid_xml(pmid)
            
            result = the_doi_slide(pma, verify=False)
            
            # Should be J-STAGE URL pattern
            assert 'jstage.jst.go.jp' in result
            assert pma.doi in result
            
            print(f"✓ PMID {pmid} URL: {result}")

    @patch('metapub.findit.dances.generic.verify_pdf_url')
    def test_jstage_paywall_handling(self, mock_verify):
        """Test paywall detection."""
        mock_verify.side_effect = AccessDenied('J-STAGE subscription required')
        
        pma = load_pmid_xml('31588070')  # Use first test PMID
        
        with pytest.raises(AccessDenied):
            the_doi_slide(pma, verify=True)

    def test_jstage_journal_coverage(self):
        """Test journal coverage across different J-STAGE publications."""
        journals_found = set()
        
        for pmid in JSTAGE_EVIDENCE_PMIDS.keys():
            pma = load_pmid_xml(pmid)
            journals_found.add(pma.journal)
        
        assert len(journals_found) >= 2
        print(f"✅ Coverage: {len(journals_found)} different J-STAGE journals")

    def test_jstage_doi_pattern_consistency(self):
        """Test J-STAGE DOI patterns."""
        for pmid, data in JSTAGE_EVIDENCE_PMIDS.items():
            # J-STAGE uses various DOI patterns like 10.5761/, 10.33160/
            assert '10.' in data['doi'], f"PMID {pmid} has invalid DOI: {data['doi']}"
            
            pma = load_pmid_xml(pmid)
            assert pma.doi == data['doi']