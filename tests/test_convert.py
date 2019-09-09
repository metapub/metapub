import unittest

from metapub.convert import pmid2doi, PubMedArticle2doi, bookid2pmid
from metapub.crossref import TITLE_SIMILARITY_IDEAL_SCORE, TITLE_SIMILARITY_MIN_SCORE

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

    def test_pmid2doi(self):
        # pmid2doi references PubMedArticle2doi, so let's consider that function
        # implicitly tested here.
        doi = pmid2doi(pmid_with_doi_in_PMA)
        assert doi == pmid_with_doi_in_PMA_expected_doi

        doi = pmid2doi(pmid_with_doi_from_CrossRef)
        assert doi == pmid_with_doi_from_CrossRef_expected_doi

        #doi = pmid2doi(pmid_with_unknown_doi)
        #assert doi is None

    def test_bookid2pmid(self):
        for item in NCBI_BOOKS:
            assert item['pmid'] == bookid2pmid(item['book_id'])

    def test_Levenshtein_pairs(self):

        for pair in title_pairs_equiv:
            assert Levenshtein.ratio(pair[0], pair[1]) > TITLE_SIMILARITY_IDEAL_SCORE

        for pair in title_pairs_nonequiv:
            assert Levenshtein.ratio(pair[0], pair[1]) < TITLE_SIMILARITY_MIN_SCORE

