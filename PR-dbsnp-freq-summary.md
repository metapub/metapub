# PR: Add dbSNP frequency-summary parser and ClinVarFetcher accessor

**Branch**: https://github.com/bgracia-cmu/metapub/tree/dev/bgracia/rsid_dbsnpid
**Issue:** (https://github.com/metapub/metapub/issues/129)

---

## Summary

Adds a focused dbSNP frequency-summary parser and a small ClinVarFetcher accessor to return that parsed view.

- New helper: `metapub/dbsnp_freq_summary.py`.  
          Class `DbSnpFreqSummary` with methods `get_studies()`, `get_global(study_id)`, and `get_subpopulations(study_id)`.

- ClinVarFetcher accessor: `ClinVarFetcher.dbsnp_freq_summary_for_variant` returns a `DbSnpFreqSummary` object.


Purpose: provide a small, well-scoped parsing surface for study-level MAFs commonly needed when combining ClinVar and dbSNP frequency data (ref/alt mapping, study-level population counts, and subpopulation rows).

---

## Files changed

- Added: `metapub/dbsnp_freq_summary.py`
- Updated: `metapub/clinvarfetcher.py` — added accessor

---

## Usage (quick example)

```python
from metapub.clinvarfetcher import ClinVarFetcher
cv = ClinVarFetcher()
snp = cv.dbsnp_freq_summary_for_variant('3000')  # or 'rs3000'

# Methods
print(snp.get_studies())
print(snp.get_global('1000Genomes'))
print(snp.get_subpopulations('GnomAD_genomes'))

# Example returns (illustrative)
# snp.get_studies() -> {
#   '1000Genomes': { 'global': { 'allele': 'T', 'frequency': 0.300319, 'population': 1504 }, 'subpopulations': [] },
#   'GnomAD_genomes': { 'global': { 'allele': 'G', 'frequency': 0.359, 'population': 53637 },
#     'subpopulations': [ { 'study': 'European', 'allele': 'G', 'frequency': 0.32, 'population': 10000 }, { 'study': 'African', 'allele': 'G', 'frequency': 0.20, 'population': 800 } ] }
# }
# snp.get_global('1000Genomes') -> { 'population': 1504, 'ref_allele': 'C', 'ref_allele_freq': 0.699681, 'alt_allele': 'T', 'alt_allele_freq': 0.300319 }
# snp.get_subpopulations('GnomAD_genomes') -> [ { 'study': 'European', 'allele': 'G', 'frequency': 0.32, 'population': 10000 }, { 'study': 'African', 'allele': 'G', 'frequency': 0.20, 'population': 800 } ]
```
---

## Tests

Offline tests added to validate `DbSnpFreqSummary` (file: `tests/test_snp_summary_throwaway.py`), plus saved live fixtures used for offline validation.

Tests added:
- `test_get_studies_and_global` — inline `DocumentSummary` XML with `SPDI` + `GLOBAL_MAFS`; verifies study mapping, population, and `alt_allele`/`alt_allele_freq`.
- `test_gnomad_global` — same inline XML; verifies `GnomAD_genomes` parsing.
- `test_many_freq_formats` — programmatically generates ~100 varied `FREQ` tokens (allele prefixes, numeric formats, sample suffixes) to stress the token parser; asserts deterministic, conservative parsing (allele, frequency, population) and tolerates malformed tokens.
- `test_fixtures_parse_saved` — iterates saved `esummary` fixtures in `tests/fixtures/dbsnp/` and verifies `get_studies()` returns the expected shape (`global` and `subpopulations` keys).

Saved fixtures (real `esummary` responses fetched 2026-04-20; included under `tests/fixtures/dbsnp/` for offline tests; examples):
`3735651.xml`, `839222.xml`, `9228453.xml`, `4682116.xml`, `3439168.xml`, `18299465.xml`, `19813641.xml`, `1066450.xml`, `999829.xml`, `7336274.xml`, `16956910.xml`, `890400.xml`.

Offline run (included tests):

```bash
$ pytest tests/test_snp_summary_throwaway.py -q
4 passed in 0.70s (1 warning from lxml truth-testing)
```

Notes:
- Live-network sampling was used only to collect representative fixtures (12 saved files); those fixtures are bundled for offline testing. Live sampling results: `Tried 100 ids — constructed=75, with_GLOBAL_MAFS=37, errors=0` (investigation-only).
- The parser was patched to accept XML strings with encoding declarations by encoding input to UTF-8 bytes before calling `lxml.etree.fromstring`.


```xml
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
```

2) MAF with subpopulations

```xml
<MAF>
  <STUDY>GnomAD_genomes</STUDY>
  <FREQ>G=0.359/53637</FREQ>
  <POPULATION>
    <STUDY>European</STUDY>
    <FREQ>G=0.320/10000</FREQ>
  </POPULATION>
  <POPULATION>
    <STUDY>African</STUDY>
    <FREQ>G=0.200/800</FREQ>
  </POPULATION>
</MAF>
```

3) FREQ without allele prefix

```xml
<FREQ>0.123/2000</FREQ>
<!-- allele absent: ref/alt frequencies remain null; parser records allele-less frequency -->
```

4) FREQ reports the reference allele

```xml
<FREQ>C=0.876/500</FREQ>
<!-- when the allele matches SPDI ref the parser maps it to ref_freq -->
```

5) Missing GLOBAL_MAFS

```xml
<DocumentSummary>
  <SPDI>NC_000004.12:11111:G:A</SPDI>
  <!-- no GLOBAL_MAFS -->
</DocumentSummary>
```

6) Malformed / non-numeric frequency

```xml
<FREQ>T=NA/0</FREQ>
```
---

## Notes & limitations

- `SPDI` is the preferred source for ref/alt mapping; `DOCSUM` `SEQ=[ref/alt]` is fallback.

SPDI vs DOCSUM: prefer `SPDI`.  `SPDI` has a structured format where the last two
colon-separated fields are reference and alternate alleles — e.g.

```xml
<SPDI>NC_000004.12:56911778:C:T</SPDI>  <!-- ref=C, alt=T -->
```

When `SPDI` is absent the code looks for a `SEQ=[ref/alt]` token inside `DOCSUM` (e.g.
`|SEQ=[C/T]|`) as a fallback; `DOCSUM` is free-form text and therefore less reliable, so it is
used only when `SPDI` is not provided.

- Returns `None` for fields it can't confidently infer.
- Multi-allelic and complex cases are out of scope — can be extended later.

---

## Tests

Local test-run summary (selected):

```bash
# Offline synthetic throwaway tests (included in this PR):
$ pytest tests/test_snp_summary_throwaway.py -q
3 passed in 0.63s

Example Synthetic Variations:

allele_prefixes = ['T=', 'G=', 'C=', 'A=', 'ref=', 'ALT=', 'a=', 'rs=', '', 'Allele=']
numbers = ['0.300319', '0.359961', '0.123', '.123', '1', '0', '0.0', '0.9999999', '1e-3', '12.34%', '0,123', '0.123e-2', '-0.1']
sample_suffixes = ['/1504', '/53637', '/2000', '/1', '/0', '/10000', '/1,000', '/unknown', '', '/1e3', '/100sample', '/100/extra']

# (Investigation-only) Live sampling run used to collect fixtures — not part of CI:
# Tried 100 live ids — constructed=75, with_GLOBAL_MAFS=37, errors=0
```



