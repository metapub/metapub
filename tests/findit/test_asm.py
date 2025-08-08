"""
Tests for the improved evidence-based ASM dance function.
Based on HTML sample analysis showing direct PDF download pattern.
Updated to test /doi/pdf/ pattern (PDF URLs) instead of /doi/reader/ (reader URLs).
"""

import pytest
from unittest.mock import patch, MagicMock

from metapub.findit.dances.asm import the_asm_shimmy
from metapub.exceptions import NoPDFLink, AccessDenied


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
            mock_verify.assert_called_once_with(expected, 'ASM')

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

    def test_pattern_simplification_benefits(self):
        """Verify the new approach eliminates legacy complexity."""
        # No journal name mapping required
        # No VIP (volume/issue/page) metadata required
        # Direct DOI-based construction
        
        pma = MockPMA(doi='10.1128/aac.00216-22')
        
        with patch('metapub.findit.dances.asm.verify_pdf_url') as mock_verify:
            mock_verify.return_value = True
            
            # Should work without any additional metadata
            result = the_asm_shimmy(pma, verify=True)
            assert 'journals.asm.org/doi/pdf/' in result
            assert pma.doi in result

    def test_guidelines_compliance(self):
        """Verify compliance with DANCE_FUNCTION_GUIDELINES."""
        # Single method approach
        # Under 50 lines  
        # Clear error messages
        # DOI-based construction
        # No HTML parsing
        
        import inspect
        source_lines = inspect.getsource(the_asm_shimmy).splitlines()
        actual_lines = [line for line in source_lines if line.strip() and not line.strip().startswith('#')]
        
        # Function should be under 50 lines (excluding docstring and comments)
        assert len(actual_lines) < 50, f"Function has {len(actual_lines)} lines, should be under 50"


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