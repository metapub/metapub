"""
Test University of Chicago Press consolidation with the_doi_slide generic function.

Following DANCE_FUNCTION_CHECKLIST.md Phase 4 guidelines:
- Test the consolidated approach with real pattern examples
- Test each error condition separately  
- Use evidence-based PMIDs from HTML samples
- Registry integration test
"""

import pytest
import tempfile
import os
from unittest.mock import patch, Mock
from metapub import PubMedFetcher
from metapub.findit.registry import JournalRegistry
from metapub.findit.dances.generic import the_doi_slide
from metapub.exceptions import NoPDFLink, AccessDenied


class TestUChicagoConsolidation:
    """Test University of Chicago Press consolidation into the_doi_slide."""
    
    @classmethod
    def setup_class(cls):
        """Create temporary database for testing."""
        cls.temp_db_file = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        cls.temp_db_path = cls.temp_db_file.name
        cls.temp_db_file.close()
    
    @classmethod
    def teardown_class(cls):
        """Clean up temporary database."""
        if os.path.exists(cls.temp_db_path):
            os.unlink(cls.temp_db_path)
    
    def setup_method(self):
        """Set up instance method access to temp db path."""
        self.temp_db_path = self.__class__.temp_db_path

    def test_registry_integration(self):
        """Test that University of Chicago Press journals are correctly registered."""
        # Use local test database to verify updated configuration
        registry = JournalRegistry(db_path=self.temp_db_path)
        
        # Test a few key UChicago journals
        test_journals = [
            'Am J Sociol',        # American Journal of Sociology
            'J Polit Econ',       # Journal of Political Economy
            'Am Nat',             # American Naturalist
        ]
        
        for journal in test_journals:
            publisher_info = registry.get_publisher_for_journal(journal)
            assert publisher_info is not None, f"Journal {journal} not found in registry"
            assert publisher_info['name'] == 'uchicago'
            assert publisher_info['dance_function'] == 'the_doi_slide'
            assert publisher_info['format_template'] == 'https://www.journals.uchicago.edu/doi/pdf/{doi}'
            
        registry.close()

    def test_url_construction_evidence_based(self):
        """Test URL construction with evidence-based DOI patterns from HTML samples."""
        # Test that template format is correctly applied based on our evidence
        registry = JournalRegistry(db_path=self.temp_db_path)
        publisher_info = registry.get_publisher_for_journal('Am J Sociol')
        template = publisher_info['format_template']
        registry.close()
        
        # Evidence-based test cases from HTML samples analyzed
        evidence_cases = [
            ('10.1086/713927', 'https://www.journals.uchicago.edu/doi/pdf/10.1086/713927'),  # AJS sample
            ('10.1086/718279', 'https://www.journals.uchicago.edu/doi/pdf/10.1086/718279'),  # Another sample  
            ('10.1086/727192', 'https://www.journals.uchicago.edu/doi/pdf/10.1086/727192'),  # Third sample
        ]
        
        for doi, expected_url in evidence_cases:
            # Test template formatting directly
            result = template.format(doi=doi)
            assert result == expected_url

    def test_doi_validation(self):
        """Test that missing DOI raises appropriate error."""
        pma = Mock()
        pma.doi = None
        pma.journal = 'Am J Sociol'
        
        with pytest.raises(NoPDFLink) as excinfo:
            the_doi_slide(pma, verify=False)
        
        assert 'MISSING: DOI required' in str(excinfo.value)


    def test_evidence_based_template(self):
        """Test that template is based on evidence from HTML samples.""" 
        registry = JournalRegistry(db_path=self.temp_db_path)
        publisher_info = registry.get_publisher_for_journal('Am J Sociol')
        template = publisher_info['format_template']
        registry.close()
        
        # Template should match the patterns we found in HTML samples
        assert template == 'https://www.journals.uchicago.edu/doi/pdf/{doi}'
        
        # Should support the DOI pattern we found in evidence (10.1086/...)  
        test_url = template.format(doi='10.1086/713927')
        assert test_url == 'https://www.journals.uchicago.edu/doi/pdf/10.1086/713927'

    def test_doi_pattern_flexibility(self):
        """Test that the consolidation accepts various DOI patterns (not just 10.1086)."""
        # University of Chicago Press has acquired journals that might have different DOI patterns
        registry = JournalRegistry(db_path=self.temp_db_path)
        publisher_info = registry.get_publisher_for_journal('Am J Sociol')
        template = publisher_info['format_template']
        registry.close()
        
        # Template should work with various DOI patterns
        test_cases = [
            '10.1086/713927',  # Standard UChicago pattern
            '10.1234/567890',  # Hypothetical different pattern
        ]
        
        for doi in test_cases:
            result = template.format(doi=doi)
            expected = f'https://www.journals.uchicago.edu/doi/pdf/{doi}'
            assert result == expected

    def test_template_structure_evidence_based(self):
        """Test that the template structure matches evidence from HTML samples."""
        registry = JournalRegistry(db_path=self.temp_db_path)
        publisher_info = registry.get_publisher_for_journal('Am J Sociol')
        template = publisher_info['format_template']
        registry.close()
        
        # Based on evidence analysis: /doi/pdf/ pattern is consistent
        test_url = template.format(doi='10.1086/713927')
        
        # Verify template structure matches evidence
        assert test_url.startswith('https://www.journals.uchicago.edu/doi/pdf/')
        assert '10.1086/713927' in test_url
        assert test_url.count('/') == 6  # https://www.journals.uchicago.edu/doi/pdf/10.1086/713927



if __name__ == '__main__':
    pytest.main([__file__])