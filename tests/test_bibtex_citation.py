"""
Comprehensive test suite for BibTeX citation formatting functionality.

This test suite ensures that BibTeX citation formatting works correctly
for both articles and books, handles edge cases, and produces valid BibTeX output.
"""

import unittest
import os
import re
from datetime import datetime
from unittest.mock import Mock

from metapub import cite
from metapub.pubmedarticle import PubMedArticle
from .test_compat import skip_network_tests


class TestBibTexCitation(unittest.TestCase):
    """Comprehensive tests for BibTeX citation formatting"""

    def _load_test_article(self, pmid):
        """Load a PubMedArticle from static XML test data"""
        test_data_dir = os.path.join(os.path.dirname(__file__), 'test_data')
        xml_file = os.path.join(test_data_dir, f'sample_article_{pmid}.xml')
        
        with open(xml_file, 'r') as f:
            xml_content = f.read()
        
        return PubMedArticle(xml_content)

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
        """Test with PubMedArticle objects using static data"""
        # Load test article from static XML data
        article = self._load_test_article('23435529')
        
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
        
        # Verify specific content from our test article
        self.assertIn('Fossella, F', bibtex)
        self.assertIn('J. Clin. Oncol', bibtex)
        self.assertIn('2013', bibtex)

    def test_book_article_integration(self):
        """Test BibTeX generation for book articles using real GeneReviews data"""
        # Load real GeneReviews book article from static XML data
        article = self._load_test_article('20301577')
        
        # Test that citation_bibtex property works for book articles
        bibtex = article.citation_bibtex
        
        # Should use book entry type
        self.assertIn('@book{', bibtex)
        self.assertIn('author = {', bibtex)
        self.assertIn('title = {', bibtex)
        
        # Verify specific content from our test GeneReviews article
        self.assertIn('Napolitano, C and Priori, SG', bibtex)
        self.assertIn('CACNA1C-Related Disorders', bibtex)
        self.assertIn('GeneReviews', bibtex)

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

    def test_real_world_pmid_data_mocked(self):
        """Test with real-world article data (Hammill2021) using mocked approach"""
        # Mock the article with real-world data structure
        mock_article = Mock()
        mock_article.authors = ['Hammill AM', 'Wusik K', 'Kasthuri RS']
        mock_article.title = 'Hereditary hemorrhagic telangiectasia and related disorders'
        mock_article.journal = 'Hematology Am Soc Hematol Educ Program'
        mock_article.year = 2021
        mock_article.volume = '2021'
        mock_article.pages = '469-477'
        mock_article.doi = '10.1182/hematology.2021000281'
        mock_article.abstract = 'Long abstract content ' * 50  # > 500 chars for truncation test
        
        # Generate bibtex using the citation function
        bibtex = cite.bibtex(
            authors=mock_article.authors,
            title=mock_article.title,
            journal=mock_article.journal,
            year=mock_article.year,
            volume=mock_article.volume,
            pages=mock_article.pages,
            doi=mock_article.doi,
            abstract=mock_article.abstract
        )
        
        # Should have proper structure and content based on realistic data
        self.assertIn('@article{Hammill2021,', bibtex)
        self.assertIn('author = {Hammill, AM and Wusik, K and Kasthuri, RS}', bibtex)
        self.assertIn('title = {Hereditary hemorrhagic telangiectasia and related disorders}', bibtex)
        self.assertIn('journal = {Hematology Am Soc Hematol Educ Program}', bibtex)
        self.assertIn('year = {2021}', bibtex)
        self.assertIn('volume = {2021}', bibtex)
        self.assertIn('pages = {469-477}', bibtex)
        self.assertIn('doi = {10.1182/hematology.2021000281}', bibtex)
        
        # Should have proper BibTeX formatting
        self.assertTrue(bibtex.startswith('@article{Hammill2021,\n'))
        self.assertTrue(bibtex.endswith('}'))
        
        # Should have abstract truncation
        if 'abstract' in bibtex:
            abstract_match = re.search(r'abstract = \{([^}]+)\}', bibtex)
            if abstract_match:
                abstract_content = abstract_match.group(1)
                self.assertLess(len(abstract_content), 510)  # 500 + "..." = 503 chars max

if __name__ == '__main__':
    unittest.main()