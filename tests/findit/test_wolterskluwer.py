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

    @patch('metapub.findit.dances.wolterskluwer.CrossRefFetcher')    # Test removed: test_wolterskluwer_volta_lrww_doi_success - functionality now handled by verify_pdf_url

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

    @patch('metapub.findit.dances.wolterskluwer.CrossRefFetcher')    # Test removed: test_wolterskluwer_volta_non_lrww_doi_patterns - functionality now handled by verify_pdf_url    # Test removed: test_wolterskluwer_volta_all_urls_fail - functionality now handled by verify_pdf_url

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

    # Test removed: Multiple tests - PDF content detection, network error handling, journal recognition - functionality now handled by verify_pdf_url

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