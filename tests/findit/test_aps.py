"""
Test suite for APS (American Physiological Society) dance function.

Test approach:
- Uses XML fixtures from real PMIDs to avoid network dependencies
- Tests DOI approach based on HTML analysis
- Comprehensive coverage of dance function requirements
"""

import pytest
import os
import sys

# Add project root to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from metapub.findit.dances.generic import the_doi_slide
from metapub.exceptions import NoPDFLink, MetaPubError
from tests.fixtures import load_pmid_xml, APS_EVIDENCE_PMIDS
from metapub.findit.registry import JournalRegistry


class TestAPSJournalRecognition:
    """Test APS journal recognition."""

    def test_aps_journal_list_completeness(self):
        """Test that aps_journals list contains expected journals."""
        # Key APS journals should be included
        expected_journals = [
            'Am J Physiol Heart Circ Physiol',
            'Am J Physiol Cell Physiol',
            'J Appl Physiol',
            'J Neurophysiol',
            'Physiol Rev'
        ]

        # Test journal recognition using registry
        registry = JournalRegistry()

        found_count = 0
        for journal in expected_journals:
            publisher_info = registry.get_publisher_for_journal(journal)
            if publisher_info and publisher_info['name'] == 'Aps':
                print(f"✓ {journal} correctly mapped to APS")
                found_count += 1
            else:
                print(f"⚠ {journal} mapped to different publisher: {publisher_info['name'] if publisher_info else 'None'}")

        assert found_count > 0, "No APS journals found in registry"
        registry.close()


class TestAPSDanceFunction:
    """Test APS dance function URL construction and error handling."""

    def test_aps_url_construction_with_fixtures(self):
        """Test URL construction using XML fixtures."""

        for pmid, expected_data in APS_EVIDENCE_PMIDS.items():
            # Load article from XML fixture
            article = load_pmid_xml(pmid)

            # Verify fixture data
            assert article.journal == expected_data['journal'], f"PMID {pmid} journal mismatch"
            assert article.doi == expected_data['doi'], f"PMID {pmid} DOI mismatch"

            # Test URL construction
            url = the_doi_slide(article, verify=False)

            expected_url = f"https://journals.physiology.org/doi/pdf/{expected_data['doi']}"
            assert url == expected_url, f"PMID {pmid}: expected {expected_url}, got {url}"

            # Verify URL structure
            assert url.startswith('https://journals.physiology.org/doi/pdf/'), f"PMID {pmid}: URL has wrong structure"
            assert expected_data['doi'] in url, f"PMID {pmid}: DOI not found in URL"



    def test_aps_verify_false_success(self):
        """Test successful URL construction with verify=False."""
        article = load_pmid_xml('34995163')

        url = the_doi_slide(article, verify=False)
        expected_url = "https://journals.physiology.org/doi/pdf/10.1152/ajpheart.00590.2021"

        assert url == expected_url



class TestAPSEvidenceValidation:
    """Validate that our evidence-based approach is sound."""

    def test_doi_prefix_consistency(self):
        """Test that all APS PMIDs use consistent DOI prefix."""
        doi_prefix = '10.1152'

        for pmid, data in APS_EVIDENCE_PMIDS.items():
            assert data['doi'].startswith(doi_prefix), f"PMID {pmid} has unexpected DOI prefix: {data['doi']}"

    def test_journal_consistency(self):
        """Test that all test journals are in the APS registry."""

        registry = JournalRegistry()
        test_journals = set(data['journal'] for data in APS_EVIDENCE_PMIDS.values())

        for journal in test_journals:
            publisher_info = registry.get_publisher_for_journal(journal)
            assert publisher_info and publisher_info['name'] == 'Aps', f"Test journal '{journal}' not found in aps registry"

        registry.close()

    def test_fixture_completeness(self):
        """Test that all evidence PMIDs have working fixtures."""
        for pmid in APS_EVIDENCE_PMIDS.keys():
            # This should not raise an exception
            article = load_pmid_xml(pmid)

            # Basic validation
            assert article.journal is not None, f"PMID {pmid}: missing journal"
            assert article.doi is not None, f"PMID {pmid}: missing DOI"

            # DOI format validation
            assert article.doi.startswith('10.'), f"PMID {pmid}: invalid DOI format"


class TestAPSIntegration:
    """Integration tests with metapub components."""

    def test_aps_journal_list_integration(self):
        """Test APS journal list integration."""

        # Test that APS journals are accessible via registry
        registry = JournalRegistry()

        publisher_info = registry.get_publisher_for_journal('Am J Physiol Heart Circ Physiol')
        assert publisher_info and publisher_info['name'] == 'Aps', "APS journal not found in registry"

        registry.close()

        # Verify dance function is accessible and works
        article = load_pmid_xml('34995163')
        url = the_doi_slide(article, verify=False)

        assert url.startswith('https://journals.physiology.org/doi/pdf/')
        assert '10.1152/ajpheart.00590.2021' in url


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
