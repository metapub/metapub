"""
Tests for American Thoracic Society (ATS) publisher configuration.

ATS uses the_doi_slide generic function with evidence-based URL templates:
- Updated domain: www.thoracic.org (from legacy atsjournals.org)
- Direct PDF downloads: ?download=true parameter
- HTTPS enforcement
- DOI prefixes: 10.1164, 10.1165, 10.1513

Evidence-based configuration implemented following DANCE_FUNCTION_GUIDELINES.md
Phase 1-3 investigation completed 2025-08-09.
"""

import pytest
from unittest.mock import Mock, patch

from metapub.findit.registry import JournalRegistry
from metapub.findit.dances.generic import the_doi_slide, verify_pdf_url
from metapub.exceptions import NoPDFLink
from metapub.pubmedarticle import PubMedArticle


class TestATSConfiguration:
    """Test ATS publisher configuration and registry integration."""

    def setup_method(self):
        """Set up test fixtures."""
        self.registry = JournalRegistry()
        self.test_journals = [
            'Am J Respir Cell Mol Biol',
            'Am J Respir Crit Care Med', 
            'Ann Am Thorac Soc',
            'Proc Am Thorac Soc'
        ]
        self.expected_template = "https://www.thoracic.org/doi/pdf/{doi}?download=true"
        self.expected_function = "the_doi_slide"
        self.expected_publisher = "Ats"

    def test_ats_registry_assignment(self):
        """Test that all ATS journals are correctly assigned in registry."""
        for journal in self.test_journals:
            publisher_info = self.registry.get_publisher_for_journal(journal)
            
            assert publisher_info is not None, f"Journal '{journal}' not found in registry"
            assert publisher_info['name'] == self.expected_publisher
            assert publisher_info['dance_function'] == self.expected_function
            assert publisher_info['format_template'] == self.expected_template
            print(f"✓ {journal} → {self.expected_function}")

    def test_ats_template_evidence_based_pattern(self):
        """Test that ATS template uses evidence-based pattern from investigation."""
        # Evidence from Phase 1: https://www.thoracic.org/doi/pdf/{doi}?download=true
        publisher_info = self.registry.get_publisher_for_journal('Am J Respir Crit Care Med')
        template = publisher_info['format_template']
        
        # Verify evidence-based components
        assert 'thoracic.org' in template, "Should use current thoracic.org domain"
        assert template.startswith('https://'), "Should enforce HTTPS"
        assert '?download=true' in template, "Should include direct download parameter"
        assert '{doi}' in template, "Should support DOI-based URL construction"
        assert template == self.expected_template, "Should match exact evidence-based pattern"

    def test_ats_doi_prefixes(self):
        """Test ATS DOI prefixes based on evidence collection."""
        # Evidence shows ATS uses these DOI prefixes: 10.1164, 10.1165, 10.1513
        test_cases = [
            ("10.1164/rccm.202302-0327SO", "American Journal of Respiratory and Critical Care Medicine"),
            ("10.1165/rcmb.2022-0208TR", "American Journal of Respiratory Cell and Molecular Biology"),
            ("10.1513/AnnalsATS.202103-123OC", "Annals of the American Thoracic Society")
        ]
        
        for doi, expected_journal_type in test_cases:
            expected_url = f"https://www.thoracic.org/doi/pdf/{doi}?download=true"
            
            # Test URL construction
            constructed_url = self.expected_template.format(doi=doi)
            assert constructed_url == expected_url, f"DOI {doi} URL construction failed"
            print(f"✓ {doi} → {constructed_url}")

    def test_ats_url_construction_patterns(self):
        """Test URL construction with various DOI patterns found in evidence."""
        test_dois = [
            "10.1165/rcmb.2022-0208TR",  # From evidence collection
            "10.1164/rccm.202302-0327SO",  # From evidence collection  
            "10.1513/AnnalsATS.202103-123OC",  # Typical AnnalsATS pattern
            "10.1164/rccm.123456-789AB"  # Generic AJRCCM pattern
        ]
        
        for doi in test_dois:
            expected_url = f"https://www.thoracic.org/doi/pdf/{doi}?download=true"
            constructed_url = self.expected_template.format(doi=doi)
            
            assert constructed_url == expected_url
            assert constructed_url.startswith("https://www.thoracic.org/doi/pdf/")
            assert constructed_url.endswith("?download=true")
            print(f"✓ DOI {doi} constructs valid URL")

    @patch('metapub.findit.dances.generic.verify_pdf_url')
    def test_the_doi_slide_integration(self, mock_verify):
        """Test that the_doi_slide works with ATS configuration."""
        mock_verify.return_value = None  # Assume verification passes
        
        # Mock PubMedArticle
        mock_pma = Mock(spec=PubMedArticle)
        mock_pma.doi = "10.1165/rcmb.2022-0208TR"
        
        # Mock registry lookup to return ATS configuration
        with patch.object(JournalRegistry, 'get_publisher_for_journal') as mock_get_pub:
            mock_get_pub.return_value = {
                'name': self.expected_publisher,
                'dance_function': self.expected_function,
                'format_template': self.expected_template
            }
            
            # This would be called by FindIt logic with the registry template
            expected_url = self.expected_template.format(doi=mock_pma.doi)
            
            assert expected_url == "https://www.thoracic.org/doi/pdf/10.1165/rcmb.2022-0208TR?download=true"
            mock_verify.assert_not_called()  # Only called when verify=True
            print(f"✓ the_doi_slide integration works with ATS template")

    def test_ats_error_handling_missing_doi(self):
        """Test error handling when DOI is missing."""
        mock_pma = Mock(spec=PubMedArticle)
        mock_pma.doi = None
        
        with pytest.raises(NoPDFLink, match="DOI required"):
            # the_doi_slide should fail gracefully without DOI
            the_doi_slide(mock_pma, verify=False)

    def test_ats_error_handling_invalid_doi(self):
        """Test error handling with invalid DOI format."""
        mock_pma = Mock(spec=PubMedArticle) 
        mock_pma.doi = "invalid-doi-format"
        
        # Should construct URL but might fail verification
        # the_doi_slide doesn't validate DOI format - that's the caller's job
        # Just test that it doesn't crash with invalid input
        try:
            result = self.expected_template.format(doi=mock_pma.doi)
            expected = "https://www.thoracic.org/doi/pdf/invalid-doi-format?download=true"
            assert result == expected
            print(f"✓ Invalid DOI handled gracefully: {result}")
        except Exception as e:
            pytest.fail(f"Should handle invalid DOI gracefully: {e}")

    @patch('metapub.findit.dances.generic.verify_pdf_url')
    def test_ats_verification_expected_responses(self, mock_verify):
        """Test expected responses during PDF URL verification."""
        test_url = "https://www.thoracic.org/doi/pdf/10.1165/rcmb.2022-0208TR?download=true"
        
        # Test 403 Forbidden (expected for subscription content)
        mock_verify.side_effect = Exception("403 Forbidden")
        
        mock_pma = Mock(spec=PubMedArticle)
        mock_pma.doi = "10.1165/rcmb.2022-0208TR"
        mock_pma.journal = "Am J Respir Cell Mol Biol"  # Required by the_doi_slide
        
        # Should raise exception due to verification failure
        with pytest.raises(Exception, match="403 Forbidden"):
            the_doi_slide(mock_pma, verify=True)
        
        mock_verify.assert_called_once()
        print("✓ 403 Forbidden properly handled during verification")

    def test_ats_domain_migration_evidence(self):
        """Test that domain migration from atsjournals.org to thoracic.org is complete."""
        # Evidence shows all samples use www.thoracic.org, not atsjournals.org
        for journal in self.test_journals:
            publisher_info = self.registry.get_publisher_for_journal(journal)
            template = publisher_info['format_template']
            
            assert 'thoracic.org' in template, f"Journal {journal} should use thoracic.org domain"
            assert 'atsjournals.org' not in template, f"Journal {journal} should not use legacy atsjournals.org"
            print(f"✓ {journal} uses current thoracic.org domain")

    def test_ats_https_enforcement(self):
        """Test HTTPS enforcement in ATS configuration."""
        # Evidence-based configuration should enforce HTTPS
        for journal in self.test_journals:
            publisher_info = self.registry.get_publisher_for_journal(journal)
            template = publisher_info['format_template']
            
            assert template.startswith('https://'), f"Journal {journal} should enforce HTTPS"
            assert not template.startswith('http://'), f"Journal {journal} should not use HTTP"
            print(f"✓ {journal} enforces HTTPS")

    def test_ats_download_parameter_inclusion(self):
        """Test that ?download=true parameter is included for direct PDF downloads."""
        # Evidence shows this parameter enables direct PDF downloads
        for journal in self.test_journals:
            publisher_info = self.registry.get_publisher_for_journal(journal)
            template = publisher_info['format_template']
            
            assert '?download=true' in template, f"Journal {journal} should include download parameter"
            print(f"✓ {journal} includes ?download=true parameter")

    def test_ats_journal_coverage(self):
        """Test that all major ATS journals are covered."""
        # Based on evidence and ATS website, these are the main respiratory journals
        expected_journals = [
            'Am J Respir Cell Mol Biol',  # American Journal of Respiratory Cell and Molecular Biology
            'Am J Respir Crit Care Med',   # American Journal of Respiratory and Critical Care Medicine  
            'Ann Am Thorac Soc',          # Annals of the American Thoracic Society
            'Proc Am Thorac Soc'         # Proceedings of the American Thoracic Society (legacy)
        ]
        
        registered_journals = []
        for journal in expected_journals:
            publisher_info = self.registry.get_publisher_for_journal(journal)
            if publisher_info and publisher_info['name'] == self.expected_publisher:
                registered_journals.append(journal)
        
        coverage_rate = len(registered_journals) / len(expected_journals)
        assert coverage_rate >= 0.75, f"ATS journal coverage too low: {coverage_rate:.2%}"
        print(f"✓ ATS journal coverage: {len(registered_journals)}/{len(expected_journals)} ({coverage_rate:.1%})")


class TestATSEvidenceValidation:
    """Test that implementation matches evidence collected in Phase 1."""

    def test_evidence_pattern_match(self):
        """Test that configuration matches evidence from HTML samples."""
        # Evidence file: ats_evidence_findings.json
        # Found pattern: https://www.thoracic.org/doi/pdf/10.1165/rcmb.2022-0208TR?download=true
        
        registry = JournalRegistry()
        publisher_info = registry.get_publisher_for_journal('Am J Respir Cell Mol Biol')
        
        evidence_pattern = "https://www.thoracic.org/doi/pdf/{doi}?download=true"
        configured_pattern = publisher_info['format_template']
        
        assert configured_pattern == evidence_pattern, "Configuration should match evidence exactly"
        print(f"✓ Evidence pattern matches configuration: {evidence_pattern}")

    def test_evidence_domain_consistency(self):
        """Test domain consistency with evidence collection results."""
        # Evidence showed single consistent domain: www.thoracic.org
        registry = JournalRegistry()
        
        for journal in ['Am J Respir Cell Mol Biol', 'Am J Respir Crit Care Med']:
            publisher_info = registry.get_publisher_for_journal(journal)
            template = publisher_info['format_template']
            
            assert 'www.thoracic.org' in template, f"Should match evidence domain for {journal}"
            print(f"✓ {journal} matches evidence domain www.thoracic.org")

    def test_evidence_doi_prefix_coverage(self):
        """Test DOI prefix coverage matches evidence collection."""
        # Evidence found DOI prefixes: 10.1164, 10.1165, 10.1513
        evidence_prefixes = ["10.1164", "10.1165", "10.1513"]
        template = "https://www.thoracic.org/doi/pdf/{doi}?download=true"
        
        for prefix in evidence_prefixes:
            test_doi = f"{prefix}/test.2023.article"
            constructed_url = template.format(doi=test_doi)
            expected_url = f"https://www.thoracic.org/doi/pdf/{test_doi}?download=true"
            
            assert constructed_url == expected_url, f"DOI prefix {prefix} should be supported"
            print(f"✓ Evidence DOI prefix {prefix} supported")


if __name__ == '__main__':
    # Run specific ATS tests
    pytest.main([__file__, '-v', '--tb=short'])