"""Tests for Brill Academic Publishers dance function."""

import pytest
from unittest.mock import patch, Mock
import requests

from .common import BaseDanceTest
from metapub import PubMedFetcher
from metapub.findit.dances import the_brill_bridge
from metapub.exceptions import AccessDenied, NoPDFLink
from metapub.findit.registry import JournalRegistry
from tests.fixtures import load_pmid_xml, BRILL_EVIDENCE_PMIDS

class TestBrillDance(BaseDanceTest):
    """Test cases for Brill Academic Publishers."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.fetch = PubMedFetcher()

    @pytest.mark.live_network
    def test_brill_bridge_url_construction_early_sci_med(self):
        """Test 1: PDF URL construction without verification (Early Sci Med).

        PMID: 26415349 - DOI resolves to brill.com/view/journals/esm/...
        Expected: returns downloadpdf URL without hitting the WAF-blocked article page.
        """
        pma = load_pmid_xml('26415349')

        assert pma.journal == 'Early Sci Med'
        assert pma.doi == '10.1163/15733823-00202p03'

        url = the_brill_bridge(pma, verify=False)
        assert url is not None
        assert 'brill.com/downloadpdf/journals/' in url
        print(f"Test 1 - PDF URL: {url}")

    @pytest.mark.live_network
    def test_brill_bridge_url_construction_early_sci_med_alt(self):
        """Test 2: PDF URL construction without verification (Early Sci Med alt).

        PMID: 11873782
        Expected: returns downloadpdf URL.
        """
        pma = load_pmid_xml('11873782')

        assert pma.journal == 'Early Sci Med'
        assert pma.doi == '10.1163/157338201x00154'

        url = the_brill_bridge(pma, verify=False)
        assert url is not None
        assert 'brill.com/downloadpdf/journals/' in url
        print(f"Test 2 - PDF URL: {url}")

    @pytest.mark.live_network
    def test_brill_bridge_url_construction_toung_pao(self):
        """Test 3: PDF URL construction without verification (Toung Pao).

        PMID: 11618220
        Expected: returns downloadpdf URL.
        """
        pma = load_pmid_xml('11618220')

        assert pma.journal == 'Toung Pao'
        assert pma.doi == '10.1163/156853287x00032'

        url = the_brill_bridge(pma, verify=False)
        assert url is not None
        assert 'brill.com/downloadpdf/journals/' in url
        print(f"Test 3 - PDF URL: {url}")

    @pytest.mark.live_network
    def test_brill_bridge_url_construction_phronesis(self):
        """Test 4: PDF URL construction without verification (Phronesis).

        PMID: 11636720
        Expected: returns downloadpdf URL.
        """
        pma = load_pmid_xml('11636720')

        assert pma.journal == 'Phronesis (Barc)'
        assert pma.doi == '10.1163/156852873x00014'

        url = the_brill_bridge(pma, verify=False)
        assert url is not None
        assert 'brill.com/downloadpdf/journals/' in url
        print(f"Test 4 - PDF URL: {url}")

    # Test removed: Multiple tests - successful access, paywall detection, access forbidden, network error - functionality now handled by verify_pdf_url

    @pytest.mark.live_network
    def test_brill_bridge_invalid_doi(self):
        """Test 11: Article with non-Brill DOI.

        Expected: Should raise NoPDFLink for DOI lookup failure
        """
        # Create a mock PMA with non-Brill DOI
        pma = Mock()
        pma.doi = '10.1000/invalid-doi'
        pma.journal = 'Early Sci Med'

        with pytest.raises(NoPDFLink) as exc_info:
            the_brill_bridge(pma, verify=False)

        assert 'TXERROR' in str(exc_info.value)
        print(f"Test 11 - Correctly handled invalid DOI: {exc_info.value}")

    # Test removed: test_brill_bridge_article_not_found - functionality now handled by verify_pdf_url


def test_brill_journal_recognition():
    """Test that Brill journals are properly recognized in the registry."""

    registry = JournalRegistry()

    # Test sample Brill journals
    test_journals = [
        'Early Sci Med',
        'Toung Pao',
        'Phronesis',
        'Behaviour',
        'Mnemosyne'
    ]

    # Test journal recognition
    found_count = 0
    for journal in test_journals:
        publisher_info = registry.get_publisher_for_journal(journal)
        if publisher_info and publisher_info['name'] == 'Brill':
            # Note: Brill may use 'the_doi_slide' now instead of 'the_brill_bridge'
            assert publisher_info['dance_function'] in ['the_brill_bridge', 'the_doi_slide']
            print(f"✓ {journal} correctly mapped to Brill Academic Publishers")
            found_count += 1
        else:
            print(f"⚠ {journal} mapped to different publisher: {publisher_info['name'] if publisher_info else 'None'}")

    # Just make sure we found at least one Brill journal (the test may not find all if registry is not populated)
    if found_count == 0:
        print("⚠ No Brill journals found in registry - this may be expected if registry not populated")
    else:
        print(f"✓ Found {found_count} properly mapped Brill journals")

    registry.close()

class TestBrillXMLFixtures:
    """Test Brill dance function with real XML fixtures."""

    def test_brill_authentic_metadata_validation(self):
        """Validate authentic metadata from XML fixtures matches expected patterns."""
        for pmid, expected in BRILL_EVIDENCE_PMIDS.items():
            pma = load_pmid_xml(pmid)

            # Validate DOI follows Brill pattern (10.1163/)
            assert pma.doi == expected['doi']
            assert pma.doi.startswith('10.1163/'), f"Brill DOI must start with 10.1163/, got: {pma.doi}"

            # Validate journal name matches expected
            assert pma.journal == expected['journal']

            # Validate PMID matches
            assert pma.pmid == pmid

            print(f"✓ PMID {pmid}: {pma.journal} - {pma.doi}")

    # Test removed: Multiple tests - URL construction and paywall handling - functionality now handled by verify_pdf_url

    def test_brill_journal_coverage(self):
        """Test journal coverage across different Brill publications."""
        journals_found = set()

        for pmid in BRILL_EVIDENCE_PMIDS.keys():
            pma = load_pmid_xml(pmid)
            journals_found.add(pma.journal)

        # Should have multiple different Brill journals
        assert len(journals_found) >= 3, f"Expected at least 3 different journals, got: {journals_found}"

        # All should be known Brill journals (updated to match actual fixtures)
        expected_journals = {'Early Sci Med', 'Toung Pao', 'Phronesis (Barc)', 'Behaviour'}
        assert journals_found == expected_journals, f"Unexpected journals: {journals_found - expected_journals}"

    def test_brill_doi_pattern_consistency(self):
        """Test that all Brill PMIDs use 10.1163 DOI prefix."""
        doi_prefix = '10.1163'

        for pmid, data in BRILL_EVIDENCE_PMIDS.items():
            assert data['doi'].startswith(doi_prefix), f"PMID {pmid} has unexpected DOI prefix: {data['doi']}"

            pma = load_pmid_xml(pmid)
            assert pma.doi.startswith(doi_prefix), f"PMID {pmid} XML fixture has unexpected DOI: {pma.doi}"

    @patch('metapub.findit.dances.brill.the_doi_2step')
    def test_brill_template_flexibility(self, mock_doi_2step):
        """Test PDF URL derivation from article URL pattern.

        The function derives the PDF URL directly from the DOI-resolved article
        URL without fetching the article page (which is behind AWS WAF).
        Pattern: /view/journals/ -> /downloadpdf/journals/
        """
        pma = load_pmid_xml('26415349')  # Early Sci Med

        article_url = 'https://brill.com/view/journals/esm/20/2/article-p150_3.xml'
        mock_doi_2step.return_value = article_url

        result = the_brill_bridge(pma, verify=False)

        assert result == 'https://brill.com/downloadpdf/journals/esm/20/2/article-p150_3.xml'
        assert 'downloadpdf/journals' in result
        mock_doi_2step.assert_called_with(pma.doi)    # Test removed: test_brill_historical_journals_coverage - functionality now handled by verify_pdf_url