"""pmc_only must reach the query built by the clinical and medical genetics wrappers.

Offline: captures the term handed to esearch instead of making real requests.
"""

import unittest

from metapub import PubMedFetcher
from tests.common import TEST_CACHEDIR

EMPTY_RESULT = '<?xml version="1.0"?><eSearchResult><IdList></IdList></eSearchResult>'
PMC_FILTER = '"pubmed pmc"[sb]'


class CapturingQueryService:
    """Stands in for the eutils query service, recording the term it was handed."""

    def __init__(self):
        self.term = None

    def esearch(self, params):
        self.term = params['term']
        return EMPTY_RESULT


class TestPmcOnlyForwarded(unittest.TestCase):

    def setUp(self):
        self.fetch = PubMedFetcher(cachedir=TEST_CACHEDIR)
        self.qs = CapturingQueryService()
        self.fetch.qs = self.qs

    def test_clinical_query_pmc_only(self):
        self.fetch.pmids_for_clinical_query('asthma', 'therapy', pmc_only=True)
        assert PMC_FILTER in self.qs.term

    def test_clinical_query_default_not_pmc_only(self):
        self.fetch.pmids_for_clinical_query('asthma', 'therapy')
        assert PMC_FILTER not in self.qs.term

    def test_medical_genetics_query_pmc_only(self):
        self.fetch.pmids_for_medical_genetics_query('cystic fibrosis', 'diagnosis', pmc_only=True)
        assert PMC_FILTER in self.qs.term

    def test_medical_genetics_query_default_not_pmc_only(self):
        self.fetch.pmids_for_medical_genetics_query('cystic fibrosis', 'diagnosis')
        assert PMC_FILTER not in self.qs.term
