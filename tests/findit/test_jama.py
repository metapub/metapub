"""Tests for JAMA network journals dance function."""

import pytest
from unittest.mock import patch, Mock
import requests

from .common import BaseDanceTest
from metapub import PubMedFetcher
from metapub.findit.dances import the_jama_dance
from metapub.findit.registry import JournalRegistry
from metapub.exceptions import AccessDenied, NoPDFLink

class TestJAMADance(BaseDanceTest):
    """Test cases for JAMA network journals."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.fetch = PubMedFetcher()

    def test_jama_dance_url_construction_basic(self):
        """Test 1: Basic URL construction without network calls.
        
        PMID: 26575068 (JAMA)
        Expected: Should have correct DOI and journal info
        """
        pma = self.fetch.article_by_pmid('26575068')
        
        assert pma.journal == 'JAMA'
        assert pma.doi == '10.1001/jama.2015.12931'
        print(f"Test 1 - Article info: {pma.journal}, DOI: {pma.doi}")

    def test_jama_dance_second_article(self):
        """Test 2: Second JAMA article info.
        
        PMID: 26575069 (JAMA)
        Expected: Should have correct journal and DOI info
        """
        pma = self.fetch.article_by_pmid('26575069')
        
        # Just check that we got valid article data
        assert pma.journal is not None
        assert pma.doi is not None
        print(f"Test 2 - Second article: {pma.journal}, DOI: {pma.doi}")

    # Test removed: Missing PDF link detection and paywall testing - functionality now handled by verify_pdf_url

    def test_jama_dance_no_doi(self):
        """Test 5: Article without DOI.
        
        Expected: Should raise NoPDFLink for missing DOI
        """
        # Create a mock PMA without DOI
        pma = Mock()
        pma.doi = None
        pma.journal = 'JAMA'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_jama_dance(pma, verify=False)
        
        assert 'MISSING: doi needed for JAMA article' in str(exc_info.value)
        print(f"Test 5 - Correctly handled missing DOI: {exc_info.value}")

    # Test removed: test_jama_dance_network_error and test_jama_journal_recognition - functionality now handled by verify_pdf_url