import unittest

from metapub.utils import parameterize, hostname_of, rootdomain_of


HOSTNAME_SAMPLES = {
    'http://www.nature.com/pr/journal/v49/n1/full/pr20018a.html': 'nature.com',
    'https://webhome.weizmann.ac.il': 'webhome.weizmann.ac.il',
    'http://www.ncbi.nlm.nih.gov/pubmed/17108762': 'ncbi.nlm.nih.gov',
    }

ROOTDOMAIN_SAMPLES = {
    'http://blood.oxfordjournals.org': 'oxfordjournals.org',
    'https://webhome.weizmann.ac.il': 'ac.il',
    'https://regex101.com/': 'regex101.com',
    'http://www.ncbi.nlm.nih.gov/pubmed/17108762': 'nih.gov',
    }


class TestUtils(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_parameterize(self):
        j = 'Muscle & Nerve'
        j_param = parameterize(j)
        assert j_param == 'Muscle+Nerve'

    def test_hostname_of(self):
        for sample, result in list(HOSTNAME_SAMPLES.items()):
            assert hostname_of(sample) == result

    def test_rootdomain_of(self):
        for sample, result in list(ROOTDOMAIN_SAMPLES.items()):
            assert rootdomain_of(sample) == result

