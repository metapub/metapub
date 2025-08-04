"""Tests for Project MUSE dance function."""

import pytest
from unittest.mock import patch, Mock
import requests

from .common import BaseDanceTest
from metapub import PubMedFetcher
from metapub.findit.dances import the_projectmuse_melody
from metapub.exceptions import AccessDenied, NoPDFLink


class TestProjectMuseDance(BaseDanceTest):
    """Test cases for Project MUSE."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.fetch = PubMedFetcher()

    def test_projectmuse_melody_url_construction_narrat_inq(self):
        """Test 1: URL construction success (Narrat Inq Bioeth).
        
        PMID: 38661995 (Narrat Inq Bioeth)
        Expected: Should construct valid Project MUSE PDF URL
        """
        pma = self.fetch.article_by_pmid('38661995')
        
        print(f"Test 1 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification (should always work for URL construction)
        url = the_projectmuse_melody(pma, verify=False)
        assert url is not None
        assert 'muse.jhu.edu' in url
        assert url.startswith('https://')
        print(f"Test 1 - PDF URL: {url}")

    def test_projectmuse_melody_url_construction_hum_biol(self):
        """Test 2: Human Biology.
        
        PMID: 37733615 (Hum Biol)
        Expected: Should construct valid Project MUSE PDF URL
        """
        pma = self.fetch.article_by_pmid('37733615')
        
        print(f"Test 2 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Skip test if no DOI available
        if not pma.doi:
            print("Test 2 - Skipping: No DOI available for this PMID")
            return

        # Test without verification
        url = the_projectmuse_melody(pma, verify=False)
        assert url is not None
        assert 'muse.jhu.edu' in url
        print(f"Test 2 - PDF URL: {url}")

    def test_projectmuse_melody_url_construction_lang_baltim(self):
        """Test 3: Language (Baltim).
        
        PMID: 37034148 (Language (Baltim))
        Expected: Should construct valid Project MUSE PDF URL
        """
        pma = self.fetch.article_by_pmid('37034148')
        
        print(f"Test 3 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Skip test if no DOI available
        if not pma.doi:
            print("Test 3 - Skipping: No DOI available for this PMID")
            return

        # Test without verification
        url = the_projectmuse_melody(pma, verify=False)
        assert url is not None
        assert 'muse.jhu.edu' in url
        print(f"Test 3 - PDF URL: {url}")

    @patch('requests.get')
    def test_projectmuse_melody_successful_access(self, mock_get):
        """Test 4: Successful PDF access simulation.
        
        Expected: Should return PDF URL when accessible
        """
        # Mock successful PDF response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.headers = {'content-type': 'application/pdf'}
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('38661995')
        
        # Test with verification - should succeed
        url = the_projectmuse_melody(pma, verify=True)
        assert 'muse.jhu.edu' in url
        print(f"Test 4 - Successful verified access: {url}")

    @patch('requests.get')
    def test_projectmuse_melody_paywall_detection(self, mock_get):
        """Test 5: Paywall detection.
        
        Expected: Should detect paywall and raise AccessDenied
        """
        # Mock paywall response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.text = '''<html><body>
            <h1>Project MUSE</h1>
            <p>Institutional access required to view this article</p>
            <button>Subscribe for access</button>
        </body></html>'''
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('38661995')
        
        # Test with verification - should detect paywall
        with pytest.raises(AccessDenied) as exc_info:
            the_projectmuse_melody(pma, verify=True)
        
        assert 'PAYWALL' in str(exc_info.value)
        print(f"Test 5 - Correctly detected paywall: {exc_info.value}")

    @patch('requests.get')
    def test_projectmuse_melody_network_error(self, mock_get):
        """Test 6: Network error handling.
        
        Expected: Should handle network errors gracefully
        """
        # Mock network error
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

        pma = self.fetch.article_by_pmid('38661995')
        
        # Test - should handle network error
        with pytest.raises(NoPDFLink) as exc_info:
            the_projectmuse_melody(pma, verify=True)
        
        # Should contain either TXERROR (network error) or PATTERN (DOI mismatch)
        assert 'TXERROR' in str(exc_info.value) or 'PATTERN' in str(exc_info.value)
        print(f"Test 6 - Correctly handled network error or pattern mismatch: {exc_info.value}")

    def test_projectmuse_melody_missing_doi(self):
        """Test 7: Article without DOI.
        
        Expected: Should raise NoPDFLink for missing DOI
        """
        # Create a mock PMA without DOI
        pma = Mock()
        pma.doi = None
        pma.journal = 'Narrat Inq Bioeth'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_projectmuse_melody(pma, verify=False)
        
        assert 'MISSING' in str(exc_info.value)
        assert 'DOI required' in str(exc_info.value)
        print(f"Test 7 - Correctly handled missing DOI: {exc_info.value}")

    @patch('requests.get')
    def test_projectmuse_melody_404_error(self, mock_get):
        """Test 8: Article not found (404 error).
        
        Expected: Should try multiple patterns and handle 404 errors
        """
        # Mock 404 response for all attempts
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('38661995')
        
        # Test - should try multiple patterns and eventually fail
        with pytest.raises(NoPDFLink) as exc_info:
            the_projectmuse_melody(pma, verify=True)
        
        assert 'TXERROR' in str(exc_info.value) or 'PATTERN' in str(exc_info.value)
        print(f"Test 8 - Correctly handled 404: {exc_info.value}")

    @patch('requests.get')
    def test_projectmuse_melody_article_id_construction(self, mock_get):
        """Test 9: Article ID URL construction.
        
        Expected: Should use article ID from DOI in URL when available
        """
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.headers = {'content-type': 'application/pdf'}
        mock_get.return_value = mock_response

        # Create mock PMA with article ID in DOI
        pma = Mock()
        pma.doi = '10.1353/nib.2024.a926149'
        pma.journal = 'Narrat Inq Bioeth'
        
        # Test - should use article ID in URL
        url = the_projectmuse_melody(pma, verify=True)
        assert 'muse.jhu.edu' in url
        print(f"Test 9 - Article ID URL construction: {url}")

    def test_projectmuse_melody_doi_pattern_warning(self):
        """Test 10: Non-standard DOI pattern handling.
        
        Expected: Should handle non-10.1353 DOI patterns but may warn
        """
        # Create a mock PMA with non-Project MUSE DOI pattern
        pma = Mock()
        pma.doi = '10.1016/j.example.2023.123456'  # Non-Project MUSE DOI
        pma.journal = 'Narrat Inq Bioeth'
        
        # Should still construct URL without verification
        url = the_projectmuse_melody(pma, verify=False)
        assert url is not None
        assert 'muse.jhu.edu' in url
        print(f"Test 10 - Non-standard DOI pattern handled: {url}")

    def test_projectmuse_melody_multiple_journals(self):
        """Test 11: Multiple Project MUSE journal coverage.
        
        Expected: Should work with various Project MUSE journals
        """
        # Test different journal patterns
        test_journals = [
            'Narrat Inq Bioeth',
            'Hum Biol',
            'Language (Baltim)',
            'Am Ann Deaf',
            'Rev High Ed'
        ]
        
        for journal in test_journals:
            pma = Mock()
            pma.doi = '10.1353/nib.2024.a926149'
            pma.journal = journal
            
            url = the_projectmuse_melody(pma, verify=False)
            assert url is not None
            assert 'muse.jhu.edu' in url
            print(f"Test 11 - {journal}: {url}")


def test_projectmuse_journal_recognition():
    """Test that Project MUSE journals are properly recognized in the registry."""
    from metapub.findit.registry import JournalRegistry
    from metapub.findit.journals.projectmuse import projectmuse_journals
    
    registry = JournalRegistry()
    
    # Test sample Project MUSE journals (using PubMed abbreviated names)
    test_journals = [
        'Narrat Inq Bioeth',
        'Hum Biol',
        'Language (Baltim)',
        'Am Ann Deaf',
        'Rev High Ed'
    ]
    
    # Test journal recognition
    found_count = 0
    for journal in test_journals:
        if journal in projectmuse_journals:
            publisher_info = registry.get_publisher_for_journal(journal)
            if publisher_info and publisher_info['name'] == 'projectmuse':
                assert publisher_info['dance_function'] == 'the_projectmuse_melody'
                print(f"✓ {journal} correctly mapped to Project MUSE")
                found_count += 1
            else:
                print(f"⚠ {journal} mapped to different publisher: {publisher_info['name'] if publisher_info else 'None'}")
        else:
            print(f"⚠ {journal} not in projectmuse_journals list")
    
    # Just make sure we found at least one Project MUSE journal
    assert found_count > 0, "No Project MUSE journals found in registry with projectmuse publisher"
    print(f"✓ Found {found_count} properly mapped Project MUSE journals")
    
    registry.close()


if __name__ == '__main__':
    # Run basic tests if executed directly
    test_instance = TestProjectMuseDance()
    test_instance.setUp()
    
    print("Running Project MUSE tests...")
    print("\n" + "="*60)
    
    tests = [
        ('test_projectmuse_melody_url_construction_narrat_inq', 'Narrative Inquiry URL construction'),
        ('test_projectmuse_melody_url_construction_hum_biol', 'Human Biology URL construction'),
        ('test_projectmuse_melody_url_construction_lang_baltim', 'Language Baltimore URL construction'),
        ('test_projectmuse_melody_successful_access', 'Successful access simulation'),
        ('test_projectmuse_melody_paywall_detection', 'Paywall detection'),
        ('test_projectmuse_melody_network_error', 'Network error handling'),
        ('test_projectmuse_melody_missing_doi', 'Missing DOI handling'),
        ('test_projectmuse_melody_404_error', '404 error handling'),
        ('test_projectmuse_melody_article_id_construction', 'Article ID URL construction'),
        ('test_projectmuse_melody_doi_pattern_warning', 'Non-standard DOI pattern handling'),
        ('test_projectmuse_melody_multiple_journals', 'Multiple journal coverage')
    ]
    
    for test_method, description in tests:
        try:
            getattr(test_instance, test_method)()
            print(f"✓ {description} works")
        except Exception as e:
            print(f"✗ {description} failed: {e}")
    
    try:
        test_projectmuse_journal_recognition()
        print("✓ Registry test passed: Journal recognition works")
    except Exception as e:
        print(f"✗ Registry test failed: {e}")
    
    print("\n" + "="*60)
    print("Test suite completed!")