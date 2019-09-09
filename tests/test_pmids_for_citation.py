import unittest

from metapub import PubMedFetcher
fetch = PubMedFetcher()

# fixtures
NOT_FOUND_INVALID_JOURNAL_params = {'jtitle': 'Computers',
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
        pass

    def tearDown(self):
        pass

    def test_citation_match_without_authors(self):
        result = fetch.pmids_for_citation(**no_authors_params)
        assert result[0] == u'25023161'

    def test_citation_match_with_many_authors(self):
        result = fetch.pmids_for_citation(**many_authors_params)
        assert result[0] == u'8741910'

    # def test_citation_match_not_found(self):
    #    result = fetch.pmids_for_citation(**NOT_FOUND_params)
    #    assert result[0] == u'NOT_FOUND'

    def test_citation_match_not_found_invalid_journal(self):
        result = fetch.pmids_for_citation(**NOT_FOUND_INVALID_JOURNAL_params)
        assert result[0] == u'NOT_FOUND;INVALID_JOURNAL'

    def test_citation_match_ambiguous(self):
        result = fetch.pmids_for_citation(**AMBIGUOUS_params)
        assert result[0] == u'AMBIGUOUS (5 citations)'
