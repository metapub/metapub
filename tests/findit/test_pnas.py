"""
Evidence-based tests for PNAS (Proceedings of the National Academy of Sciences) configuration.

Based on HTML sample analysis showing simple DOI-based PDF URL pattern:
- Pattern: https://www.pnas.org/doi/pdf/10.1073/pnas.{DOI_SUFFIX}
- DOI format: 10.1073/pnas.{SUFFIX} (PNAS DOI prefix)  
- Uses the_doi_slide generic function (no custom dance needed)

This represents optimal simplicity through DOI-based URL construction.

Following TRANSITION_TESTS_TO_REAL_DATA.md - using XML fixtures instead of mocking.
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

from metapub.findit.dances.generic import the_doi_slide
from metapub.exceptions import NoPDFLink
from tests.fixtures import load_pmid_xml, PNAS_EVIDENCE_PMIDS


class MockResponse:
    """Mock HTTP response for testing."""
    def __init__(self, status_code=200, content=b'%PDF-1.5'):
        self.status_code = status_code
        self.content = content


class TestPNASConfiguration(BaseDanceTest):
    """Evidence-based test cases for PNAS (Proceedings of the National Academy of Sciences)."""

    def setUp(self):
        """Set up test fixtures.""" 
        super().setUp()

    def test_pnas_journal_configuration(self):
        """Test that PNAS journals are properly configured."""
        from metapub.findit.journals.single_journal_publishers import pnas_journals, pnas_template
        
        # Verify PNAS configuration  
        assert pnas_template == 'https://www.pnas.org/doi/pdf/{doi}'
        assert len(pnas_journals) > 0, "PNAS journals list should not be empty"
        
        # Check expected journal names are in the list
        expected_journals = ['Proc Natl Acad Sci USA']
        for expected in expected_journals:
            assert expected in pnas_journals, f"{expected} should be in PNAS journals list"
            print(f"✓ {expected} found in PNAS journals list")
        
        print(f"✓ Found {len(pnas_journals)} PNAS journal variants in configuration")
        print(f"✓ Template uses HTTPS: {pnas_template}")

    @patch('metapub.findit.dances.generic.verify_pdf_url')
    @patch('metapub.findit.dances.generic.JournalRegistry')
    def test_pnas_doi_slide_url_construction(self, mock_registry_class, mock_verify):
        """Test 1: DOI-based URL construction using the_doi_slide."""
        # Mock the registry
        mock_registry = Mock()
        mock_registry_class.return_value = mock_registry
        mock_registry.get_publisher_for_journal.return_value = {
            'name': 'Proceedings of the National Academy of Sciences',
            'dance_function': 'the_doi_slide',
            'format_template': 'https://www.pnas.org/doi/pdf/{doi}'
        }
        
        # Mock PMA with real DOI from HTML sample
        pma = Mock()
        pma.doi = '10.1073/pnas.2305772120'  # From evidence sample
        pma.journal = 'Proc Natl Acad Sci USA'
        
        mock_verify.return_value = True
        
        result = the_doi_slide(pma, verify=True)
        
        # Verify the constructed URL
        expected_url = 'https://www.pnas.org/doi/pdf/10.1073/pnas.2305772120'
        assert result == expected_url
        assert '10.1073/pnas.2305772120' in result
        
        # Verify function calls
        mock_registry.get_publisher_for_journal.assert_called_once()
        mock_verify.assert_called_once_with(expected_url)
        
        print(f"Test 1 - DOI-based URL construction: {result}")

    @patch('metapub.findit.dances.generic.JournalRegistry')
    def test_pnas_verify_false_skips_verification(self, mock_registry_class):
        """Test 2: verify=False skips PDF verification."""
        # Mock the registry
        mock_registry = Mock()
        mock_registry_class.return_value = mock_registry
        mock_registry.get_publisher_for_journal.return_value = {
            'name': 'Proceedings of the National Academy of Sciences',
            'dance_function': 'the_doi_slide',
            'format_template': 'https://www.pnas.org/doi/pdf/{doi}'
        }
        
        pma = Mock()
        pma.doi = '10.1073/pnas.2308706120'  # From evidence sample
        pma.journal = 'PNAS'
        
        result = the_doi_slide(pma, verify=False)
        
        expected_url = 'https://www.pnas.org/doi/pdf/10.1073/pnas.2308706120'
        assert result == expected_url
        
        print(f"Test 2 - Skip verification: {result}")

    def test_pnas_missing_doi_error(self):
        """Test 3: Missing DOI raises informative error."""
        pma = Mock()
        pma.doi = None
        pma.journal = 'Proc Natl Acad Sci USA'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_doi_slide(pma)
        
        error_msg = str(exc_info.value)
        assert 'DOI required' in error_msg
        print(f"Test 3 - Missing DOI error: {error_msg}")

    @patch('metapub.findit.dances.generic.verify_pdf_url')
    @patch('metapub.findit.dances.generic.JournalRegistry')
    def test_pnas_evidence_dois_coverage(self, mock_registry_class, mock_verify):
        """Test 4: Coverage of all evidence DOIs from HTML samples."""
        # Mock the registry
        mock_registry = Mock()
        mock_registry_class.return_value = mock_registry
        mock_registry.get_publisher_for_journal.return_value = {
            'name': 'Proceedings of the National Academy of Sciences',
            'dance_function': 'the_doi_slide',
            'format_template': 'https://www.pnas.org/doi/pdf/{doi}'
        }
        
        evidence_dois = [
            '10.1073/pnas.2305772120',   # Sample 1 - Ketamine neurobiology
            '10.1073/pnas.2308706120',   # Sample 2 - Social anxiety disorder
            '10.1073/pnas.2308214120',   # Sample 3 - CD200 retinopathy
        ]
        
        for doi in evidence_dois:
            pma = Mock()
            pma.doi = doi
            pma.journal = 'Proc Natl Acad Sci USA'
            
            mock_verify.return_value = True
            
            result = the_doi_slide(pma, verify=False)
            
            # Verify URL construction for each evidence DOI
            expected_url = f'https://www.pnas.org/doi/pdf/{doi}'
            assert result == expected_url
            assert doi in result
            
            print(f"✓ Evidence DOI {doi}: {result}")

    def test_pnas_doi_pattern_validation(self):
        """Test 5: DOI pattern validation for PNAS format."""
        # All evidence DOIs should follow 10.1073/pnas. pattern
        evidence_dois = [
            '10.1073/pnas.2305772120',
            '10.1073/pnas.2308706120',
            '10.1073/pnas.2308214120',
        ]
        
        for doi in evidence_dois:
            # Verify DOI starts with 10.1073/pnas.
            assert doi.startswith('10.1073/pnas.'), f"Invalid PNAS DOI pattern: {doi}"
            
            # Verify DOI has proper PNAS structure
            assert 'pnas' in doi.lower(), f"DOI should contain PNAS identifier: {doi}"
            
            print(f"✓ DOI pattern valid: {doi}")

    def test_pnas_url_template_format(self):
        """Test 6: Verify URL template format is correct."""
        from metapub.findit.journals.single_journal_publishers import pnas_template
        
        template = pnas_template
        
        # Test template substitution
        test_doi = '10.1073/pnas.test123'
        result = template.format(doi=test_doi)
        
        expected = 'https://www.pnas.org/doi/pdf/10.1073/pnas.test123'
        assert result == expected, f"Template format error: {result}"
        
        # Verify template components
        assert 'https://www.pnas.org' in template
        assert '/doi/pdf/' in template
        assert '{doi}' in template
        
        print(f"✓ URL template format correct: {template}")

    def test_pnas_simplicity_through_generics(self):
        """Test 7: Verify PNAS achieves simplicity through generic function."""
        # PNAS should use the_doi_slide generic function (configured in migrate_journals.py)
        # No direct way to test this without checking the migration script
        
        # No custom dance function should exist for PNAS
        try:
            from metapub.findit.dances import pnas
            assert False, "PNAS should not have a custom dance module"
        except ImportError:
            print("✓ No custom dance function - using generic the_doi_slide")
        
        # Configuration should be minimal
        from metapub.findit.journals.single_journal_publishers import pnas_template
        assert pnas_template is not None
        assert 'https://' in pnas_template  # Uses modern HTTPS
        
        print("✓ PNAS achieves maximum simplicity through generic DOI function")

    @patch('metapub.findit.dances.generic.verify_pdf_url')
    @patch('metapub.findit.dances.generic.JournalRegistry')
    def test_pnas_real_pmids_xml_fixtures(self, mock_registry_class, mock_verify):
        """Test 8: Real PMIDs with XML fixtures (TRANSITION_TESTS_TO_REAL_DATA.md)."""
        # Mock the registry
        mock_registry = Mock()
        mock_registry_class.return_value = mock_registry
        mock_registry.get_publisher_for_journal.return_value = {
            'name': 'Proceedings of the National Academy of Sciences',
            'dance_function': 'the_doi_slide',
            'format_template': 'https://www.pnas.org/doi/pdf/{doi}'
        }
        
        # Test with real PMIDs using XML fixtures
        for pmid, expected_data in PNAS_EVIDENCE_PMIDS.items():
            # Load real article data from XML fixture
            pma = load_pmid_xml(pmid)
            
            # Verify authentic metadata matches expectations
            assert pma.pmid == pmid, f"PMID mismatch: {pma.pmid} != {pmid}"
            assert pma.doi == expected_data['doi'], f"DOI mismatch for {pmid}: {pma.doi} != {expected_data['doi']}"
            assert expected_data['journal'] in pma.journal, f"Journal mismatch for {pmid}: {expected_data['journal']} not in {pma.journal}"
            
            # Verify PNAS DOI pattern
            assert pma.doi.startswith('10.1073/pnas.'), f"Invalid PNAS DOI pattern: {pma.doi}"
            
            # Mock verification to pass
            mock_verify.return_value = True
            
            # Test the dance function
            result = the_doi_slide(pma, verify=False)
            
            # Verify URL construction
            expected_url = f"https://www.pnas.org/doi/pdf/{pma.doi}"
            assert result == expected_url, f"URL mismatch for {pmid}: {result} != {expected_url}"
            
            # Verify URL components
            assert 'https://www.pnas.org' in result
            assert '/doi/pdf/' in result
            assert pma.doi in result
            
            print(f"✓ Real PMID {pmid} ({expected_data['journal']}): {result}")
        
        print(f"✅ All {len(PNAS_EVIDENCE_PMIDS)} real PMIDs tested with XML fixtures")


if __name__ == '__main__':
    # Run basic tests if executed directly
    test_instance = TestPNASConfiguration()
    test_instance.setUp()
    
    print("Running PNAS configuration tests...")
    print("\\n" + "="*60)
    
    tests = [
        ('test_pnas_journal_configuration', 'Journal configuration'),
        ('test_pnas_doi_slide_url_construction', 'DOI-based URL construction'),
        ('test_pnas_verify_false_skips_verification', 'Skip verification mode'),
        ('test_pnas_missing_doi_error', 'Missing DOI error handling'),
        ('test_pnas_evidence_dois_coverage', 'Evidence DOIs coverage'),
        ('test_pnas_doi_pattern_validation', 'DOI pattern validation'),
        ('test_pnas_url_template_format', 'URL template format'),
        ('test_pnas_simplicity_through_generics', 'Simplicity through generics'),
        ('test_pnas_real_pmids_xml_fixtures', 'Real PMIDs with XML fixtures')
    ]
    
    for test_method, description in tests:
        try:
            getattr(test_instance, test_method)()
            print(f"✓ {description}")
        except Exception as e:
            print(f"✗ {description}: {e}")
    
    print("\\n" + "="*60)
    print("Test suite completed!")