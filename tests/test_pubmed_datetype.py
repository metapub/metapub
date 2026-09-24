"""Tests for the `datetype` parameter of PubMedFetcher.pmids_for_query.

These are offline tests: they capture the term metapub hands to esearch rather
than making real requests, since what's under test is query construction.

See issue #169 -- since/until searched [CRDT] (record creation date) rather than
[DP] (publication date) from 0.3.5.1 (2015) through 0.7.4.
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


class TestDatetype(unittest.TestCase):

    def setUp(self):
        self.fetch = PubMedFetcher(cachedir=TEST_CACHEDIR)
        self.qs = CapturingQueryService()
        self.fetch.qs = self.qs

    def term_for(self, **kwargs):
        self.fetch.pmids_for_query(**kwargs)
        return self.qs.term

    def test_default_datetype_is_publication_date(self):
        # The PubMed website's date filter searches publication date, so metapub's
        # default should agree with it.
        term = self.term_for(author='Smith JA', since='2026/04/01', until='2026/06/30')
        assert '("2026/04/01"[DP] : "2026/06/30"[DP])' in term
        assert 'CRDT' not in term

    def test_crdt_still_available_opt_in(self):
        term = self.term_for(author='Smith JA', since='2026/04/01', until='2026/06/30',
                             datetype='crdt')
        assert '("2026/04/01"[CRDT] : "2026/06/30"[CRDT])' in term

    def test_each_datetype_maps_to_its_pubmed_tag(self):
        expected = {'pdat': 'DP', 'edat': 'EDAT', 'crdt': 'CRDT', 'mdat': 'LR'}
        for datetype, tag in expected.items():
            term = self.term_for(since='2020', datetype=datetype)
            assert '"2020"[%s]' % tag in term, '%s should map to [%s], got %s' % (
                datetype, tag, term)

    def test_datetype_is_case_insensitive(self):
        assert '[DP]' in self.term_for(since='2020', datetype='PDAT')

    def test_invalid_datetype_raises(self):
        with self.assertRaises(MetaPubError):
            self.fetch.pmids_for_query(since='2020', datetype='bogus')

    def test_since_alone_is_open_ended_at_the_top(self):
        term = self.term_for(author='Smith JA', since='2020/01/01')
        assert '("2020/01/01"[DP] : "3000"[DP])' in term

    def test_until_alone_is_honored(self):
        # Regression: `if since:` guarded the whole block, so until-only was
        # silently dropped and the search came back unbounded.
        term = self.term_for(author='Smith JA', until='2020/12/31')
        assert '("1000"[DP] : "2020/12/31"[DP])' in term

    def test_no_date_range_when_neither_bound_given(self):
        term = self.term_for(author='Smith JA')
        assert '[DP]' not in term
        assert ':' not in term

    def test_datetype_reaches_clinical_query(self):
        self.fetch.pmids_for_clinical_query('asthma', 'therapy', since='2020', datetype='crdt')
        assert '"2020"[CRDT]' in self.qs.term

    def test_datetype_reaches_medical_genetics_query(self):
        self.fetch.pmids_for_medical_genetics_query('Brugada Syndrome', 'diagnosis',
                                                    since='2020', datetype='crdt')
        assert '"2020"[CRDT]' in self.qs.term


if __name__ == '__main__':
    unittest.main()
