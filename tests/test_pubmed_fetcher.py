import unittest, os
import tempfile

from metapub import PubMedFetcher
from metapub.cache_utils import cleanup_dir
from metapub.pubmedfetcher import parse_related_pmids_result
from metapub.pubmedcentral import *
from metapub.exceptions import InvalidPMID
from metapub.pubmedarticle import PubMedArticle
from tests.common import TEST_CACHEDIR


class TestPubmedFetcher(unittest.TestCase):

    def setUp(self):
        # Create a unique temporary cache directory for each test run
        self.temp_cache = tempfile.mkdtemp(prefix='pubmed_test_cache_')
        self.fetch = PubMedFetcher(cachedir=self.temp_cache)

    def tearDown(self):
        # Clean up the temporary cache directory
        if hasattr(self, 'temp_cache') and os.path.exists(self.temp_cache):
            cleanup_dir(self.temp_cache)

    def test_article_by_pmid(self):
        pmid = '4'
        article = self.fetch.article_by_pmid(pmid)
        assert str(article.pmid) == pmid

        pmid = '25763451'
        article = self.fetch.article_by_pmid(pmid)
        assert str(article.pmid) == pmid

    def test_article_by_pmid_with_html(self):
        pmid = '30109010'
        title = b'Discovery of a tetrazolyl \xce\xb2-carboline with in vitro and in vivo osteoprotective activity under estrogen-deficient conditions.'.decode('utf-8')
        article = self.fetch.article_by_pmid(pmid)
        assert str(article.pmid) == pmid
        assert article.title == title
    # Doesn't work...
    #def test_article_by_pmid_with_bookID(self):
    #    bookID = 'NBK2040'
    #    fetch = PubMedFetcher()
    #    article = self.fetch.article_by_pmid(bookID)
    #    assert article.pubmed_type == 'book'

    def test_related_pmids(self):
        """ * pubmed    (all related links)
            * citedin   (papers that cited this paper)
            * five      (the "five" that pubmed displays as the top related results)
            * reviews   (review papers that cite this paper)
            * combined  (?)
        """

        expected_keys = ['pubmed', 'citedin', 'five', 'reviews', 'combined']
        with open('tests/data/sample_related_pmids_result.xml') as f:
            xmlstr = f.read()
        resd = parse_related_pmids_result(xmlstr)
        for key in resd.keys():
            assert key in expected_keys
        assert len(resd['citedin']) == 6

    def test_invalid_pmid_raises_invalid_pmid_exception(self):
        """Test that InvalidPMID exceptions bubble up correctly instead of being wrapped."""
        # Create XML response that will cause PubMedArticle to have pmid=None
        # This simulates what happens when NCBI returns empty or malformed results for invalid PMIDs
        invalid_xml = '''<?xml version="1.0"?>
<!DOCTYPE PubmedArticleSet PUBLIC "-//NLM//DTD PubMedArticle, 1st January 2015//EN" 
    "http://www.ncbi.nlm.nih.gov/corehtml/query/DTD/pubmed_150101.dtd">
<PubmedArticleSet>
    <!-- Empty article set - no PMID found -->
</PubmedArticleSet>'''
        
        # Test that PubMedArticle creation with empty XML results in pmid=None
        pma = PubMedArticle(invalid_xml)
        self.assertIsNone(pma.pmid)
        
        # Mock the efetch method to return our invalid XML
        original_efetch = self.fetch.qs.efetch
        
        def mock_efetch(args):
            return invalid_xml.encode('utf-8')  # efetch returns bytes
            
        self.fetch.qs.efetch = mock_efetch
        
        try:
            # This should raise InvalidPMID, not NCBIServiceError or any other exception
            with self.assertRaises(InvalidPMID) as cm:
                self.fetch.article_by_pmid('26350465')  # Using the PMID from the original error
                
            # Verify the exception message contains the PMID and expected text
            self.assertIn('26350465', str(cm.exception))
            self.assertIn('not found', str(cm.exception))
            
        finally:
            # Restore the original method
            self.fetch.qs.efetch = original_efetch

