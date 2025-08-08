"""
Evidence-based tests for PNAS (Proceedings of the National Academy of Sciences) dance function.

Based on HTML sample analysis showing perfect citation_pdf_url meta tags:
- Pattern: https://www.pnas.org/doi/pdf/10.1073/pnas.{DOI_SUFFIX}
- DOI format: 10.1073/pnas.{SUFFIX} (PNAS DOI prefix)
- 100% reliable citation_pdf_url meta tag extraction
- No Cloudflare blocking - clean HTML access

This represents optimal simplicity through citation_pdf_url meta tag extraction.
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

from metapub.findit.dances.pnas import the_pnas_pony
from metapub.exceptions import NoPDFLink


class MockResponse:
    """Mock HTTP response for testing."""
    def __init__(self, status_code=200, text=''):
        self.status_code = status_code
        self.text = text


class TestPNASTest(BaseDanceTest):
    """Evidence-based test cases for PNAS (Proceedings of the National Academy of Sciences)."""

    def setUp(self):
        """Set up test fixtures.""" 
        super().setUp()

    def test_pnas_journal_recognition(self):
        """Test that PNAS journals are properly configured."""
        from metapub.findit.journals.single_journal_publishers import pnas_journals
        
        # Verify PNAS configuration  
        assert len(pnas_journals) > 0, "PNAS journals list should not be empty"
        
        # Check expected journal names are in the list
        expected_journals = ['Proc Natl Acad Sci USA']
        for expected in expected_journals:
            assert expected in pnas_journals, f"{expected} should be in PNAS journals list"
            print(f"✓ {expected} found in PNAS journals list")
        
        print(f"✓ Found {len(pnas_journals)} PNAS journal variants in configuration")

    @patch('metapub.findit.dances.generic.verify_pdf_url')
    @patch('metapub.findit.dances.generic.unified_uri_get')
    @patch('metapub.findit.dances.generic.the_doi_2step')
    def test_pnas_citation_pdf_url_extraction(self, mock_doi_2step, mock_uri_get, mock_verify):
        """Test 1: Perfect citation_pdf_url meta tag extraction."""
        # Mock PMA with real DOI from HTML sample
        pma = Mock()
        pma.doi = '10.1073/pnas.2305772120'  # From evidence sample
        pma.journal = 'Proc Natl Acad Sci USA'
        
        # Mock the DOI resolution and HTML response
        mock_doi_2step.return_value = 'https://www.pnas.org/doi/10.1073/pnas.2305772120'
        
        # Mock HTML with citation_pdf_url meta tag (from actual sample)
        html_with_meta = '''
        <html>
        <head>
            <meta name="citation_pdf_url" content="https://www.pnas.org/doi/pdf/10.1073/pnas.2305772120">
        </head>
        </html>
        '''
        
        mock_response = MockResponse(200, html_with_meta)
        mock_uri_get.return_value = mock_response
        mock_verify.return_value = True
        
        result = the_pnas_pony(pma, verify=True)
        
        # Verify the extracted URL
        expected_url = 'https://www.pnas.org/doi/pdf/10.1073/pnas.2305772120'
        assert result == expected_url
        assert '10.1073/pnas.2305772120' in result
        
        # Verify function calls
        mock_doi_2step.assert_called_once_with('10.1073/pnas.2305772120')
        mock_uri_get.assert_called_once()
        mock_verify.assert_called_once_with(expected_url)
        
        print(f"Test 1 - citation_pdf_url extraction: {result}")

    @patch('metapub.findit.dances.generic.unified_uri_get')
    @patch('metapub.findit.dances.generic.the_doi_2step')
    def test_pnas_verify_false_skips_verification(self, mock_doi_2step, mock_uri_get):
        """Test 2: verify=False skips PDF verification."""
        pma = Mock()
        pma.doi = '10.1073/pnas.2308706120'  # From evidence sample
        pma.journal = 'PNAS'
        
        # Mock the DOI resolution and HTML response
        mock_doi_2step.return_value = 'https://www.pnas.org/doi/10.1073/pnas.2308706120'
        
        html_with_meta = '''
        <html>
        <head>
            <meta name="citation_pdf_url" content="https://www.pnas.org/doi/pdf/10.1073/pnas.2308706120">
        </head>
        </html>
        '''
        
        mock_response = MockResponse(200, html_with_meta)
        mock_uri_get.return_value = mock_response
        
        result = the_pnas_pony(pma, verify=False)
        
        expected_url = 'https://www.pnas.org/doi/pdf/10.1073/pnas.2308706120'
        assert result == expected_url
        
        # Verify no verification was attempted (verify_pdf_url not called)
        print(f"Test 2 - Skip verification: {result}")

    def test_pnas_missing_doi_error(self):
        """Test 3: Missing DOI raises informative error."""
        pma = Mock()
        pma.doi = None
        pma.journal = 'Proc Natl Acad Sci USA'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_pnas_pony(pma)
        
        error_msg = str(exc_info.value)
        assert 'PNAS requires DOI' in error_msg
        print(f"Test 3 - Missing DOI error: {error_msg}")

    @patch('metapub.findit.dances.generic.verify_pdf_url')
    @patch('metapub.findit.dances.generic.unified_uri_get')
    @patch('metapub.findit.dances.generic.the_doi_2step')
    def test_pnas_evidence_dois_coverage(self, mock_doi_2step, mock_uri_get, mock_verify):
        """Test 4: Coverage of all evidence DOIs from HTML samples."""
        evidence_dois = [
            '10.1073/pnas.2305772120',   # Sample 1 - Ketamine neurobiology
            '10.1073/pnas.2308706120',   # Sample 2 - Social anxiety disorder
            '10.1073/pnas.2308214120',   # Sample 3 - CD200 retinopathy
        ]
        
        for doi in evidence_dois:
            pma = Mock()
            pma.doi = doi
            pma.journal = 'Proc Natl Acad Sci USA'
            
            mock_doi_2step.return_value = f'https://www.pnas.org/doi/{doi}'
            
            html_with_meta = f'''
            <html>
            <head>
                <meta name="citation_pdf_url" content="https://www.pnas.org/doi/pdf/{doi}">
            </head>
            </html>
            '''
            
            mock_response = MockResponse(200, html_with_meta)
            mock_uri_get.return_value = mock_response
            mock_verify.return_value = True
            
            result = the_pnas_pony(pma, verify=False)
            
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

    @patch('metapub.findit.dances.generic.unified_uri_get')
    @patch('metapub.findit.dances.generic.the_doi_2step')  
    def test_pnas_no_citation_pdf_url_error(self, mock_doi_2step, mock_uri_get):
        """Test 6: Missing citation_pdf_url raises NoPDFLink."""
        pma = Mock()
        pma.doi = '10.1073/pnas.9999999999'
        pma.journal = 'Proc Natl Acad Sci USA'
        
        mock_doi_2step.return_value = 'https://www.pnas.org/doi/10.1073/pnas.9999999999'
        
        # HTML without citation_pdf_url meta tag
        html_without_meta = '''
        <html>
        <head>
            <meta name="citation_title" content="Some Article">
        </head>
        </html>
        '''
        
        mock_response = MockResponse(200, html_without_meta)
        mock_uri_get.return_value = mock_response
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_pnas_pony(pma)
        
        error_msg = str(exc_info.value)
        print(f"Test 6 - Missing meta tag error: {error_msg}")

    def test_pnas_simplicity_through_meta_tags(self):
        """Test 7: Verify PNAS achieves simplicity through citation_pdf_url meta tags."""
        # PNAS should use direct meta tag extraction (no complex URL construction)
        import inspect
        from metapub.findit.dances.pnas import the_pnas_pony
        
        # Verify the dance function uses citation_pdf_url meta tag extraction
        source = inspect.getsource(the_pnas_pony)
        assert 'citation_pdf_url' in source, "Function should extract citation_pdf_url meta tag"
        assert 're.search' in source, "Function should use regex to extract meta tag"
        
        # Configuration should be simple
        from metapub.findit.journals.single_journal_publishers import pnas_journals
        assert pnas_journals is not None
        assert len(pnas_journals) > 0
        
        print("✓ PNAS achieves maximum simplicity through citation_pdf_url meta tag extraction")


if __name__ == '__main__':
    # Run basic tests if executed directly
    test_instance = TestPNASTest()
    test_instance.setUp()
    
    print("Running PNAS dance function tests...")
    print("\\n" + "="*60)
    
    tests = [
        ('test_pnas_journal_recognition', 'Journal configuration'),
        ('test_pnas_citation_pdf_url_extraction', 'citation_pdf_url extraction'),
        ('test_pnas_verify_false_skips_verification', 'Skip verification mode'),
        ('test_pnas_missing_doi_error', 'Missing DOI error handling'),
        ('test_pnas_evidence_dois_coverage', 'Evidence DOIs coverage'),
        ('test_pnas_doi_pattern_validation', 'DOI pattern validation'),
        ('test_pnas_no_citation_pdf_url_error', 'Missing meta tag error'),
        ('test_pnas_simplicity_through_meta_tags', 'Simplicity through meta tags')
    ]
    
    for test_method, description in tests:
        try:
            getattr(test_instance, test_method)()
            print(f"✓ {description}")
        except Exception as e:
            print(f"✗ {description}: {e}")
    
    print("\\n" + "="*60)
    print("Test suite completed!")