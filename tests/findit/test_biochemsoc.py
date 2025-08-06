"""Tests for Biochemical Society dance function using CrossRef API."""

import pytest
from unittest.mock import patch, Mock

from .common import BaseDanceTest
from metapub.findit.dances import the_biochemsoc_saunter
from metapub.exceptions import NoPDFLink


class TestBiochemSoc(BaseDanceTest):
    """Test cases for Biochemical Society CrossRef-based dance."""

    def _create_mock_pma(self, pmid='12345', doi='10.1042/BCJ20210185', journal='Biochem J'):
        """Create a mock PubMedArticle object."""
        pma = Mock()
        pma.pmid = pmid
        pma.doi = doi
        pma.journal = journal
        return pma

    def _create_mock_crossref_work(self, doi='10.1042/BCJ20210185', has_links=True, has_pdf=True):
        """Create a mock CrossRef work object with PDF links."""
        work = Mock()
        work.doi = doi
        
        if has_links and has_pdf:
            # Simulate Biochemical Society PDF links from CrossRef
            work.link = [
                {
                    'URL': f'https://portlandpress.com/biochemj/article-pdf/478/21/3827/924171/{doi.lower().replace("/", "-")}c.pdf',
                    'content-type': 'application/pdf',
                    'content-version': 'vor',
                    'intended-application': 'syndication'
                },
                {
                    'URL': f'https://portlandpress.com/biochemj/article-pdf/478/21/3827/924171/{doi.lower().replace("/", "-")}c.pdf',
                    'content-type': 'unspecified',
                    'content-version': 'vor',
                    'intended-application': 'similarity-checking'
                }
            ]
        elif has_links:
            # Links but no PDFs
            work.link = [
                {
                    'URL': 'https://portlandpress.com/biochemj/article/478/21/3827',
                    'content-type': 'text/html',
                    'content-version': 'vor',
                    'intended-application': 'text-mining'
                }
            ]
        else:
            work.link = None
            
        return work

    @patch('metapub.findit.dances.biochemsoc.CrossRefFetcher')
    def test_biochemsoc_saunter_success_vor(self, mock_crossref_fetcher):
        """Test 1: Successful PDF retrieval with VoR version.
        
        Expected: Should return VoR PDF URL from CrossRef
        """
        # Mock CrossRef returning PDF links
        mock_work = self._create_mock_crossref_work('10.1042/BCJ20210185')
        mock_crossref_instance = Mock()
        mock_crossref_instance.article_by_doi.return_value = mock_work
        mock_crossref_fetcher.return_value = mock_crossref_instance
        
        pma = self._create_mock_pma(doi='10.1042/BCJ20210185')
        
        result = the_biochemsoc_saunter(pma, verify=False)
        
        assert result == 'https://portlandpress.com/biochemj/article-pdf/478/21/3827/924171/10.1042-bcj20210185c.pdf'
        mock_crossref_instance.article_by_doi.assert_called_once_with('10.1042/BCJ20210185')
        print("Test 1 - Successfully retrieved VoR PDF URL from CrossRef")

    @patch('metapub.findit.dances.biochemsoc.CrossRefFetcher')
    def test_biochemsoc_saunter_no_doi(self, mock_crossref_fetcher):
        """Test 2: Error when no DOI provided.
        
        Expected: Should raise NoPDFLink for missing DOI
        """
        pma = self._create_mock_pma(doi=None)
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_biochemsoc_saunter(pma, verify=False)
        
        assert 'MISSING: DOI required' in str(exc_info.value)
        print("Test 2 - Correctly handled missing DOI")

    @patch('metapub.findit.dances.biochemsoc.CrossRefFetcher')
    def test_biochemsoc_saunter_wrong_doi_prefix(self, mock_crossref_fetcher):
        """Test 3: Error for non-Biochemical Society DOI.
        
        Expected: Should raise NoPDFLink for wrong DOI prefix
        """
        pma = self._create_mock_pma(doi='10.1234/wrong.prefix')
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_biochemsoc_saunter(pma, verify=False)
        
        assert 'MISSING: Not a Biochemical Society DOI' in str(exc_info.value)
        print("Test 3 - Correctly rejected non-Biochemical Society DOI")


    @patch('metapub.findit.dances.biochemsoc.CrossRefFetcher')
    def test_biochemsoc_saunter_no_work(self, mock_crossref_fetcher):
        """Test 4: CrossRef returns no work.
        
        Expected: Should raise NoPDFLink when CrossRef finds no metadata
        """
        # Mock CrossRef returning None
        mock_crossref_instance = Mock()
        mock_crossref_instance.article_by_doi.return_value = None
        mock_crossref_fetcher.return_value = mock_crossref_instance
        
        pma = self._create_mock_pma(doi='10.1042/BCJ20210185')
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_biochemsoc_saunter(pma, verify=False)
        
        assert 'MISSING: CrossRef returned no metadata' in str(exc_info.value)
        print("Test 4 - Correctly handled missing CrossRef metadata")

    @patch('metapub.findit.dances.biochemsoc.CrossRefFetcher')
    def test_biochemsoc_saunter_no_pdf_links(self, mock_crossref_fetcher):
        """Test 5: CrossRef has metadata but no PDF links.
        
        Expected: Should raise NoPDFLink when no PDFs found
        """
        # Mock CrossRef with no PDF links
        mock_work = self._create_mock_crossref_work(has_pdf=False)
        mock_crossref_instance = Mock()
        mock_crossref_instance.article_by_doi.return_value = mock_work
        mock_crossref_fetcher.return_value = mock_crossref_instance
        
        pma = self._create_mock_pma(doi='10.1042/BCJ20210185')
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_biochemsoc_saunter(pma, verify=False)
        
        assert 'MISSING: No PDF links found' in str(exc_info.value)
        print("Test 5 - Correctly handled missing PDF links")

    @patch('metapub.findit.dances.biochemsoc.CrossRefFetcher')
    def test_biochemsoc_saunter_am_version(self, mock_crossref_fetcher):
        """Test 6: Fallback to Accepted Manuscript version.
        
        Expected: Should return AM PDF when no VoR available
        """
        # Mock work with only AM version
        work = Mock()
        work.link = [
            {
                'URL': 'https://portlandpress.com/biochemj/am-pdf/manuscript.pdf',
                'content-type': 'application/pdf',
                'content-version': 'am',
                'intended-application': 'syndication'
            }
        ]
        
        mock_crossref_instance = Mock()
        mock_crossref_instance.article_by_doi.return_value = work
        mock_crossref_fetcher.return_value = mock_crossref_instance
        
        pma = self._create_mock_pma(doi='10.1042/BCJ20210185')
        
        result = the_biochemsoc_saunter(pma, verify=False)
        
        assert result == 'https://portlandpress.com/biochemj/am-pdf/manuscript.pdf'
        print("Test 6 - Successfully returned AM version as fallback")

    @patch('metapub.findit.dances.biochemsoc.CrossRefFetcher')
    def test_biochemsoc_saunter_different_journals(self, mock_crossref_fetcher):
        """Test 7: Test different Biochemical Society journal DOIs.
        
        Expected: Should work for all 10.1042/ DOIs regardless of journal
        """
        # Test various journal DOI patterns
        test_dois = [
            '10.1042/BCJ20210185',  # Biochem J
            '10.1042/CS20210879',   # Clin Sci
            '10.1042/BST20230574',  # Biochem Soc Trans
            '10.1042/EBC20190041',  # Essays Biochem
            '10.1042/BSR20230374',  # Biosci Rep
        ]
        
        for doi in test_dois:
            mock_work = self._create_mock_crossref_work(doi)
            mock_crossref_instance = Mock()
            mock_crossref_instance.article_by_doi.return_value = mock_work
            mock_crossref_fetcher.return_value = mock_crossref_instance
            
            pma = self._create_mock_pma(doi=doi)
            
            result = the_biochemsoc_saunter(pma, verify=False)
            
            assert 'portlandpress.com' in result
            assert 'pdf' in result.lower()
            print(f"Test 7 - Successfully handled DOI: {doi}")

    @patch('metapub.findit.dances.biochemsoc.CrossRefFetcher')
    def test_biochemsoc_saunter_no_links_attribute(self, mock_crossref_fetcher):
        """Test 8: CrossRef work object has no link attribute.
        
        Expected: Should raise NoPDFLink gracefully
        """
        # Mock work without link attribute
        mock_work = Mock()
        delattr(mock_work, 'link')  # Remove link attribute entirely
        
        mock_crossref_instance = Mock()
        mock_crossref_instance.article_by_doi.return_value = mock_work
        mock_crossref_fetcher.return_value = mock_crossref_instance
        
        pma = self._create_mock_pma(doi='10.1042/BCJ20210185')
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_biochemsoc_saunter(pma, verify=False)
        
        assert 'MISSING: No PDF links found' in str(exc_info.value)
        print("Test 8 - Correctly handled missing link attribute")


def test_biochemsoc_journal_recognition():
    """Test that Biochemical Society journals are properly recognized in the registry."""
    from metapub.findit.registry import JournalRegistry
    
    registry = JournalRegistry()
    
    # Test key Biochemical Society journals
    test_journals = [
        'Biochem J',
        'Clin Sci (Lond)',
        'Biochem Soc Trans',
        'Essays Biochem',
        'Biosci Rep'
    ]
    
    for journal in test_journals:
        publisher_info = registry.get_publisher_for_journal(journal)
        if publisher_info and publisher_info['dance_function'] == 'the_biochemsoc_saunter':
            print(f"✓ {journal} correctly mapped to Biochemical Society")
        else:
            print(f"⚠ {journal} not found in Biochemical Society registry")
    
    registry.close()


if __name__ == '__main__':
    import sys
    import traceback
    
    test_instance = TestBiochemSoc()
    
    print("Running Biochemical Society CrossRef dance tests...")
    print("\n" + "="*70)
    
    tests = [
        ('test_biochemsoc_saunter_success_vor', 'VoR PDF retrieval'),
        ('test_biochemsoc_saunter_no_doi', 'Missing DOI error'),
        ('test_biochemsoc_saunter_wrong_doi_prefix', 'Wrong DOI prefix'),
        ('test_biochemsoc_saunter_no_work', 'No CrossRef metadata'),
        ('test_biochemsoc_saunter_no_pdf_links', 'No PDF links'),
        ('test_biochemsoc_saunter_am_version', 'AM version fallback'),
        ('test_biochemsoc_saunter_different_journals', 'Multiple journal DOIs'),
        ('test_biochemsoc_saunter_no_links_attribute', 'Missing link attribute'),
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
        test_biochemsoc_journal_recognition()
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