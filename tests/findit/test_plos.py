"""
Evidence-based tests for PLOS (Public Library of Science) dance function.

Based on HTML sample analysis showing perfect citation_pdf_url meta tags:
- Pattern: https://journals.plos.org/[journal]/article/file?id=[DOI]&type=printable
- DOI format: 10.1371/journal.[code] (consistent across all journals)
- 100% reliable citation_pdf_url meta tag extraction
- Open access publisher - no paywalls

This represents the ideal case for reducing logical complication.
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

from metapub.findit.dances.plos import the_plos_pogo
from metapub.exceptions import NoPDFLink


class MockResponse:
    """Mock HTTP response for testing."""
    def __init__(self, status_code=200, text=''):
        self.status_code = status_code
        self.text = text


class TestPLOSTest(BaseDanceTest):
    """Evidence-based test cases for PLOS (Public Library of Science) journals."""

    def setUp(self):
        """Set up test fixtures.""" 
        super().setUp()

    def test_plos_journal_recognition(self):
        """Test that PLOS journals are properly recognized in the registry."""
        # Test the function directly with known PLOS patterns rather than registry lookup
        # since registry may not be populated during tests
        
        from metapub.findit.journals.plos import plos_journals
        
        # Verify PLOS configuration
        assert len(plos_journals) > 0, "PLOS journals list should not be empty"
        
        # Check some expected PLOS journals are in the list
        expected_journals = ['PLoS Biol', 'PLoS One', 'PLoS Comput Biol']
        found_journals = []
        
        for expected in expected_journals:
            if expected in plos_journals:
                found_journals.append(expected)
                print(f"✓ {expected} found in PLOS journals list")
        
        assert len(found_journals) > 0, f"Should find at least some expected journals, found: {found_journals}"
        print(f"✓ Found {len(found_journals)} expected PLOS journals in configuration")

    @patch('metapub.findit.dances.plos.verify_pdf_url')
    @patch('metapub.findit.dances.plos.unified_uri_get')
    @patch('metapub.findit.dances.plos.the_doi_2step')
    def test_plos_citation_pdf_url_extraction(self, mock_doi_2step, mock_uri_get, mock_verify):
        """Test 1: Perfect citation_pdf_url meta tag extraction."""
        # Mock PMA with real DOI from HTML sample
        pma = Mock()
        pma.doi = '10.1371/journal.pbio.3001547'  # From evidence sample
        pma.journal = 'PLoS Biol'
        
        # Mock the DOI resolution and HTML response
        mock_doi_2step.return_value = 'https://journals.plos.org/plosbiology/article?id=10.1371/journal.pbio.3001547'
        
        # Mock HTML with citation_pdf_url meta tag (from actual sample)
        html_with_meta = '''
        <html>
        <head>
            <meta name="citation_pdf_url" content="https://journals.plos.org/plosbiology/article/file?id=10.1371/journal.pbio.3001547&type=printable">
        </head>
        </html>
        '''
        
        mock_response = MockResponse(200, html_with_meta)
        mock_uri_get.return_value = mock_response
        mock_verify.return_value = True
        
        result = the_plos_pogo(pma, verify=True)
        
        # Verify the extracted URL
        expected_url = 'https://journals.plos.org/plosbiology/article/file?id=10.1371/journal.pbio.3001547&type=printable'
        assert result == expected_url
        
        # Verify function calls
        mock_doi_2step.assert_called_once_with('10.1371/journal.pbio.3001547')
        mock_uri_get.assert_called_once()
        mock_verify.assert_called_once_with(expected_url, 'PLOS')
        
        print(f"Test 1 - citation_pdf_url extraction: {result}")

    @patch('metapub.findit.dances.plos.unified_uri_get')
    @patch('metapub.findit.dances.plos.the_doi_2step')
    def test_plos_verify_false_skips_verification(self, mock_doi_2step, mock_uri_get):
        """Test 2: verify=False skips PDF verification."""
        pma = Mock()
        pma.doi = '10.1371/journal.pcbi.1012441'  # From evidence sample
        pma.journal = 'PLoS Comput Biol'
        
        mock_doi_2step.return_value = 'https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1012441'
        
        html_with_meta = '''
        <html>
        <head>
            <meta name="citation_pdf_url" content="https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1012441&type=printable">
        </head>
        </html>
        '''
        
        mock_response = MockResponse(200, html_with_meta)
        mock_uri_get.return_value = mock_response
        
        result = the_plos_pogo(pma, verify=False)
        
        expected_url = 'https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1012441&type=printable'
        assert result == expected_url
        
        print(f"Test 2 - Skip verification: {result}")


    @patch('metapub.findit.dances.plos.unified_uri_get')
    @patch('metapub.findit.dances.plos.the_doi_2step')
    def test_plos_http_error_handling(self, mock_doi_2step, mock_uri_get):
        """Test 4: HTTP error handling."""
        pma = Mock()
        pma.doi = '10.1371/journal.test.error'
        pma.journal = 'PLoS Test'
        
        mock_doi_2step.return_value = 'https://example.com/error'
        mock_uri_get.return_value = MockResponse(404)
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_plos_pogo(pma)
        
        error_msg = str(exc_info.value)
        assert 'TXERROR: Could not access PLOS article page (HTTP 404)' in error_msg
        print(f"Test 4 - HTTP error: {error_msg}")

    @patch('metapub.findit.dances.plos.unified_uri_get')
    @patch('metapub.findit.dances.plos.the_doi_2step')
    def test_plos_missing_citation_meta_error(self, mock_doi_2step, mock_uri_get):
        """Test 5: Missing citation_pdf_url meta tag error."""
        pma = Mock()
        pma.doi = '10.1371/journal.test.nometa'
        pma.journal = 'PLoS Test'
        
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
            the_plos_pogo(pma)
        
        error_msg = str(exc_info.value)
        assert 'MISSING: No citation_pdf_url found' in error_msg
        print(f"Test 5 - Missing meta tag error: {error_msg}")

    @patch('metapub.findit.dances.plos.verify_pdf_url')
    @patch('metapub.findit.dances.plos.unified_uri_get')
    @patch('metapub.findit.dances.plos.the_doi_2step')
    def test_plos_evidence_dois_coverage(self, mock_doi_2step, mock_uri_get, mock_verify):
        """Test 6: Coverage of all evidence DOIs from HTML samples."""
        evidence_dois = [
            '10.1371/journal.pbio.3001547',   # Sample 1 - PLoS Biology
            '10.1371/journal.pbio.3002554',   # Sample 2 - PLoS Biology
            '10.1371/journal.pcbi.1012441',   # Sample 3 - PLoS Computational Biology
            '10.1371/journal.pcbi.1012632',   # Sample 4 - PLoS Computational Biology
        ]
        
        for i, doi in enumerate(evidence_dois):
            pma = Mock()
            pma.doi = doi
            pma.journal = 'PLoS Biol' if 'pbio' in doi else 'PLoS Comput Biol'
            
            # Mock the responses
            mock_doi_2step.return_value = f'https://journals.plos.org/test/article?id={doi}'
            
            expected_url = f'https://journals.plos.org/test/article/file?id={doi}&type=printable'
            html_with_meta = f'''
            <html>
            <head>
                <meta name="citation_pdf_url" content="{expected_url}">
            </head>
            </html>
            '''
            
            mock_uri_get.return_value = MockResponse(200, html_with_meta)
            mock_verify.return_value = True
            
            result = the_plos_pogo(pma, verify=False)
            
            # Verify URL construction for each evidence DOI
            assert result == expected_url
            assert doi in result
            
            print(f"✓ Evidence DOI {doi}: {result}")





if __name__ == '__main__':
    # Run basic tests if executed directly
    test_instance = TestPLOSTest()
    test_instance.setUp()
    
    print("Running PLOS dance function tests...")
    print("\\n" + "="*60)
    
    tests = [
        ('test_plos_journal_recognition', 'Journal recognition in registry'),
        ('test_plos_citation_pdf_url_extraction', 'citation_pdf_url extraction'),
        ('test_plos_verify_false_skips_verification', 'Skip verification mode'),
        ('test_plos_missing_doi_error', 'Missing DOI error handling'),
        ('test_plos_http_error_handling', 'HTTP error handling'),
        ('test_plos_missing_citation_meta_error', 'Missing meta tag error'),
        ('test_plos_evidence_dois_coverage', 'Evidence DOIs coverage'),
        ('test_plos_doi_pattern_validation', 'DOI pattern validation'),
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