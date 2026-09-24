"""FindIt journal -> dance resolution guard (offline, runs in CI).

This is the CI-safe half of FindIt testing. It verifies that every evidence
journal still routes to the dance function we expect, using only the local
registry (SQLite) -- no publisher network, no PMID fetch, no HTML fixtures.

What it deliberately does NOT do: check that a dance produces a working PDF URL.
That requires hitting the publisher and lives in the live_network suite
(`pytest -m live_network`). Verifying a real download is inherently a live,
drift-prone operation; it is not something CI can or should do.

What it catches that the mocked per-dance tests cannot: a journal silently
falling out of the registry, or getting re-routed to the wrong publisher/dance
(the multi-publisher conflict class from #159/#160/#162). The mocked dance tests
stub the dance out entirely, so they never exercise routing at all.

Expected values are pinned from the registry and eyeballed for sanity. When
routing legitimately changes, update EXPECTED_ROUTING in the same change.
"""
import pytest

from metapub.findit.registry import JournalRegistry, standardize_journal_name

# journal (as it appears in a PubMedArticle) -> (expected publisher, expected dance)
EXPECTED_ROUTING = {
    'ACI open': ('Thieme', 'the_doi_slide'),
    'ACR Open Rheumatol': ('Wiley', 'the_doi_slide'),
    'AIDS Care': ('Taylor Francis', 'the_doi_slide'),
    'AIDS Res Hum Retroviruses': ('Liebert', 'the_doi_slide'),
    'Acad Med': ('Wolterskluwer', 'the_wolterskluwer_volta'),
    'Adolesc Health Med Ther': ('dovepress', 'the_dovepress_peacock'),
    'Adv Alzheimer Dis': ('Scirp', 'the_scirp_timewarp'),
    'Am J Gastroenterol': ('nature', 'the_nature_ballet'),
    'Am J Hum Genet': ('sciencedirect', 'the_sciencedirect_disco'),
    'Am J Hypertens': ('Oxford', 'the_oxford_academic_foxtrot'),
    'Am J Physiol Cell Physiol': ('Aps', 'the_doi_slide'),
    'Am J Physiol Heart Circ Physiol': ('Aps', 'the_doi_slide'),
    'Am J Public Health': ('Ajph', 'the_doi_slide'),
    'Am Psychol': ('apa', 'the_doi_slide'),
    'Ann Rev Mar Sci': ('annualreviews', 'the_annualreviews_round'),
    'Ann Thorac Cardiovasc Surg': ('Jstage', 'the_jstage_dive'),
    'Annu Rev Chem Biomol Eng': ('annualreviews', 'the_annualreviews_round'),
    'Antimicrob Agents Chemother': ('Asm', 'the_asm_shimmy'),
    'Arq Gastroenterol': ('Scielo', 'the_scielo_chula'),
    'Behaviour': ('Brill', 'the_brill_bridge'),
    'Clin Chem Lab Med': ('degruyter', 'the_doi_slide'),
    'Comp Polit': ('Ingentaconnect', 'the_ingenta_flux'),
    'Curr Mol Pharmacol': ('Eurekaselect', 'the_doi_slide'),
    'Curr Opin Crit Care': ('Wolterskluwer', 'the_wolterskluwer_volta'),
    'Dentistry (Sunnyvale)': ('Walshmedia', 'the_walshmedia_bora'),
    'Drugs (Abingdon Engl)': ('Taylor Francis', 'the_doi_slide'),
    'Early Sci Med': ('Brill', 'the_brill_bridge'),
    'Environ Sci Process Impacts': ('Rsc', 'the_rsc_reaction'),
    'Evid Based Spine Care J': ('Thieme', 'the_doi_slide'),
    'Horm Mol Biol Clin Investig': ('degruyter', 'the_doi_slide'),
    'Int J Artif Intell Tools': ('Worldscientific', 'the_doi_slide'),
    'Int J Bioinform Res Appl': ('inderscience', 'the_inderscience_ula'),
    'Int J Cardiovasc Imaging': ('Springer', 'the_doi_slide'),
    'Int J Mol Sci': ('Mdpi', 'the_mdpi_moonwalk'),
    'J Appl Econ': ('Taylor Francis', 'the_doi_slide'),
    'J Appl Mech': ('asme', 'the_asme_animal'),
    'J Bacteriol': ('Asm', 'the_asm_shimmy'),
    'J Biomech Eng': ('asme', 'the_asme_animal'),
    'J Black Sex Relatsh': ('Projectmuse', 'the_projectmuse_syrtos'),
    'J Clin Invest': ('jci', 'the_jci_jig'),
    'J Comp Psychol': ('apa', 'the_doi_slide'),
    'J Environ Anal Toxicol': ('Hilaris', 'the_hilaris_hop'),
    'J Finance': ('Wiley', 'the_doi_slide'),
    'J Heat Transfer': ('asme', 'the_asme_animal'),
    'J Neurosci Psychol Econ': ('apa', 'the_doi_slide'),
    'J Pediatr Endocrinol Metab': ('degruyter', 'the_doi_slide'),
    'J Porphyr Phthalocyanines': ('Worldscientific', 'the_doi_slide'),
    'J Syst Integr Neurosci': ('Oatext', 'the_oatext_orbit'),
    'J Venom Anim Toxins Incl Trop Dis': ('Scielo', 'the_scielo_chula'),
    'JAMIA Open': ('Oxford', 'the_oxford_academic_foxtrot'),
    'Methods Inf Med': ('Thieme', 'the_doi_slide'),
    'Nat Prod Rep': ('Rsc', 'the_rsc_reaction'),
    'Neuropadiatrie': ('Thieme', 'the_doi_slide'),
    'Nucleic Acids Res': ('Oxford', 'the_oxford_academic_foxtrot'),
    'Nutr Res Rev': ('Cambridge', 'the_cambridge_foxtrot'),
    'Phys Med Biol': ('Iop', 'the_iop_fusion'),
    'Psychiatr Rehabil J': ('apa', 'the_doi_slide'),
    'Psychother Psychosom Med Psychol': ('Thieme', 'the_doi_slide'),
    'Recent Pat Biotechnol': ('Eurekaselect', 'the_doi_slide'),
    'Rehabil Psychol': ('apa', 'the_doi_slide'),
    'Science': ('Science Magazine', 'the_aaas_twist'),
    'Technol Innov': ('Ingentaconnect', 'the_ingenta_flux'),
    'Thorac Cancer': ('Wiley', 'the_doi_slide'),
    'Toung Pao': ('Brill', 'the_brill_bridge'),
    'Wirel Commun Mob Comput': ('Wiley', 'the_doi_slide'),
    'World J Nephrol': ('Wjgnet', 'the_wjgnet_wave'),
    'Xenobiotica': ('Taylor Francis', 'the_doi_slide'),
    'Yonago Acta Med': ('Jstage', 'the_jstage_dive'),
    'mSystems': ('Asm', 'the_asm_shimmy'),
}

# Evidence journals that currently resolve to NO dance. Documented here rather
# than silently dropped. The xfail below is strict: if any of these starts
# resolving (a fix, or a registry change), the xfail flips to a failure so we
# notice and promote it into EXPECTED_ROUTING above.
KNOWN_UNRESOLVED = {
    'Biochem J': 'Biochemical Society journals not routed (BIOCHEMSOC dance tests mock CrossRef)',
    'Phronesis (Barc)': 'Brill journal not in registry (other Brill journals resolve)',
    'Proc Natl Acad Sci U S A': 'PNAS not routed to a dance',
    'Sci Adv': 'AAAS Sci Adv not mapped (only Science resolves to the_aaas_twist)',
    'Sci Signal': 'AAAS Sci Signal not mapped',
    'Technology (Singap World Sci)': 'WorldScientific journal not mapped (others resolve)',
}


@pytest.fixture(scope='module')
def registry():
    reg = JournalRegistry()
    yield reg
    reg.close()


@pytest.mark.parametrize('journal', sorted(EXPECTED_ROUTING))
def test_journal_resolves_to_expected_dance(registry, journal):
    """Every evidence journal still routes to the publisher/dance we expect."""
    expected_publisher, expected_dance = EXPECTED_ROUTING[journal]
    info = registry.get_publisher_for_journal(standardize_journal_name(journal))

    assert info and info.get('dance_function'), \
        "%r resolved to no dance (dropped from registry?)" % journal
    assert info['dance_function'] == expected_dance, \
        "%r routed to %r, expected %r" % (journal, info['dance_function'], expected_dance)
    assert info['name'].lower() == expected_publisher.lower(), \
        "%r routed to publisher %r, expected %r" % (journal, info['name'], expected_publisher)


@pytest.mark.parametrize('journal', sorted(KNOWN_UNRESOLVED))
@pytest.mark.xfail(strict=True, reason='documented FindIt routing gap; see KNOWN_UNRESOLVED')
def test_known_unresolved_journal_still_unresolved(registry, journal):
    """Pin the documented gaps: these should resolve, but don't yet.

    Written as the desired assertion (it *should* resolve) so that when the gap
    is fixed the strict xfail turns into a failure, prompting us to move the
    journal into EXPECTED_ROUTING.
    """
    info = registry.get_publisher_for_journal(standardize_journal_name(journal))
    assert info and info.get('dance_function'), \
        "%r resolves to no dance: %s" % (journal, KNOWN_UNRESOLVED[journal])
