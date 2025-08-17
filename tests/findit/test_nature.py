"""Tests for Nature Publishing Group dance function."""

import pytest
from unittest.mock import patch, Mock
import requests

from .common import BaseDanceTest
from metapub import PubMedFetcher
from metapub.findit.dances import the_nature_ballet
from metapub.exceptions import AccessDenied, NoPDFLink
from tests.fixtures import load_pmid_xml, NATURE_EVIDENCE_PMIDS

class TestNatureDance(BaseDanceTest):
    """Test cases for Nature Publishing Group."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.fetch = PubMedFetcher()

    def test_nature_ballet_modern_doi_url_construction(self):
        """Test 1: Modern DOI-based URL construction.
        
        PMID: 35459787 (Sci Rep - Scientific Reports)
        Expected: Should construct modern Nature DOI-based PDF URL
        """
        pma = self.fetch.article_by_pmid('35459787')
        
        assert pma.journal == 'Sci Rep'
        assert pma.doi == '10.1038/s41598-022-10666-2'
        
        # Test without verification (should always work for URL construction)
        url = the_nature_ballet(pma, verify=False)
        assert url is not None
        assert url == 'https://www.nature.com/articles/s41598-022-10666-2.pdf'
        assert 'nature.com/articles/' in url
        print(f"Test 1 - Modern DOI URL: {url}")

    def test_nature_ballet_traditional_fallback_url_construction(self):
        """Test 2: Traditional fallback URL construction.
        
        PMID: 10201537 (J Invest Dermatol)
        Expected: Should construct legacy articles/{id}.pdf URL using our evidence-driven approach
        """
        pma = self.fetch.article_by_pmid('10201537')
        
        assert pma.journal == 'J Invest Dermatol'
        assert pma.doi == '10.1046/j.1523-1747.1999.00551.x'  # Not a Nature DOI
        assert pma.volume == '112'
        assert pma.issue == '4'
        
        # Test without verification - should construct legacy URL using journal/year/page pattern
        url = the_nature_ballet(pma, verify=False)
        assert url is not None
        assert 'nature.com/articles/' in url  # Evidence-driven: all Nature URLs use /articles/
        assert url.endswith('.pdf')
        print(f"Test 2 - Traditional fallback URL: {url}")

    def test_nature_ballet_different_article(self):
        """Test 3: Different Nature article with modern DOI.
        
        Let's try a different approach - test with a different modern Nature DOI
        """
        # Create a mock PMA with a different Nature DOI pattern
        pma = Mock()
        pma.doi = '10.1038/s41467-022-28794-6'  # Nature Communications pattern
        pma.journal = 'Nat Commun'
        pma.volume = None
        pma.issue = None
        pma.pii = None
        
        # Test URL construction (verify=False to avoid network calls)
        url = the_nature_ballet(pma, verify=False)
        assert url is not None
        assert url == 'https://www.nature.com/articles/s41467-022-28794-6.pdf'
        print(f"Test 3 - Different Nature DOI URL: {url}")    # Test removed: test_nature_ballet_successful_pdf_access - functionality now handled by verify_pdf_url    # Test removed: test_nature_ballet_paywall_detection - functionality now handled by verify_pdf_url

    @patch('metapub.findit.dances.nature.verify_pdf_url')
    def test_nature_ballet_access_denied(self, mock_verify):
        """Test 6: Access denied - PDF verification fails.
        
        Expected: Should handle access denied gracefully
        """
        # Mock failed PDF verification (access denied)
        mock_verify.return_value = False

        pma = self.fetch.article_by_pmid('35459787')
        
        # Test with verification - should handle access denied
        with pytest.raises(AccessDenied) as exc_info:
            the_nature_ballet(pma, verify=True)
        
        assert 'PAYWALL' in str(exc_info.value)
        assert 'subscription' in str(exc_info.value)
        print(f"Test 6 - Correctly handled access denied: {exc_info.value}")

    def test_nature_ballet_missing_data(self):
        """Test 7: Article without sufficient data.
        
        Expected: Should raise NoPDFLink for missing data
        """
        # Create a mock PMA without proper Nature data
        pma = Mock()
        pma.doi = None  # No DOI
        pma.volume = None  # No volume data
        pma.issue = None
        pma.pii = None
        pma.journal = 'Some Journal'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_nature_ballet(pma, verify=False)
        
        assert 'MISSING' in str(exc_info.value)
        print(f"Test 7 - Correctly handled missing data: {exc_info.value}")    # Test removed: test_nature_ballet_network_error - functionality now handled by verify_pdf_url    # Test removed: test_nature_journal_recognition - functionality now handled by verify_pdf_url

class TestNatureXMLFixtures:
    """Test Nature dance function with real XML fixtures."""

    def test_nature_authentic_metadata_validation(self):
        """Validate authentic metadata from XML fixtures matches expected patterns."""
        for pmid, expected in NATURE_EVIDENCE_PMIDS.items():
            pma = load_pmid_xml(pmid)
            assert pma.doi == expected['doi']
            assert pma.journal == expected['journal']
            assert pma.pmid == pmid
            print(f"✓ PMID {pmid}: {pma.journal} - {pma.doi}")

    def test_nature_doi_pattern_consistency(self):
        """Test Nature DOI patterns (10.14309/)."""
        for pmid, data in NATURE_EVIDENCE_PMIDS.items():
            pma = load_pmid_xml(pmid)
            assert pma.doi.startswith('10.14309/'), f"Nature DOI must start with 10.14309/, got: {pma.doi}"
            print(f"✓ PMID {pmid} DOI pattern: {pma.doi}")