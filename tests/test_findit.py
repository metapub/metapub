import unittest
import os

from metapub import FindIt
from metapub.findit import SUPPORTED_JOURNALS 
from metapub.findit.findit import CACHE_FILENAME

SAMPLE_PMIDS = {'embargoed': ['25575644', '25700512', '25554792', '25146281', '25766237', '25370453'],
                'nonembargoed': ['26098888'],
                'non_pmc': ['26111251', '17373727']
                }

TEST_CACHEDIR = "/tmp/metapub_test"

# HTD (Hard-to-do):
# http://rheumatology.oxfordjournals.org/content/48/6/704.2.full.pdf --> 19304793


class TestFindIt(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        #cleanup the test cache
        #os.remove(os.path.join(TEST_CACHEDIR, CACHE_FILENAME))
        #os.rmdir(TEST_CACHEDIR)
        pass

    def test_skipping_cache(self):
        "Test skipping the cache using cachedir=None"
        # use a known working, non-PMC pubmed ID
        src = FindIt(pmid=26111251, cachedir=None)
        assert src._cache is None
        assert src.url is not None
        assert not src.reason

    def test_using_cache(self):
        "Test that cached entries provide the same information as freshly pulled ones."
        src = FindIt(pmid=SAMPLE_PMIDS['nonembargoed'][0], cachedir=TEST_CACHEDIR)
        assert os.path.exists(os.path.join(TEST_CACHEDIR, CACHE_FILENAME))

        assert src.url is not None
        assert src._cache is not None

        # source from the same pmid. check that result is same as if we used no cache.
        cached_src = FindIt(pmid=SAMPLE_PMIDS['nonembargoed'][0])
        fresh_src = FindIt(pmid=SAMPLE_PMIDS['nonembargoed'][0], cachedir=None)
        
        assert cached_src.url == fresh_src.url
        assert cached_src.pma.title == fresh_src.pma.title
        assert cached_src.pma.journal == fresh_src.pma.journal

    def test_backup_url(self):
        "Test @backup_url magic property on a known result."
        src = FindIt(18048598, cachedir=TEST_CACHEDIR)  # from journal "Tobacco Control"
        assert 'europepmc.org' in src.url
        assert 'bmj.com' in src.backup_url
        #TODO: add a few more sample PMIDs 

    def test_supported_journals_list(self):
        "Test that SUPPORTED_JOURNALS list exists and has entries."
        assert len(SUPPORTED_JOURNALS) > 100
        assert "Cell" in SUPPORTED_JOURNALS
        assert "Nature" in SUPPORTED_JOURNALS

    def test_embargoed_pmid(self):
        "Test that FindIt redirects currently embargoed PMC article to publisher."
        pass
        # TODO: stock with currently embargoed articles
        # src = FindIt(pmid=SAMPLE_PMIDS['embargoed'][0], cachedir=None)
        # assert src.url is None
        # assert src.reason.startswith('DENIED')
