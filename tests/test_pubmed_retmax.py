"""Tests for retmax truncation reporting in PubMedFetcher.pmids_for_query.

Offline tests: esearch is stubbed with canned XML, since what's under test is how
we read <Count> and report a truncated result.

See issue #170 -- pmids_for_query returned at most retmax (250 by default) pmids
and never looked at <Count>, so a query matching more was silently cut with no
indication anything was missing.
"""

import logging
import unittest
from contextlib import contextmanager

from metapub import PubMedFetcher
from metapub.pubmedfetcher import (PMIDList, parse_esearch_result,
                                   get_uids_from_esearch_result)
from tests.common import TEST_CACHEDIR


def esearch_xml(count, pmids):
    """Build an ESearch response with a given <Count> and IdList."""
    ids = ''.join('<Id>%s</Id>' % p for p in pmids)
    return ('<?xml version="1.0"?><eSearchResult><Count>%s</Count>'
            '<IdList>%s</IdList></eSearchResult>' % (count, ids))


class StubQueryService:
    def __init__(self, xml):
        self.xml = xml

    def esearch(self, params):
        return self.xml


class _Collector(logging.Handler):
    def __init__(self):
        super().__init__()
        self.messages = []

    def emit(self, record):
        self.messages.append(record.getMessage())


@contextmanager
def captured_warnings():
    """Collect WARNING-level messages from the pubmedfetcher logger.

    assertNoLogs would be tidier but landed in Python 3.10, and metapub still
    declares support back to 3.8.
    """
    log = logging.getLogger('metapub.pubmedfetcher')
    handler = _Collector()
    handler.setLevel(logging.WARNING)
    previous = log.level
    log.setLevel(logging.WARNING)
    log.addHandler(handler)
    try:
        yield handler.messages
    finally:
        log.removeHandler(handler)
        log.setLevel(previous)


class TestParseEsearchResult(unittest.TestCase):

    def test_total_count_comes_from_count_element(self):
        result = parse_esearch_result(esearch_xml(3922, ['1', '2', '3']))
        assert result == ['1', '2', '3']
        assert result.total_count == 3922

    def test_total_count_falls_back_to_page_size_when_count_absent(self):
        xml = '<?xml version="1.0"?><eSearchResult><IdList><Id>1</Id></IdList></eSearchResult>'
        result = parse_esearch_result(xml)
        assert result.total_count == 1

    def test_empty_result(self):
        result = parse_esearch_result(esearch_xml(0, []))
        assert result == []
        assert result.total_count == 0

    def test_get_uids_wrapper_returns_a_plain_list(self):
        # Kept for callers that only want pmids; should not leak the subclass.
        uids = get_uids_from_esearch_result(esearch_xml(99, ['1', '2']))
        assert uids == ['1', '2']
        assert type(uids) is list


class TestPMIDList(unittest.TestCase):

    def test_behaves_as_an_ordinary_list(self):
        pmids = PMIDList(['3', '1', '2'], total_count=500)
        assert isinstance(pmids, list)
        assert len(pmids) == 3
        assert pmids == ['3', '1', '2']
        assert sorted(pmids) == ['1', '2', '3']
        assert [p for p in pmids] == ['3', '1', '2']

    def test_total_count_defaults_to_length(self):
        assert PMIDList(['1', '2']).total_count == 2


class TestTruncationWarning(unittest.TestCase):

    def fetch_with(self, count, pmids):
        fetch = PubMedFetcher(cachedir=TEST_CACHEDIR)
        fetch.qs = StubQueryService(esearch_xml(count, pmids))
        return fetch

    def test_warns_when_result_is_truncated(self):
        fetch = self.fetch_with(3922, [str(n) for n in range(250)])
        with captured_warnings() as messages:
            pmids = fetch.pmids_for_query(author='Smith JA')
        assert len(pmids) == 250
        assert pmids.total_count == 3922
        assert len(messages) == 1
        assert '250' in messages[0] and '3922' in messages[0]

    def test_no_warning_when_everything_fits(self):
        fetch = self.fetch_with(3, ['1', '2', '3'])
        with captured_warnings() as messages:
            pmids = fetch.pmids_for_query(author='Smith JA')
        assert messages == []
        assert pmids.total_count == 3

    def test_no_warning_on_the_final_page(self):
        # retstart=240 returning the last 10 of 250 is complete, not truncated.
        fetch = self.fetch_with(250, [str(n) for n in range(10)])
        with captured_warnings() as messages:
            fetch.pmids_for_query(author='Smith JA', retstart=240, retmax=250)
        assert messages == []

    def test_warns_on_an_interior_page(self):
        fetch = self.fetch_with(3922, [str(n) for n in range(250)])
        with captured_warnings() as messages:
            fetch.pmids_for_query(author='Smith JA', retstart=500, retmax=250)
        assert len(messages) == 1


if __name__ == '__main__':
    unittest.main()
