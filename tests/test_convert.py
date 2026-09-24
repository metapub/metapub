import unittest
from unittest.mock import patch, MagicMock

import pytest

import metapub.convert as convert
from metapub.convert import pmid2doi, PubMedArticle2doi, bookid2pmid
from metapub.crossref import TITLE_SIMILARITY_IDEAL_SCORE, TITLE_SIMILARITY_MIN_SCORE
from tests.fixtures import load_pmid_xml

import Levenshtein

pmid_with_doi_in_PMA = 25847151
pmid_with_doi_in_PMA_expected_doi = "10.1016/j.neulet.2015.04.001"

pmid_with_doi_from_CrossRef = 11228145
pmid_with_doi_from_CrossRef_expected_doi = '10.1126/science.1057766'

#TODO: find such an example?!?!?  the CrossRef rewire now works so well it's very uncommon to stump it! 
#pmid_with_unknown_doi = 19634325


# For testing expected Levenshtein distance on various similar academic titles. 
# see also https://www.intact-project.org/general/openapc/2018/01/29/doi-reverse-lookup/
title_pairs_equiv = [
    ('The phosphorylation of Hsp20 enhances its association with amyloid-\u03b2 to increase protection against neuronal cell death', 'The phosphorylation of Hsp20 enhances its association with amyloid-<beta> to increase protection against neuronal cell death'),
]

title_pairs_nonequiv = [
    ('Mutation of the TP53 gene and allelic imbalance at chromosome 17p13 in ductal carcinoma in situ.', 'Allelic expression imbalance of TP53 mutated and polymorphic alleles in head and neck tumors.'),   # .42
    ('Growth Hormones Links to Cancer.', 'CORRIGENDUM FOR "Growth Hormone\'s Links to Cancer".'),  # .77
    ('Anything but', 'anything goes'),  # .64 as-is, .72 after lowercasing!
]


NCBI_BOOKS = [
        {'book_id': 'NBK21248', 'pmid': None,},
        {'book_id': 'NBK26468', 'pmid': '20301790',},
        {'book_id': 'NBK1424', 'pmid': '20301597',},
        {'book_id': 'NBK201366', 'pmid': '24830047',},
]


class TestConversions(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_pmid2doi_from_pma(self):
        # When the DOI is present in the MedLine XML, pmid2doi returns it
        # directly without touching CrossRef. Fixture-backed so it stays offline
        # and deterministic -- the efetch call is the part that flakes on NCBI
        # rate limiting / connection resets, and that path is not what this test
        # is checking.
        pma = load_pmid_xml(str(pmid_with_doi_in_PMA))
        fake_fetch = MagicMock()
        fake_fetch.article_by_pmid.return_value = pma
        with patch.object(convert, 'pm_fetch', fake_fetch):
            doi = pmid2doi(pmid_with_doi_in_PMA)
        assert doi == pmid_with_doi_in_PMA_expected_doi
        fake_fetch.article_by_pmid.assert_called_once_with(pmid_with_doi_in_PMA)

    @pytest.mark.live_network
    def test_pmid2doi_from_crossref(self):
        # This PMID has no DOI in its MedLine XML, so pmid2doi must fall back to
        # CrossRef's fuzzy title match. That fallback is real external integration
        # (CrossRef can change its matching/scoring), so it lives behind
        # live_network as a drift detector rather than being mocked into a
        # tautology. See CLAUDE.md on live vs offline tests.
        doi = pmid2doi(pmid_with_doi_from_CrossRef)
        assert doi == pmid_with_doi_from_CrossRef_expected_doi

    @pytest.mark.live_network
    def test_bookid2pmid(self):
        # Live NCBI ID conversion (bookID -> PMID via eutils): excluded from the
        # offline CI run. A synthetic mock would only prove the mock works.
        for item in NCBI_BOOKS:
            assert item['pmid'] == bookid2pmid(item['book_id'])

    def test_Levenshtein_pairs(self):

        for pair in title_pairs_equiv:
            assert Levenshtein.ratio(pair[0], pair[1]) > TITLE_SIMILARITY_IDEAL_SCORE

        for pair in title_pairs_nonequiv:
            assert Levenshtein.ratio(pair[0], pair[1]) < TITLE_SIMILARITY_MIN_SCORE

