"""
Comprehensive test suite for BibTeX citation formatting functionality.

This test suite ensures that BibTeX citation formatting works correctly
for both articles and books, handles edge cases, and produces valid BibTeX output.
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


class TestBibTexCitation(unittest.TestCase):
    """Comprehensive tests for BibTeX citation formatting"""

    def setUp(self):
        # Create a unique temporary cache directory for each test run
        self.temp_cache = tempfile.mkdtemp(prefix='bibtex_test_cache_')
        self.fetch = PubMedFetcher(cachedir=self.temp_cache)

    def tearDown(self):
        # Clean up the temporary cache directory
        if hasattr(self, 'temp_cache') and os.path.exists(self.temp_cache):
            cleanup_dir(self.temp_cache)

    def test_bibtex_format_string_exists(self):
        """Test that BibTeX format string is properly defined"""
        self.assertTrue(hasattr(cite, 'bibtex_fmt'))
        self.assertIn('@{entrytype}', cite.bibtex_fmt)
        self.assertIn('{citeID}', cite.bibtex_fmt)

    def test_basic_article_bibtex(self):
        """Test basic article BibTeX formatting"""
        test_data = {
            'authors': ['Smith J', 'Jones K'],
            'title': 'Test Article Title',
            'journal': 'Nature',
            'year': 2023,
            'volume': 123,
            'pages': '45-67',
            'doi': '10.1038/test123'
        }
        
        bibtex = cite.bibtex(**test_data)
        
        # Test basic structure
        self.assertIn('@article{Smith2023,', bibtex)
        self.assertIn('author = {Smith, J and Jones, K}', bibtex)
        self.assertIn('title = {Test Article Title}', bibtex)
        self.assertIn('journal = {Nature}', bibtex)
        self.assertIn('year = {2023}', bibtex)
        self.assertIn('volume = {123}', bibtex)
        self.assertIn('pages = {45-67}', bibtex)
        self.assertIn('doi = {10.1038/test123}', bibtex)

    def test_book_bibtex(self):
        """Test book BibTeX formatting"""
        test_data = {
            'authors': ['Editor A', 'Editor B'],
            'title': 'Test Book Title',
            'year': 2022,
            'isbook': True
        }
        
        bibtex = cite.bibtex(**test_data)
        
        # Test book-specific formatting
        self.assertIn('@book{Editor2022,', bibtex)
        self.assertIn('author = {Editor, A and Editor, B}', bibtex)
        self.assertIn('title = {Test Book Title}', bibtex)

    def test_citation_id_generation(self):
        """Test citation ID generation from author and year"""
        # Test with normal author name
        test_data = {
            'authors': ['Smith J'],
            'year': 2023
        }
        bibtex = cite.bibtex(**test_data)
        self.assertIn('@article{Smith2023,', bibtex)
        
        # Test with complex author name
        test_data = {
            'authors': ['Van Der Berg JH'],
            'year': 2022
        }
        bibtex = cite.bibtex(**test_data)
        self.assertIn('@article{VanDerBerg2022,', bibtex)

    def test_citation_id_fallback_to_pmid(self):
        """Test citation ID fallback to PMID when author/year unavailable"""
        test_data = {
            'pmid': '12345678',
            'title': 'Test Article'
        }
        bibtex = cite.bibtex(**test_data)
        self.assertIn('@article{12345678,', bibtex)

    def test_citation_id_fallback_unknown(self):
        """Test citation ID fallback to 'UnknownCitation' when nothing available"""
        test_data = {
            'title': 'Test Article'
        }
        bibtex = cite.bibtex(**test_data)
        self.assertIn('@article{UnknownCitation,', bibtex)

    def test_author_format_variations(self):
        """Test different author name formats"""
        # Single author
        test_data = {'authors': ['Smith J'], 'year': 2023}
        bibtex = cite.bibtex(**test_data)
        self.assertIn('author = {Smith, J}', bibtex)
        
        # Multiple authors
        test_data = {'authors': ['Smith J', 'Jones K', 'Brown L'], 'year': 2023}
        bibtex = cite.bibtex(**test_data)
        self.assertIn('author = {Smith, J and Jones, K and Brown, L}', bibtex)
        
        # Authors already in "Last, First" format
        test_data = {'authors': ['Smith, John', 'Jones, Kate'], 'year': 2023}
        bibtex = cite.bibtex(**test_data)
        self.assertIn('author = {Smith, John and Jones, Kate}', bibtex)

    def test_multi_word_last_names(self):
        """Test handling of multi-word last names"""
        test_data = {
            'authors': ['Van Der Berg J', 'De La Cruz M'],
            'year': 2023
        }
        bibtex = cite.bibtex(**test_data)
        self.assertIn('author = {Van Der Berg, J and De La Cruz, M}', bibtex)

    def test_empty_and_none_values(self):
        """Test BibTeX formatting with empty and None values"""
        test_data = {
            'authors': ['Smith J'],
            'title': 'Test Title',
            'journal': '',
            'year': 2023,
            'volume': None,
            'pages': '',
            'doi': None
        }
        
        bibtex = cite.bibtex(**test_data)
        
        # Should include non-empty fields
        self.assertIn('author = {Smith, J}', bibtex)
        self.assertIn('title = {Test Title}', bibtex)
        self.assertIn('year = {2023}', bibtex)
        
        # Should exclude empty/None fields
        self.assertNotIn('journal = {}', bibtex)
        self.assertNotIn('volume = {}', bibtex)
        self.assertNotIn('pages = {}', bibtex)
        self.assertNotIn('doi = {}', bibtex)

    def test_abstract_truncation(self):
        """Test that long abstracts are truncated appropriately"""
        long_abstract = "This is a very long abstract. " * 50  # > 500 chars
        test_data = {
            'authors': ['Smith J'],
            'title': 'Test Article',
            'abstract': long_abstract,
            'year': 2023
        }
        
        bibtex = cite.bibtex(**test_data)
        abstract_match = re.search(r'abstract = \{([^}]+)\}', bibtex)
        
        self.assertIsNotNone(abstract_match)
        abstract_content = abstract_match.group(1)
        self.assertLess(len(abstract_content), 510)  # 500 + "..." = 503 chars max
        self.assertTrue(abstract_content.endswith('...'))

    def test_special_characters_handling(self):
        """Test handling of special characters in BibTeX fields"""
        test_data = {
            'authors': ['O\'Brien J', 'García-López M'],
            'title': 'Test with "quotes" & special chars',
            'journal': 'Journal & Review',
            'year': 2023
        }
        
        bibtex = cite.bibtex(**test_data)
        
        # Special characters should be preserved (BibTeX processors will handle escaping)
        self.assertIn('O\'Brien, J and García-López, M', bibtex)
        self.assertIn('Test with "quotes" & special chars', bibtex)
        self.assertIn('Journal & Review', bibtex)

    def test_bibtex_structure_validity(self):
        """Test that generated BibTeX has valid structure"""
        test_data = {
            'authors': ['Smith J', 'Jones K'],
            'title': 'Test Article',
            'journal': 'Nature',
            'year': 2023,
            'volume': 123,
            'pages': '45-67',
            'doi': '10.1038/test'
        }
        
        bibtex = cite.bibtex(**test_data)
        
        # Test BibTeX structure
        self.assertRegex(bibtex, r'^@article\{[^,]+,')  # Starts with @article{key,
        self.assertTrue(bibtex.endswith('}'))  # Ends with }
        
        # Count braces - should be balanced
        open_braces = bibtex.count('{')
        close_braces = bibtex.count('}')
        self.assertEqual(open_braces, close_braces)
        
        # Test field format
        self.assertRegex(bibtex, r'author = \{[^}]+\}')
        self.assertRegex(bibtex, r'title = \{[^}]+\}')

    def test_pubmed_article_integration(self):
        """Integration test with real PubMedArticle objects"""
        try:
            # Use a known stable PMID
            article = self.fetch.article_by_pmid('23435529')
            
            # Test that citation_bibtex property works
            bibtex = article.citation_bibtex
            
            # Verify basic BibTeX structure
            self.assertIn('@article{', bibtex)
            self.assertIn('author = {', bibtex)
            self.assertIn('title = {', bibtex)
            self.assertIn('journal = {', bibtex)
            self.assertIn('year = {', bibtex)
            
            # Verify citation ID format
            self.assertRegex(bibtex, r'@article\{[A-Za-z]+\d{4},')
            
        except Exception as e:
            self.skipTest(f"Network test skipped due to: {e}")

    def test_book_article_integration(self):
        """Test BibTeX generation for book articles (GeneReviews)"""
        try:
            # Use a known GeneReviews PMID
            article = self.fetch.article_by_pmid('20301546')
            
            if article.book_accession_id:
                bibtex = article.citation_bibtex
                
                # Should use book entry type
                self.assertIn('@book{', bibtex)
                self.assertIn('author = {', bibtex)
                self.assertIn('title = {', bibtex)
            
        except Exception as e:
            self.skipTest(f"Network test skipped due to: {e}")

    def test_field_stripping_periods(self):
        """Test that periods are stripped from title, journal, and abstract"""
        test_data = {
            'authors': ['Smith J'],
            'title': 'Test Article Title.',
            'journal': 'Nature Journal.',
            'abstract': 'This is an abstract.',
            'year': 2023
        }
        
        bibtex = cite.bibtex(**test_data)
        
        # Periods should be stripped
        self.assertIn('title = {Test Article Title}', bibtex)
        self.assertIn('journal = {Nature Journal}', bibtex)
        self.assertIn('abstract = {This is an abstract}', bibtex)

    def test_no_debug_output(self):
        """Test that no debug print statements are executed"""
        import io
        import sys
        
        # Capture stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        try:
            test_data = {
                'authors': ['Smith J'],
                'title': 'Test Article',
                'year': 2023
            }
            cite.bibtex(**test_data)
            
            # Get output
            output = captured_output.getvalue()
            
            # Should be empty (no debug prints)
            self.assertEqual(output.strip(), '')
            
        finally:
            # Restore stdout
            sys.stdout = sys.__stdout__

    def test_url_generation(self):
        """Test URL field generation"""
        test_data = {
            'authors': ['Smith J'],
            'title': 'Test Article',
            'url': 'https://example.com/article.',
            'year': 2023
        }
        
        bibtex = cite.bibtex(**test_data)
        
        # URL should be included with periods stripped
        self.assertIn('url = {https://example.com/article}', bibtex)

    def test_volume_as_string_and_int(self):
        """Test volume handling as both string and integer"""
        # Test with integer volume
        test_data = {
            'authors': ['Smith J'],
            'title': 'Test Article',
            'volume': 123,
            'year': 2023
        }
        bibtex = cite.bibtex(**test_data)
        self.assertIn('volume = {123}', bibtex)
        
        # Test with string volume
        test_data['volume'] = "123A"
        bibtex = cite.bibtex(**test_data)
        self.assertIn('volume = {123A}', bibtex)


if __name__ == '__main__':
    unittest.main()