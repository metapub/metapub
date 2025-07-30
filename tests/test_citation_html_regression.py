"""
Regression tests for HTML citation formatting functionality.

This test suite contains specific regression tests to ensure that the HTML 
citation formatting functionality remains working and doesn't break due to 
future changes. These tests are based on the exact requirements from the 
GitHub issue and the expected behavior documented in the code.

Key requirements being protected:
1. Journal names must be wrapped in <i> tags
2. Volume numbers must be wrapped in <b> tags  
3. "et al" must be wrapped in <i> tags
4. Book titles must be wrapped in <i> tags
5. Plain citations must never contain HTML tags
6. HTML formatting only applies when as_html=True
"""

import unittest
from metapub import cite


class TestCitationHTMLRegression(unittest.TestCase):
    """Regression tests for HTML citation formatting"""

    def test_github_issue_exact_format_requirements(self):
        """
        Test exact format requirements from the GitHub issue.
        
        This test ensures the original HTML format strings are working:
        article_cit_fmt_html = '{author}. {title}. <i>{journal}</i>. {year}; <b>{volume}</b>:{pages}.{doi}'
        book_cit_fmt_html = '{author}. <i>{book.title}</i>. {cdate} (Update {mdate}). In: {editors}, editors. <i>{book.journal}</i> (Internet). {book.book_publisher}'
        """
        # Test data based on the GitHub issue example
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
        
        # These are the EXACT requirements from the GitHub issue
        self.assertIn('<i>Journal of Clinical Investigation</i>', html_citation,
                     "Journal name must be wrapped in <i> tags")
        self.assertIn('<b>123</b>', html_citation,
                     "Volume number must be wrapped in <b> tags")
        self.assertIn('<i>et al</i>', html_citation,
                     '"et al" must be wrapped in <i> tags')

    def test_mavedb_integration_requirements(self):
        """
        Test that citations work for MaveDB integration as mentioned in the issue.
        
        MaveDB needs HTML citations to display properly formatted references.
        This test ensures the output is suitable for web application display.
        """
        test_data = {
            'authors': ['Smith J', 'Jones K', 'Brown L'],
            'title': 'A test article for MaveDB',
            'journal': 'Nature Genetics',
            'year': 2023,
            'volume': 55,
            'pages': '100-110',
            'doi': '10.1038/ng.test'
        }
        
        html_citation = cite.article(as_html=True, **test_data)
        
        # Verify the citation is web-ready
        self.assertIn('<i>Nature Genetics</i>', html_citation)
        self.assertIn('<b>55</b>', html_citation)
        self.assertIn('Smith J, <i>et al</i>', html_citation)
        
        # Verify no broken HTML
        self.assertEqual(html_citation.count('<i>'), html_citation.count('</i>'))
        self.assertEqual(html_citation.count('<b>'), html_citation.count('</b>'))

    def test_pypi_installation_compatibility(self):
        """
        Test that functionality works when installed from PyPI.
        
        The GitHub issue mentions wanting to install from PyPI rather than
        a specific commit. This test ensures the functionality is complete.
        """
        # Test that all expected format strings exist
        self.assertTrue(hasattr(cite, 'article_cit_fmt_html'))
        self.assertTrue(hasattr(cite, 'book_cit_fmt_html'))
        
        # Test that they contain the required HTML tags
        self.assertIn('<i>{journal}</i>', cite.article_cit_fmt_html)
        self.assertIn('<b>{volume}</b>', cite.article_cit_fmt_html) 
        self.assertIn('<i>{book.title}</i>', cite.book_cit_fmt_html)
        self.assertIn('<i>{book.journal}</i>', cite.book_cit_fmt_html)

    def test_backward_compatibility_preserved(self):
        """
        Test that existing code using plain citations still works unchanged.
        
        This ensures that restoring HTML functionality doesn't break existing users.
        """
        test_data = {
            'authors': ['Test Author'],
            'title': 'Test Title',
            'journal': 'Test Journal',
            'year': 2023,
            'volume': 42,
            'pages': '1-10'
        }
        
        # Code that doesn't specify as_html should work exactly as before
        citation_default = cite.article(**test_data)
        citation_explicit_false = cite.article(as_html=False, **test_data)
        
        # They should be identical
        self.assertEqual(citation_default, citation_explicit_false)
        
        # Neither should contain HTML tags
        self.assertNotIn('<', citation_default)
        self.assertNotIn('>', citation_default)

    def test_html_only_when_requested(self):
        """
        Test that HTML tags only appear when explicitly requested.
        
        This is a critical requirement - HTML should never leak into plain citations.
        """
        test_data = {
            'authors': ['Test Author', 'Another Author', 'Third Author'],
            'title': 'Test Title',
            'journal': 'Test Journal',
            'year': 2023,
            'volume': 42,
            'pages': '1-10'
        }
        
        plain_citation = cite.article(as_html=False, **test_data)
        html_citation = cite.article(as_html=True, **test_data)
        
        # Plain citation must never have HTML
        self.assertNotIn('<i>', plain_citation)
        self.assertNotIn('<b>', plain_citation)
        self.assertNotIn('</i>', plain_citation)
        self.assertNotIn('</b>', plain_citation)
        
        # HTML citation must have HTML
        self.assertIn('<i>', html_citation)
        self.assertIn('<b>', html_citation)

    def test_author_et_al_html_formatting(self):
        """
        Test the specific "et al" HTML formatting requirement.
        
        The GitHub issue specifically mentions that only <i> around "et al" 
        was retained. This test ensures it works correctly.
        """
        # Single author - no et al
        single = cite.author_str(['Smith J'], as_html=True)
        self.assertEqual(single, 'Smith J')
        self.assertNotIn('<i>', single)
        
        # Two authors - no et al  
        two = cite.author_str(['Smith J', 'Jones K'], as_html=True)
        self.assertEqual(two, 'Smith J and Jones K')
        self.assertNotIn('<i>', two)
        
        # Three authors - et al with HTML
        three = cite.author_str(['Smith J', 'Jones K', 'Brown L'], as_html=True)
        self.assertEqual(three, 'Smith J, <i>et al</i>')
        
        # Four authors - et al with HTML
        four = cite.author_str(['Smith J', 'Jones K', 'Brown L', 'Davis M'], as_html=True)
        self.assertEqual(four, 'Smith J, <i>et al</i>')

    def test_format_string_structure_maintained(self):
        """
        Test that the format string structure matches the documented examples.
        
        The GitHub issue shows specific format string examples. This test
        ensures the structure is maintained.
        """
        # Check that HTML format strings follow the expected pattern
        expected_article_pattern = r'\{author\}.*<i>\{journal\}</i>.*<b>\{volume\}</b>'
        self.assertRegex(cite.article_cit_fmt_html, expected_article_pattern)
        
        expected_book_pattern = r'\{author\}.*<i>\{book\.title\}</i>.*<i>\{book\.journal\}</i>'
        self.assertRegex(cite.book_cit_fmt_html, expected_book_pattern)

    def test_no_html_escaping_regression(self):
        """
        Test that special characters in content don't break HTML structure.
        
        Ensures that content with < > & characters doesn't break the HTML formatting.
        """
        test_data = {
            'authors': ['Test Author'],
            'title': 'Study of <gene> & expression',
            'journal': 'Journal & Review',
            'year': 2023,
            'volume': 42,
            'pages': '1-10'
        }
        
        html_citation = cite.article(as_html=True, **test_data)
        
        # HTML structure should still be intact
        self.assertIn('<i>Journal & Review</i>', html_citation)
        self.assertIn('<b>42</b>', html_citation)
        
        # Tag balance should be maintained
        self.assertEqual(html_citation.count('<i>'), html_citation.count('</i>'))
        self.assertEqual(html_citation.count('<b>'), html_citation.count('</b>'))


if __name__ == '__main__':
    unittest.main()