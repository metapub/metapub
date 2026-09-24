"""Live drift-detection dances for publishers backfilled in issue #177.

These are the live (manual) half of the coverage added for the ~half of the
registry that previously had zero test evidence. The offline resolution guard
(test_journal_resolution.py) proves each journal still *routes* to the right
dance; this file proves the dance still *runs* against the real publisher.

Run manually:  pytest -m live_network tests/findit/test_uncovered_publisher_dances.py

Never runs in CI (every test is marked live_network). Each PMID was verified via
eutils so the real pma.journal routes to the expected publisher/dance -- see
UNCOVERED_PUBLISHER_EVIDENCE_PMIDS in tests/fixtures/__init__.py.
"""
import pytest

from metapub import FindIt
from metapub.findit.registry import JournalRegistry, standardize_journal_name
from tests.fixtures import UNCOVERED_PUBLISHER_EVIDENCE_PMIDS

_CASES = sorted(
    UNCOVERED_PUBLISHER_EVIDENCE_PMIDS.items(),
    key=lambda kv: (kv[1]['publisher'], kv[0]),
)
_IDS = ['%s:%s' % (meta['publisher'], pmid) for pmid, meta in _CASES]


@pytest.mark.live_network
@pytest.mark.parametrize('pmid,meta', _CASES, ids=_IDS)
def test_uncovered_publisher_dance_reaches_pdf(pmid, meta):
    """The dance is reached and yields a PDF URL (or an honest paywall reason).

    A NOFORMAT reason means routing/format broke -- that is the drift signal.
    A URL or an access/paywall reason both mean the dance ran correctly; the
    article simply may not be openly downloadable. That distinction is for a
    human to read, which is exactly why this is a manual live test.
    """
    source = FindIt(pmid=pmid)

    assert source.pma.journal == meta['journal'], (
        'PMID %s journal drifted: got %r, expected %r'
        % (pmid, source.pma.journal, meta['journal']))

    if source.reason:
        assert 'NOFORMAT' not in source.reason, (
            '%s (%s): dance not reached -- %s'
            % (meta['publisher'], meta['dance'], source.reason))
    if source.url:
        assert source.url.startswith('http'), \
            '%s: unexpected URL %r' % (meta['publisher'], source.url)

    assert source.url or source.reason, \
        '%s: FindIt returned neither a URL nor a reason' % meta['publisher']


@pytest.mark.live_network
def test_uncovered_evidence_routes_to_declared_dance():
    """Sanity net: every backfill PMID's journal routes to its declared dance.

    Offline routing is already asserted in test_journal_resolution.py; this
    repeats the check against the evidence dict itself so a mistyped
    publisher/dance in the fixture surfaces here too.
    """
    reg = JournalRegistry()
    try:
        mismatches = []
        for pmid, meta in UNCOVERED_PUBLISHER_EVIDENCE_PMIDS.items():
            info = reg.get_publisher_for_journal(standardize_journal_name(meta['journal']))
            got = (info or {}).get('dance_function')
            if got != meta['dance']:
                mismatches.append((pmid, meta['journal'], got, meta['dance']))
        assert not mismatches, 'evidence dance mismatches: %r' % mismatches
    finally:
        reg.close()
