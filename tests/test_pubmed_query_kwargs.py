"""Tests for keyword-argument handling in PubMedFetcher.pmids_for_query.

These are offline tests: they capture the term metapub hands to esearch (or
assert on the exception raised) rather than making real requests, since what's
under test is query construction and kwarg validation.

See issue #168 -- unrecognized kwargs (e.g. a guessed `keyword=`) were silently
dropped, producing a query missing that clause with no warning or error.
"""

import unittest

from metapub import PubMedFetcher
from metapub.exceptions import MetaPubError
from metapub.pubmedfetcher import RECOGNIZED_QUERY_KWARGS, QUERY_FIELD_ALIASES
from tests.common import TEST_CACHEDIR

EMPTY_RESULT = '<?xml version="1.0"?><eSearchResult><IdList></IdList></eSearchResult>'


class CapturingQueryService:
    """Stands in for the eutils query service, recording the term it was handed."""

    def __init__(self):
        self.term = None

    def esearch(self, params):
        self.term = params['term']
        return EMPTY_RESULT


class TestQueryKwargs(unittest.TestCase):

    def setUp(self):
        self.fetch = PubMedFetcher(cachedir=TEST_CACHEDIR)
        self.qs = CapturingQueryService()
        self.fetch.qs = self.qs

    def term_for(self, *args, **kwargs):
        self.fetch.pmids_for_query(*args, **kwargs)
        return self.qs.term

    # --- unrecognized kwargs -------------------------------------------------

    def test_unrecognized_kwarg_raises(self):
        # `keyword` was the guessed-but-unsupported name from #168; it now raises
        # instead of being dropped. (It is also aliased to [TW] -- tested below --
        # so this uses a genuinely unknown name.)
        with self.assertRaises(MetaPubError):
            self.fetch.pmids_for_query(author='Smith JA', bogus='nope')

    def test_unrecognized_kwarg_names_the_offender(self):
        with self.assertRaises(MetaPubError) as ctx:
            self.fetch.pmids_for_query(author='Smith JA', notafield='x')
        assert 'notafield' in str(ctx.exception)

    def test_recognized_kwargs_do_not_raise(self):
        # A spread of aliases across different field tags should all be accepted.
        term = self.term_for(author='Smith JA', journal='PLoS One', year=2013,
                             affiliation='Stanford', vol=121, issue=3)
        assert '"Smith JA"[AU]' in term
        assert '"PLoS One"[TA]' in term
        assert '"Stanford"[AD]' in term

    # --- keyword alias -------------------------------------------------------

    def test_keyword_alias_maps_to_textword(self):
        term = self.term_for(keyword='crispr')
        assert '"crispr"[TW]' in term

    def test_kw_alias_maps_to_textword(self):
        term = self.term_for(kw='crispr')
        assert '"crispr"[TW]' in term

    # --- internal control kwargs still accepted ------------------------------

    def test_clinical_query_flag_accepted(self):
        # forwarded by pmids_for_clinical_query; must not trip the guard
        self.fetch.pmids_for_clinical_query('asthma', 'therapy', since='2020')
        assert self.qs.term is not None

    def test_debug_kwarg_accepted(self):
        # callers pass debug=True through the clinical/genetics helpers
        term = self.term_for(author='Smith JA', debug=True)
        assert '"Smith JA"[AU]' in term

    # --- table integrity -----------------------------------------------------

    def test_control_kwargs_in_recognized_set(self):
        assert 'clinical_query' in RECOGNIZED_QUERY_KWARGS
        assert 'debug' in RECOGNIZED_QUERY_KWARGS

    def test_every_alias_is_recognized(self):
        for aliases in QUERY_FIELD_ALIASES.values():
            for alias in aliases:
                assert alias in RECOGNIZED_QUERY_KWARGS


if __name__ == '__main__':
    unittest.main()
