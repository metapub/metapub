"""
Test suite for De Gruyter publisher dance function.

Following TRANSITION_TESTS_TO_REAL_DATA.md approach:
- Uses XML fixtures from real PMIDs to avoid network dependencies  
- Tests evidence-based DOI approach for true De Gruyter journals (10.1515 prefix)
- Comprehensive coverage of the_doi_slide generic function requirements
"""

import pytest
import os
import sys

# Add project root to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from metapub.findit.dances.generic import the_doi_slide
from metapub.findit.journals.single_journal_publishers import degruyter_journals
from metapub.exceptions import NoPDFLink, MetaPubError
from tests.fixtures import load_pmid_xml, DEGRUYTER_EVIDENCE_PMIDS


class TestDeGruyterJournalRecognition:
    """Test De Gruyter journal recognition."""
    
    def test_degruyter_journal_list_completeness(self):
        """Test that degruyter_journals list contains expected journals."""
        # Key De Gruyter journals should be included
        expected_journals = [
            'Clin Chem Lab Med',
            'J Pediatr Endocrinol Metab',
            'Horm Mol Biol Clin Investig',
            'Biol Chem',
            'Pure Appl Chem'
        ]
        
        for journal in expected_journals:
            assert journal in degruyter_journals, f"Expected De Gruyter journal '{journal}' missing from degruyter_journals list"


class TestDeGruyterDanceFunction:
    """Test De Gruyter dance function URL construction and error handling."""
    
    def test_degruyter_url_construction_with_fixtures(self):
        """Test URL construction using XML fixtures."""
        
        for pmid, expected_data in DEGRUYTER_EVIDENCE_PMIDS.items():
            # Load article from XML fixture
            article = load_pmid_xml(pmid)
            
            # Verify fixture data
            assert article.journal == expected_data['journal'], f"PMID {pmid} journal mismatch"
            assert article.doi == expected_data['doi'], f"PMID {pmid} DOI mismatch"
            
            # Test URL construction with the_doi_slide
            url = the_doi_slide(article, verify=False)
            
            expected_url = f"https://www.degruyter.com/document/doi/{expected_data['doi']}/pdf"
            assert url == expected_url, f"PMID {pmid}: expected {expected_url}, got {url}"
            
            # Verify URL structure
            assert url.startswith('https://www.degruyter.com/document/doi/'), f"PMID {pmid}: URL has wrong structure"
            assert expected_data['doi'] in url, f"PMID {pmid}: DOI not found in URL"
    
    def test_degruyter_missing_journal_error(self):
        """Test error handling for non-De Gruyter journals."""
        # Create mock article with non-De Gruyter journal
        class MockArticle:
            def __init__(self):
                self.journal = 'Nature'  # Not a De Gruyter journal
                self.doi = '10.1038/nature12345'
        
        fake_article = MockArticle()
        
        # Should fail because Nature journal uses different template parameters
        with pytest.raises((NoPDFLink, KeyError)):
            the_doi_slide(fake_article, verify=False)
    
    def test_degruyter_missing_doi_error(self):
        """Test error handling for missing DOI."""
        # Create mock De Gruyter article without DOI
        class MockArticle:
            def __init__(self):
                self.journal = 'Clin Chem Lab Med'
                self.doi = None  # Missing DOI
        
        fake_article = MockArticle()
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_doi_slide(fake_article, verify=False)
        
        error_msg = str(exc_info.value)
        assert 'DOI required for DOI-based publishers' in error_msg
    
    def test_degruyter_verify_false_success(self):
        """Test successful URL construction with verify=False."""
        article = load_pmid_xml('38534005')
        
        url = the_doi_slide(article, verify=False)
        expected_url = "https://www.degruyter.com/document/doi/10.1515/cclm-2024-0070/pdf"
        
        assert url == expected_url
    
    def test_degruyter_verify_true_paywall_detection(self):
        """Test that verify=True properly detects paywalled content."""
        article = load_pmid_xml('36318760')  # This one returns HTML (paywalled)
        
        # With verify=True, should detect paywall or similar access issues
        with pytest.raises((NoPDFLink, MetaPubError)):
            the_doi_slide(article, verify=True)


class TestDeGruyterEvidenceValidation:
    """Validate that our evidence-based approach is sound."""
    
    def test_doi_prefix_consistency(self):
        """Test that all De Gruyter PMIDs use 10.1515 DOI prefix."""
        doi_prefix = '10.1515'
        
        for pmid, data in DEGRUYTER_EVIDENCE_PMIDS.items():
            assert data['doi'].startswith(doi_prefix), f"PMID {pmid} has unexpected DOI prefix: {data['doi']}"
    
    def test_journal_consistency(self):
        """Test that all test journals are in the De Gruyter journal list."""
        test_journals = set(data['journal'] for data in DEGRUYTER_EVIDENCE_PMIDS.values())
        
        for journal in test_journals:
            assert journal in degruyter_journals, f"Test journal '{journal}' not in degruyter_journals list"
    
    def test_fixture_completeness(self):
        """Test that all evidence PMIDs have working fixtures."""
        for pmid in DEGRUYTER_EVIDENCE_PMIDS.keys():
            # This should not raise an exception
            article = load_pmid_xml(pmid)
            
            # Basic validation
            assert article.journal is not None, f"PMID {pmid}: missing journal"
            assert article.doi is not None, f"PMID {pmid}: missing DOI"
            
            # DOI format validation for De Gruyter
            assert article.doi.startswith('10.1515'), f"PMID {pmid}: not a true De Gruyter DOI"


class TestDeGruyterIntegration:
    """Integration tests with metapub components."""
    
    def test_degruyter_template_validation(self):
        """Test De Gruyter template produces expected URLs."""
        
        # Test template with known DOI
        template = 'https://www.degruyter.com/document/doi/{doi}/pdf'
        test_doi = '10.1515/cclm-2024-0070'
        
        expected_url = template.format(doi=test_doi)
        assert expected_url == 'https://www.degruyter.com/document/doi/10.1515/cclm-2024-0070/pdf'
        
        # Verify template structure
        assert '{doi}' in template
        assert 'degruyter.com' in template
        assert '/pdf' in template
    
    def test_degruyter_journal_list_integration(self):
        """Test De Gruyter journal list integration."""
        
        # Test that De Gruyter journal list is accessible
        assert 'Clin Chem Lab Med' in degruyter_journals
        
        # Verify dance function works with registry system
        article = load_pmid_xml('38534005')
        url = the_doi_slide(article, verify=False)
        
        assert url.startswith('https://www.degruyter.com/document/doi/')
        assert '10.1515/cclm-2024-0070' in url


if __name__ == '__main__':
    pytest.main([__file__, '-v'])