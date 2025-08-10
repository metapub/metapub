"""
Test Schattauer consolidation with the_doi_slide generic function.

Following DANCE_FUNCTION_GUIDELINES.md Phase 4 guidelines:
- Test the consolidated approach with real pattern examples
- Test each error condition separately  
- Use evidence-based patterns from HTML samples
- Registry integration test

Evidence discovered from HTML samples:
- Schattauer uses Thieme's platform (thieme-connect.de)
- PDF URLs follow pattern: http://www.thieme-connect.de/products/ejournals/pdf/{doi}.pdf
- DOI patterns: 10.1055/a-XXXX-XXXX
- All samples showed consistent citation_pdf_url meta tags
"""

import pytest
from unittest.mock import patch, Mock
from metapub.findit.registry import JournalRegistry
from metapub.findit.dances.generic import the_doi_slide
from metapub.exceptions import NoPDFLink, AccessDenied


class TestSchattauerConsolidation:
    """Test Schattauer consolidation into the_doi_slide."""

    def test_registry_integration(self):
        """Test that Schattauer journals are correctly registered."""
        registry = JournalRegistry()
        
        # Test the key Schattauer journal
        publisher_info = registry.get_publisher_for_journal('Thromb Haemost')
        assert publisher_info is not None, "Thromb Haemost not found in registry"
        assert publisher_info['name'] == 'schattauer'
        assert publisher_info['dance_function'] == 'the_doi_slide'
        assert publisher_info['format_template'] == 'http://www.thieme-connect.de/products/ejournals/pdf/{doi}.pdf'
            
        registry.close()

    def test_url_construction_evidence_based(self):
        """Test URL construction with evidence-based DOI patterns from HTML samples."""
        # Evidence-based test cases from HTML samples analyzed
        evidence_cases = [
            ('10.1055/a-1653-4699', 'http://www.thieme-connect.de/products/ejournals/pdf/10.1055/a-1653-4699.pdf'),  # PMID 34560806
            ('10.1055/a-2434-9244', 'http://www.thieme-connect.de/products/ejournals/pdf/10.1055/a-2434-9244.pdf'),  # PMID 39374908
            ('10.1055/a-2043-0346', 'http://www.thieme-connect.de/products/ejournals/pdf/10.1055/a-2043-0346.pdf'),  # PMID 36841245
            ('10.1055/a-1952-1946', 'http://www.thieme-connect.de/products/ejournals/pdf/10.1055/a-1952-1946.pdf'),  # PMID 36170884
            ('10.1055/a-2165-1142', 'http://www.thieme-connect.de/products/ejournals/pdf/10.1055/a-2165-1142.pdf'),  # PMID 37657485
            ('10.1055/a-1690-8897', 'http://www.thieme-connect.de/products/ejournals/pdf/10.1055/a-1690-8897.pdf'),  # PMID 34753192
        ]
        
        for doi, expected_url in evidence_cases:
            # Create mock PMA
            pma = Mock()
            pma.doi = doi
            pma.journal = 'Thromb Haemost'
            
            # Mock verify_pdf_url to avoid network calls
            with patch('metapub.findit.dances.generic.verify_pdf_url') as mock_verify:
                result = the_doi_slide(pma, verify=False)
                assert result == expected_url
                assert not mock_verify.called  # verify=False so shouldn't be called

    def test_doi_validation(self):
        """Test that missing DOI raises appropriate error."""
        pma = Mock()
        pma.doi = None
        pma.journal = 'Thromb Haemost'
        
        with pytest.raises(NoPDFLink) as excinfo:
            the_doi_slide(pma, verify=False)
        
        assert 'MISSING: DOI required' in str(excinfo.value)

    @patch('metapub.findit.dances.generic.verify_pdf_url')
    def test_verification_success(self, mock_verify):
        """Test successful PDF verification."""
        mock_verify.return_value = True
        
        pma = Mock()
        pma.doi = '10.1055/a-1653-4699'
        pma.journal = 'Thromb Haemost'
        
        result = the_doi_slide(pma, verify=True)
        
        assert result == 'http://www.thieme-connect.de/products/ejournals/pdf/10.1055/a-1653-4699.pdf'
        mock_verify.assert_called_once_with('http://www.thieme-connect.de/products/ejournals/pdf/10.1055/a-1653-4699.pdf')

    @patch('metapub.findit.dances.generic.verify_pdf_url')
    def test_verification_failure(self, mock_verify):
        """Test that verification failures bubble up appropriately."""
        mock_verify.side_effect = AccessDenied('Test paywall')
        
        pma = Mock()
        pma.doi = '10.1055/a-1653-4699'
        pma.journal = 'Thromb Haemost'
        
        with pytest.raises(AccessDenied):
            the_doi_slide(pma, verify=True)

    def test_doi_pattern_flexibility(self):
        """Test that the consolidation accepts Schattauer/Thieme DOI patterns."""
        # Schattauer/Thieme uses 10.1055/ DOI pattern consistently
        test_cases = [
            '10.1055/a-1653-4699',  # Standard Schattauer pattern (evidence-based)
            '10.1055/a-2434-9244',  # Another standard pattern (evidence-based)
            '10.1055/s-0041-1234567',  # Hypothetical s-prefix pattern
        ]
        
        for doi in test_cases:
            pma = Mock()
            pma.doi = doi
            pma.journal = 'Thromb Haemost'
            
            result = the_doi_slide(pma, verify=False)
            expected = f'http://www.thieme-connect.de/products/ejournals/pdf/{doi}.pdf'
            assert result == expected


    def test_evidence_based_format_template(self):
        """Test that format template matches evidence from HTML samples."""
        registry = JournalRegistry()
        publisher_info = registry.get_publisher_for_journal('Thromb Haemost')
        template = publisher_info['format_template']
        registry.close()
        
        # Template should match the patterns we found in HTML samples
        assert template == 'http://www.thieme-connect.de/products/ejournals/pdf/{doi}.pdf'
        
        # Should support the DOI patterns we found in evidence
        test_url = template.format(doi='10.1055/a-1653-4699')
        assert test_url == 'http://www.thieme-connect.de/products/ejournals/pdf/10.1055/a-1653-4699.pdf'

    def test_template_structure_evidence_based(self):
        """Test that the template structure matches evidence from HTML samples."""
        registry = JournalRegistry()
        publisher_info = registry.get_publisher_for_journal('Thromb Haemost')
        template = publisher_info['format_template']
        registry.close()
        
        # Based on evidence analysis: /products/ejournals/pdf/ pattern with .pdf extension
        test_url = template.format(doi='10.1055/a-1653-4699')
        
        # Verify template structure matches evidence
        assert test_url.startswith('http://www.thieme-connect.de/products/ejournals/pdf/')
        assert '10.1055/a-1653-4699' in test_url
        assert test_url.endswith('.pdf')

    def test_schattauer_thieme_platform_integration(self):
        """Test that Schattauer properly uses Thieme's platform infrastructure."""
        # Evidence shows Schattauer articles are hosted on thieme-connect.de
        # This test verifies the integration is working correctly
        
        pma = Mock()
        pma.doi = '10.1055/a-1653-4699'
        pma.journal = 'Thromb Haemost'
        
        result = the_doi_slide(pma, verify=False)
        
        # Should use Thieme's domain and path structure  
        assert 'thieme-connect.de' in result
        assert '/products/ejournals/pdf/' in result
        
        # Should match the exact pattern from HTML evidence
        assert result == 'http://www.thieme-connect.de/products/ejournals/pdf/10.1055/a-1653-4699.pdf'



if __name__ == '__main__':
    pytest.main([__file__, '-v'])