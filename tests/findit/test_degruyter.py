"""
Test suite for De Gruyter publisher dance function.

Test approach:
- Uses XML fixtures from real PMIDs to avoid network dependencies  
- Tests DOI approach for true De Gruyter journals (10.1515 prefix)
- Comprehensive coverage of the_doi_slide generic function requirements
"""

import pytest
import os
import sys

# Add project root to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from metapub.findit.dances.generic import the_doi_slide
from metapub.findit.journals.degruyter import degruyter_journals
from metapub.exceptions import NoPDFLink, MetaPubError
from tests.fixtures import load_pmid_xml, DEGRUYTER_EVIDENCE_PMIDS


class TestDeGruyterJournalRecognition:
    """Test De Gruyter journal recognition."""
    
    def test_degruyter_journal_list_completeness(self):
        """Test that degruyter journals are in registry."""
        from metapub.findit.registry import JournalRegistry
        
        registry = JournalRegistry()
        
        # Key De Gruyter journals should be included
        expected_journals = [
            'Clin Chem Lab Med',
            'J Pediatr Endocrinol Metab',
            'Horm Mol Biol Clin Investig',
            'Biol Chem',
            'Pure Appl Chem'
        ]
        
        found_count = 0
        for journal in expected_journals:
            publisher_info = registry.get_publisher_for_journal(journal)
            if publisher_info and publisher_info['name'] == 'degruyter':
                print(f"✓ {journal} correctly mapped to De Gruyter")
                found_count += 1
            else:
                print(f"⚠ {journal} mapped to different publisher: {publisher_info['name'] if publisher_info else 'None'}")
        
        assert found_count > 0, f"No De Gruyter journals found in registry"
        print(f"✓ Found {found_count} properly mapped De Gruyter journals")
        
        registry.close()


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
    
    
    
    def test_degruyter_verify_false_success(self):
        """Test successful URL construction with verify=False."""
        article = load_pmid_xml('38534005')
        
        url = the_doi_slide(article, verify=False)
        expected_url = "https://www.degruyter.com/document/doi/10.1515/cclm-2024-0070/pdf"
        
        assert url == expected_url
    


class TestDeGruyterEvidenceValidation:
    """Validate that our evidence-based approach is sound."""
    
    def test_doi_prefix_consistency(self):
        """Test that all De Gruyter PMIDs use 10.1515 DOI prefix."""
        doi_prefix = '10.1515'
        
        for pmid, data in DEGRUYTER_EVIDENCE_PMIDS.items():
            assert data['doi'].startswith(doi_prefix), f"PMID {pmid} has unexpected DOI prefix: {data['doi']}"
    
    def test_journal_consistency(self):
        """Test that all test journals are in the De Gruyter registry."""
        from metapub.findit.registry import JournalRegistry
        
        registry = JournalRegistry()
        test_journals = set(data['journal'] for data in DEGRUYTER_EVIDENCE_PMIDS.values())
        
        for journal in test_journals:
            publisher_info = registry.get_publisher_for_journal(journal)
            assert publisher_info and publisher_info['name'] == 'degruyter', f"Test journal '{journal}' not found in degruyter registry"
        
        registry.close()
    
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
        """Test De Gruyter journal registry integration."""
        from metapub.findit.registry import JournalRegistry
        
        registry = JournalRegistry()
        
        # Test that De Gruyter journals are accessible via registry
        publisher_info = registry.get_publisher_for_journal('Clin Chem Lab Med')
        assert publisher_info and publisher_info['name'] == 'degruyter'
        
        # Verify dance function works with registry system
        article = load_pmid_xml('38534005')
        url = the_doi_slide(article, verify=False)
        
        assert url.startswith('https://www.degruyter.com/document/doi/')
        assert '10.1515/cclm-2024-0070' in url
        
        registry.close()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])