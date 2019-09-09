import unittest

from metapub import PubMedFetcher
from metapub.pubmedcentral import *

# List of Book IDs that should give us back singular PMIDs when we search for them.
NCBI_BOOKS = [
        {'book_id': 'NBK21248', 'pmid': None,},
        {'book_id': 'NBK26468', 'pmid': '20301790',},
        {'book_id': 'NBK1424', 'pmid': '20301597',},
        {'book_id': 'NBK201366', 'pmid': '24830047',},
]

class TestPubmedFetcher(unittest.TestCase):

    def setUp(self):
        self.fetch = PubMedFetcher()

    def tearDown(self):
        pass

    def test_pmids_for_query(self):
        params = {'journal': 'PLoS One',
                  'year': 2013,
                  'author': 'McMurry AJ'}

        pmids = self.fetch.pmids_for_query(**params)
        assert len(pmids) == 1
        assert pmids[0] == '23533569'

        # this pubmed ID was deleted
        params = {'TA': 'Journal of Neural Transmission',
                  'pdat': 2014,
                  'vol': 121,
                  'aulast': 'Freitag'
                  }

        pmids = self.fetch.pmids_for_query(**params)
        assert len(pmids) == 0

    def test_medical_genetics_query(self):
        # we presume that the results for a fixed year prior to this one will not change.
        results = self.fetch.pmids_for_medical_genetics_query('Brugada Syndrome', 'diagnosis', debug=True, year=2013)
        assert '24775617' in results

    def test_clinical_query(self):
        # we presume that the results for a fixed year prior to this one will not change.
        results = self.fetch.pmids_for_clinical_query('Global developmental delay', 'etiology', 'narrow', debug=True, year=2013)
        assert results[0] == '24257216'
        assert results[1] == '24123848'
        assert results[2] == '24089199'

    def test_specified_return_slice(self):
        pmids = self.fetch.pmids_for_query(since='2015/3/1', retmax=1000)
        assert len(pmids) == 1000

        pmids = self.fetch.pmids_for_query(since='2015/3/1', retstart=200, retmax=500)
        assert len(pmids) == 500

    def test_pmc_only(self):
        params = {'mesh': 'breast neoplasm'}
        stuff = self.fetch.pmids_for_query(since='2015/1/1', until='2015/3/1', pmc_only=True, **params)
        print(stuff)

    def test_ncbi_book_id_to_pubmed(self):
        for eg in NCBI_BOOKS:
            result = self.fetch.pmids_for_query(eg['book_id'])
            if len(result) > 0:
                assert result[0] == eg['pmid']
            else:
                assert eg['pmid'] is None
                print(eg, result)


