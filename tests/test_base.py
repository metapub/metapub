from __future__ import absolute_import, unicode_literals

import unittest
import os

from metapub.base import parse_elink_response

from .common import CWD

datadir = os.path.join(CWD, 'data')


class TestConversions(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_medgen_pubmed_elink_response_0_ids(self):
        fixture = open(os.path.join(datadir, 'medgen_elink_pubmed_0_entries.xml')).read()
        ids = parse_elink_response(fixture)
        assert len(ids) == 0

