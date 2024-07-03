from __future__ import absolute_import, unicode_literals

import unittest
import os
from lxml.html import fromstring

from metapub.base import MetaPubObject, parse_elink_response

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

    
    def test_clean_html(self):
        obj = MetaPubObject('<br/>')
        test_cases = [
            ('<a href="#">Link</a> <i>italic</i> <b>bold</b> <em>emphasis</em> text', 'Link italic bold emphasis text'),
            ('<a href="#"><i>italic link</i></a> text', 'italic link text'),
            ('plain text', 'plain text'),
        ]
        for html, expected_output in test_cases:
            actual_output = obj._clean_html(fromstring(f'<div>{html}</div>'))
            self.assertEqual(actual_output, expected_output)

    def test_extract_text(self):
        obj = MetaPubObject('<br/>')
        self.assertEqual(obj._extract_text(None), None)
        test_cases = [
            ('<a href="#">Link</a>', 'Link'),
            ('<i>italic</i>', 'italic'),
            ('<b>bold</b>', 'bold'),
            ('<em>emphasis</em>', 'emphasis'),
            ('plain text', 'plain text'),
            
        ]
        for html, expected_output in test_cases:
            actual_output = obj._extract_text(fromstring(f'<div>{html}</div>'))
            self.assertEqual(actual_output, expected_output)
    
