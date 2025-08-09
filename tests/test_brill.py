#!/usr/bin/env python
"""
Test suite for Brill evidence-driven rewrite.

Tests the rewritten the_brill_bridge function based on evidence collection
showing perfect citation_pdf_url meta tags in HTML samples.

Evidence-based test data from HTML samples:
- https://brill.com/downloadpdf/view/journals/beh/158/11/article-p1007_4.pdf
- https://brill.com/downloadpdf/view/journals/beh/161/1/article-p71_5.pdf
"""

import unittest
from unittest.mock import patch, Mock

from metapub.findit.dances.brill import the_brill_bridge
from metapub.exceptions import NoPDFLink


class TestBrillRewrite(unittest.TestCase):
    """Test Brill evidence-driven rewrite functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Evidence-based test data from HTML sample analysis
        self.evidence_urls = {
            'sample1': 'https://brill.com/downloadpdf/view/journals/beh/158/11/article-p1007_4.pdf',
            'sample2': 'https://brill.com/downloadpdf/view/journals/beh/161/1/article-p71_5.pdf'
        }

    @patch('metapub.findit.dances.brill.the_doi_2step')
    @patch('metapub.findit.dances.brill.unified_uri_get')
    def test_brill_evidence_based_meta_tag_extraction(self, mock_get, mock_doi):
        """Test evidence-based citation_pdf_url meta tag extraction."""
        mock_pma = Mock()
        mock_pma.doi = '10.1163/1568539X-00003344'
        mock_doi.return_value = 'https://brill.com/view/journals/test'
        
        # Mock HTML response with evidence-based meta tag
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''<html><head>
            <meta name="citation_pdf_url" content="https://brill.com/downloadpdf/view/journals/beh/158/11/article-p1007_4.pdf" />
        </head></html>'''
        mock_get.return_value = mock_response
        
        result = the_brill_bridge(mock_pma, verify=False)
        self.assertEqual(result, 'https://brill.com/downloadpdf/view/journals/beh/158/11/article-p1007_4.pdf')

    @patch('metapub.findit.dances.brill.the_doi_2step') 
    @patch('metapub.findit.dances.brill.unified_uri_get')
    def test_brill_multiple_doi_prefixes_support(self, mock_get, mock_doi):
        """Test that rewritten function supports multiple DOI prefixes (not just 10.1163)."""
        test_dois = [
            '10.1163/1568539X-00003344',  # Brill's own prefix
            '10.1007/BF02381613',         # Springer (found in evidence)
            '10.1016/j.anbehav.2005.05.015',  # Elsevier (found in evidence)
            '10.1098/rstb.2012.0113'      # Royal Society (found in evidence)
        ]
        
        for doi in test_dois:
            with self.subTest(doi=doi):
                mock_pma = Mock()
                mock_pma.doi = doi
                mock_doi.return_value = f'https://brill.com/view/{doi}'
                
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.text = '''<meta name="citation_pdf_url" content="https://brill.com/downloadpdf/test.pdf" />'''
                mock_get.return_value = mock_response
                
                result = the_brill_bridge(mock_pma, verify=False)
                self.assertEqual(result, 'https://brill.com/downloadpdf/test.pdf')

    def test_brill_missing_doi_error(self):
        """Test handling when DOI is missing."""
        mock_pma = Mock()
        mock_pma.doi = None
        
        with self.assertRaises(NoPDFLink) as context:
            the_brill_bridge(mock_pma, verify=False)
        
        self.assertIn('MISSING: DOI required', str(context.exception))

    @patch('metapub.findit.dances.brill.the_doi_2step')
    @patch('metapub.findit.dances.brill.unified_uri_get')
    def test_brill_http_error_handling(self, mock_get, mock_doi):
        """Test handling of HTTP errors when accessing article page."""
        mock_pma = Mock()
        mock_pma.doi = '10.1163/test'
        mock_doi.return_value = 'https://brill.com/article/test'
        
        # Test various HTTP error codes
        error_codes = [404, 500, 403]
        for code in error_codes:
            with self.subTest(status_code=code):
                mock_response = Mock()
                mock_response.status_code = code
                mock_get.return_value = mock_response
                
                with self.assertRaises(NoPDFLink) as context:
                    the_brill_bridge(mock_pma, verify=False)
                
                self.assertIn('TXERROR: Could not access', str(context.exception))

    @patch('metapub.findit.dances.brill.the_doi_2step')
    @patch('metapub.findit.dances.brill.unified_uri_get')
    def test_brill_missing_meta_tag_error(self, mock_get, mock_doi):
        """Test handling when citation_pdf_url meta tag is missing."""
        mock_pma = Mock()
        mock_pma.doi = '10.1163/test'
        mock_doi.return_value = 'https://brill.com/article/test'
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><head><title>Test</title></head></html>'
        mock_get.return_value = mock_response
        
        with self.assertRaises(NoPDFLink) as context:
            the_brill_bridge(mock_pma, verify=False)
        
        self.assertIn('MISSING: No PDF URL found', str(context.exception))

    @patch('metapub.findit.dances.brill.the_doi_2step')
    @patch('metapub.findit.dances.brill.verify_pdf_url')
    @patch('metapub.findit.dances.brill.unified_uri_get')
    def test_brill_verify_mode_calls_verification(self, mock_get, mock_verify, mock_doi):
        """Test that verify=True calls PDF URL verification."""
        mock_pma = Mock()
        mock_pma.doi = '10.1163/test'
        mock_doi.return_value = 'https://brill.com/article/test'
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''<meta name="citation_pdf_url" content="https://brill.com/test.pdf" />'''
        mock_get.return_value = mock_response
        
        result = the_brill_bridge(mock_pma, verify=True)
        
        mock_verify.assert_called_once_with('https://brill.com/test.pdf', 'Brill')
        self.assertEqual(result, 'https://brill.com/test.pdf')

    @patch('metapub.findit.dances.brill.the_doi_2step')
    @patch('metapub.findit.dances.brill.unified_uri_get')
    def test_brill_verify_false_skips_verification(self, mock_get, mock_doi):
        """Test that verify=False skips PDF URL verification."""
        mock_pma = Mock()
        mock_pma.doi = '10.1163/test'
        mock_doi.return_value = 'https://brill.com/article/test'
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''<meta name="citation_pdf_url" content="https://brill.com/test.pdf" />'''
        mock_get.return_value = mock_response
        
        result = the_brill_bridge(mock_pma, verify=False)
        self.assertEqual(result, 'https://brill.com/test.pdf')

    def test_evidence_based_url_patterns(self):
        """Test that evidence URLs follow expected Brill patterns."""
        for sample, url in self.evidence_urls.items():
            with self.subTest(sample=sample):
                self.assertIn('brill.com', url)
                self.assertIn('downloadpdf', url)
                self.assertTrue(url.endswith('.pdf'))
                self.assertTrue(url.startswith('https://'))

    def test_function_line_count_compliance(self):
        """Test that rewritten function meets DANCE_FUNCTION_GUIDELINES line count."""
        import inspect
        source_lines = inspect.getsource(the_brill_bridge).split('\n')
        
        # Count non-empty, non-comment lines
        code_lines = [line for line in source_lines 
                     if line.strip() and not line.strip().startswith('#') and not line.strip().startswith('"""')]
        
        # Should be under 50 lines per guidelines (rewritten from 104 lines)
        self.assertLess(len(code_lines), 50, f"Function has {len(code_lines)} lines, should be under 50")

    @patch('metapub.findit.dances.brill.the_doi_2step')
    @patch('metapub.findit.dances.brill.unified_uri_get')
    def test_brill_evidence_doi_coverage(self, mock_get, mock_doi):
        """Test function works with DOI prefixes found in evidence."""
        evidence_prefixes = ['10.1007', '10.1016', '10.1023', '10.1037', '10.1038', 
                           '10.1046', '10.1073', '10.1086', '10.1098', '10.1111', 
                           '10.1126', '10.1159', '10.1163']
        
        for prefix in evidence_prefixes[:5]:  # Test first 5 for performance
            with self.subTest(prefix=prefix):
                mock_pma = Mock()
                mock_pma.doi = f'{prefix}/test.article'
                mock_doi.return_value = f'https://brill.com/article/{prefix}/test'
                
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.text = f'''<meta name="citation_pdf_url" content="https://brill.com/downloadpdf/{prefix.replace(".", "")}/test.pdf" />'''
                mock_get.return_value = mock_response
                
                result = the_brill_bridge(mock_pma, verify=False)
                self.assertIn('brill.com/downloadpdf', result)


if __name__ == '__main__':
    unittest.main()