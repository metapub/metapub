"""
Evidence-based tests for NEJM (New England Journal of Medicine) configuration.

Based on HTML sample analysis showing simple DOI-based PDF URL pattern:
- Pattern: https://www.nejm.org/doi/pdf/{doi}
- DOI format: 10.1056/ prefix (consistent across all articles)
- Uses the_doi_slide generic function (no custom dance needed)

This represents optimal simplicity through DOI-based URL construction.
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


class MockResponse:
    """Mock HTTP response for testing."""
    def __init__(self, status_code=200, content=b'%PDF-1.5'):
        self.status_code = status_code
        self.content = content


class TestNEJMConfiguration(BaseDanceTest):
    """Evidence-based test cases for NEJM (New England Journal of Medicine)."""

    def setUp(self):
        """Set up test fixtures.""" 
        super().setUp()

    def test_nejm_journal_configuration(self):
        """Test that NEJM journals are properly configured."""
        from metapub.findit.journals.single_journal_publishers import nejm_journals, nejm_template
        
        # Verify NEJM configuration  
        assert nejm_template == 'https://www.nejm.org/doi/pdf/{doi}'
        assert len(nejm_journals) > 0, "NEJM journals list should not be empty"
        
        # Check expected journal names are in the list
        expected_journals = ['N Engl J Med']
        for expected in expected_journals:
            assert expected in nejm_journals, f"{expected} should be in NEJM journals list"
            print(f"✓ {expected} found in NEJM journals list")
        
        print(f"✓ Found {len(nejm_journals)} NEJM journal variants in configuration")
        print(f"✓ Template uses HTTPS: {nejm_template}")

    @patch('metapub.findit.dances.generic.verify_pdf_url')
    @patch('metapub.findit.dances.generic.JournalRegistry')
    def test_nejm_doi_slide_url_construction(self, mock_registry_class, mock_verify):
        """Test 1: DOI-based URL construction using the_doi_slide."""
        # Mock the registry
        mock_registry = Mock()
        mock_registry_class.return_value = mock_registry
        mock_registry.get_publisher_for_journal.return_value = {
            'name': 'New England Journal of Medicine',
            'dance_function': 'the_doi_slide',
            'format_template': 'https://www.nejm.org/doi/pdf/{doi}'
        }
        
        # Mock PMA with real DOI from HTML sample
        pma = Mock()
        pma.doi = '10.1056/NEJMoa2404204'  # From evidence sample
        pma.journal = 'N Engl J Med'
        
        mock_verify.return_value = True
        
        result = the_doi_slide(pma, verify=True)
        
        # Verify the constructed URL
        expected_url = 'https://www.nejm.org/doi/pdf/10.1056/NEJMoa2404204'
        assert result == expected_url
        assert '10.1056/NEJMoa2404204' in result
        
        # Verify function calls
        mock_registry.get_publisher_for_journal.assert_called_once()
        mock_verify.assert_called_once_with(expected_url)
        
        print(f"Test 1 - DOI-based URL construction: {result}")

    @patch('metapub.findit.dances.generic.JournalRegistry')
    def test_nejm_verify_false_skips_verification(self, mock_registry_class):
        """Test 2: verify=False skips PDF verification."""
        # Mock the registry
        mock_registry = Mock()
        mock_registry_class.return_value = mock_registry
        mock_registry.get_publisher_for_journal.return_value = {
            'name': 'New England Journal of Medicine',
            'dance_function': 'the_doi_slide',
            'format_template': 'https://www.nejm.org/doi/pdf/{doi}'
        }
        
        pma = Mock()
        pma.doi = '10.1056/NEJMoa2309000'  # From evidence sample
        pma.journal = 'NEJM'
        
        result = the_doi_slide(pma, verify=False)
        
        expected_url = 'https://www.nejm.org/doi/pdf/10.1056/NEJMoa2309000'
        assert result == expected_url
        
        print(f"Test 2 - Skip verification: {result}")

    def test_nejm_missing_doi_error(self):
        """Test 3: Missing DOI raises informative error."""
        pma = Mock()
        pma.doi = None
        pma.journal = 'N Engl J Med'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_doi_slide(pma)
        
        error_msg = str(exc_info.value)
        assert 'DOI required' in error_msg
        print(f"Test 3 - Missing DOI error: {error_msg}")

    @patch('metapub.findit.dances.generic.verify_pdf_url')
    @patch('metapub.findit.dances.generic.JournalRegistry')
    def test_nejm_evidence_dois_coverage(self, mock_registry_class, mock_verify):
        """Test 4: Coverage of all evidence DOIs from HTML samples."""
        # Mock the registry
        mock_registry = Mock()
        mock_registry_class.return_value = mock_registry
        mock_registry.get_publisher_for_journal.return_value = {
            'name': 'New England Journal of Medicine',
            'dance_function': 'the_doi_slide',
            'format_template': 'https://www.nejm.org/doi/pdf/{doi}'
        }
        
        evidence_dois = [
            '10.1056/NEJMoa2404204',   # Sample 1 - Beta-Blocker study
            '10.1056/NEJMoa2309000',   # Sample 2 - NASH trial
        ]
        
        for doi in evidence_dois:
            pma = Mock()
            pma.doi = doi
            pma.journal = 'N Engl J Med'
            
            mock_verify.return_value = True
            
            result = the_doi_slide(pma, verify=False)
            
            # Verify URL construction for each evidence DOI
            expected_url = f'https://www.nejm.org/doi/pdf/{doi}'
            assert result == expected_url
            assert doi in result
            
            print(f"✓ Evidence DOI {doi}: {result}")

    def test_nejm_doi_pattern_validation(self):
        """Test 5: DOI pattern validation for NEJM format."""
        # All evidence DOIs should follow 10.1056/ pattern
        evidence_dois = [
            '10.1056/NEJMoa2404204',
            '10.1056/NEJMoa2309000',
        ]
        
        for doi in evidence_dois:
            # Verify DOI starts with 10.1056/
            assert doi.startswith('10.1056/'), f"Invalid NEJM DOI pattern: {doi}"
            
            # Verify DOI has proper NEJM structure
            assert 'NEJM' in doi, f"DOI should contain NEJM identifier: {doi}"
            
            print(f"✓ DOI pattern valid: {doi}")

    def test_nejm_url_template_format(self):
        """Test 6: Verify URL template format is correct."""
        from metapub.findit.journals.single_journal_publishers import nejm_template
        
        template = nejm_template
        
        # Test template substitution
        test_doi = '10.1056/NEJMtest123'
        result = template.format(doi=test_doi)
        
        expected = 'https://www.nejm.org/doi/pdf/10.1056/NEJMtest123'
        assert result == expected, f"Template format error: {result}"
        
        # Verify template components
        assert 'https://www.nejm.org' in template
        assert '/doi/pdf/' in template
        assert '{doi}' in template
        
        print(f"✓ URL template format correct: {template}")

    def test_nejm_simplicity_through_generics(self):
        """Test 7: Verify NEJM achieves simplicity through generic function."""
        # NEJM should use the_doi_slide generic function (configured in migrate_journals.py)
        # No direct way to test this without checking the migration script
        
        # No custom dance function should exist for NEJM
        try:
            from metapub.findit.dances import nejm
            assert False, "NEJM should not have a custom dance module"
        except ImportError:
            print("✓ No custom dance function - using generic the_doi_slide")
        
        # Configuration should be minimal
        from metapub.findit.journals.single_journal_publishers import nejm_template
        assert nejm_template is not None
        assert 'https://' in nejm_template  # Uses modern HTTPS
        
        print("✓ NEJM achieves maximum simplicity through generic DOI function")


if __name__ == '__main__':
    # Run basic tests if executed directly
    test_instance = TestNEJMConfiguration()
    test_instance.setUp()
    
    print("Running NEJM configuration tests...")
    print("\n" + "="*60)
    
    tests = [
        ('test_nejm_journal_configuration', 'Journal configuration'),
        ('test_nejm_doi_slide_url_construction', 'DOI-based URL construction'),
        ('test_nejm_verify_false_skips_verification', 'Skip verification mode'),
        ('test_nejm_missing_doi_error', 'Missing DOI error handling'),
        ('test_nejm_evidence_dois_coverage', 'Evidence DOIs coverage'),
        ('test_nejm_doi_pattern_validation', 'DOI pattern validation'),
        ('test_nejm_url_template_format', 'URL template format'),
        ('test_nejm_simplicity_through_generics', 'Simplicity through generics')
    ]
    
    for test_method, description in tests:
        try:
            getattr(test_instance, test_method)()
            print(f"✓ {description}")
        except Exception as e:
            print(f"✗ {description}: {e}")
    
    print("\n" + "="*60)
    print("Test suite completed!")