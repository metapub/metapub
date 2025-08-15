"""
Test suite for APA (American Psychological Association) publisher dance function.

Test approach:
- Uses XML fixtures from real PMIDs to avoid network dependencies  
- Tests subscription model with proper paywall detection
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
from metapub.exceptions import NoPDFLink, MetaPubError, AccessDenied
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
        
        from metapub.findit.registry import JournalRegistry
        registry = JournalRegistry()
        
        for journal in expected_journals:
            publisher_info = registry.get_publisher_for_journal(journal)
            assert publisher_info and publisher_info['name'] == 'apa', f"Expected APA journal '{journal}' not found in registry or mapped to wrong publisher"
        
        registry.close()


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
        """Test that all test journals are in the APA registry."""
        from metapub.findit.registry import JournalRegistry
        registry = JournalRegistry()
        
        test_journals = set(data['journal'] for data in APA_EVIDENCE_PMIDS.values())
        
        for journal in test_journals:
            publisher_info = registry.get_publisher_for_journal(journal)
            assert publisher_info and publisher_info['name'] == 'apa', f"Test journal '{journal}' not found in APA registry"
        
        registry.close()
    
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
        """Test APA registry integration."""
        from metapub.findit.registry import JournalRegistry
        registry = JournalRegistry()
        
        # Test that APA journals are accessible via registry
        publisher_info = registry.get_publisher_for_journal('Am Psychol')
        assert publisher_info and publisher_info['name'] == 'apa'
        
        # Verify dance function works with registry system
        article = load_pmid_xml('34843274')
        url = the_doi_slide(article, verify=False)
        
        assert url.startswith('https://psycnet.apa.org/fulltext/')
        assert '10.1037/amp0000904' in url
        
        registry.close()
    
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


class TestAPAXMLFixturesComprehensive:
    """Comprehensive XML fixtures tests following TRANSITION_TESTS_TO_REAL_DATA.md guidelines."""
    
    def test_apa_xml_fixtures_metadata_validation(self):
        """Test comprehensive metadata validation from XML fixtures."""
        for pmid, expected_data in APA_EVIDENCE_PMIDS.items():
            pma = load_pmid_xml(pmid)
            
            # Verify authentic metadata matches expectations
            assert pma.pmid == pmid, f"PMID mismatch: {pma.pmid} != {pmid}"
            assert pma.doi == expected_data['doi'], f"DOI mismatch for {pmid}: {pma.doi} != {expected_data['doi']}"
            assert expected_data['journal'] in pma.journal, f"Journal mismatch for {pmid}: {expected_data['journal']} not in {pma.journal}"
            
            print(f"✓ Real PMID {pmid} - {expected_data['journal']}: {pma.doi}")
        
        print(f"✅ All {len(APA_EVIDENCE_PMIDS)} XML fixtures validated")

    @patch('metapub.findit.dances.generic.verify_pdf_url')
    def test_apa_url_construction_with_mocked_verification(self, mock_verify):
        """Test URL construction with mocked verification."""
        mock_verify.return_value = True
        
        for pmid, expected_data in APA_EVIDENCE_PMIDS.items():
            pma = load_pmid_xml(pmid)
            
            result = the_doi_slide(pma, verify=True)
            expected_url = f"https://psycnet.apa.org/fulltext/{pma.doi}.pdf"
            
            assert result == expected_url
            mock_verify.assert_called_with(expected_url, request_timeout=10, max_redirects=3)
            print(f"✓ PMID {pmid} URL with verification: {result}")

    @patch('metapub.findit.dances.generic.verify_pdf_url')
    def test_apa_paywall_handling(self, mock_verify):
        """Test paywall detection and error handling."""
        mock_verify.side_effect = AccessDenied('APA subscription required')
        
        pma = load_pmid_xml('34843274')  # Use first test PMID
        
        with pytest.raises(AccessDenied):
            the_doi_slide(pma, verify=True)

    def test_apa_journal_coverage_comprehensive(self):
        """Test journal coverage across different APA publications."""
        journal_coverage = {}
        
        for pmid, expected_data in APA_EVIDENCE_PMIDS.items():
            pma = load_pmid_xml(pmid)
            
            journal = expected_data['journal']
            if journal not in journal_coverage:
                journal_coverage[journal] = []
            journal_coverage[journal].append(pmid)
            
            assert journal in pma.journal, f"Journal mismatch: {journal} not in {pma.journal}"
            print(f"✓ {journal} PMID {pmid}: DOI={pma.doi}")
        
        # Should have multiple different APA journals
        assert len(journal_coverage) >= 4, f"Expected at least 4 different journals, got: {journal_coverage}"
        
        for journal, pmids in journal_coverage.items():
            print(f"✓ {journal}: {len(pmids)} PMIDs - {pmids}")
        
        print(f"✅ Coverage: {len(journal_coverage)} different APA journals")

    def test_apa_doi_pattern_consistency(self):
        """Test that all APA PMIDs use 10.1037 DOI prefix."""
        doi_prefix = '10.1037'
        
        for pmid, data in APA_EVIDENCE_PMIDS.items():
            assert data['doi'].startswith(doi_prefix), f"PMID {pmid} has unexpected DOI prefix: {data['doi']}"
            
            pma = load_pmid_xml(pmid)
            assert pma.doi.startswith(doi_prefix), f"PMID {pmid} XML fixture has unexpected DOI: {pma.doi}"

    def test_apa_authentic_data_consistency(self):
        """Test consistency between expected and authentic XML data."""
        for pmid, expected_data in APA_EVIDENCE_PMIDS.items():
            pma = load_pmid_xml(pmid)
            
            # Compare DOI exactly
            assert pma.doi == expected_data['doi'], \
                f"DOI inconsistency for {pmid}: expected {expected_data['doi']}, got {pma.doi}"
            
            # Compare journal (flexible matching for abbreviations)
            expected_journal = expected_data['journal']
            actual_journal = pma.journal
            
            assert expected_journal in actual_journal or actual_journal in expected_journal, \
                f"Journal inconsistency for {pmid}: expected '{expected_journal}', got '{actual_journal}'"
            
            print(f"✓ Consistency check PMID {pmid}: DOI={pma.doi}, Journal={actual_journal}")
        
        print(f"✅ All {len(APA_EVIDENCE_PMIDS)} PMIDs show consistent authentic data")


    def test_apa_template_flexibility(self):
        """Test template flexibility for APA URL patterns."""
        pma = load_pmid_xml('34843274')  # Am Psychol
        
        # Test with registry-based template lookup
        result = the_doi_slide(pma, verify=False)
        
        expected = f'https://psycnet.apa.org/fulltext/{pma.doi}.pdf'
        assert result == expected
        
        # Should work with any APA DOI
        assert pma.doi in result
        assert 'psycnet.apa.org/fulltext/' in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])