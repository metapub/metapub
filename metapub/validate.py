from __future__ import absolute_import, unicode_literals

from .text_mining import re_doi, re_pmid

def _assert_match_is_string_length(match, inp):
    if match:
        len_match = match.end() - match.start()
        if len_match == len(inp):
            assert True
        else:
            assert False
    else:
        assert False


def assert_is_good_doi(doi):
    match = re_doi.match(doi)
    _assert_match_is_string_length(match, doi)


def assert_is_good_pmid(pmid):
    match = re_pmid.match(pmid)
    _assert_match_is_string_length(match, pmid)

