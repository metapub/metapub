import unittest
import tempfile
import os

from metapub import PubMedFetcher
from metapub.cache_utils import cleanup_dir
from tests.common import TEST_CACHEDIR

# fixtures
NOT_FOUND_params = {'jtitle': 'Computers',
                    'year': 2000,
                    'volume': 40,
                    'spage': 885
                   }

many_authors_params = {'jtitle': 'American Journal of Medical Genetics',
                       'year': 1996,
                       'volume': 61,
                       'spage': 10,
                       'authors': 'Katherine M. Hegmann; Aimee S. Spikes; Avi Orr-Urtreger; Lisa G. Shaffer'
                       }

no_authors_params = {'jtitle': 'Journal of Neural Transmission',
                     'year': 2014,
                     'volume': 121,
                     'first_page': 1077,
                     }

# PNAS|2008|||An|metapub|AMBIGUOUS (5 citations)
AMBIGUOUS_params = {'jtitle': 'PNAS', 'year': 2008, 'aulast': 'An'}


class TestPubmedCitationMatch(unittest.TestCase):

    def setUp(self):
        # Create a unique temporary cache directory for each test run
        self.temp_cache = tempfile.mkdtemp(prefix='citation_test_cache_')
        self.fetch = PubMedFetcher(cachedir=self.temp_cache)

    def tearDown(self):
        # Clean up the temporary cache directory
        if hasattr(self, 'temp_cache') and os.path.exists(self.temp_cache):
            cleanup_dir(self.temp_cache)

    def test_citation_match_without_authors(self):
        result = self.fetch.pmids_for_citation(**no_authors_params)
        assert result[0] == u'25023161'

    def test_citation_match_with_many_authors(self):
        result = self.fetch.pmids_for_citation(**many_authors_params)
        assert result[0] == u'8741910'

    # def test_citation_match_not_found(self):
    #    result = self.fetch.pmids_for_citation(**NOT_FOUND_params)
    #    assert result[0] == u'NOT_FOUND'

    def test_citation_match_not_found_invalid_journal(self):
        "Test an expected result of a list containing only 1 element returned when zero PMIDs found."
        result = self.fetch.pmids_for_citation(**NOT_FOUND_params)
        assert result[0] == u'NOT_FOUND'

    def test_citation_match_ambiguous(self):
        result = self.fetch.pmids_for_citation(**AMBIGUOUS_params)
        assert result[0] == u'AMBIGUOUS (5 citations)'
