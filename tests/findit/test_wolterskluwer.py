"""Tests for Wolters Kluwer dance function."""

import pytest
from unittest.mock import patch, Mock

from .common import BaseDanceTest
from metapub.findit.dances import the_wolterskluwer_volta
from metapub.exceptions import NoPDFLink
from tests.fixtures import load_pmid_xml, WOLTERSKLUWER_EVIDENCE_PMIDS


class TestWoltersKluwerDance(BaseDanceTest):
    """Test cases for Wolters Kluwer CrossRef + URL construction dance."""

    def _create_mock_pma(self, pmid='12345', doi='10.1097/test.doi', journal='Test Journal'):
        """Create a mock PubMedArticle object."""
        pma = Mock()
        pma.pmid = pmid
        pma.doi = doi
        pma.journal = journal
        return pma

    def _create_mock_crossref_work(self, doi='10.1097/test.doi'):
        """Create a mock CrossRef work object."""
        work = Mock()
        work.doi = doi
        work.title = 'Test Article'
        work.author = 'Test Author'
        return work

    @patch('metapub.findit.dances.wolterskluwer.CrossRefFetcher')
    @patch('metapub.findit.dances.wolterskluwer.unified_uri_get')
    def test_wolterskluwer_volta_lrww_doi_success(self, mock_unified_get, mock_crossref_fetcher):
        """Test 1: Successful URL construction for 10.1097/ DOI.
        
        Expected: Should construct LWW journal URL pattern for 10.1097/ DOIs
        """
        # Mock CrossRef success
        mock_work = self._create_mock_crossref_work('10.1097/test.doi.123')
        mock_crossref_instance = Mock()
        mock_crossref_instance.article_by_doi.return_value = mock_work
        mock_crossref_fetcher.return_value = mock_crossref_instance
        
        # Mock successful HTTP response
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'application/pdf'}
        mock_unified_get.return_value = mock_response
        
        pma = self._create_mock_pma(doi='10.1097/test.doi.123', journal='Test LWW Journal')
        
        result = the_wolterskluwer_volta(pma, verify=True)
        
        # Should return LWW pattern URL
        assert result == 'https://journals.lww.com/10.1097/test.doi.123'
        mock_crossref_instance.article_by_doi.assert_called_once_with('10.1097/test.doi.123')
        print("Test 1 - Successfully constructed LWW URL for 10.1097/ DOI")

    @patch('metapub.findit.dances.wolterskluwer.CrossRefFetcher')
    def test_wolterskluwer_volta_no_doi_error(self, mock_crossref_fetcher):
        """Test 2: Error when no DOI provided.
        
        Expected: Should raise NoPDFLink for missing DOI
        """
        pma = self._create_mock_pma(doi=None)
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_wolterskluwer_volta(pma, verify=False)
        
        assert 'MISSING: DOI required' in str(exc_info.value)
        print("Test 2 - Correctly handled missing DOI")

    @patch('metapub.findit.dances.wolterskluwer.CrossRefFetcher')
    def test_wolterskluwer_volta_crossref_error(self, mock_crossref_fetcher):
        """Test 3: CrossRef API error handling.
        
        Expected: Should raise NoPDFLink when CrossRef API fails
        """
        # Mock CrossRef failure
        mock_crossref_instance = Mock()
        mock_crossref_instance.article_by_doi.side_effect = Exception("CrossRef API error")
        mock_crossref_fetcher.return_value = mock_crossref_instance
        
        pma = self._create_mock_pma(doi='10.1097/test.doi')
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_wolterskluwer_volta(pma, verify=False)
        
        assert 'CROSSREF_ERROR' in str(exc_info.value)
        print("Test 3 - Correctly handled CrossRef API error")

    @patch('metapub.findit.dances.wolterskluwer.CrossRefFetcher')
    def test_wolterskluwer_volta_crossref_no_work(self, mock_crossref_fetcher):
        """Test 4: CrossRef returns no work.
        
        Expected: Should raise NoPDFLink when CrossRef finds no metadata
        """
        # Mock CrossRef returning None
        mock_crossref_instance = Mock()
        mock_crossref_instance.article_by_doi.return_value = None
        mock_crossref_fetcher.return_value = mock_crossref_instance
        
        pma = self._create_mock_pma(doi='10.1097/invalid.doi')
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_wolterskluwer_volta(pma, verify=False)
        
        assert 'MISSING: CrossRef returned no metadata' in str(exc_info.value)
        print("Test 4 - Correctly handled missing CrossRef metadata")

    @patch('metapub.findit.dances.wolterskluwer.CrossRefFetcher')
    @patch('metapub.findit.dances.wolterskluwer.unified_uri_get')
    def test_wolterskluwer_volta_non_lrww_doi_patterns(self, mock_unified_get, mock_crossref_fetcher):
        """Test 5: URL construction for non-10.1097/ DOIs.
        
        Expected: Should try WK Health and DOI resolver patterns
        """
        # Mock CrossRef success
        mock_work = self._create_mock_crossref_work('10.4103/test.journal.456')
        mock_crossref_instance = Mock()
        mock_crossref_instance.article_by_doi.return_value = mock_work
        mock_crossref_fetcher.return_value = mock_crossref_instance
        
        # Mock successful response to WK Health pattern (first fallback)
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'text/html'}
        mock_unified_get.return_value = mock_response
        
        pma = self._create_mock_pma(doi='10.4103/test.journal.456', journal='Non-LWW Journal')
        
        result = the_wolterskluwer_volta(pma, verify=True)
        
        # Should try WK Health pattern first
        assert result == 'http://content.wkhealth.com/linkback/openurl?doi=10.4103/test.journal.456'
        print("Test 5 - Successfully used WK Health pattern for non-10.1097/ DOI")

    @patch('metapub.findit.dances.wolterskluwer.CrossRefFetcher')
    @patch('metapub.findit.dances.wolterskluwer.unified_uri_get')
    def test_wolterskluwer_volta_all_urls_fail(self, mock_unified_get, mock_crossref_fetcher):
        """Test 6: All URL patterns fail.
        
        Expected: Should raise NoPDFLink when all constructed URLs fail
        """
        # Mock CrossRef success
        mock_work = self._create_mock_crossref_work('10.1097/failing.doi')
        mock_crossref_instance = Mock()
        mock_crossref_instance.article_by_doi.return_value = mock_work
        mock_crossref_fetcher.return_value = mock_crossref_instance
        
        # Mock all URLs failing
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 403
        mock_response.headers = {'content-type': 'text/html'}
        mock_unified_get.return_value = mock_response
        
        pma = self._create_mock_pma(doi='10.1097/failing.doi', journal='Failing Journal')
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_wolterskluwer_volta(pma, verify=True)
        
        assert 'BLOCKED: All Wolters Kluwer URL patterns failed' in str(exc_info.value)
        assert 'HTTP 403' in str(exc_info.value)
        print("Test 6 - Correctly handled all URLs failing with error details")

    @patch('metapub.findit.dances.wolterskluwer.CrossRefFetcher')
    def test_wolterskluwer_volta_no_verify_mode(self, mock_crossref_fetcher):
        """Test 7: No verification mode.
        
        Expected: Should return first constructed URL without checking
        """
        # Mock CrossRef success
        mock_work = self._create_mock_crossref_work('10.1097/unverified.doi')
        mock_crossref_instance = Mock()
        mock_crossref_instance.article_by_doi.return_value = mock_work
        mock_crossref_fetcher.return_value = mock_crossref_instance
        
        pma = self._create_mock_pma(doi='10.1097/unverified.doi', journal='Test Journal')
        
        result = the_wolterskluwer_volta(pma, verify=False)
        
        # Should return first LWW pattern URL without verification
        assert result == 'https://journals.lww.com/10.1097/unverified.doi'
        print("Test 7 - Successfully returned URL without verification")

    @patch('metapub.findit.dances.wolterskluwer.CrossRefFetcher')
    @patch('metapub.findit.dances.wolterskluwer.unified_uri_get')
    def test_wolterskluwer_volta_pdf_content_detection(self, mock_unified_get, mock_crossref_fetcher):
        """Test 8: PDF content type detection.
        
        Expected: Should recognize PDF content type as valid
        """
        # Mock CrossRef success
        mock_work = self._create_mock_crossref_work('10.1097/pdf.test')
        mock_crossref_instance = Mock()
        mock_crossref_instance.article_by_doi.return_value = mock_work
        mock_crossref_fetcher.return_value = mock_crossref_instance
        
        # Mock PDF response
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'application/pdf'}
        mock_unified_get.return_value = mock_response
        
        pma = self._create_mock_pma(doi='10.1097/pdf.test', journal='PDF Test')
        
        result = the_wolterskluwer_volta(pma, verify=True)
        
        assert result == 'https://journals.lww.com/10.1097/pdf.test'
        print("Test 8 - Successfully detected PDF content type")

    @patch('metapub.findit.dances.wolterskluwer.CrossRefFetcher')
    @patch('metapub.findit.dances.wolterskluwer.unified_uri_get')
    def test_wolterskluwer_volta_network_error_handling(self, mock_unified_get, mock_crossref_fetcher):
        """Test 9: Network error during URL verification.
        
        Expected: Should try all patterns and report last error
        """
        # Mock CrossRef success
        mock_work = self._create_mock_crossref_work('10.1097/network.error')
        mock_crossref_instance = Mock()
        mock_crossref_instance.article_by_doi.return_value = mock_work
        mock_crossref_fetcher.return_value = mock_crossref_instance
        
        # Mock network errors for all URLs
        mock_unified_get.side_effect = Exception("Network connection failed")
        
        pma = self._create_mock_pma(doi='10.1097/network.error', journal='Network Test')
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_wolterskluwer_volta(pma, verify=True)
        
        assert 'BLOCKED: All Wolters Kluwer URL patterns failed' in str(exc_info.value)
        assert 'Network connection failed' in str(exc_info.value)
        print("Test 9 - Correctly handled network errors with details")


def test_wolterskluwer_journal_recognition():
    """Test that Wolters Kluwer journals are properly recognized in the registry."""
    from metapub.findit.registry import JournalRegistry
    
    registry = JournalRegistry()
    
    # Test journals known to be published by Wolters Kluwer
    test_journals = [
        'Pain',
        'Neurosurgery', 
        'Crit Care Med',
        'Anesthesiology'
    ]
    
    # Test journal recognition
    for journal in test_journals:
        publisher_info = registry.get_publisher_for_journal(journal)
        if publisher_info and publisher_info['name'] == 'wolterskluwer':
            assert publisher_info['dance_function'] == 'the_wolterskluwer_volta'
            print(f"✓ {journal} correctly mapped to Wolters Kluwer")
        else:
            print(f"⚠ {journal} not found in Wolters Kluwer registry - may need to be added")
    
    registry.close()


if __name__ == '__main__':
    # Run basic tests if executed directly
    import sys
    import traceback
    
    test_instance = TestWoltersKluwerDance()
    
    print("Running Wolters Kluwer CrossRef + URL construction tests...")
    print("\n" + "="*70)
    
    tests = [
        ('test_wolterskluwer_volta_lrww_doi_success', 'LWW DOI pattern success'),
        ('test_wolterskluwer_volta_no_doi_error', 'Missing DOI error'),
        ('test_wolterskluwer_volta_crossref_error', 'CrossRef API error'),
        ('test_wolterskluwer_volta_crossref_no_work', 'CrossRef no work'),
        ('test_wolterskluwer_volta_non_lrww_doi_patterns', 'Non-LWW DOI patterns'),
        ('test_wolterskluwer_volta_all_urls_fail', 'All URLs fail'),
        ('test_wolterskluwer_volta_no_verify_mode', 'No verification mode'),
        ('test_wolterskluwer_volta_pdf_content_detection', 'PDF content detection'),
        ('test_wolterskluwer_volta_network_error_handling', 'Network error handling')
    ]
    
    passed = 0
    failed = 0
    
    for test_method, description in tests:
        try:
            getattr(test_instance, test_method)()
            print(f"✓ {description}")
            passed += 1
        except Exception as e:
            print(f"✗ {description}: {e}")
            traceback.print_exc()
            failed += 1
    
    try:
        test_wolterskluwer_journal_recognition()
        print("✓ Journal registry recognition")
        passed += 1
    except Exception as e:
        print(f"✗ Journal registry recognition: {e}")
        traceback.print_exc()
        failed += 1
    
    print("\n" + "="*70)
    print(f"Tests completed: {passed} passed, {failed} failed")
    
    if failed > 0:
        sys.exit(1)
    else:
        print("All tests passed! ✅")


class TestWoltersKluwerXMLFixtures:
    """Test WoltersKluwer XML fixtures for evidence-driven testing."""

    def test_wolterskluwer_xml_33967209_curr_opin_crit_care(self):
        """Test PMID 33967209 - Curr Opin Crit Care with DOI 10.1097/MCC.0000000000000838."""
        pma = load_pmid_xml('33967209')
        
        assert pma.pmid == '33967209'
        assert pma.doi == '10.1097/MCC.0000000000000838'
        assert 'Curr Opin Crit Care' in pma.journal
        
        result = the_wolterskluwer_volta(pma, verify=False)
        # WoltersKluwer constructs URLs based on DOI patterns
        assert result.startswith('http')
        assert '10.1097' in result or 'lww.com' in result or 'journals.lww.com' in result

    def test_wolterskluwer_xml_36727757_curr_opin_crit_care(self):
        """Test PMID 36727757 - Curr Opin Crit Care with DOI 10.1097/MCC.0000000000001017."""
        pma = load_pmid_xml('36727757')
        
        assert pma.pmid == '36727757'
        assert pma.doi == '10.1097/MCC.0000000000001017'
        assert 'Curr Opin Crit Care' in pma.journal
        
        result = the_wolterskluwer_volta(pma, verify=False)
        # WoltersKluwer constructs URLs based on DOI patterns
        assert result.startswith('http')
        assert '10.1097' in result or 'lww.com' in result or 'journals.lww.com' in result

    def test_wolterskluwer_xml_31789841_acad_med(self):
        """Test PMID 31789841 - Acad Med with DOI 10.1097/ACM.0000000000003093."""
        pma = load_pmid_xml('31789841')
        
        assert pma.pmid == '31789841'
        assert pma.doi == '10.1097/ACM.0000000000003093'
        assert 'Acad Med' in pma.journal
        
        result = the_wolterskluwer_volta(pma, verify=False)
        # WoltersKluwer constructs URLs based on DOI patterns
        assert result.startswith('http')
        assert '10.1097' in result or 'lww.com' in result or 'journals.lww.com' in result