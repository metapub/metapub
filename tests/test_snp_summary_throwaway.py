import textwrap
from pathlib import Path

from metapub.dbsnp_freq_summary import DbSnpFreqSummary


SAMPLE_XML = textwrap.dedent("""<?xml version="1.0"?>
<DocumentSummarySet>
  <DocumentSummary>
    <SNP_ID>3000</SNP_ID>
    <SPDI>NC_000004.12:56911778:C:T</SPDI>
    <DOCSUM>HGVS=NC_000004.12:g.56911779C&gt;T,NC_000004.11:g.57777945C&gt;T,NG_029447.1:g.8904C&gt;T|SEQ=[C/T]|LEN=1|GENE=REST:5978</DOCSUM>
    <GLOBAL_MAFS>
      <MAF>
        <STUDY>1000Genomes</STUDY>
        <FREQ>T=0.300319/1504</FREQ>
      </MAF>
      <MAF>
        <STUDY>GnomAD_genomes</STUDY>
        <FREQ>T=0.359961/53637</FREQ>
      </MAF>
    </GLOBAL_MAFS>
  </DocumentSummary>
</DocumentSummarySet>
""")


def build_docsummary_xml(snp_id: int, study: str, freq_text: str) -> str:
    base = textwrap.dedent("""<?xml version="1.0"?>
    <DocumentSummarySet>
      <DocumentSummary>
        <SNP_ID>{snp_id}</SNP_ID>
        <SPDI>NC_000004.12:56911778:C:T</SPDI>
        <DOCSUM>SEQ=[C/T]</DOCSUM>
        <GLOBAL_MAFS>
          <MAF>
            <STUDY>{study}</STUDY>
            <FREQ>{freq_text}</FREQ>
          </MAF>
        </GLOBAL_MAFS>
      </DocumentSummary>
    </DocumentSummarySet>
    """)
    return base.format(snp_id=snp_id, study=study, freq_text=freq_text)


def expected_from_token(freq_text: str):
    """Replicate the parser's token logic to compute expected allele/freq/sample."""
    if not freq_text:
        return None, None, None
    rest = freq_text.strip()
    allele = None
    if '=' in rest:
        allele_part, rest = rest.split('=', 1)
        allele = allele_part.strip()
        rest = rest.strip()

    sample = None
    if '/' in rest:
        freq_str, sample_str = rest.split('/', 1)
        freq_str = freq_str.strip()
        sample_str = sample_str.strip()
        try:
            sample = int(sample_str)
        except Exception:
            sample = None
    else:
        freq_str = rest.strip()

    try:
        freq = float(freq_str)
    except Exception:
        freq = None

    return allele, freq, sample


def test_get_studies_and_global():
    s = DbSnpFreqSummary(SAMPLE_XML)
    studies = s.get_studies()
    assert '1000Genomes' in studies
    g1000 = s.get_global('1000Genomes')
    assert g1000['population'] == 1504
    assert g1000['alt_allele'] == 'T'
    assert abs(g1000['alt_allele_freq'] - 0.300319) < 1e-9


def test_gnomad_global():
    s = DbSnpFreqSummary(SAMPLE_XML)
    g = s.get_global('GnomAD_genomes')
    assert g['population'] == 53637
    assert g['alt_allele'] == 'T'


def test_many_freq_formats():
    """Generate ~100 varied FREQ token syntaxes and assert the parser behaves predictably."""
    variants = []
    allele_prefixes = ['T=', 'G=', 'C=', 'A=', 'ref=', 'ALT=', 'a=', 'rs=', '', 'Allele=']
    numbers = ['0.300319', '0.359961', '0.123', '.123', '1', '0', '0.0', '0.9999999', '1e-3', '12.34%', '0,123', '0.123e-2', '-0.1']
    sample_suffixes = ['/1504', '/53637', '/2000', '/1', '/0', '/10000', '/1,000', '/unknown', '', '/1e3', '/100sample', '/100/extra']

    for a in allele_prefixes:
        for n in numbers:
            for sfx in sample_suffixes:
                variants.append(a + n + sfx)
                if len(variants) >= 100:
                    break
            if len(variants) >= 100:
                break
        if len(variants) >= 100:
            break

    variants = variants[:100]

    for i, freq_text in enumerate(variants):
        study = f'TestStudy{i}'
        xml = build_docsummary_xml(4000 + i, study, freq_text)
        s = DbSnpFreqSummary(xml)
        studies = s.get_studies()
        assert study in studies, f"missing study for case {i}: {freq_text}"
        global_row = studies[study]['global']
        expected_allele, expected_freq, expected_sample = expected_from_token(freq_text)
        assert global_row['allele'] == expected_allele
        if expected_freq is None:
            assert global_row['frequency'] is None
        else:
            assert abs((global_row['frequency'] or 0.0) - expected_freq) < 1e-9
        expected_pop = expected_sample or 0
        assert global_row['population'] == expected_pop


def test_fixtures_parse_saved():
    """Load any saved live esummary fixtures and ensure the parser handles them."""
    fixtures_dir = Path('tests') / 'fixtures' / 'dbsnp'
    fixtures = list(fixtures_dir.glob('*.xml'))
    assert len(fixtures) >= 1

    for fx in fixtures:
        xml = fx.read_text(encoding='utf-8')
        s = DbSnpFreqSummary(xml)
        studies = s.get_studies()
        assert isinstance(studies, dict)
        for st, info in studies.items():
            assert 'global' in info and 'subpopulations' in info
            g = info['global']
            if g is not None:
                assert 'allele' in g and 'frequency' in g and 'population' in g
