"""Tests for kwargs validation in PubMedFetcher.pmids_for_query.

These are offline tests: they capture the term metapub hands to esearch rather
than making real requests, since what's under test is query construction.

See issue #168 -- `keyword=` (an easy guess given PubMedArticle.keywords) was
silently dropped because the TW kpick knew only tw/text, and nothing validated
unrecognized kwargs, so the typo'd/guessed kwarg failed silently.
"""

import unittest

from metapub import PubMedFetcher
from metapub.exceptions import MetaPubError
from tests.common import TEST_CACHEDIR

EMPTY_RESULT = '<?xml version="1.0"?><eSearchResult><IdList></IdList></eSearchResult>'


class CapturingQueryService:
    """Stands in for the eutils query service, recording the term it was handed."""

    def __init__(self):
        self.term = None

    def esearch(self, params):
        self.term = params['term']
        return EMPTY_RESULT


class TestKwargsValidation(unittest.TestCase):

    def setUp(self):
        self.fetch = PubMedFetcher(cachedir=TEST_CACHEDIR)
        self.qs = CapturingQueryService()
        self.fetch.qs = self.qs

    def term_for(self, **kwargs):
        self.fetch.pmids_for_query(**kwargs)
        return self.qs.term

    def test_keyword_alias_reaches_query_as_text_word(self):
        term = self.term_for(author='Smith JA', keyword='Stanford University')
        assert '"Stanford University"[TW]' in term, term

    def test_kw_alias_matches_keyword(self):
        term = self.term_for(kw='cold water immersion')
        assert '"cold water immersion"[TW]' in term, term

    def test_keyword_alias_reaches_sibling_query_methods(self):
        self.fetch.pmids_for_clinical_query('asthma', 'therapy', keyword='steroids')
        assert '"steroids"[TW]' in self.qs.term

        self.fetch.pmids_for_medical_genetics_query('Brugada Syndrome', 'diagnosis',
                                                    keyword='mutation')
        assert '"mutation"[TW]' in self.qs.term

    def test_unknown_kwarg_raises_instead_of_being_dropped(self):
        # The root cause in #168: a kwarg nobody consumes fell through every
        # kpick without a whisper, so `keyword=` searched as if absent.
        with self.assertRaises(MetaPubError):
            self.term_for(author='Smith JA', abstract='foo', keywrd='typo')  # 'keywrd' unknown


if __name__ == '__main__':
    unittest.main()
