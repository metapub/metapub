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

    def test_invalid_doi_prefix_raises_nopdflink(self):
        """Test that non-Dustri DOI raises NoPDFLink with INVALID prefix"""
        with self.assertRaises(NoPDFLink) as context:
            the_dustri_polka(self.pma_wrong_doi)
        
        self.assertIn('INVALID:', str(context.exception))
        self.assertIn('DOI format not recognized', str(context.exception))    # Test removed: test_free_article_with_verification_raises_postonly - functionality now handled by verify_pdf_url    # Test removed: test_paywall_article_raises_access_denied - functionality now handled by verify_pdf_url    # Test removed: test_http_error_raises_nopdflink - functionality now handled by verify_pdf_url    # Test removed: test_unknown_content_raises_nopdflink - functionality now handled by verify_pdf_url

    def test_no_verification_raises_postonly(self):
        """Test that verify=False still raises NoPDFLink with POSTONLY explanation"""
        with self.assertRaises(NoPDFLink) as context:
            the_dustri_polka(self.pma_free, verify=False)
        
        self.assertIn('POSTONLY:', str(context.exception))
        self.assertIn('POST form submission', str(context.exception))
        self.assertIn('visit:', str(context.exception))    # Test removed: test_network_exception_raises_nopdflink - functionality now handled by verify_pdf_url

    def test_url_construction_pattern(self):
        """Test that correct URL pattern is constructed from DOI"""
        # Since verify=False raises NoPDFLink with POSTONLY and URL, check the URL pattern
        with self.assertRaises(NoPDFLink) as context:
            the_dustri_polka(self.pma_free, verify=False)
        
        exception_message = str(context.exception)
        self.assertIn('https://www.dustri.com/nc/article-response-page.html', exception_message)
        self.assertIn('doi=10.5414/CN110175Intro', exception_message)    # Test removed: test_evidence_based_patterns - functionality now handled by verify_pdf_url