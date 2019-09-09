from metapub.text_mining import *

import unittest

# "fixtures"

real_dois = ['10.1002/(SICI)1098-1004(1999)14:1<91::AID-HUMU21>3.0.CO;2-B',
             '10.1007/s12020-014-0368-x',
             '10.1101/gad.14.3.278',
             '10.1016/S0898-1221(00)00204-2',
             ]

fake_dois = ['abcdefg', 'ab.efgh/1234567890', '1.2/blargh']

almost_dois = ['10.10.1.0/26', '10.1234/gad.15.4).']

text_with_many_dois = open('tests/data/text_with_many_dois.txt', 'r').read()
text_with_one_doi = open('tests/data/text_with_one_doi.txt', 'r').read()
text_with_no_dois = open('tests/data/text_with_no_dois.txt', 'r').read()
text_with_one_whitespace_doi = open('tests/data/text_with_one_whitespace_doi.txt', 'r').read()


class TestFindDOIs(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_find_whitespace_doi(self):
        result = find_doi_in_string(text_with_one_whitespace_doi, whitespace=True)
        if result:
            assert result == '10.1002/pd.354'
        else:
            assert False

    def test_find_no_doi_in_text(self):
        result = find_doi_in_string(text_with_no_dois)
        if result:
            assert False
        else:
            assert True

    def test_find_one_doi_in_text(self):
        results = findall_dois_in_text(text_with_one_doi)
        assert len(results) == 1

    def test_findall_dois_in_text(self):
        results = findall_dois_in_text(text_with_many_dois)
        assert len(results) > 40

    def test_find_doi_returns_None_for_fake_DOIs(self):
        for fake_doi in fake_dois:
            assert (find_doi_in_string(fake_doi) is None)

    def test_find_doi_in_string(self):
        for doi in almost_dois:
            assert (find_doi_in_string(doi) is not None)

    def test_find_doi_in_exact_strings(self):
        for doi in real_dois:
            result = find_doi_in_string(doi)
            assert len(result) == len(doi)

    def test_findall_ncbi_bookIDs(self):
        text = 'NBK01 and NBK200 but not NBKarhg or MBK20'
        results = findall_ncbi_bookIDs(text)
        expected = ['NBK01', 'NBK200']
        for bookid in expected:
            assert bookid in results
        assert is_ncbi_bookID(expected[0]) is True
        assert is_ncbi_bookID('9234135') is False
        assert is_ncbi_bookID('10.1002/pd.354') is False

    def test_findall_pmcIDs(self):
        text = 'PMC12345 and PMC10420 but not PMCasfhl or PM10394 or 9234135'
        results = findall_pmcIDs(text)
        expected = ['PMC12345', 'PMC10420']
        for pmcid in expected:
            assert pmcid in results
        assert is_pmcid(expected[0]) is True
        assert is_pmcid('9234135') is False
        assert is_pmcid('10.1002/pd.354') is False

