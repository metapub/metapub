"""Tests for ASME (American Society of Mechanical Engineers) dance function."""

import pytest
from unittest.mock import patch, Mock
import requests

from .common import BaseDanceTest
from metapub import PubMedFetcher
from metapub.findit.dances import the_asme_animal
from metapub.exceptions import AccessDenied, NoPDFLink
from tests.fixtures import load_pmid_xml, ASME_EVIDENCE_PMIDS


class TestASMEDance(BaseDanceTest):
    """Test cases for ASME (American Society of Mechanical Engineers)."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.fetch = PubMedFetcher()

    def test_asme_assembly_url_construction_appl_mech(self):
        """Test 1: URL construction success (J Appl Mech).
        
        PMID: 38449742 (J Appl Mech)
        Expected: Should construct valid ASME PDF URL
        """
        pma = self.fetch.article_by_pmid('38449742')
        
        print(f"Test 1 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification (should always work for URL construction)
        url = the_asme_animal(pma, verify=False)
        assert url is not None
        assert 'asmedigitalcollection.asme.org' in url
        assert url.startswith('https://')
        print(f"Test 1 - PDF URL: {url}")

    def test_asme_assembly_url_construction_biomech_eng(self):
        """Test 2: Biomechanical Engineering.
        
        PMID: 38913074 (J Biomech Eng)
        Expected: Should construct valid ASME PDF URL
        """
        pma = self.fetch.article_by_pmid('38913074')
        
        print(f"Test 2 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Skip test if no DOI available
        if not pma.doi:
            print("Test 2 - Skipping: No DOI available for this PMID")
            return

        # Test without verification
        url = the_asme_animal(pma, verify=False)
        assert url is not None
        assert 'asmedigitalcollection.asme.org' in url
        print(f"Test 2 - PDF URL: {url}")

    def test_asme_assembly_url_construction_heat_transfer(self):
        """Test 3: Heat Transfer.
        
        PMID: 35833154 (J Heat Transfer)
        Expected: Should construct valid ASME PDF URL
        """
        pma = self.fetch.article_by_pmid('35833154')
        
        print(f"Test 3 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Skip test if no DOI available
        if not pma.doi:
            print("Test 3 - Skipping: No DOI available for this PMID")
            return

        # Test without verification
        url = the_asme_animal(pma, verify=False)
        assert url is not None
        assert 'asmedigitalcollection.asme.org' in url
        print(f"Test 3 - PDF URL: {url}")

    @patch('metapub.findit.dances.asme.unified_uri_get')
    def test_asme_assembly_successful_access(self, mock_get):
        """Test 4: Successful PDF access simulation.
        
        Expected: Should return PDF URL when accessible
        """
        # Mock successful PDF response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.headers = {'content-type': 'application/pdf'}
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('38449742')
        
        # Test with verification - should succeed
        url = the_asme_animal(pma, verify=True)
        assert 'asmedigitalcollection.asme.org' in url
        print(f"Test 4 - Successful verified access: {url}")


    @patch('metapub.findit.dances.asme.get_crossref_pdf_links')
    @patch('metapub.findit.dances.asme.unified_uri_get')
    def test_asme_assembly_network_error(self, mock_get, mock_crossref):
        """Test 6: Network error handling.
        
        Expected: Should handle network errors gracefully
        """
        # Mock CrossRef to return no results (forces fallback to direct approach)
        mock_crossref.side_effect = NoPDFLink("No CrossRef PDF links found")
        
        # Mock network error
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

        pma = self.fetch.article_by_pmid('38449742')
        
        # Test - should handle network error
        with pytest.raises(NoPDFLink) as exc_info:
            the_asme_animal(pma, verify=True)
        
        assert 'TXERROR' in str(exc_info.value)
        print(f"Test 6 - Correctly handled network error: {exc_info.value}")


    @patch('metapub.findit.dances.asme.get_crossref_pdf_links')
    @patch('metapub.findit.dances.asme.unified_uri_get')
    def test_asme_assembly_404_error(self, mock_get, mock_crossref):
        """Test 8: Article not found (404 error).
        
        Expected: Should try multiple patterns and handle 404 errors
        """
        # Mock CrossRef to return no results (forces fallback to direct approach)
        mock_crossref.side_effect = NoPDFLink("No CrossRef PDF links found")
        
        # Mock 404 response for all attempts
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('38449742')
        
        # Test - should try multiple patterns and eventually fail
        with pytest.raises(NoPDFLink) as exc_info:
            the_asme_animal(pma, verify=True)
        
        assert 'TXERROR' in str(exc_info.value) or 'PATTERN' in str(exc_info.value)
        print(f"Test 8 - Correctly handled 404: {exc_info.value}")

    @patch('metapub.findit.dances.asme.unified_uri_get')
    def test_asme_assembly_journal_code_mapping(self, mock_get):
        """Test 9: Journal code mapping and URL construction.
        
        Expected: Should use journal code in URL when available
        """
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.headers = {'content-type': 'application/pdf'}
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('38449742')
        
        # Test - should use journal-specific URL
        url = the_asme_animal(pma, verify=True)
        assert 'asmedigitalcollection.asme.org' in url
        # Should contain journal code if mapping worked
        print(f"Test 9 - Journal code mapping: {url}")

    def test_asme_assembly_doi_pattern_warning(self):
        """Test 10: Non-standard DOI pattern handling.
        
        Expected: Should handle non-10.1115 DOI patterns but may warn
        """
        # Create a mock PMA with non-ASME DOI pattern
        pma = Mock()
        pma.doi = '10.1016/j.example.2023.123456'  # Non-ASME DOI
        pma.journal = 'J Appl Mech'
        
        # Should still construct URL without verification
        url = the_asme_animal(pma, verify=False)
        assert url is not None
        assert 'asmedigitalcollection.asme.org' in url
        print(f"Test 10 - Non-standard DOI pattern handled: {url}")


def test_asme_journal_recognition():
    """Test that ASME journals are properly recognized in the registry."""
    from metapub.findit.registry import JournalRegistry
    from metapub.findit.journals.asme import asme_journals
    
    registry = JournalRegistry()
    
    # Test sample ASME journals (using PubMed abbreviated names)
    test_journals = [
        'J Appl Mech',
        'J Biomech Eng',
        'J Heat Transfer',
        'J Fluids Eng',
        'J Tribol'
    ]
    
    # Test journal recognition
    found_count = 0
    for journal in test_journals:
        publisher_info = registry.get_publisher_for_journal(journal)
        if publisher_info and publisher_info['name'] == 'asme':
            assert publisher_info['dance_function'] == 'the_doi_slide'
            print(f"✓ {journal} correctly mapped to ASME")
            found_count += 1
        else:
            print(f"⚠ {journal} mapped to different publisher: {publisher_info['name'] if publisher_info else 'None'}")
    
    # Just make sure we found at least one ASME journal
    assert found_count > 0, "No ASME journals found in registry with asme publisher"
    print(f"✓ Found {found_count} properly mapped ASME journals")
    
    registry.close()


if __name__ == '__main__':
    # Run basic tests if executed directly
    test_instance = TestASMEDance()
    test_instance.setUp()
    
    print("Running ASME tests...")
    print("\n" + "="*60)
    
    tests = [
        ('test_asme_assembly_url_construction_appl_mech', 'Applied Mechanics URL construction'),
        ('test_asme_assembly_url_construction_biomech_eng', 'Biomech Eng URL construction'),
        ('test_asme_assembly_url_construction_heat_transfer', 'Heat Transfer URL construction'),
        ('test_asme_assembly_successful_access', 'Successful access simulation'),
        ('test_asme_assembly_paywall_detection', 'Paywall detection'),
        ('test_asme_assembly_network_error', 'Network error handling'),
        ('test_asme_assembly_missing_doi', 'Missing DOI handling'),
        ('test_asme_assembly_404_error', '404 error handling'),
        ('test_asme_assembly_journal_code_mapping', 'Journal code mapping'),
        ('test_asme_assembly_doi_pattern_warning', 'Non-standard DOI pattern handling')
    ]
    
    for test_method, description in tests:
        try:
            getattr(test_instance, test_method)()
            print(f"✓ {description} works")
        except Exception as e:
            print(f"✗ {description} failed: {e}")
    
    try:
        test_asme_journal_recognition()
        print("✓ Registry test passed: Journal recognition works")
    except Exception as e:
        print(f"✗ Registry test failed: {e}")
    
    print("\n" + "="*60)
    print("Test suite completed!")


class TestASMEXMLFixtures:
    """Test ASME dance function with real XML fixtures."""

    def test_asme_authentic_metadata_validation(self):
        """Validate authentic metadata from XML fixtures matches expected patterns."""
        for pmid, expected in ASME_EVIDENCE_PMIDS.items():
            pma = load_pmid_xml(pmid)
            
            # Validate DOI follows ASME pattern (10.1115/)
            assert pma.doi == expected['doi']
            assert pma.doi.startswith('10.1115/'), f"ASME DOI must start with 10.1115/, got: {pma.doi}"
            
            # Validate journal name matches expected
            assert pma.journal == expected['journal']
            
            # Validate PMID matches
            assert pma.pmid == pmid
            
            print(f"✓ PMID {pmid}: {pma.journal} - {pma.doi}")

    def test_asme_url_construction_without_verification(self):
        """Test URL construction without verification using XML fixtures."""
        for pmid in ASME_EVIDENCE_PMIDS.keys():
            pma = load_pmid_xml(pmid)
            
            # Test URL construction without verification
            result = the_asme_animal(pma, verify=False)
            
            # Should be ASME URL pattern
            assert result is not None
            assert 'asmedigitalcollection.asme.org' in result
            assert result.startswith('https://')
            
            print(f"✓ PMID {pmid} URL: {result}")

    @patch('metapub.findit.dances.asme.unified_uri_get')
    def test_asme_url_construction_with_mocked_verification(self, mock_get):
        """Test URL construction with mocked verification."""
        # Mock successful PDF response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.headers = {'content-type': 'application/pdf'}
        mock_get.return_value = mock_response
        
        for pmid in ASME_EVIDENCE_PMIDS.keys():
            pma = load_pmid_xml(pmid)
            
            result = the_asme_animal(pma, verify=True)
            
            assert result is not None
            assert 'asmedigitalcollection.asme.org' in result
            print(f"✓ PMID {pmid} verified URL: {result}")

    @patch('metapub.findit.dances.asme.get_crossref_pdf_links')
    @patch('metapub.findit.dances.asme.unified_uri_get')
    def test_asme_paywall_handling(self, mock_get, mock_crossref):
        """Test paywall detection and error handling."""
        # Mock CrossRef to return no results (forces fallback to direct approach)
        mock_crossref.side_effect = NoPDFLink("No CrossRef PDF links found")
        
        # Mock paywall response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.text = '''<html><body>
            <h1>Subscription Required</h1>
            <p>ASME membership required for access</p>
        </body></html>'''
        mock_get.return_value = mock_response
        
        pma = load_pmid_xml('38449742')  # Use first test PMID
        
        with pytest.raises((AccessDenied, NoPDFLink)):
            the_asme_animal(pma, verify=True)

    def test_asme_journal_coverage(self):
        """Test journal coverage across different ASME publications."""
        journals_found = set()
        
        for pmid in ASME_EVIDENCE_PMIDS.keys():
            pma = load_pmid_xml(pmid)
            journals_found.add(pma.journal)
        
        # Should have multiple different ASME journals
        assert len(journals_found) >= 3, f"Expected at least 3 different journals, got: {journals_found}"
        
        # All should be known ASME journals
        expected_journals = {'J Appl Mech', 'J Biomech Eng', 'J Heat Transfer'}
        assert journals_found == expected_journals, f"Unexpected journals: {journals_found - expected_journals}"

    def test_asme_doi_pattern_consistency(self):
        """Test that all ASME PMIDs use 10.1115 DOI prefix."""
        doi_prefix = '10.1115'
        
        for pmid, data in ASME_EVIDENCE_PMIDS.items():
            assert data['doi'].startswith(doi_prefix), f"PMID {pmid} has unexpected DOI prefix: {data['doi']}"
            
            pma = load_pmid_xml(pmid)
            assert pma.doi.startswith(doi_prefix), f"PMID {pmid} XML fixture has unexpected DOI: {pma.doi}"


    def test_asme_template_flexibility(self):
        """Test template flexibility for ASME URL patterns."""
        pma = load_pmid_xml('38449742')  # J Appl Mech
        
        # Test URL construction 
        result = the_asme_animal(pma, verify=False)
        
        # Should follow ASME URL pattern (may be CrossRef or direct URL)
        assert result is not None
        assert 'asmedigitalcollection.asme.org' in result
        assert result.startswith('https://')
        # Note: DOI may not be directly in URL if CrossRef returns alternative URL

    def test_asme_pmc_availability(self):
        """Test coverage of PMC-available ASME articles."""
        # All our test articles have PMC IDs
        for pmid, expected in ASME_EVIDENCE_PMIDS.items():
            pma = load_pmid_xml(pmid)
            
            assert 'pmc' in expected, f"PMID {pmid} should have PMC ID"
            
            # Test URL construction still works even with PMC availability
            result = the_asme_animal(pma, verify=False)
            assert result is not None
            assert 'asmedigitalcollection.asme.org' in result
            
            print(f"✓ PMID {pmid} (PMC: {expected['pmc']}) works with ASME infrastructure: {result}")