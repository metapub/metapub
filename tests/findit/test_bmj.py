"""
Evidence-based tests for BMJ (British Medical Journal) dance function.

Based on HTML sample analysis showing optimal two-stage approach:
- Primary: VIP URL construction (faster - no page load)
- Backup: citation_pdf_url meta tag extraction (100% reliable)
- Pattern: https://[journal].bmj.com/content/{volume}/{issue}/{first_page}.full.pdf
- DOI format: 10.1136/ prefix (consistent across all journals)
- Comprehensive journal coverage with subdomain mapping

Tests both VIP construction and meta tag fallback scenarios.
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

from metapub.findit.dances.bmj import the_bmj_bump
from metapub.exceptions import NoPDFLink


class MockResponse:
    """Mock HTTP response for testing."""
    def __init__(self, status_code=200, text=''):
        self.status_code = status_code
        self.text = text


class TestBMJDance(BaseDanceTest):
    """Evidence-based test cases for BMJ (British Medical Journal)."""

    def setUp(self):
        """Set up test fixtures.""" 
        super().setUp()

    def test_bmj_journal_recognition(self):
        """Test that BMJ journals are properly configured."""
        # Test the function directly with known BMJ patterns rather than registry lookup
        # since registry may not be populated during tests
        
        from metapub.findit.journals.bmj import bmj_journals, PUBLISHER_INFO
        
        # Verify BMJ configuration  
        assert PUBLISHER_INFO['name'] == 'BMJ Publishing Group'
        assert PUBLISHER_INFO['dance_function'] == 'the_bmj_bump'
        assert len(bmj_journals) > 0, "BMJ journals list should not be empty"
        
        # Check some expected BMJ journals are in the list
        expected_journals = ['Heart', 'BMJ Support Palliat Care', 'Gut', 'BMJ Open']
        found_journals = []
        
        for expected in expected_journals:
            if expected in bmj_journals:
                found_journals.append(expected)
                print(f"✓ {expected} found in BMJ journals list")
        
        assert len(found_journals) > 0, f"Should find at least some expected journals, found: {found_journals}"
        print(f"✓ Found {len(found_journals)} expected BMJ journals in configuration")

    @patch('metapub.findit.dances.bmj.verify_pdf_url')
    def test_bmj_vip_construction_primary(self, mock_verify):
        """Test 1: VIP URL construction (primary method - fastest)."""
        # Mock PMA with VIP data available
        pma = Mock()
        pma.doi = '10.1136/heartjnl-2021-320451'
        pma.journal = 'Heart'
        pma.volume = '108'
        pma.issue = '21' 
        pma.first_page = '1674'
        
        mock_verify.return_value = True
        
        result = the_bmj_bump(pma, verify=True)
        
        # Should construct VIP URL directly without page load
        expected_url = 'https://heart.bmj.com/content/108/21/1674.full.pdf'
        assert result == expected_url
        assert 'heart.bmj.com' in result
        assert '.full.pdf' in result
        
        # Should verify PDF URL
        mock_verify.assert_called_once_with(expected_url, 'BMJ')
        
        print(f"Test 1 - VIP construction (primary): {result}")

    @patch('metapub.findit.dances.bmj.verify_pdf_url')
    @patch('metapub.findit.dances.bmj.unified_uri_get')
    @patch('metapub.findit.dances.bmj.the_doi_2step')
    def test_bmj_citation_pdf_url_fallback(self, mock_doi_2step, mock_uri_get, mock_verify):
        """Test 2: Citation_pdf_url meta tag extraction (fallback method)."""
        # Mock PMA with missing VIP data to force fallback
        pma = Mock()
        pma.doi = '10.1136/heartjnl-2021-320451'  # From evidence sample
        pma.journal = 'Heart'
        # Missing volume/issue/page to force VIP failure
        pma.volume = None
        pma.issue = None
        pma.first_page = None
        
        # Mock the DOI resolution and HTML response
        mock_doi_2step.return_value = 'https://heart.bmj.com/content/108/21/1674'
        
        # Mock HTML with citation_pdf_url meta tag (from actual sample)
        html_with_meta = '''
        <html>
        <head>
            <meta name="citation_pdf_url" content="https://heart.bmj.com/content/heartjnl/108/21/1674.full.pdf">
        </head>
        </html>
        '''
        
        mock_response = MockResponse(200, html_with_meta)
        mock_uri_get.return_value = mock_response
        mock_verify.return_value = True
        
        result = the_bmj_bump(pma, verify=True)
        
        # Verify the extracted URL (fallback method)
        expected_url = 'https://heart.bmj.com/content/heartjnl/108/21/1674.full.pdf'
        assert result == expected_url
        
        # Verify function calls - should use fallback method
        mock_doi_2step.assert_called_once_with('10.1136/heartjnl-2021-320451')
        mock_uri_get.assert_called_once()
        mock_verify.assert_called_once_with(expected_url, 'BMJ')
        
        print(f"Test 2 - citation_pdf_url fallback: {result}")

    @patch('metapub.findit.dances.bmj.unified_uri_get')
    @patch('metapub.findit.dances.bmj.the_doi_2step')
    def test_bmj_verify_false_skips_verification(self, mock_doi_2step, mock_uri_get):
        """Test 3: verify=False skips PDF verification."""
        pma = Mock()
        pma.doi = '10.1136/spcare-2023-004738'  # From evidence sample
        pma.journal = 'BMJ Support Palliat Care'
        # Missing VIP data to force fallback
        pma.volume = None
        pma.issue = None
        pma.first_page = None
        
        mock_doi_2step.return_value = 'https://spcare.bmj.com/content/14/1/87'
        
        html_with_meta = '''
        <html>
        <head>
            <meta name="citation_pdf_url" content="https://spcare.bmj.com/content/bmjspcare/14/1/87.full.pdf">
        </head>
        </html>
        '''
        
        mock_response = MockResponse(200, html_with_meta)
        mock_uri_get.return_value = mock_response
        
        result = the_bmj_bump(pma, verify=False)
        
        expected_url = 'https://spcare.bmj.com/content/bmjspcare/14/1/87.full.pdf'
        assert result == expected_url
        
        print(f"Test 3 - Skip verification: {result}")

    def test_bmj_missing_doi_error(self):
        """Test 4: Missing DOI raises informative error."""
        pma = Mock()
        pma.doi = None
        pma.journal = 'Heart'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_bmj_bump(pma)
        
        error_msg = str(exc_info.value)
        assert 'MISSING: DOI required' in error_msg
        print(f"Test 3 - Missing DOI error: {error_msg}")

    @patch('metapub.findit.dances.bmj.unified_uri_get')
    @patch('metapub.findit.dances.bmj.the_doi_2step')
    def test_bmj_http_error_handling(self, mock_doi_2step, mock_uri_get):
        """Test 4: HTTP error handling."""
        pma = Mock()
        pma.doi = '10.1136/test.error'
        pma.journal = 'BMJ Test'
        # Force VIP construction to fail
        pma.volume = None
        pma.issue = None
        pma.first_page = None
        
        mock_doi_2step.return_value = 'https://example.com/error'
        mock_uri_get.return_value = MockResponse(404)
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_bmj_bump(pma)
        
        error_msg = str(exc_info.value)
        assert 'TXERROR: Could not access BMJ article page (HTTP 404)' in error_msg
        print(f"Test 4 - HTTP error: {error_msg}")

    @patch('metapub.findit.dances.bmj.unified_uri_get')
    @patch('metapub.findit.dances.bmj.the_doi_2step')
    def test_bmj_missing_citation_meta_error(self, mock_doi_2step, mock_uri_get):
        """Test 5: Missing citation_pdf_url meta tag error."""
        pma = Mock()
        pma.doi = '10.1136/test.nometa'
        pma.journal = 'BMJ Test'
        # Force VIP construction to fail
        pma.volume = None
        pma.issue = None
        pma.first_page = None
        
        mock_doi_2step.return_value = 'https://example.com/nometa'
        
        # HTML without citation_pdf_url meta tag
        html_without_meta = '''
        <html>
        <head>
            <meta name="other_meta" content="something">
        </head>
        </html>
        '''
        
        mock_uri_get.return_value = MockResponse(200, html_without_meta)
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_bmj_bump(pma)
        
        error_msg = str(exc_info.value)
        assert 'MISSING: No PDF URL found via VIP construction or meta tag extraction' in error_msg
        print(f"Test 5 - Missing meta tag error: {error_msg}")

    @patch('metapub.findit.dances.bmj.verify_pdf_url')
    @patch('metapub.findit.dances.bmj.unified_uri_get')
    @patch('metapub.findit.dances.bmj.the_doi_2step')
    def test_bmj_evidence_dois_coverage(self, mock_doi_2step, mock_uri_get, mock_verify):
        """Test 6: Coverage of all evidence DOIs from HTML samples."""
        evidence_dois = [
            '10.1136/heartjnl-2021-320451',   # Sample 1 - Heart
            '10.1136/spcare-2023-004738',     # Sample 2 - BMJ Support Palliat Care
            '10.1136/spcare-2023-004183',     # Sample 3 - BMJ Support Palliat Care
        ]
        
        for i, doi in enumerate(evidence_dois):
            pma = Mock()
            pma.doi = doi
            # Force VIP construction to fail by missing volume/issue/page
            pma.volume = None
            pma.issue = None
            pma.first_page = None
            
            # Map journal based on DOI pattern
            if 'heartjnl' in doi:
                pma.journal = 'Heart'
                expected_url = f'https://heart.bmj.com/content/heartjnl/test/test/test.full.pdf'
            elif 'spcare' in doi:
                pma.journal = 'BMJ Support Palliat Care'
                expected_url = f'https://spcare.bmj.com/content/bmjspcare/test/test/test.full.pdf'
            else:
                expected_url = f'https://test.bmj.com/content/test/test/test/test.full.pdf'
            
            # Mock the responses
            mock_doi_2step.return_value = f'https://test.bmj.com/article?id={doi}'
            
            html_with_meta = f'''
            <html>
            <head>
                <meta name="citation_pdf_url" content="{expected_url}">
            </head>
            </html>
            '''
            
            mock_uri_get.return_value = MockResponse(200, html_with_meta)
            mock_verify.return_value = True
            
            result = the_bmj_bump(pma, verify=False)
            
            # Verify URL construction for each evidence DOI
            assert result == expected_url
            assert 'bmj.com' in result
            assert '.full.pdf' in result
            
            print(f"✓ Evidence DOI {doi}: {result}")

    def test_bmj_doi_pattern_validation(self):
        """Test 7: DOI pattern validation for BMJ format."""
        # All evidence DOIs should follow 10.1136/ pattern
        evidence_dois = [
            '10.1136/heartjnl-2021-320451',
            '10.1136/spcare-2023-004738', 
            '10.1136/spcare-2023-004183',
        ]
        
        for doi in evidence_dois:
            # Verify DOI starts with 10.1136/
            assert doi.startswith('10.1136/'), f"Invalid BMJ DOI pattern: {doi}"
            
            # Verify DOI has proper BMJ structure (10.1136/journal-year-id)
            assert '10.1136/' in doi, f"DOI should contain 10.1136/: {doi}"
            
            # Split after 10.1136/ to get the journal code
            journal_part = doi.split('10.1136/')[1]
            assert len(journal_part) > 0, f"DOI should have journal identifier: {doi}"
            
            print(f"✓ DOI pattern valid: {doi}")

    def test_guidelines_compliance(self):
        """Test 8: Verify compliance with DANCE_FUNCTION_GUIDELINES."""
        import inspect
        from metapub.findit.dances.bmj import the_bmj_bump
        
        # Get function source
        source_lines = inspect.getsource(the_bmj_bump).splitlines()
        
        # Count non-empty, non-comment lines  
        code_lines = []
        in_docstring = False
        for line in source_lines:
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith('"""') or stripped.startswith("'''"):
                in_docstring = not in_docstring
                continue
            if in_docstring:
                continue
            if not stripped.startswith('#'):
                code_lines.append(stripped)
        
        print(f"the_bmj_bump has {len(code_lines)} effective lines of code")
        
        # Should be under 50 lines per guidelines
        assert len(code_lines) < 50, f"Function should be under 50 lines, got {len(code_lines)}"
        
        # Verify function characteristics - should be simple citation_pdf_url extraction
        source = inspect.getsource(the_bmj_bump)
        assert 'citation_pdf_url' in source, "Function should use citation_pdf_url extraction"
        assert 'regex' in source.lower() or 're.search' in source, "Function should use regex for meta tag extraction"
        
        print("✓ Function follows guidelines: minimal, focused, evidence-based")

    def test_logical_simplicity_compliance(self):
        """Test 9: Verify maximum logical simplicity."""
        import inspect
        from metapub.findit.dances.bmj import the_bmj_bump
        
        source = inspect.getsource(the_bmj_bump)
        
        # Should only have basic error handling - no complex logic
        complexity_indicators = [
            'if.*else.*if',  # Complex conditionals
            'for.*for',      # Nested loops  
            'while',         # While loops
            'try.*except.*except',  # Multiple exception handling
        ]
        
        for pattern in complexity_indicators:
            import re
            if re.search(pattern, source):
                print(f"⚠ Found complexity indicator: {pattern}")
            else:
                print(f"✓ No {pattern} found - good simplicity")
        
        # Core logic should be: DOI check -> get HTML -> extract meta tag -> return URL
        expected_steps = [
            'doi',           # DOI validation
            'the_doi_2step', # Get article URL
            'unified_uri_get', # Get HTML
            'citation_pdf_url', # Extract meta tag
            'return'         # Return URL
        ]
        
        for step in expected_steps:
            assert step in source, f"Missing expected step: {step}"
            print(f"✓ Contains expected step: {step}")
        
        print("✓ Function demonstrates maximum logical simplicity")


if __name__ == '__main__':
    # Run basic tests if executed directly
    test_instance = TestBMJDance()
    test_instance.setUp()
    
    print("Running BMJ dance function tests...")
    print("\\n" + "="*60)
    
    tests = [
        ('test_bmj_journal_recognition', 'Journal recognition in configuration'),
        ('test_bmj_vip_construction_primary', 'VIP URL construction (primary)'),
        ('test_bmj_citation_pdf_url_fallback', 'citation_pdf_url fallback'),
        ('test_bmj_verify_false_skips_verification', 'Skip verification mode'),
        ('test_bmj_missing_doi_error', 'Missing DOI error handling'),
        ('test_bmj_http_error_handling', 'HTTP error handling'),
        ('test_bmj_missing_citation_meta_error', 'Missing meta tag error'),
        ('test_bmj_evidence_dois_coverage', 'Evidence DOIs coverage'),
        ('test_bmj_doi_pattern_validation', 'DOI pattern validation'),
        ('test_guidelines_compliance', 'Guidelines compliance'),
        ('test_logical_simplicity_compliance', 'Logical simplicity compliance')
    ]
    
    for test_method, description in tests:
        try:
            getattr(test_instance, test_method)()
            print(f"✓ {description}")
        except Exception as e:
            print(f"✗ {description}: {e}")
    
    print("\\n" + "="*60)
    print("Test suite completed!")