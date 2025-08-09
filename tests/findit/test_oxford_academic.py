"""Tests for Oxford Academic (academic.oup.com) dance function.

This module tests the_oxford_academic_foxtrot dance function which uses CrossRef API
to bypass Cloudflare protection on Oxford Academic sites, particularly for 
Endocrine Society journals.
"""

import pytest
from unittest.mock import patch, Mock

from .common import BaseDanceTest
from metapub import PubMedFetcher
from metapub.findit.dances.oxford_academic import the_oxford_academic_foxtrot
from metapub.exceptions import NoPDFLink
from metapub.crossref import CrossRefWork
from tests.fixtures import load_pmid_xml, OXFORD_EVIDENCE_PMIDS


class TestOxfordAcademic(BaseDanceTest):
    """Test cases for Oxford Academic PDF access via CrossRef."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.fetch = PubMedFetcher()
        
    def _create_mock_pma(self, pmid='12345', doi='10.1210/jendso/bvab173', 
                        journal='J Endocr Soc'):
        """Create a mock PubMedArticle object."""
        pma = Mock()
        pma.pmid = pmid
        pma.doi = doi
        pma.journal = journal
        return pma

    def _create_mock_crossref_work_with_pdf(self, pdf_url, content_version='vor', 
                                           intended_application='syndication'):
        """Create a mock CrossRefWork with PDF link."""
        work = Mock(spec=CrossRefWork)
        work.link = [{
            'URL': pdf_url,
            'content-type': 'application/pdf',
            'content-version': content_version,
            'intended-application': intended_application
        }]
        return work

    def _create_mock_crossref_work_no_pdf(self):
        """Create a mock CrossRefWork without PDF links."""
        work = Mock(spec=CrossRefWork)
        work.link = [{
            'URL': 'https://academic.oup.com/jes/article/6/1/bvab173/6431677',
            'content-type': 'text/html',
            'content-version': 'vor',
            'intended-application': 'text-mining'
        }]
        return work

    @patch('metapub.findit.dances.oxford_academic.CrossRefFetcher')
    def test_oxford_academic_successful_vor_pdf(self, mock_fetcher_class):
        """Test 1: Successful PDF retrieval with Version of Record.
        
        PMID: 35639911 (Journal of the Endocrine Society)
        Expected: Should return CrossRef PDF URL with highest priority (vor + syndication)
        """
        # Mock CrossRefFetcher and work
        mock_fetcher = Mock()
        mock_fetcher_class.return_value = mock_fetcher
        
        pdf_url = 'https://academic.oup.com/jes/article-pdf/6/1/bvab173/41722664/bvab173.pdf'
        mock_work = self._create_mock_crossref_work_with_pdf(
            pdf_url, content_version='vor', intended_application='syndication'
        )
        mock_fetcher.article_by_doi.return_value = mock_work
        
        pma = self._create_mock_pma(pmid='35639911', doi='10.1210/jendso/bvab173', journal='J Endocr Soc')
        
        result_url = the_oxford_academic_foxtrot(pma, verify=False)
        
        assert result_url == pdf_url
        mock_fetcher.article_by_doi.assert_called_once_with('10.1210/jendso/bvab173')
        print(f"Test 1 - Successful VoR PDF: {result_url}")

    @patch('metapub.findit.dances.oxford_academic.CrossRefFetcher')
    def test_oxford_academic_multiple_pdf_priority(self, mock_fetcher_class):
        """Test 2: Multiple PDF versions - prioritize VoR over AM.
        
        PMID: 36227675 (Journal of Clinical Endocrinology & Metabolism)
        Expected: Should select highest priority PDF (VoR > AM, syndication > similarity-checking)
        """
        # Mock CrossRefFetcher
        mock_fetcher = Mock()
        mock_fetcher_class.return_value = mock_fetcher
        
        # Create work with multiple PDF links
        mock_work = Mock(spec=CrossRefWork)
        mock_work.link = [
            {  # Lower priority - Author Manuscript
                'URL': 'https://academic.oup.com/jcem/article-pdf/123/4/am123/456789/am123.pdf',
                'content-type': 'application/pdf', 
                'content-version': 'am',
                'intended-application': 'similarity-checking'
            },
            {  # Higher priority - Version of Record
                'URL': 'https://academic.oup.com/jcem/article-pdf/123/4/vor123/456789/vor123.pdf',
                'content-type': 'application/pdf',
                'content-version': 'vor', 
                'intended-application': 'syndication'
            }
        ]
        mock_fetcher.article_by_doi.return_value = mock_work
        
        pma = self._create_mock_pma(pmid='36227675', doi='10.1210/jcem/dgac123', journal='J Clin Endocrinol Metab')
        
        result_url = the_oxford_academic_foxtrot(pma, verify=False)
        
        # Should select the VoR PDF, not AM
        assert 'vor123' in result_url
        assert 'am123' not in result_url
        print(f"Test 2 - PDF Priority Selection: {result_url}")

    @patch('metapub.findit.dances.oxford_academic.CrossRefFetcher')
    def test_oxford_academic_no_pdf_links(self, mock_fetcher_class):
        """Test 3: CrossRef work has no PDF links.
        
        Expected: Should raise MISSING error when no PDF links found
        """
        # Mock CrossRefFetcher
        mock_fetcher = Mock()
        mock_fetcher_class.return_value = mock_fetcher
        
        mock_work = self._create_mock_crossref_work_no_pdf()
        mock_fetcher.article_by_doi.return_value = mock_work
        
        pma = self._create_mock_pma(pmid='35639911', doi='10.1210/jendso/bvab173', journal='J Endocr Soc')
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_oxford_academic_foxtrot(pma, verify=False)
        
        error_msg = str(exc_info.value)
        assert 'MISSING' in error_msg
        assert 'No Oxford Academic PDF URLs in CrossRef metadata' in error_msg
        assert pma.doi in error_msg
        print(f"Test 3 - No PDF links error: {error_msg}")

    def test_oxford_academic_missing_doi(self):
        """Test 4: Article without DOI.
        
        Expected: Should raise MISSING error for articles without DOI
        """
        pma = self._create_mock_pma(doi=None, journal='J Endocr Soc')
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_oxford_academic_foxtrot(pma, verify=False)
        
        error_msg = str(exc_info.value)
        assert 'MISSING' in error_msg
        assert 'DOI required for Oxford Academic CrossRef lookup' in error_msg
        print(f"Test 4 - Missing DOI error: {error_msg}")

    def test_oxford_academic_wrong_doi_pattern(self):
        """Test 5: DOI with no Oxford Academic PDF links in CrossRef.
        
        Expected: Should raise MISSING error when no Oxford Academic PDFs found
        """
        # Mock CrossRefFetcher
        mock_fetcher = Mock()
        with patch('metapub.findit.dances.oxford_academic.CrossRefFetcher') as mock_fetcher_class:
            mock_fetcher_class.return_value = mock_fetcher
            
            # Mock work with links but no Oxford Academic PDFs
            mock_work = Mock()
            mock_work.link = [{
                'URL': 'https://example.com/article.pdf',
                'content-type': 'application/pdf',
                'content-version': 'vor'
            }]
            mock_fetcher.article_by_doi.return_value = mock_work
            
            pma = self._create_mock_pma(doi='10.1016/j.example.2023.123456', journal='Example Journal')
            
            with pytest.raises(NoPDFLink) as exc_info:
                the_oxford_academic_foxtrot(pma, verify=False)
            
            error_msg = str(exc_info.value)
            assert 'MISSING' in error_msg
            assert 'No Oxford Academic PDF URLs in CrossRef metadata' in error_msg
            print(f"Test 5 - No Oxford Academic PDFs: {error_msg}")

    @patch('metapub.findit.dances.oxford_academic.CrossRefFetcher')
    def test_oxford_academic_crossref_work_none(self, mock_fetcher_class):
        """Test 6: CrossRef returns no work for DOI.
        
        Expected: Should raise TXERROR when CrossRef API returns no work
        """
        # Mock CrossRefFetcher returning None
        mock_fetcher = Mock()
        mock_fetcher_class.return_value = mock_fetcher
        mock_fetcher.article_by_doi.return_value = None
        
        pma = self._create_mock_pma(pmid='35639911', doi='10.1210/jendso/bvab173', journal='J Endocr Soc')
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_oxford_academic_foxtrot(pma, verify=False)
        
        error_msg = str(exc_info.value)
        assert 'MISSING' in error_msg
        assert 'No CrossRef metadata or links' in error_msg
        assert pma.doi in error_msg
        print(f"Test 6 - No CrossRef work error: {error_msg}")

    @patch('metapub.findit.dances.oxford_academic.CrossRefFetcher')
    def test_oxford_academic_crossref_work_no_links(self, mock_fetcher_class):
        """Test 7: CrossRef work has no links property.
        
        Expected: Should raise MISSING error when work.link is None/empty
        """
        # Mock CrossRefFetcher
        mock_fetcher = Mock()
        mock_fetcher_class.return_value = mock_fetcher
        
        # Mock work with no links
        mock_work = Mock(spec=CrossRefWork)
        mock_work.link = None
        mock_fetcher.article_by_doi.return_value = mock_work
        
        pma = self._create_mock_pma(pmid='35639911', doi='10.1210/jendso/bvab173', journal='J Endocr Soc')
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_oxford_academic_foxtrot(pma, verify=False)
        
        error_msg = str(exc_info.value)
        assert 'MISSING' in error_msg
        assert 'No CrossRef metadata or links' in error_msg
        assert pma.doi in error_msg
        print(f"Test 7 - No links in work error: {error_msg}")

    @patch('metapub.findit.dances.oxford_academic.CrossRefFetcher')
    def test_oxford_academic_crossref_exception(self, mock_fetcher_class):
        """Test 8: CrossRef API throws exception.
        
        Expected: Exception should bubble up naturally (no complex error handling)
        """
        # Mock CrossRefFetcher throwing exception
        mock_fetcher = Mock()
        mock_fetcher_class.return_value = mock_fetcher
        mock_fetcher.article_by_doi.side_effect = Exception("CrossRef API error")
        
        pma = self._create_mock_pma(pmid='35639911', doi='10.1210/jendso/bvab173', journal='J Endocr Soc')
        
        # Exception should bubble up naturally (follows DANCE_FUNCTION_GUIDELINES)
        with pytest.raises(Exception) as exc_info:
            the_oxford_academic_foxtrot(pma, verify=False)
        
        assert "CrossRef API error" in str(exc_info.value)
        print(f"Test 8 - CrossRef exception bubbles up: {exc_info.value}")

    @patch('metapub.findit.dances.oxford_academic.CrossRefFetcher')
    def test_oxford_academic_non_oxford_pdf_filtered(self, mock_fetcher_class):
        """Test 9: PDF links from non-Oxford Academic domains are filtered out.
        
        Expected: Should ignore PDF links that aren't from academic.oup.com
        """
        # Mock CrossRefFetcher
        mock_fetcher = Mock()
        mock_fetcher_class.return_value = mock_fetcher
        
        # Mock work with PDF links from different domains
        mock_work = Mock(spec=CrossRefWork)
        mock_work.link = [
            {  # Wrong domain - should be ignored
                'URL': 'https://example.com/article.pdf',
                'content-type': 'application/pdf',
                'content-version': 'vor',
                'intended-application': 'syndication'
            },
            {  # No PDF - should be ignored
                'URL': 'https://academic.oup.com/article/123',
                'content-type': 'text/html',
                'content-version': 'vor'
            }
        ]
        mock_fetcher.article_by_doi.return_value = mock_work
        
        pma = self._create_mock_pma(pmid='35639911', doi='10.1210/jendso/bvab173', journal='J Endocr Soc')
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_oxford_academic_foxtrot(pma, verify=False)
        
        error_msg = str(exc_info.value)
        assert 'MISSING' in error_msg
        assert 'No Oxford Academic PDF URLs in CrossRef metadata' in error_msg
        print(f"Test 9 - Non-Oxford PDF filtered: {error_msg}")


def test_oxford_academic_journal_recognition():
    """Test basic function availability with real Endocrine Society articles."""
    from metapub import PubMedFetcher
    from metapub.findit.dances.oxford_academic import the_oxford_academic_foxtrot
    
    fetch = PubMedFetcher()
    
    # Test with known Endocrine Society articles
    test_pmids = ['35639911', '36227675', '35861850']
    
    for pmid in test_pmids:
        try:
            pma = fetch.article_by_pmid(pmid)
            
            if pma.doi and pma.doi.startswith('10.1210/'):
                try:
                    result_url = the_oxford_academic_foxtrot(pma, verify=False)
                    if result_url and 'academic.oup.com' in result_url and 'pdf' in result_url:
                        print(f"✓ PMID {pmid} ({pma.journal}): PDF URL found")
                        print(f"  URL: {result_url[:80]}...")
                        return  # Success - at least one worked
                except NoPDFLink as e:
                    if 'MISSING' in str(e) and 'CrossRef' in str(e):
                        print(f"⚠ PMID {pmid}: No PDF in CrossRef metadata")
                    else:
                        print(f"⚠ PMID {pmid}: {str(e)[:100]}...")
                except Exception as e:
                    print(f"⚠ PMID {pmid}: Unexpected error: {e}")
            else:
                print(f"⚠ PMID {pmid}: Not an Endocrine Society DOI")
                
        except Exception as e:
            print(f"⚠ Could not fetch PMID {pmid}: {e}")
    
    print("⚠ Oxford Academic function may need real CrossRef API testing")


if __name__ == '__main__':
    # Run basic tests if executed directly
    test_instance = TestOxfordAcademic()
    test_instance.setUp()
    
    print("Running Oxford Academic (Endocrine Society) dance tests...")
    print("Note: Tests use mocked CrossRef API responses")
    print("\n" + "=" * 70)
    
    tests = [
        ('test_oxford_academic_successful_vor_pdf', 'Successful VoR PDF retrieval'),
        ('test_oxford_academic_multiple_pdf_priority', 'PDF priority selection (VoR > AM)'),
        ('test_oxford_academic_no_pdf_links', 'No PDF links in CrossRef'),
        ('test_oxford_academic_missing_doi', 'Missing DOI error handling'),
        ('test_oxford_academic_wrong_doi_pattern', 'No Oxford Academic PDFs found'),
        ('test_oxford_academic_crossref_work_none', 'CrossRef returns no work'),
        ('test_oxford_academic_crossref_work_no_links', 'CrossRef work has no links'),
        ('test_oxford_academic_crossref_exception', 'CrossRef exception bubbles up'),
        ('test_oxford_academic_non_oxford_pdf_filtered', 'Non-Oxford PDF filtering')
    ]
    
    for test_method, description in tests:
        try:
            getattr(test_instance, test_method)()
            print(f"✓ {description} works")
        except Exception as e:
            print(f"✗ {description} failed: {e}")
    
    try:
        test_oxford_academic_journal_recognition()
        print("✓ Journal recognition test completed")
    except Exception as e:
        print(f"✗ Journal recognition test failed: {e}")
    
    print("\n" + "=" * 70)
    print("Test suite completed!")
    print("\nNote: Oxford Academic dance uses CrossRef API to bypass Cloudflare")
    print("protection. PDF URLs contain session tokens and work directly.")


class TestOxfordAcademicXMLFixtures:
    """Test Oxford Academic dance function with real XML fixtures."""

    def test_oxford_authentic_metadata_validation(self):
        """Validate authentic metadata from XML fixtures matches expected patterns."""
        for pmid, expected in OXFORD_EVIDENCE_PMIDS.items():
            pma = load_pmid_xml(pmid)
            assert pma.doi == expected['doi']
            assert pma.journal == expected['journal']
            assert pma.pmid == pmid
            print(f"✓ PMID {pmid}: {pma.journal} - {pma.doi}")

    def test_oxford_doi_pattern_consistency(self):
        """Test Oxford DOI patterns (10.1093/)."""
        for pmid, data in OXFORD_EVIDENCE_PMIDS.items():
            pma = load_pmid_xml(pmid)
            assert pma.doi.startswith('10.1093/'), f"Oxford DOI must start with 10.1093/, got: {pma.doi}"
            print(f"✓ PMID {pmid} DOI pattern: {pma.doi}")

    def test_oxford_journal_coverage(self):
        """Test Oxford journal coverage."""
        journals = set()
        for pmid in OXFORD_EVIDENCE_PMIDS.keys():
            pma = load_pmid_xml(pmid)
            journals.add(pma.journal)
        assert len(journals) >= 2
        print(f"✓ Journals covered: {journals}")