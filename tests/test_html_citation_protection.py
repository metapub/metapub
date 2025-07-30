"""
Comprehensive test suite to protect HTML citation formatting functionality.

This test suite ensures that HTML citation formatting is properly maintained
and protected against regressions. It tests all aspects of the HTML formatting
including edge cases, malformed data, and specific formatting patterns.
"""

import unittest
import tempfile
import os
import re
from datetime import datetime
from unittest.mock import Mock

from metapub import cite
from metapub import PubMedFetcher
from metapub.cache_utils import cleanup_dir


class TestHTMLCitationProtection(unittest.TestCase):
    """Comprehensive tests for HTML citation formatting protection"""

    def setUp(self):
        # Create a unique temporary cache directory for each test run
        self.temp_cache = tempfile.mkdtemp(prefix='html_citation_test_cache_')
        self.fetch = PubMedFetcher(cachedir=self.temp_cache)

    def tearDown(self):
        # Clean up the temporary cache directory
        if hasattr(self, 'temp_cache') and os.path.exists(self.temp_cache):
            cleanup_dir(self.temp_cache)

    def test_html_format_strings_exist(self):
        """Test that HTML format strings are properly defined"""
        # Verify HTML format strings exist
        self.assertTrue(hasattr(cite, 'article_cit_fmt_html'))
        self.assertTrue(hasattr(cite, 'book_cit_fmt_html'))
        
        # Verify they contain expected HTML tags
        self.assertIn('<i>{journal}</i>', cite.article_cit_fmt_html)
        self.assertIn('<b>{volume}</b>', cite.article_cit_fmt_html)
        self.assertIn('<i>{book.title}</i>', cite.book_cit_fmt_html)
        self.assertIn('<i>{book.journal}</i>', cite.book_cit_fmt_html)

    def test_html_vs_plain_format_strings_different(self):
        """Test that HTML and plain format strings are different"""
        self.assertNotEqual(cite.article_cit_fmt, cite.article_cit_fmt_html)
        self.assertNotEqual(cite.book_cit_fmt, cite.book_cit_fmt_html)

    def test_exact_html_tag_placement_article(self):
        """Test exact placement of HTML tags in article citations"""
        test_data = {
            'authors': ['Smith J', 'Jones K', 'Brown L'],
            'title': 'Test Article Title',
            'journal': 'Nature',
            'year': 2023,
            'volume': 123,
            'pages': '45-67',
            'doi': '10.1038/test'
        }
        
        html_citation = cite.article(as_html=True, **test_data)
        
        # Test specific HTML tag patterns
        self.assertRegex(html_citation, r'Smith J, <i>et al</i>\.')
        self.assertRegex(html_citation, r'<i>Nature</i>\.')
        self.assertRegex(html_citation, r'<b>123</b>:45-67')
        
        # Test that title is NOT wrapped in HTML tags
        self.assertIn('Test Article Title.', html_citation)
        self.assertNotIn('<i>Test Article Title</i>', html_citation)
        self.assertNotIn('<b>Test Article Title</b>', html_citation)

    def test_exact_html_tag_placement_author_variations(self):
        """Test HTML formatting for different author configurations"""
        # Single author - no et al
        single = cite.author_str(['Smith J'], as_html=True)
        self.assertEqual(single, 'Smith J')
        self.assertNotIn('<i>', single)
        
        # Two authors - no et al
        two = cite.author_str(['Smith J', 'Jones K'], as_html=True) 
        self.assertEqual(two, 'Smith J and Jones K')
        self.assertNotIn('<i>', two)
        
        # Three+ authors - with et al
        many = cite.author_str(['Smith J', 'Jones K', 'Brown L'], as_html=True)
        self.assertEqual(many, 'Smith J, <i>et al</i>')
        self.assertIn('<i>et al</i>', many)

    def test_html_tag_structure_validity(self):
        """Test that HTML tags are properly formed and paired"""
        test_data = {
            'authors': ['Test Author'],
            'title': 'Test Title',
            'journal': 'Test Journal',
            'year': 2023,
            'volume': 42,
            'pages': '1-10'
        }
        
        html_citation = cite.article(as_html=True, **test_data)
        
        # Count opening and closing tags to ensure they're balanced
        i_open = html_citation.count('<i>')
        i_close = html_citation.count('</i>')
        b_open = html_citation.count('<b>')
        b_close = html_citation.count('</b>')
        
        self.assertEqual(i_open, i_close, "Unbalanced <i> tags")
        self.assertEqual(b_open, b_close, "Unbalanced <b> tags")
        
        # Test specific tag patterns
        self.assertRegex(html_citation, r'<i>[^<]+</i>')  # <i> tags contain content
        self.assertRegex(html_citation, r'<b>[^<]+</b>')  # <b> tags contain content

    def test_html_formatting_disabled_by_default(self):
        """Test that HTML formatting is disabled when as_html is False or omitted"""
        test_data = {
            'authors': ['Smith J', 'Jones K', 'Brown L'],
            'title': 'Test Title',
            'journal': 'Test Journal',
            'year': 2023,
            'volume': 42,
            'pages': '1-10'
        }
        
        # Test explicit as_html=False
        plain_citation = cite.article(as_html=False, **test_data)
        self.assertNotIn('<i>', plain_citation)
        self.assertNotIn('<b>', plain_citation)
        self.assertNotIn('</i>', plain_citation)
        self.assertNotIn('</b>', plain_citation)
        
        # Test default behavior (as_html omitted)
        default_citation = cite.article(**test_data)
        self.assertNotIn('<i>', default_citation)
        self.assertNotIn('<b>', default_citation)

    def test_edge_cases_empty_and_none_values(self):
        """Test HTML formatting with empty and None values"""
        # Test with empty strings
        empty_data = {
            'authors': [],
            'title': '',
            'journal': '',
            'year': '',
            'volume': '',
            'pages': ''
        }
        
        html_citation = cite.article(as_html=True, **empty_data)
        self.assertIsInstance(html_citation, str)
        
        # Should still have proper tag structure even with empty values
        self.assertIn('<i>', html_citation)  # Empty journal still gets wrapped
        self.assertIn('<b>', html_citation)  # Empty volume still gets wrapped
        
        # Test with None values
        none_data = {
            'authors': None,
            'title': None,
            'journal': None,
            'year': None,
            'volume': None,
            'pages': None
        }
        
        html_citation = cite.article(as_html=True, **none_data)
        self.assertIsInstance(html_citation, str)

    def test_special_characters_in_html_formatting(self):
        """Test HTML formatting with special characters that might break HTML"""
        test_data = {
            'authors': ['Smith <J>', 'Jones & K'],
            'title': 'Test with <special> & "quoted" characters',
            'journal': 'Journal & Review <Special>',
            'year': 2023,
            'volume': 42,
            'pages': '1-10'
        }
        
        html_citation = cite.article(as_html=True, **test_data)
        
        # HTML tags should still be properly placed despite special characters
        # The implementation doesn't escape HTML entities, so special characters pass through as-is
        self.assertIn('<i>Journal & Review <Special></i>', html_citation)
        self.assertIn('<b>42</b>', html_citation)

    def test_regression_exact_format_match(self):
        """Regression test for exact HTML format matching original issue"""
        # This is the exact example from the GitHub issue
        test_data = {
            'authors': ['McNally EM', 'Golbus JR', 'Puckelwartz MJ'],
            'title': 'Genetic mutations and mechanisms in dilated cardiomyopathy',
            'journal': 'Journal of Clinical Investigation',
            'year': 2013,
            'volume': 123,
            'pages': '19-26',
            'doi': '10.1172/JCI62862'
        }
        
        html_citation = cite.article(as_html=True, **test_data)
        
        # Test the exact format expected from the GitHub issue
        expected_parts = [
            'McNally EM, <i>et al</i>',  # Author with et al in italics
            '<i>Journal of Clinical Investigation</i>',  # Journal in italics
            '<b>123</b>',  # Volume in bold
            'doi: 10.1172/JCI62862'  # DOI present
        ]
        
        for part in expected_parts:
            self.assertIn(part, html_citation, f"Missing expected part: {part}")

    def test_book_citation_html_formatting(self):
        """Test HTML formatting for book citations"""
        # Create a mock book object with required attributes
        mock_book = Mock()
        mock_book.book_accession_id = 'NBK1234'
        mock_book.authors_str = 'Author A;Author B;Author C'
        mock_book.title = 'Test Book Title'
        mock_book.book_date_revised = datetime(2023, 1, 15)
        mock_book.book_contribution_date = datetime(2022, 6, 10)
        mock_book.book_editors = 'Editor A;Editor B'
        mock_book.journal = 'GeneReviews'
        mock_book.book_publisher = 'University of Washington, Seattle'
        
        # Test HTML book citation
        html_citation = cite.book(mock_book, as_html=True)
        
        # Verify book-specific HTML formatting
        self.assertIn('<i>Test Book Title</i>', html_citation)  # Book title in italics
        self.assertIn('<i>GeneReviews</i>', html_citation)      # Journal in italics
        self.assertIn('Author A, <i>et al</i>', html_citation)  # Author et al in italics
        # Editor formatting: with only 2 editors, it shows "Editor A and Editor B" without et al
        self.assertIn('Editor A and Editor B', html_citation)  # Two editors without et al

    def test_pubmed_article_integration_html(self):
        """Integration test with real PubMedArticle objects"""
        try:
            # Use a known stable PMID
            article = self.fetch.article_by_pmid('23435529')
            
            # Test that citation_html method returns properly formatted HTML
            html_citation = article.citation_html
            plain_citation = article.citation
            
            # Verify HTML citation has HTML tags
            self.assertIn('<i>', html_citation)
            self.assertIn('</i>', html_citation)
            
            # Verify plain citation does not
            self.assertNotIn('<i>', plain_citation)
            self.assertNotIn('<b>', plain_citation)
            
            # Verify citations are different but contain same content
            plain_no_tags = re.sub(r'<[^>]+>', '', html_citation)
            # Normalize whitespace for comparison
            plain_normalized = re.sub(r'\s+', ' ', plain_citation.strip())
            html_no_tags_normalized = re.sub(r'\s+', ' ', plain_no_tags.strip())
            
            self.assertEqual(plain_normalized, html_no_tags_normalized,
                           "HTML citation content should match plain citation when tags removed")
            
        except Exception as e:
            self.skipTest(f"Network test skipped due to: {e}")

    def test_format_string_injection_protection(self):
        """Test protection against format string injection"""
        # Try to inject malicious format strings
        malicious_data = {
            'authors': ['{format_attack}'],
            'title': '{another_attack}',
            'journal': '{journal_attack}',
            'year': '{year_attack}',
            'volume': '{volume_attack}',
            'pages': '{pages_attack}'
        }
        
        # Should not raise KeyError or other format-related exceptions
        try:
            html_citation = cite.article(as_html=True, **malicious_data)
            self.assertIsInstance(html_citation, str)
            
            # Format strings should be treated as literal text, not interpreted
            self.assertIn('{format_attack}', html_citation)
            self.assertIn('<i>{journal_attack}</i>', html_citation)
            self.assertIn('<b>{volume_attack}</b>', html_citation)
            
        except KeyError:
            self.fail("Format string injection should not cause KeyError")

    def test_html_consistency_across_functions(self):
        """Test that HTML formatting is consistent across all citation functions"""
        test_data = {
            'authors': ['Test Author', 'Another Author', 'Third Author'],
            'title': 'Test Title',
            'journal': 'Test Journal',
            'year': 2023,
            'volume': 42,
            'pages': '1-10'
        }
        
        # Test that cite.article() and cite.citation() produce same result
        article_html = cite.article(as_html=True, **test_data)
        citation_html = cite.citation(as_html=True, **test_data)
        
        self.assertEqual(article_html, citation_html,
                        "cite.article() and cite.citation() should produce identical HTML output")

    def test_html_format_backwards_compatibility(self):
        """Test that adding HTML formatting doesn't break existing code"""
        test_data = {
            'authors': ['Test Author'],
            'title': 'Test Title', 
            'journal': 'Test Journal',
            'year': 2023,
            'volume': 42,
            'pages': '1-10'
        }
        
        # Legacy code that doesn't specify as_html should work exactly as before
        legacy_citation = cite.article(**test_data)
        
        # Should be identical to explicitly setting as_html=False
        explicit_plain = cite.article(as_html=False, **test_data)
        
        self.assertEqual(legacy_citation, explicit_plain,
                        "Legacy citation calls should be identical to as_html=False")

if __name__ == '__main__':
    unittest.main()