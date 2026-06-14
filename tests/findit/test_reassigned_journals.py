"""Drift-check for journals reassigned to their true (DOI-prefix-verified) publisher.

Each journal below was claimed by the wrong publisher in the registry. Its true
publisher was established from the DOI prefix of recent articles (one PMID = one
authoritative registration fact), and the assigned handler was confirmed to build
a scheme-correct PDF URL.

This test pins one evidence PMID per journal (saved as an XML fixture) and asserts
the journal's *assigned handler* still builds a URL on the expected publisher
domain. It runs offline (verify=False) and is the early-warning if a future change
silently re-points one of these journals at the wrong publisher.

It deliberately exercises the publisher handler directly rather than
find_article_from_pma(), because open-access journals (Frontiers, BMC) are served
from europepmc by the PMC route before the publisher dance is reached — which is
correct behaviour, but not what this test is checking.
"""
import pytest

from metapub.findit.handlers import RegistryBackedLookupSystem
from metapub.findit.registry import JournalRegistry
from ..fixtures import load_pmid_xml

# (evidence PMID, journal, expected publisher, expected URL domain)
REASSIGNED = [
    ('42283648', 'Ophthalmology',           'sciencedirect',  'sciencedirect.com'),
    ('42285338', 'J Invest Dermatol',        'sciencedirect',  'sciencedirect.com'),
    ('42273363', 'Transpl Int',              'Frontiers',      'frontiersin.org'),
    ('42274351', 'Plast Reconstr Surg',      'Lww',            'journals.lww.com'),
    ('42281389', 'J Investig Med',           'Sage',           'sagepub.com'),
    ('41264517', 'Psychiatry',               'Taylor Francis', 'tandfonline.com'),
    ('42287096', 'Int J Gynaecol Obstet',    'Wiley',          'wiley.com'),
    ('42265698', 'J Biomed Sci',             'Bmc',            'biomedcentral.com'),
    ('34744534', 'Ann Microbiol',            'Bmc',            'biomedcentral.com'),
]


@pytest.fixture(scope='module')
def lookup():
    return RegistryBackedLookupSystem(JournalRegistry())


@pytest.mark.parametrize('pmid,journal,publisher,domain', REASSIGNED)
def test_reassigned_journal_resolves_and_builds_url(lookup, pmid, journal, publisher, domain):
    # registry maps the journal to the expected publisher
    info = lookup.registry.get_publisher_for_journal(journal)
    assert info is not None, f"{journal!r} not in registry"
    assert info['name'] == publisher, f"{journal!r} -> {info['name']}, expected {publisher}"

    # the assigned handler builds a scheme-correct URL for the evidence article
    pma = load_pmid_xml(pmid)
    handler = lookup.get_handler_for_journal(journal)
    url, reason = handler.get_pdf_url(pma, verify=False)
    assert url, f"{journal!r} built no URL (reason={reason})"
    assert domain in url, f"{journal!r} built {url}, expected domain {domain}"
