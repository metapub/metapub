import unittest, os

from metapub import PubMedFetcher
from metapub.cache_utils import cleanup_dir
from metapub.pubmedfetcher import parse_related_pmids_result
from metapub.pubmedcentral import *
from tests.common import TEST_CACHEDIR

fetch = PubMedFetcher(cachedir=TEST_CACHEDIR)


class TestPubmedFetcher(unittest.TestCase):

    def test_article_by_pmid(self):
        pmid = '4'
        article = fetch.article_by_pmid(pmid)
        assert str(article.pmid) == pmid

        pmid = '25763451'
        article = fetch.article_by_pmid(pmid)
        assert str(article.pmid) == pmid

    def test_article_by_pmid_with_html(self):
        pmid = '30109010'
        title = b'Discovery of a tetrazolyl \xce\xb2-carboline with in vitro and in vivo osteoprotective activity under estrogen-deficient conditions.'.decode('utf-8')
        article = fetch.article_by_pmid(pmid)
        assert str(article.pmid) == pmid
        assert article.title == title
    # Doesn't work...
    #def test_article_by_pmid_with_bookID(self):
    #    bookID = 'NBK2040'
    #    fetch = PubMedFetcher()
    #    article = fetch.article_by_pmid(bookID)
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

