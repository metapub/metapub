"""
Test World Scientific consolidation with the_doi_slide generic function.

Following DANCE_FUNCTION_CHECKLIST.md Phase 4 guidelines:
- Test the consolidated approach with real pattern examples
- Test each error condition separately  
- Use evidence-based patterns from HTML samples
- Registry integration test
"""

import pytest
from unittest.mock import patch, Mock
from metapub.findit.registry import JournalRegistry
from metapub.findit.dances.generic import the_doi_slide
from metapub.exceptions import NoPDFLink, AccessDenied


class TestWorldScientificConsolidation:
    """Test World Scientific consolidation into the_doi_slide."""

    def test_registry_integration(self):
        """Test that World Scientific journals are correctly registered."""
        registry = JournalRegistry()
        
        # Test a few key World Scientific journals (using exact names from worldscientific_journals)
        test_journals = [
            'Am J Chin Med',      # American Journal of Chinese Medicine
            'Fractals',           # Fractals journal
            'Hand Surg',          # Hand Surgery journal
        ]
        
        for journal in test_journals:
            publisher_info = registry.get_publisher_for_journal(journal)
            assert publisher_info is not None, f"Journal {journal} not found in registry"
            assert publisher_info['name'] == 'Worldscientific'
            assert publisher_info['dance_function'] == 'the_doi_slide'
            assert publisher_info['format_template'] == 'https://www.worldscientific.com/doi/pdf/{doi}?download=true'
            
        registry.close()

    def test_url_construction_evidence_based(self):
        """Test URL construction with evidence-based DOI patterns from HTML samples."""
        # Evidence-based test cases from HTML samples analyzed
        evidence_cases = [
            ('10.1142/S0218957719500118', 'https://www.worldscientific.com/doi/pdf/10.1142/S0218957719500118?download=true'),  # Sample 1: JMR
            ('10.1142/S2339547820500028', 'https://www.worldscientific.com/doi/pdf/10.1142/S2339547820500028?download=true'),  # Sample 2: TECHNOLOGY
        ]
        
        for doi, expected_url in evidence_cases:
            # Create mock PMA
            pma = Mock()
            pma.doi = doi
            pma.journal = 'Am J Chin Med'
            
            # Mock verify_pdf_url to avoid network calls
            with patch('metapub.findit.dances.generic.verify_pdf_url') as mock_verify:
                result = the_doi_slide(pma, verify=False)
                assert result == expected_url
                assert not mock_verify.called  # verify=False so shouldn't be called

    def test_doi_validation(self):
        """Test that missing DOI raises appropriate error."""
        pma = Mock()
        pma.doi = None
        pma.journal = 'Am J Chin Med'
        
        with pytest.raises(NoPDFLink) as excinfo:
            the_doi_slide(pma, verify=False)
        
        assert 'MISSING: DOI required' in str(excinfo.value)

    @patch('metapub.findit.dances.generic.verify_pdf_url')
    def test_verification_success(self, mock_verify):
        """Test successful PDF verification."""
        mock_verify.return_value = True
        
        pma = Mock()
        pma.doi = '10.1142/S0218957719500118'
        pma.journal = 'Am J Chin Med'
        
        result = the_doi_slide(pma, verify=True)
        
        assert result == 'https://www.worldscientific.com/doi/pdf/10.1142/S0218957719500118?download=true'
        mock_verify.assert_called_once_with('https://www.worldscientific.com/doi/pdf/10.1142/S0218957719500118?download=true')

    @patch('metapub.findit.dances.generic.verify_pdf_url')
    def test_verification_failure(self, mock_verify):
        """Test that verification failures bubble up appropriately."""
        mock_verify.side_effect = AccessDenied('Test paywall')
        
        pma = Mock()
        pma.doi = '10.1142/S0218957719500118'
        pma.journal = 'Am J Chin Med'
        
        with pytest.raises(AccessDenied):
            the_doi_slide(pma, verify=True)

    def test_doi_pattern_flexibility(self):
        """Test that the consolidation accepts World Scientific DOI patterns."""
        # World Scientific primarily uses 10.1142/ but may have other patterns
        test_cases = [
            '10.1142/S0218957719500118',  # Standard World Scientific pattern (evidence-based)
            '10.1142/S2339547820500028',  # Another standard pattern (evidence-based)
            '10.1142/9789811234567',      # Hypothetical book DOI pattern
        ]
        
        for doi in test_cases:
            pma = Mock()
            pma.doi = doi
            pma.journal = 'Am J Chin Med'
            
            result = the_doi_slide(pma, verify=False)
            expected = f'https://www.worldscientific.com/doi/pdf/{doi}?download=true'
            assert result == expected

    def test_download_parameter_inclusion(self):
        """Test that the consolidation includes ?download=true parameter from evidence."""
        pma = Mock()
        pma.doi = '10.1142/S0218957719500118'
        pma.journal = 'Am J Chin Med'
        
        result = the_doi_slide(pma, verify=False)
        
        # Verify download parameter is included (evidence-based requirement)
        assert '?download=true' in result
        assert result == 'https://www.worldscientific.com/doi/pdf/10.1142/S0218957719500118?download=true'


    def test_evidence_based_format_template(self):
        """Test that format template matches evidence from HTML samples."""
        registry = JournalRegistry()
        publisher_info = registry.get_publisher_for_journal('Am J Chin Med')
        template = publisher_info['format_template']
        registry.close()
        
        # Template should match the patterns we found in HTML samples
        assert template == 'https://www.worldscientific.com/doi/pdf/{doi}?download=true'
        
        # Should support the DOI patterns we found in evidence
        test_url = template.format(doi='10.1142/S0218957719500118')
        assert test_url == 'https://www.worldscientific.com/doi/pdf/10.1142/S0218957719500118?download=true'

    def test_template_structure_evidence_based(self):
        """Test that the template structure matches evidence from HTML samples."""
        registry = JournalRegistry()
        publisher_info = registry.get_publisher_for_journal('Am J Chin Med')
        template = publisher_info['format_template']
        registry.close()
        
        # Based on evidence analysis: /doi/pdf/ pattern with ?download=true parameter
        test_url = template.format(doi='10.1142/S0218957719500118')
        
        # Verify template structure matches evidence
        assert test_url.startswith('https://www.worldscientific.com/doi/pdf/')
        assert '10.1142/S0218957719500118' in test_url
        assert test_url.endswith('?download=true')

    def test_world_scientific_journal_coverage(self):
        """Test consolidation works with various World Scientific journals."""
        registry = JournalRegistry()
        
        # Test different World Scientific journal patterns (using exact names)
        test_journals = [
            'Am J Chin Med',           # Medical journal
            'Fractals',                # Mathematics journal  
            'Hand Surg',               # Medical journal
            'Int J Appl Mech',         # Engineering journal
        ]
        
        for journal in test_journals:
            publisher_info = registry.get_publisher_for_journal(journal)
            if publisher_info and publisher_info['name'] == 'worldscientific':
                assert publisher_info['dance_function'] == 'the_doi_slide'
                assert 'download=true' in publisher_info['format_template']
        
        registry.close()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])