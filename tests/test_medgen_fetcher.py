import unittest, os

from metapub import MedGenFetcher

hugos = ['ACVRL1', 'FOXP3', 'ATM']

TEST_CACHEDIR = 'tests/testcachedir'

fetch = MedGenFetcher()


class TestMedGenFetcher(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_fetch_concepts_for_known_gene(self):
        hugo = 'ACVRL1'
        result = fetch.uids_by_term(hugo+'[gene]')
        assert result is not None
        assert result[0] == '324960'
    
    def test_fetch_concepts_for_incorrect_term(self):
        term = 'AVCRL'
        result = fetch.uids_by_term(term+'[gene]')
        assert result == []

    def test_attributes_on_medgen_concept(self):
        concept = fetch.concept_by_uid(324960)
        assert concept.OMIM[0] == '600376'

        # names is a list of dictionaries. We can't predict what order they come in or 
        # even if the list of names will stay the same. 
        # 
        # the goal here is to use the tests to monitor when/how these
        # schemas change.
        
        FIELDS = ['name', 'SDUI', 'CODE', 'SAB', 'TTY', 'PT', 'type']

        name0 = concept.names[0]
        for field in FIELDS:
            assert field in name0.keys()

        # synonyms is constructed by Metapub from .names; it's a list of strings.
        assert len(concept.synonyms) > 1
        for item in concept.synonyms:
            assert type(item) == str

        # title should always be a simple string.
        assert str(concept.title) == concept.title

        # Definitions is in the shape of the XML.  But usually there's only 1 definition. 
        assert len(concept.definitions) > 0
        assert type(concept.definition) == str
        
        # semantic_id should be a short string like "T047".  semantic_type is like "Disease or Syndrome".
        assert concept.semantic_id == 'T047'
        assert concept.semantic_type == 'Disease or Syndrome'

        # this particular concept doesn't have any associated_genes (maybe pick a diff't one)
        assert type(concept.associated_genes) == list

        # the following properties are often blank or absent from the XML.
        assert concept.cytogenic == '' or concept.cytogenic is None or concept.cytogenic
        assert concept.chromosome == '' or concept.chromosome is None or concept.chromosome

        # Two properties, one actual memory location on the object.
        assert concept.medgen_uid is not None
        assert concept.uid is not None

