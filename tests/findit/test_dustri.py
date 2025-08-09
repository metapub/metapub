#!/usr/bin/env python3
"""
Test suite for Dustri-Verlag dance function
Following DANCE_FUNCTION_GUIDELINES.md Phase 4: Test Development
"""

import unittest
from unittest.mock import patch, Mock

from metapub.findit.dances.dustri import the_dustri_polka
from metapub.exceptions import NoPDFLink, AccessDenied
from metapub import PubMedArticle


class TestDustriDance(unittest.TestCase):
    """Test suite for the_dustri_polka dance function"""

    def setUp(self):
        """Set up test fixtures"""
        # Create mock PubMedArticle with Dustri DOI pattern
        self.pma_free = Mock(spec=PubMedArticle)
        self.pma_free.doi = '10.5414/CN110175Intro'
        self.pma_free.pmid = '32909542'
        
        self.pma_paywall = Mock(spec=PubMedArticle)
        self.pma_paywall.doi = '10.5414/CN110989'
        self.pma_paywall.pmid = '36633378'
        
        self.pma_no_doi = Mock(spec=PubMedArticle)
        self.pma_no_doi.doi = None
        self.pma_no_doi.pmid = '12345678'
        
        self.pma_wrong_doi = Mock(spec=PubMedArticle)
        self.pma_wrong_doi.doi = '10.1016/j.example.2023.01.001'
        self.pma_wrong_doi.pmid = '12345679'

    def test_missing_doi_raises_nopdflink(self):
        """Test that missing DOI raises NoPDFLink with MISSING prefix"""
        with self.assertRaises(NoPDFLink) as context:
            the_dustri_polka(self.pma_no_doi)
        
        self.assertIn('MISSING:', str(context.exception))
        self.assertIn('DOI required', str(context.exception))

    def test_invalid_doi_prefix_raises_nopdflink(self):
        """Test that non-Dustri DOI raises NoPDFLink with INVALID prefix"""
        with self.assertRaises(NoPDFLink) as context:
            the_dustri_polka(self.pma_wrong_doi)
        
        self.assertIn('INVALID:', str(context.exception))
        self.assertIn('DOI format not recognized', str(context.exception))

    @patch('metapub.findit.dances.dustri.unified_uri_get')
    def test_free_article_with_verification_raises_postonly(self, mock_get):
        """Test that free article with POST form raises NoPDFLink with POSTONLY"""
        # Mock HTML response with free PDF form
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = '''
        <form method="POST" action="/index.php">
            <input type="hidden" name="file" value="uploads/repository/21/g9ff07_cn94217.pdf">
            <input type="submit" name="artDownloader" value="Free Full Text" class="btn btn-success">
        </form>
        '''
        mock_get.return_value = mock_response
        
        with self.assertRaises(NoPDFLink) as context:
            the_dustri_polka(self.pma_free, verify=True)
        
        self.assertIn('POSTONLY:', str(context.exception))
        self.assertIn('POST request', str(context.exception))
        self.assertIn('dustri.com', str(context.exception))

    @patch('metapub.findit.dances.dustri.unified_uri_get')
    def test_paywall_article_raises_access_denied(self, mock_get):
        """Test that paywall article raises AccessDenied"""
        # Mock HTML response with "Add to Cart" button
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = '''
        <div class="addtocart-download">
            <p><a href="index.php?id=12&prdId=190015"><img src="btnAddCart.png" alt="Add to Cart" /></a></p>
        </div>
        '''
        mock_get.return_value = mock_response
        
        with self.assertRaises(AccessDenied) as context:
            the_dustri_polka(self.pma_paywall, verify=True)
        
        self.assertIn('PAYWALL:', str(context.exception))
        self.assertIn('requires purchase', str(context.exception))

    @patch('metapub.findit.dances.dustri.unified_uri_get')
    def test_http_error_raises_nopdflink(self, mock_get):
        """Test that HTTP errors raise NoPDFLink with TXERROR prefix"""
        # Mock HTTP 404 response
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        with self.assertRaises(NoPDFLink) as context:
            the_dustri_polka(self.pma_free, verify=True)
        
        self.assertIn('TXERROR:', str(context.exception))
        self.assertIn('Could not access', str(context.exception))

    @patch('metapub.findit.dances.dustri.unified_uri_get')
    def test_unknown_content_raises_nopdflink(self, mock_get):
        """Test that unknown content pattern raises NoPDFLink"""
        # Mock response without recognizable patterns
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = '<html><body>Unknown content</body></html>'
        mock_get.return_value = mock_response
        
        with self.assertRaises(NoPDFLink) as context:
            the_dustri_polka(self.pma_free, verify=True)
        
        self.assertIn('TXERROR:', str(context.exception))
        self.assertIn('Could not determine PDF access method', str(context.exception))

    def test_no_verification_raises_postonly(self):
        """Test that verify=False still raises NoPDFLink with POSTONLY explanation"""
        with self.assertRaises(NoPDFLink) as context:
            the_dustri_polka(self.pma_free, verify=False)
        
        self.assertIn('POSTONLY:', str(context.exception))
        self.assertIn('POST form submission', str(context.exception))
        self.assertIn('visit:', str(context.exception))

    @patch('metapub.findit.dances.dustri.unified_uri_get')
    def test_network_exception_raises_nopdflink(self, mock_get):
        """Test that network exceptions are caught and converted to NoPDFLink"""
        mock_get.side_effect = Exception("Network timeout")
        
        with self.assertRaises(NoPDFLink) as context:
            the_dustri_polka(self.pma_free, verify=True)
        
        self.assertIn('TXERROR:', str(context.exception))
        self.assertIn('Error accessing', str(context.exception))

    def test_url_construction_pattern(self):
        """Test that correct URL pattern is constructed from DOI"""
        # Since verify=False raises NoPDFLink with POSTONLY and URL, check the URL pattern
        with self.assertRaises(NoPDFLink) as context:
            the_dustri_polka(self.pma_free, verify=False)
        
        exception_message = str(context.exception)
        self.assertIn('https://www.dustri.com/nc/article-response-page.html', exception_message)
        self.assertIn('doi=10.5414/CN110175Intro', exception_message)

    def test_doi_pattern_validation(self):
        """Test that DOI pattern validation works correctly"""
        # Valid Dustri DOI should pass initial validation (and then raise NoPDFLink with POSTONLY)
        with self.assertRaises(NoPDFLink):
            the_dustri_polka(self.pma_free, verify=False)
        
        # Invalid DOI pattern should fail immediately
        with self.assertRaises(NoPDFLink) as context:
            the_dustri_polka(self.pma_wrong_doi, verify=False)
        self.assertIn('INVALID:', str(context.exception))

    @patch('metapub.findit.dances.dustri.unified_uri_get')
    def test_evidence_based_patterns(self, mock_get):
        """Test that function recognizes evidence-based patterns from investigation"""
        # Test free PDF pattern (from 32909542.html evidence)
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = '''
        <input type="submit" name="artDownloader" value="Free Full Text" class="btn btn-success" />
        '''
        mock_get.return_value = mock_response
        
        with self.assertRaises(NoPDFLink):
            the_dustri_polka(self.pma_free, verify=True)
        
        # Test paywall pattern (from 36633378.html evidence)
        mock_response.text = '''
        <a href="index.php?id=12&prdId=190015"><img src="fileadmin/templates/images/btnAddCart.png" alt="Add to Cart" /></a>
        '''
        mock_get.return_value = mock_response
        
        with self.assertRaises(AccessDenied):
            the_dustri_polka(self.pma_paywall, verify=True)


if __name__ == '__main__':
    unittest.main()