import unittest

from metapub import FindIt

SAMPLE_PMIDS = {'embargoed': ['25575644', '25700512', '25554792', '25146281', '25766237', '25370453'],
                'nonembargoed': ['26098888'],
                'non_pmc': ['26111251', '17373727']
                }

# HTD (Hard-to-do):
# http://rheumatology.oxfordjournals.org/content/48/6/704.2.full.pdf --> 19304793


class TestFindIt(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_skipping_cache(self):
        # use a known working, non-PMC pubmed ID
        src = FindIt(pmid=26111251, cachedir=None)
        assert src._cache is None
        assert src.url is not None
        assert not src.reason

    def test_using_cache(self):
        src = FindIt(pmid=SAMPLE_PMIDS['nonembargoed'][0])
        assert src.url is not None
        assert src._cache is not None

        # source from the same pmid. check that result is same as if we used no cache.
        cached_src = FindIt(pmid=SAMPLE_PMIDS['nonembargoed'][0])
        fresh_src = FindIt(pmid=SAMPLE_PMIDS['nonembargoed'][0])
        
        assert cached_src.url == fresh_src.url

    def test_backup_url(self):
        src = FindIt(18048598)  # from journal "Tobacco Control"
        assert 'europepmc.org' in src.url
        assert 'bmj.com' in src.backup_url

    # def test_embargoed_pmid(self):
        # use a currently PMC embargoed pmid, since its status is bound to change (eventually)
    #    src = FindIt(pmid=SAMPLE_PMIDS['embargoed'][0], cachedir=None)
    #    assert src.url is None
    #    assert src.reason.startswith('DENIED')
