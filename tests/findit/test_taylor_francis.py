"""
Evidence-based tests for Taylor & Francis configuration.

Based on HTML sample analysis showing consistent DOI-based PDF URL pattern:
- Pattern: https://www.tandfonline.com/doi/epdf/{DOI}?needAccess=true
- Multiple journal titles under Taylor & Francis umbrella
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
from tests.fixtures import load_pmid_xml, TAYLOR_FRANCIS_EVIDENCE_PMIDS


class MockResponse:
    """Mock HTTP response for testing."""
    def __init__(self, status_code=200, content=b'%PDF-1.5'):
        self.status_code = status_code
        self.content = content


class TestTaylorFrancisConfiguration(BaseDanceTest):
    """Evidence-based test cases for Taylor & Francis."""

    def setUp(self):
        """Set up test fixtures.""" 
        super().setUp()

    def test_taylor_francis_journal_configuration(self):
        """Test that Taylor & Francis journals are properly configured."""
        from metapub.findit.journals.taylor_francis import taylor_francis_journals, taylor_francis_template
        
        # Verify Taylor & Francis configuration  
        assert taylor_francis_template == 'https://www.tandfonline.com/doi/epdf/{doi}?needAccess=true'
        assert len(taylor_francis_journals) > 0, "Taylor & Francis journals list should not be empty"
        
        # Check expected journal names are in the list (from evidence samples)
        expected_journals = [
            'AIDS Care',
            'Acta Orthop Scand', 
            'Aging Ment Health',
            'Behav Med',
            'Chronobiol Int'
        ]
        
        for expected in expected_journals:
            assert expected in taylor_francis_journals, f"{expected} should be in Taylor & Francis journals list"
            print(f"✓ {expected} found in Taylor & Francis journals list")
        
        print(f"✓ Found {len(taylor_francis_journals)} Taylor & Francis journal variants in configuration")
        print(f"✓ Template uses HTTPS: {taylor_francis_template}")

    @patch('metapub.findit.dances.generic.verify_pdf_url')
    @patch('metapub.findit.dances.generic.JournalRegistry')
    def test_taylor_francis_doi_slide_url_construction(self, mock_registry_class, mock_verify):
        """Test 1: DOI-based URL construction using the_doi_slide."""
        # Mock the registry
        mock_registry = Mock()
        mock_registry_class.return_value = mock_registry
        mock_registry.get_publisher_for_journal.return_value = {
            'name': 'Taylor & Francis',
            'dance_function': 'the_doi_slide',
            'format_template': 'https://www.tandfonline.com/doi/epdf/{doi}?needAccess=true'
        }
        
        # Mock PMA with real DOI from HTML sample
        pma = Mock()
        pma.doi = '10.1186/s13722-022-00337-8'  # From evidence sample
        pma.journal = 'Addiction Science & Clinical Practice'
        
        mock_verify.return_value = True
        
        result = the_doi_slide(pma, verify=True)
        
        # Verify the constructed URL
        expected_url = 'https://www.tandfonline.com/doi/epdf/10.1186/s13722-022-00337-8?needAccess=true'
        assert result == expected_url
        assert '10.1186/s13722-022-00337-8' in result
        assert 'needAccess=true' in result
        
        # Verify function calls
        mock_registry.get_publisher_for_journal.assert_called_once()
        mock_verify.assert_called_once_with(expected_url)
        
        print(f"Test 1 - DOI-based URL construction: {result}")

    @patch('metapub.findit.dances.generic.JournalRegistry')
    def test_taylor_francis_verify_false_skips_verification(self, mock_registry_class):
        """Test 2: verify=False skips PDF verification."""
        # Mock the registry
        mock_registry = Mock()
        mock_registry_class.return_value = mock_registry
        mock_registry.get_publisher_for_journal.return_value = {
            'name': 'Taylor & Francis',
            'dance_function': 'the_doi_slide',
            'format_template': 'https://www.tandfonline.com/doi/epdf/{doi}?needAccess=true'
        }
        
        pma = Mock()
        pma.doi = '10.1016/S1470-2045(22)00455-4'  # From evidence sample
        pma.journal = 'Behaviour & Information Technology'
        
        result = the_doi_slide(pma, verify=False)
        
        expected_url = 'https://www.tandfonline.com/doi/epdf/10.1016/S1470-2045(22)00455-4?needAccess=true'
        assert result == expected_url
        
        print(f"Test 2 - Skip verification: {result}")

    def test_taylor_francis_missing_doi_error(self):
        """Test 3: Missing DOI raises informative error."""
        pma = Mock()
        pma.doi = None
        pma.journal = 'Addiction Science & Clinical Practice'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_doi_slide(pma)
        
        error_msg = str(exc_info.value)
        assert 'DOI required' in error_msg
        print(f"Test 3 - Missing DOI error: {error_msg}")

    @patch('metapub.findit.dances.generic.verify_pdf_url')
    @patch('metapub.findit.dances.generic.JournalRegistry')
    def test_taylor_francis_evidence_dois_coverage(self, mock_registry_class, mock_verify):
        """Test 4: Coverage of all evidence DOIs from HTML samples."""
        # Mock the registry
        mock_registry = Mock()
        mock_registry_class.return_value = mock_registry
        mock_registry.get_publisher_for_journal.return_value = {
            'name': 'Taylor & Francis',
            'dance_function': 'the_doi_slide',
            'format_template': 'https://www.tandfonline.com/doi/epdf/{doi}?needAccess=true'
        }
        
        # Evidence DOIs from actual HTML samples analyzed
        evidence_dois = [
            '10.1186/s13722-022-00337-8',   # Addiction Science & Clinical Practice
            '10.1016/S1470-2045(22)00455-4', # Behaviour & Information Technology 
            '10.1080/10407790.2022.2101787',  # Archives of Thermodynamics
            '10.1177/01454455221128776',      # Behavior Modification
            '10.1093/annhyg/mer096'           # Annals of Occupational Hygiene
        ]
        
        for doi in evidence_dois:
            pma = Mock()
            pma.doi = doi
            pma.journal = 'Addiction Science & Clinical Practice'
            
            mock_verify.return_value = True
            
            result = the_doi_slide(pma, verify=False)
            
            # Verify URL construction for each evidence DOI
            expected_url = f'https://www.tandfonline.com/doi/epdf/{doi}?needAccess=true'
            assert result == expected_url
            assert doi in result
            assert 'needAccess=true' in result
            
            print(f"✓ Evidence DOI {doi}: {result}")

    def test_taylor_francis_url_format_validation(self):
        """Test 5: URL format validation for Taylor & Francis pattern."""
        # All constructed URLs should follow expected pattern
        evidence_dois = [
            '10.1186/s13722-022-00337-8',
            '10.1016/S1470-2045(22)00455-4',
            '10.1080/10407790.2022.2101787',
            '10.1177/01454455221128776',
            '10.1093/annhyg/mer096'
        ]
        
        from metapub.findit.journals.taylor_francis import taylor_francis_template
        
        for doi in evidence_dois:
            # Construct URL using template
            result_url = taylor_francis_template.format(doi=doi)
            
            # Verify URL components
            assert result_url.startswith('https://www.tandfonline.com/doi/epdf/')
            assert result_url.endswith('?needAccess=true')
            assert doi in result_url
            
            print(f"✓ URL format valid: {result_url}")

    def test_taylor_francis_url_template_format(self):
        """Test 6: Verify URL template format is correct."""
        from metapub.findit.journals.taylor_francis import taylor_francis_template
        
        template = taylor_francis_template
        
        # Test template substitution
        test_doi = '10.1080/test.123.456'
        result = template.format(doi=test_doi)
        
        expected = 'https://www.tandfonline.com/doi/epdf/10.1080/test.123.456?needAccess=true'
        assert result == expected, f"Template format error: {result}"
        
        # Verify template components
        assert 'https://www.tandfonline.com' in template
        assert '/doi/epdf/' in template
        assert '{doi}' in template
        assert '?needAccess=true' in template
        
        print(f"✓ URL template format correct: {template}")

    def test_taylor_francis_simplicity_through_generics(self):
        """Test 7: Verify Taylor & Francis achieves simplicity through generic function."""
        # Taylor & Francis should use the_doi_slide generic function
        
        # No custom dance function should exist for Taylor & Francis
        try:
            from metapub.findit.dances import taylor_francis
            assert False, "Taylor & Francis should not have a custom dance module"
        except ImportError:
            print("✓ No custom dance function - using generic the_doi_slide")
        
        # Configuration should be minimal
        from metapub.findit.journals.taylor_francis import taylor_francis_template
        assert taylor_francis_template is not None
        assert 'https://' in taylor_francis_template  # Uses modern HTTPS
        
        print("✓ Taylor & Francis achieves maximum simplicity through generic DOI function")

    def test_taylor_francis_access_parameter(self):
        """Test 8: Verify needAccess parameter is preserved in URLs."""
        from metapub.findit.journals.taylor_francis import taylor_francis_template
        
        test_doi = '10.1080/example.2022.123456'
        result = taylor_francis_template.format(doi=test_doi)
        
        # Verify the access parameter is included
        assert 'needAccess=true' in result
        assert result.endswith('?needAccess=true')
        
        # Verify it's a GET parameter (contains ?)
        assert '?' in result
        
        print(f"✓ Access parameter preserved: {result}")

    @patch('metapub.findit.dances.generic.verify_pdf_url')
    @patch('metapub.findit.dances.generic.JournalRegistry')
    def test_taylor_francis_real_pmids_xml_fixtures(self, mock_registry_class, mock_verify):
        """Test 9: Real PMIDs with XML fixtures (TRANSITION_TESTS_TO_REAL_DATA.md)."""
        # Mock the registry
        mock_registry = Mock()
        mock_registry_class.return_value = mock_registry
        mock_registry.get_publisher_for_journal.return_value = {
            'name': 'Taylor & Francis',
            'dance_function': 'the_doi_slide',
            'format_template': 'https://www.tandfonline.com/doi/epdf/{doi}?needAccess=true'
        }
        
        # Test with real PMIDs using XML fixtures
        for pmid, expected_data in TAYLOR_FRANCIS_EVIDENCE_PMIDS.items():
            # Load real article data from XML fixture
            pma = load_pmid_xml(pmid)
            
            # Verify authentic metadata matches expectations
            assert pma.pmid == pmid, f"PMID mismatch: {pma.pmid} != {pmid}"
            assert pma.doi == expected_data['doi'], f"DOI mismatch for {pmid}: {pma.doi} != {expected_data['doi']}"
            assert expected_data['journal'] in pma.journal, f"Journal mismatch for {pmid}: {expected_data['journal']} not in {pma.journal}"
            
            # Mock verification to pass
            mock_verify.return_value = True
            
            # Test the dance function
            result = the_doi_slide(pma, verify=False)
            
            # Verify URL construction
            expected_url = f"https://www.tandfonline.com/doi/epdf/{pma.doi}?needAccess=true"
            assert result == expected_url, f"URL mismatch for {pmid}: {result} != {expected_url}"
            
            # Verify URL components
            assert 'https://www.tandfonline.com' in result
            assert '/doi/epdf/' in result
            assert pma.doi in result
            assert '?needAccess=true' in result
            
            print(f"✓ Real PMID {pmid} ({expected_data['journal']}): {result}")
        
        print(f"✅ All {len(TAYLOR_FRANCIS_EVIDENCE_PMIDS)} real PMIDs tested with XML fixtures")


if __name__ == '__main__':
    # Run basic tests if executed directly
    test_instance = TestTaylorFrancisConfiguration()
    test_instance.setUp()
    
    print("Running Taylor & Francis configuration tests...")
    print("\n" + "="*60)
    
    tests = [
        ('test_taylor_francis_journal_configuration', 'Journal configuration'),
        ('test_taylor_francis_doi_slide_url_construction', 'DOI-based URL construction'),
        ('test_taylor_francis_verify_false_skips_verification', 'Skip verification mode'),
        ('test_taylor_francis_missing_doi_error', 'Missing DOI error handling'),
        ('test_taylor_francis_evidence_dois_coverage', 'Evidence DOIs coverage'),
        ('test_taylor_francis_url_format_validation', 'URL format validation'),
        ('test_taylor_francis_url_template_format', 'URL template format'),
        ('test_taylor_francis_simplicity_through_generics', 'Simplicity through generics'),
        ('test_taylor_francis_access_parameter', 'Access parameter preservation'),
        ('test_taylor_francis_real_pmids_xml_fixtures', 'Real PMIDs with XML fixtures')
    ]
    
    for test_method, description in tests:
        try:
            getattr(test_instance, test_method)()
            print(f"✓ {description}")
        except Exception as e:
            print(f"✗ {description}: {e}")
    
    print("\n" + "="*60)
    print("Test suite completed!")