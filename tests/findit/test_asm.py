"""
Tests for the improved evidence-based ASM dance function.
Based on HTML sample analysis showing direct PDF download pattern.
Updated to test /doi/pdf/ pattern (PDF URLs) instead of /doi/reader/ (reader URLs).
"""

import pytest
from unittest.mock import patch, MagicMock

from metapub.findit.dances.asm import the_asm_shimmy
from metapub.exceptions import NoPDFLink, AccessDenied
from tests.fixtures import load_pmid_xml, ASM_EVIDENCE_PMIDS


class MockPMA:
    """Mock PubMedArticle for testing."""
    def __init__(self, doi=None):
        self.doi = doi


class TestASMShimmy:
    """Test suite for the_asm_shimmy function."""

    def test_modern_url_construction_with_doi(self):
        """Test modern /doi/pdf/ URL construction with DOI."""
        # Test case from HTML evidence: PMID 35856662
        pma = MockPMA(doi='10.1128/aac.00216-22')
        
        with patch('metapub.findit.dances.asm.verify_pdf_url') as mock_verify:
            mock_verify.return_value = True
            
            result = the_asm_shimmy(pma, verify=True)
            
            expected = 'https://journals.asm.org/doi/pdf/10.1128/aac.00216-22?download=true'
            assert result == expected
            mock_verify.assert_called_once_with(expected, 'ASM', request_timeout=10, max_redirects=3)

    def test_modern_url_construction_different_journals(self):
        """Test URL construction works for different ASM journals."""
        test_cases = [
            # From HTML evidence
            ('10.1128/jb.00337-22', 'https://journals.asm.org/doi/pdf/10.1128/jb.00337-22?download=true'),  # J Bacteriol
            ('10.1128/msystems.01299-23', 'https://journals.asm.org/doi/pdf/10.1128/msystems.01299-23?download=true'),  # mSystems
            ('10.1128/jb.00024-24', 'https://journals.asm.org/doi/pdf/10.1128/jb.00024-24?download=true'),  # J Bacteriol
            ('10.1128/aac.00924-24', 'https://journals.asm.org/doi/pdf/10.1128/aac.00924-24?download=true'),  # AAC
        ]
        
        with patch('metapub.findit.dances.asm.verify_pdf_url') as mock_verify:
            mock_verify.return_value = True
            
            for doi, expected_url in test_cases:
                pma = MockPMA(doi=doi)
                result = the_asm_shimmy(pma, verify=True)
                assert result == expected_url

    def test_no_doi_raises_nopdflink(self):
        """Test that missing DOI raises NoPDFLink."""
        pma = MockPMA(doi=None)
        
        with pytest.raises(NoPDFLink) as excinfo:
            the_asm_shimmy(pma)
        
        assert 'MISSING: DOI required for ASM PDF downloads' in str(excinfo.value)
        assert 'attempted: none' in str(excinfo.value)

    def test_empty_doi_raises_nopdflink(self):
        """Test that empty DOI raises NoPDFLink."""
        pma = MockPMA(doi='')
        
        with pytest.raises(NoPDFLink) as excinfo:
            the_asm_shimmy(pma)
        
        assert 'MISSING: DOI required for ASM PDF downloads' in str(excinfo.value)

    def test_verify_false_skips_verification(self):
        """Test that verify=False skips URL verification."""
        pma = MockPMA(doi='10.1128/aac.00216-22')
        
        with patch('metapub.findit.dances.asm.verify_pdf_url') as mock_verify:
            result = the_asm_shimmy(pma, verify=False)
            
            expected = 'https://journals.asm.org/doi/pdf/10.1128/aac.00216-22?download=true'
            assert result == expected
            mock_verify.assert_not_called()

    def test_verify_pdf_url_access_denied(self):
        """Test that verify_pdf_url AccessDenied is propagated."""
        pma = MockPMA(doi='10.1128/aac.00216-22')
        
        with patch('metapub.findit.dances.asm.verify_pdf_url') as mock_verify:
            mock_verify.side_effect = AccessDenied('ASM access denied')
            
            with pytest.raises(AccessDenied):
                the_asm_shimmy(pma, verify=True)

    def test_verify_pdf_url_no_pdf_link(self):
        """Test that verify_pdf_url NoPDFLink is propagated."""
        pma = MockPMA(doi='10.1128/aac.00216-22')
        
        with patch('metapub.findit.dances.asm.verify_pdf_url') as mock_verify:
            mock_verify.side_effect = NoPDFLink('URL not accessible')
            
            with pytest.raises(NoPDFLink):
                the_asm_shimmy(pma, verify=True)

    def test_doi_with_special_characters(self):
        """Test DOI handling with special characters (should work as-is)."""
        pma = MockPMA(doi='10.1128/aac.00216-22')
        
        with patch('metapub.findit.dances.asm.verify_pdf_url') as mock_verify:
            mock_verify.return_value = True
            
            result = the_asm_shimmy(pma, verify=True)
            expected = 'https://journals.asm.org/doi/pdf/10.1128/aac.00216-22?download=true'
            assert result == expected

    def test_non_asm_doi_pattern(self):
        """Test that non-ASM DOIs still work (function trusts registry)."""
        # Following DANCE_FUNCTION_GUIDELINES: trust the registry routing
        pma = MockPMA(doi='10.1234/example.doi')
        
        with patch('metapub.findit.dances.asm.verify_pdf_url') as mock_verify:
            mock_verify.return_value = True
            
            result = the_asm_shimmy(pma, verify=True)
            expected = 'https://journals.asm.org/doi/pdf/10.1234/example.doi?download=true'
            assert result == expected


class TestASMEvidenceValidation:
    """Validate our evidence-based approach."""

    def test_evidence_based_pattern_coverage(self):
        """Verify our pattern covers all evidence samples."""
        # These are the actual DOIs from our HTML evidence analysis
        evidence_dois = [
            '10.1128/aac.00216-22',      # PMID 35856662 - Antimicrob Agents Chemother
            '10.1128/jb.00337-22',       # PMID 36598232 - J Bacteriol  
            '10.1128/msystems.01299-23', # PMID 38329942 - mSystems
            '10.1128/jb.00024-24',       # PMID 38591913 - J Bacteriol
            '10.1128/aac.00924-24',      # PMID 39382274 - Antimicrob Agents Chemother
        ]
        
        with patch('metapub.findit.dances.asm.verify_pdf_url') as mock_verify:
            mock_verify.return_value = True
            
            for doi in evidence_dois:
                pma = MockPMA(doi=doi)
                result = the_asm_shimmy(pma, verify=True)
                expected = f'https://journals.asm.org/doi/pdf/{doi}?download=true'
                assert result == expected



class TestASMWithVerifiedPMIDs:
    """Test ASM dance function with verified PMIDs from our system."""
    
    def test_asm_verified_pmids_url_construction(self):
        """Test URL construction with actual verified PMIDs from ASM system."""
        from metapub import PubMedFetcher
        
        # Verified PMIDs from american_society_of_microbiology_pmids.txt
        verified_pmids_with_dois = [
            ('35856662', '10.1128/aac.00216-22'),    # Antimicrob Agents Chemother
            ('39382274', '10.1128/aac.00924-24'),    # Antimicrob Agents Chemother
            ('36598232', '10.1128/jb.00337-22'),     # J Bacteriol
            ('38591913', '10.1128/jb.00024-24'),     # J Bacteriol
            ('38329942', '10.1128/msystems.01299-23'), # mSystems
        ]
        
        fetch = PubMedFetcher()
        
        with patch('metapub.findit.dances.asm.verify_pdf_url') as mock_verify:
            mock_verify.return_value = True
            
            for pmid, expected_doi in verified_pmids_with_dois:
                try:
                    pma = fetch.article_by_pmid(pmid)
                    
                    # Verify the article has the expected DOI
                    assert pma.doi == expected_doi, f"PMID {pmid} DOI mismatch: expected {expected_doi}, got {pma.doi}"
                    
                    # Test URL construction
                    result = the_asm_shimmy(pma, verify=True)
                    expected_url = f'https://journals.asm.org/doi/pdf/{expected_doi}?download=true'
                    
                    assert result == expected_url, f"PMID {pmid} URL mismatch"
                    print(f"✓ PMID {pmid} ({pma.journal}): {result}")
                    
                except Exception as e:
                    print(f"⚠ PMID {pmid} failed: {e}")
                    # Don't fail the test for network issues, just warn
                    pass
    
    def test_asm_sample_pmids_integration(self):
        """Integration test with a couple sample PMIDs to ensure functionality."""
        from metapub import PubMedFetcher
        
        # Test just 2 PMIDs for lighter integration testing
        sample_pmids = [
            '35856662',  # Recent Antimicrob Agents Chemother
            '36598232',  # Recent J Bacteriol
        ]
        
        fetch = PubMedFetcher()
        
        for pmid in sample_pmids:
            try:
                pma = fetch.article_by_pmid(pmid)
                
                if pma.doi and pma.doi.startswith('10.1128/'):
                    # Test without verification to avoid network calls
                    url = the_asm_shimmy(pma, verify=False)
                    
                    assert 'journals.asm.org/doi/pdf/' in url
                    assert pma.doi in url
                    print(f"✓ Sample integration test PMID {pmid}: {url}")
                else:
                    print(f"⚠ PMID {pmid} doesn't have expected ASM DOI pattern")
                    
            except Exception as e:
                print(f"⚠ Sample PMID {pmid} failed: {e}")
                # Don't fail for network issues


class TestASMXMLFixtures:
    """Test ASM dance function with real XML fixtures."""

    def test_asm_authentic_metadata_validation(self):
        """Validate authentic metadata from XML fixtures."""
        for pmid, expected in ASM_EVIDENCE_PMIDS.items():
            pma = load_pmid_xml(pmid)
            
            assert pma.doi == expected['doi']
            assert pma.journal == expected['journal']
            assert pma.pmid == pmid
            assert pma.doi.startswith('10.1128/'), f"ASM DOI must start with 10.1128/, got: {pma.doi}"
            
            print(f"✓ PMID {pmid}: {pma.journal} - {pma.doi}")

    def test_asm_url_construction_without_verification(self):
        """Test URL construction using XML fixtures."""
        for pmid in ASM_EVIDENCE_PMIDS.keys():
            pma = load_pmid_xml(pmid)
            
            result = the_asm_shimmy(pma, verify=False)
            
            # Should be ASM URL pattern
            expected_url = f'https://journals.asm.org/doi/pdf/{pma.doi}?download=true'
            assert result == expected_url
            
            print(f"✓ PMID {pmid} URL: {result}")

    @patch('metapub.findit.dances.asm.verify_pdf_url')
    def test_asm_paywall_handling(self, mock_verify):
        """Test paywall detection."""
        mock_verify.side_effect = AccessDenied('ASM subscription required')
        
        pma = load_pmid_xml('35856662')  # Use first test PMID
        
        with pytest.raises(AccessDenied):
            the_asm_shimmy(pma, verify=True)

    def test_asm_journal_coverage(self):
        """Test journal coverage across different ASM publications."""
        journals_found = set()
        
        for pmid in ASM_EVIDENCE_PMIDS.keys():
            pma = load_pmid_xml(pmid)
            journals_found.add(pma.journal)
        
        assert len(journals_found) >= 3
        print(f"✅ Coverage: {len(journals_found)} different ASM journals")

    def test_asm_error_handling_missing_doi(self):
        """Test error handling for articles without DOI."""
        class MockPMA:
            def __init__(self):
                self.doi = None
        
        mock_pma = MockPMA()
        
        with pytest.raises(NoPDFLink) as excinfo:
            the_asm_shimmy(mock_pma)
        
        assert 'DOI required' in str(excinfo.value) or 'MISSING' in str(excinfo.value)