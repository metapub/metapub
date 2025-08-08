"""
Evidence-based tests for APA (American Psychological Association) using XML fixtures.

Following TRANSITION_TESTS_TO_REAL_DATA.md - using XML fixtures instead of mocking.

Based on verified PMIDs showing APA DOI pattern (10.1037/) and psycnet.apa.org URLs.
APA uses subscription-based access model with paywall detection.
"""

import pytest
from unittest.mock import patch, Mock
try:
    from .common import BaseDanceTest
except ImportError:
    # For direct execution
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from tests.findit.common import BaseDanceTest

from metapub.findit.dances.apa import the_apa_dab
from metapub.exceptions import NoPDFLink, AccessDenied
from tests.fixtures import load_pmid_xml, APA_EVIDENCE_PMIDS


class MockResponse:
    """Mock HTTP response for testing."""
    def __init__(self, status_code=200, content_type='application/pdf', text=''):
        self.status_code = status_code
        self.headers = {'content-type': content_type}
        self.text = text
        self.content = text.encode() if isinstance(text, str) else text


class TestAPAXMLFixtures(BaseDanceTest):
    """Evidence-based test cases for APA using XML fixtures."""

    def setUp(self):
        """Set up test fixtures.""" 
        super().setUp()

    def test_apa_xml_fixtures_metadata_validation(self):
        """Test 1: Validate authentic metadata from XML fixtures."""
        for pmid, expected_data in APA_EVIDENCE_PMIDS.items():
            # Load real article data from XML fixture
            pma = load_pmid_xml(pmid)
            
            # Verify authentic metadata matches expectations
            assert pma.pmid == pmid, f"PMID mismatch: {pma.pmid} != {pmid}"
            assert pma.doi == expected_data['doi'], f"DOI mismatch for {pmid}: {pma.doi} != {expected_data['doi']}"
            assert expected_data['journal'] in pma.journal, f"Journal mismatch for {pmid}: {expected_data['journal']} not in {pma.journal}"
            
            # TRUST THE REGISTRY: No DOI pattern validation needed
            
            print(f"✓ Real PMID {pmid} - {expected_data['journal']}: {pma.doi}")
        
        print(f"✅ All {len(APA_EVIDENCE_PMIDS)} XML fixtures validated")

    @patch('metapub.findit.dances.apa.verify_pdf_url')
    def test_apa_url_construction_with_xml_fixtures(self, mock_verify):
        """Test 2: URL construction using real PMIDs with successful PDF access."""
        # Mock successful PDF verification
        mock_verify.return_value = True
        
        for pmid, expected_data in APA_EVIDENCE_PMIDS.items():
            # Load real article data from XML fixture
            pma = load_pmid_xml(pmid)
            
            # Test URL construction
            result = the_apa_dab(pma, verify=True)
            
            # Verify URL pattern
            expected_url = f"https://psycnet.apa.org/fulltext/{pma.doi}.pdf"
            assert result == expected_url, f"URL mismatch for {pmid}: {result} != {expected_url}"
            
            # Verify URL components
            assert 'https://psycnet.apa.org/fulltext/' in result
            assert pma.doi in result
            assert result.endswith('.pdf')
            
            print(f"✓ PMID {pmid} URL: {result}")
        
        print(f"✅ All {len(APA_EVIDENCE_PMIDS)} URLs constructed successfully")

    @patch('metapub.findit.dances.apa.verify_pdf_url')
    def test_apa_paywall_detection_with_xml_fixtures(self, mock_verify):
        """Test 3: Paywall detection using real PMIDs."""
        # Mock failed PDF verification (indicates paywall)
        mock_verify.return_value = False
        
        # Test with first PMID
        pmid = list(APA_EVIDENCE_PMIDS.keys())[0]
        pma = load_pmid_xml(pmid)
        
        with pytest.raises(AccessDenied) as exc_info:
            the_apa_dab(pma, verify=True)
        
        error_msg = str(exc_info.value)
        assert 'PAYWALL' in error_msg
        assert 'psycnet.apa.org' in error_msg
        
        print(f"✓ Paywall detection working for PMID {pmid}: {error_msg}")

    def test_apa_missing_doi_error_with_xml_fixtures(self):
        """Test 4: Missing DOI error handling."""
        # Load real article and remove DOI
        pmid = list(APA_EVIDENCE_PMIDS.keys())[0]
        pma = load_pmid_xml(pmid)
        pma.doi = None  # Simulate missing DOI
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_apa_dab(pma)
        
        error_msg = str(exc_info.value)
        assert 'MISSING: DOI required' in error_msg
        
        print(f"✓ Missing DOI error: {error_msg}")

    def test_apa_trust_registry_no_doi_validation(self):
        """Test 5: TRUST THE REGISTRY - no DOI validation needed."""
        # Load real article and modify DOI to non-APA pattern
        pmid = list(APA_EVIDENCE_PMIDS.keys())[0]
        pma = load_pmid_xml(pmid)
        pma.doi = '10.1016/non.apa.doi'  # Non-APA DOI
        
        # Should construct URL regardless of DOI pattern (TRUST THE REGISTRY)
        result = the_apa_dab(pma, verify=False)
        expected_url = f"https://psycnet.apa.org/fulltext/{pma.doi}.pdf"
        assert result == expected_url
        
        print(f"✓ TRUST THE REGISTRY - DOI pattern ignored: {result}")

    def test_apa_verify_false_skips_verification_with_xml_fixtures(self):
        """Test 6: verify=False skips HTTP verification."""
        for pmid, expected_data in APA_EVIDENCE_PMIDS.items():
            # Load real article data from XML fixture
            pma = load_pmid_xml(pmid)
            
            # Test without verification (should always work)
            result = the_apa_dab(pma, verify=False)
            
            # Verify URL construction
            expected_url = f"https://psycnet.apa.org/fulltext/{pma.doi}.pdf"
            assert result == expected_url
            
            print(f"✓ No verification PMID {pmid}: {result}")
        
        print(f"✅ All {len(APA_EVIDENCE_PMIDS)} URLs constructed without verification")

    @patch('metapub.findit.dances.apa.verify_pdf_url')
    def test_apa_404_error_handling_with_xml_fixtures(self, mock_verify):
        """Test 7: 404/Access error handling."""
        # Mock failed PDF verification (could be 404, access denied, etc.)
        mock_verify.return_value = False
        
        # Test with first PMID
        pmid = list(APA_EVIDENCE_PMIDS.keys())[0]
        pma = load_pmid_xml(pmid)
        
        with pytest.raises(AccessDenied) as exc_info:
            the_apa_dab(pma, verify=True)
        
        error_msg = str(exc_info.value)
        assert 'PAYWALL' in error_msg
        assert 'subscription' in error_msg.lower()
        
        print(f"✓ Access error handling for PMID {pmid}: {error_msg}")

    def test_apa_journal_coverage_with_xml_fixtures(self):
        """Test 8: Journal coverage across different APA publications."""
        journal_coverage = {}
        
        for pmid, expected_data in APA_EVIDENCE_PMIDS.items():
            pma = load_pmid_xml(pmid)
            
            # Track journal coverage
            journal = expected_data['journal']
            if journal not in journal_coverage:
                journal_coverage[journal] = []
            journal_coverage[journal].append(pmid)
            
            # Verify journal title consistency
            assert journal in pma.journal, f"Journal mismatch: {journal} not in {pma.journal}"
            
            # Note: DOI patterns observed but not validated per TRUST THE REGISTRY
            print(f"✓ {journal} PMID {pmid}: DOI={pma.doi}")
        
        # Report coverage
        for journal, pmids in journal_coverage.items():
            print(f"✓ {journal}: {len(pmids)} PMIDs - {pmids}")
        
        print(f"✅ Coverage: {len(journal_coverage)} different APA journals")

    def test_apa_authentic_data_consistency(self):
        """Test 9: Verify consistency between expected and authentic data."""
        for pmid, expected_data in APA_EVIDENCE_PMIDS.items():
            pma = load_pmid_xml(pmid)
            
            # Compare DOI
            assert pma.doi == expected_data['doi'], \
                f"DOI inconsistency for {pmid}: expected {expected_data['doi']}, got {pma.doi}"
            
            # Compare journal (flexible matching)
            expected_journal = expected_data['journal']
            actual_journal = pma.journal
            
            # Handle journal name variations
            assert expected_journal in actual_journal or actual_journal in expected_journal, \
                f"Journal inconsistency for {pmid}: expected '{expected_journal}', got '{actual_journal}'"
            
            print(f"✓ Consistency check PMID {pmid}: DOI={pma.doi}, Journal={actual_journal}")
        
        print(f"✅ All {len(APA_EVIDENCE_PMIDS)} PMIDs show consistent authentic data")


if __name__ == '__main__':
    # Run basic tests if executed directly
    test_instance = TestAPAXMLFixtures()
    test_instance.setUp()
    
    print("Running APA XML fixtures tests...")
    print("\n" + "="*60)
    
    tests = [
        ('test_apa_xml_fixtures_metadata_validation', 'XML fixtures metadata validation'),
        ('test_apa_url_construction_with_xml_fixtures', 'URL construction with XML fixtures'),
        ('test_apa_paywall_detection_with_xml_fixtures', 'Paywall detection'),
        ('test_apa_missing_doi_error_with_xml_fixtures', 'Missing DOI error handling'),
        ('test_apa_trust_registry_no_doi_validation', 'TRUST THE REGISTRY validation'),
        ('test_apa_verify_false_skips_verification_with_xml_fixtures', 'Skip verification mode'),
        ('test_apa_404_error_handling_with_xml_fixtures', 'Access error handling'),
        ('test_apa_journal_coverage_with_xml_fixtures', 'Journal coverage'),
        ('test_apa_authentic_data_consistency', 'Authentic data consistency')
    ]
    
    for test_method, description in tests:
        try:
            getattr(test_instance, test_method)()
            print(f"✓ {description}")
        except Exception as e:
            print(f"✗ {description}: {e}")
    
    print("\n" + "="*60)
    print("APA XML fixtures test suite completed!")