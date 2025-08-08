"""
Test suite for APA (American Psychological Association) publisher dance function.

Following TRANSITION_TESTS_TO_REAL_DATA.md approach:
- Uses XML fixtures from real PMIDs to avoid network dependencies  
- Tests evidence-based subscription model with proper paywall detection
- Comprehensive coverage of the_apa_dab dance function requirements
"""

import pytest
import os
import sys
from unittest.mock import patch, Mock
import requests

# Add project root to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from metapub.findit.dances.generic import the_doi_slide
from metapub.findit.journals.apa import apa_journals
from metapub.exceptions import NoPDFLink, MetaPubError
from tests.fixtures import load_pmid_xml, APA_EVIDENCE_PMIDS


class TestAPAJournalRecognition:
    """Test APA journal recognition."""
    
    def test_apa_journal_list_completeness(self):
        """Test that apa_journals list contains expected journals."""
        # Key APA journals should be included
        expected_journals = [
            'Am Psychol',
            'J Comp Psychol', 
            'Psychiatr Rehabil J',
            'Rehabil Psychol',
            'Dev Psychol',
            'Health Psychol',
            'J Pers Soc Psychol'
        ]
        
        for journal in expected_journals:
            assert journal in apa_journals, f"Expected APA journal '{journal}' missing from apa_journals list"


class TestAPADanceFunction:
    """Test APA dance function URL construction and error handling."""
    
    def test_apa_url_construction_with_fixtures(self):
        """Test URL construction using XML fixtures."""
        
        for pmid, expected_data in APA_EVIDENCE_PMIDS.items():
            # Load article from XML fixture
            article = load_pmid_xml(pmid)
            
            # Verify fixture data
            assert article.journal == expected_data['journal'], f"PMID {pmid} journal mismatch"
            assert article.doi == expected_data['doi'], f"PMID {pmid} DOI mismatch"
            
            # Test URL construction with verify=False
            url = the_doi_slide(article, verify=False)
            
            # Verify URL structure - APA uses template-based URL construction
            expected_url = f"https://psycnet.apa.org/fulltext/{expected_data['doi']}.pdf"
            assert url == expected_url, f"PMID {pmid}: expected {expected_url}, got {url}"
            
            # Verify URL structure
            assert url.startswith('https://psycnet.apa.org/fulltext/'), f"PMID {pmid}: URL has wrong structure"
            assert expected_data['doi'] in url, f"PMID {pmid}: DOI not found in URL"
    
    def test_apa_missing_journal_error(self):
        """Test error handling for non-APA journals."""
        # Create mock article with non-APA journal
        class MockArticle:
            def __init__(self):
                self.journal = 'Nature'  # Not an APA journal
                self.doi = '10.1038/nature12345'
        
        fake_article = MockArticle()
        
        # Should fail because journal uses different template parameters
        with pytest.raises((NoPDFLink, KeyError)):
            the_doi_slide(fake_article, verify=False)
    
    def test_apa_missing_doi_error(self):
        """Test error handling for missing DOI."""
        # Create mock APA article without DOI
        class MockArticle:
            def __init__(self):
                self.journal = 'Am Psychol'
                self.doi = None  # Missing DOI
        
        fake_article = MockArticle()
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_doi_slide(fake_article, verify=False)
        
        error_msg = str(exc_info.value)
        assert 'DOI required for DOI-based publishers' in error_msg
    
    def test_apa_invalid_doi_pattern(self):
        """Test that non-APA DOIs still work but produce different URLs."""
        # Create mock APA article with non-APA DOI
        class MockArticle:
            def __init__(self):
                self.journal = 'Am Psychol'
                self.doi = '10.1016/j.example.2024.01.001'  # Not an APA DOI (10.1037)
        
        fake_article = MockArticle()
        
        # the_doi_slide doesn't validate DOI patterns, it just constructs URLs
        # This will create a URL but it won't be a valid APA URL
        url = the_doi_slide(fake_article, verify=False)
        expected_url = "https://psycnet.apa.org/fulltext/10.1016/j.example.2024.01.001.pdf"
        assert url == expected_url
    
    def test_apa_verify_false_success(self):
        """Test successful URL construction with verify=False."""
        article = load_pmid_xml('34843274')  # Am Psychol article
        
        url = the_doi_slide(article, verify=False)
        expected_url = "https://psycnet.apa.org/fulltext/10.1037/amp0000904.pdf"
        
        assert url == expected_url
    
    def test_apa_verify_true_paywall_detection(self):
        """Test that verify=True properly detects paywalled content."""
        article = load_pmid_xml('32437181')  # Am Psychol article
        
        # With verify=True, should detect paywall or similar access issues for subscription content
        with pytest.raises((NoPDFLink, MetaPubError)):
            the_doi_slide(article, verify=True)


class TestAPAEvidenceValidation:
    """Validate that our evidence-based approach is sound."""
    
    def test_doi_prefix_consistency(self):
        """Test that all APA PMIDs use 10.1037 DOI prefix."""
        doi_prefix = '10.1037'
        
        for pmid, data in APA_EVIDENCE_PMIDS.items():
            assert data['doi'].startswith(doi_prefix), f"PMID {pmid} has unexpected DOI prefix: {data['doi']}"
    
    def test_journal_consistency(self):
        """Test that all test journals are in the APA journal list."""
        test_journals = set(data['journal'] for data in APA_EVIDENCE_PMIDS.values())
        
        for journal in test_journals:
            assert journal in apa_journals, f"Test journal '{journal}' not in apa_journals list"
    
    def test_fixture_completeness(self):
        """Test that all evidence PMIDs have working fixtures."""
        for pmid in APA_EVIDENCE_PMIDS.keys():
            # This should not raise an exception
            article = load_pmid_xml(pmid)
            
            # Basic validation
            assert article.journal is not None, f"PMID {pmid}: missing journal"
            assert article.doi is not None, f"PMID {pmid}: missing DOI"
            
            # DOI format validation for APA
            assert article.doi.startswith('10.1037'), f"PMID {pmid}: not an APA DOI"


class TestAPAIntegration:
    """Integration tests with metapub components."""
    
    def test_apa_journal_list_integration(self):
        """Test APA journal list integration."""
        
        # Test that APA journal list is accessible
        assert 'Am Psychol' in apa_journals
        
        # Verify dance function works with registry system
        article = load_pmid_xml('34843274')
        url = the_doi_slide(article, verify=False)
        
        assert url.startswith('https://psycnet.apa.org/fulltext/')
        assert '10.1037/amp0000904' in url
    
    def test_apa_multiple_journal_types(self):
        """Test APA dance function across different journal types."""
        
        # Test different journal types from fixtures
        test_cases = [
            ('34843274', 'Am Psychol'),      # American Psychologist
            ('38546579', 'J Comp Psychol'),  # Journal of Comparative Psychology
            ('38573673', 'Psychiatr Rehabil J'),  # Psychiatric Rehabilitation Journal
            ('38271020', 'Rehabil Psychol'),  # Rehabilitation Psychology
        ]
        
        for pmid, expected_journal in test_cases:
            article = load_pmid_xml(pmid)
            assert article.journal == expected_journal
            
            url = the_doi_slide(article, verify=False)
            assert url is not None
            assert article.doi in url


if __name__ == '__main__':
    pytest.main([__file__, '-v'])