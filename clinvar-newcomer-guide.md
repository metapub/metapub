# ClinVar Newcomer Guide

## Overview

ClinVar is a public database where clinical laboratories and researchers submit their interpretations of genetic variants. Working with it programmatically is non-trivial: records use multiple overlapping identifier systems, the same variant can be assessed independently for several diseases, and the data model mixes objective biological facts with subjective clinical judgments submitted by different organizations.

---

## Biology Background

### Physical Organization

- `genome` > `chromosomes` > `genes`
- humans have 23 chromosome pairs
- examples of genes: `BRCA1`, `CFTR`, `TSC2`

### DNA, Transcription, and Translation

- DNA is double-stranded; strands run in opposite directions (`5'→3'` and `3'→5'`), often written as `+` / `-`
- `transcript`: RNA copied from a gene
- `protein`: product translated from a coding transcript, made of amino acids
- `exons`: segments kept in mature RNA; `introns`: segments removed during splicing
- `alternative splicing`: different exon combinations can produce different transcripts — and therefore different proteins — from the same gene
- a `codon` is three nucleotides; codons map to amino acids (`ATG` = start codon / methionine)

### Variants and Haplotypes

- `variant`: a sequence change relative to a reference
- common classes: single-nucleotide variant (SNV), insertion, deletion, larger rearrangement
- `SNV` vs `SNP`: SNV = one base change; SNP more strictly refers to a population-level polymorphism
- `haplotype`: a linked set of variants inherited together — not a gene

### HGVS Notation

HGVS ([Human Genome Variation Society](https://hgvs-nomenclature.org/)) notation is the standard format for describing variants:

| Prefix | Meaning | Example |
|--------|---------|---------|
| `g.` | genomic | `NC_000017.11:g.43094692del` |
| `c.` | coding DNA (relative to a transcript) | `NM_000492.4:c.1521_1523delCTT` |
| `p.` | protein | `p.Phe508del`, `p.Met1Val` |

- An `accession` is the stable unique ID a database assigns to a submitted record; e.g. `NM_000492.4` is a transcript accession where `.4` is the version number
- `NM_...` identifies a RefSeq transcript accession; `NP_...` identifies the corresponding RefSeq protein accession
- RefSeq is NCBI's curated reference sequence database
- `c.1A>G`: at coding position 1, `A` is replaced by `G`
- `p.Met1Val`: methionine changes to valine at amino-acid position 1
- `cytogenetic location`: chromosome position based on banding patterns, not exact coordinates

---

## ClinVar Concepts

### What ClinVar Stores

ClinVar is a database of variant interpretations. Each record links:
- a variant
- an associated condition or trait
- one or more submitted interpretations (`submissions` / `assertions`)
- an aggregate `clinical significance` and `review status`
- cross-references to related databases

Clinical significance describes whether a variant causes disease (full list at the [ClinVar clinsig page](https://www.ncbi.nlm.nih.gov/clinvar/docs/clinsig/)):
- `pathogenic`: causes disease
- `likely pathogenic`: probably causes disease
- `uncertain significance`: insufficient evidence to classify
- `likely benign`: probably does not cause disease
- `benign`: does not cause disease

One variant may have multiple submissions that disagree.

### ClinVar Identifiers

There are four distinct identifier roles — mixing them up is the most common source of bugs. See the [ClinVar identifiers reference](https://www.ncbi.nlm.nih.gov/clinvar/docs/identifiers/) for the official definitions.

Entrez is NCBI's integrated search and retrieval system. An Entrez UID is the internal numeric key Entrez assigns to each record in a given database; it is separate from any accession the originating database uses.

| ID | What it is | Example |
|----|-----------|---------|
| `Variation ID` | ClinVar's own variant concept ID | numeric; appears in the URL at `/variation/<id>` |
| `VCV accession` | Variation-centered accession (one per variant) | `VCV000485538` |
| `RCV accession` | Condition-centered accession (one per variant-condition pair) | `RCV000123456` |
| `Entrez UID` | Retrieval ID used internally by NCBI's search system | numeric; distinct from the ClinVar-native IDs above |

**Critical:** `Entrez UID` and `Variation ID` are **not** the same. They can differ numerically for the same record.

### Related Databases

External identifiers link ClinVar records to these hubs:

- `rsID` — dbSNP (Single Nucleotide Polymorphism database) variant identifier; despite the name, dbSNP catalogs all short variant types, not just SNPs
- `OMIM ID` — OMIM (Online Mendelian Inheritance in Man) catalogs Mendelian disorders and gene-disease relationships; a Mendelian disorder is a disease caused by a variant in a single gene
- `MedGen ID` — condition or phenotype concept; a phenotype is an observable trait or characteristic of an organism
- `Orphanet ID` — rare disease catalog
- `PubMed ID` — literature reference
- `Gene ID` — NCBI Gene record

These are cross-references embedded in ClinVar records, not primary fetch keys.

**Where each cross-reference type appears in the XML matters.** rsID and OMIM are stored at the variant/allele level (`SimpleAllele/XRefList`) — they describe the variant itself. MedGen and Orphanet are stored at the condition level (`RCVList`, `TraitSet`) — they identify the disease associated with the variant, not the variant itself. This distinction affects which API properties return real data and which always return empty. See [`clinvar_vcv_4819894_glb1.manifest.txt`](metapub/tests/data/clinvar_vcv_4819894_glb1.manifest.txt) for the confirmed XRef locations in a real record.

---

## What a ClinVar Record Contains

A ClinVar record has two distinct layers: **variant biology** (objective facts about the variant) and **clinical assertions** (submitted interpretations of what that variant means for disease).

### Variant Biology Layer

These are the biological facts about the variant itself, independent of any clinical claim.

**Location** — where in the genome the variant occurs:
- Cytogenetic location (e.g. `16p13.3`)
- Sequence coordinates per genome assembly — GRCh38 and GRCh37 are the two current human reference genome builds
- An `allele` is one specific version of a sequence at a given position: the reference allele is what the reference genome has; the alternate allele is what the variant has
- Coordinates are provided per assembly and include chromosome, start/stop positions, and reference and alternate alleles in VCF format (Variant Call Format, a standard text representation for genomic variants)

**Gene context**:
- Gene symbol, full name, NCBI Gene ID, and HGNC ID
- HGNC (HUGO Gene Nomenclature Committee) is the body that standardizes human gene names
- Whether the variant falls within a single gene or spans multiple genes
- Haploinsufficiency and triplosensitivity scores from ClinGen (Clinical Genome Resource), a consortium that curates gene-disease validity
  - `haploinsufficiency`: one functional gene copy is insufficient for normal function
  - `triplosensitivity`: having three copies of a gene causes disease

**HGVS expressions** — the same variant described at multiple levels:
- Genomic (`g.`): one expression per genome assembly, e.g. `NC_000016.10:g.2070571G>A`
- Coding (`c.`): one per transcript, e.g. `NM_000548.4:c.1832G>A`
- Protein (`p.`): derived from the coding change, e.g. `NP_000539.2:p.Arg611Gln`
- UniProtKB protein (`p.`): e.g. `P49815:p.Arg611Gln`; UniProtKB is a curated protein sequence and function database
- Each expression carries a molecular consequence term — the effect of the variant at the molecular level — from the Sequence Ontology (SO), a controlled vocabulary for sequence features:
  - `missense`: changes one amino acid
  - `synonymous`: changes the codon but not the amino acid
  - `splice`: affects the splicing of introns

**Cross-references** (variant-level links to external databases, stored in `SimpleAllele/XRefList`):
- `dbSNP rsID`: the variant's identifier in dbSNP
- `OMIM` entry ID for this specific variant
- `UniProtKB` protein variant ID

MedGen and Orphanet IDs appear at the condition level (in `RCVList` and `TraitSet`), not here.

### Clinical Assertion Layer

This layer holds the interpretations — what submitters believe the variant means clinically.

**The variant-condition pairing** — a single variant can be associated with multiple conditions. Each pairing gets its own RCV accession and is assessed independently. For example, the same TSC2 variant might be classified as pathogenic for *Tuberous sclerosis 2* and separately assessed for *Lymphangiomyomatosis*.

**Conditions / traits** — each condition is a structured concept, not just a name:
- Preferred name and alternate names/symbols
- Cross-references: MedGen ID, OMIM ID, Orphanet ID, and SNOMED CT (a clinical terminology system used in healthcare records)
- Supporting citations from GeneReviews (NCBI's expert-authored disease summaries) and ACMG guidelines
- ACMG (American College of Medical Genetics and Genomics) publishes the variant classification standards widely used in clinical genetics

**Aggregate classification** — the rolled-up view across all submissions for a given variant-condition pair:
- `clinical significance`: e.g. `Pathogenic`, `Likely benign`, `Uncertain significance`
- `review status`: level of evidence, e.g. `criteria provided, multiple submitters, no conflicts`
- Date last evaluated, number of submissions, number of submitters
- Citations supporting the aggregate classification

**Individual submissions (SCV records)** — each submitter's independent claim:
- SCV (Submitted ClinVar Variant) is the accession assigned to one submitter's interpretation
- Submitter name, organization, and submission date
- Their own classification and review status
- Variant origin: germline (inherited, present in every cell) vs somatic (acquired after birth, present in a subset of cells)
- Affected status and number of individuals tested
- Method: clinical testing, literature only, curation, research, etc.
- Free-text comment explaining the classification rationale
- Assertion method and criteria URL (e.g. ACMG 2015 guidelines)

---

## Worked Example

The following walks through a real ClinVar record — `VCV000012397` — to show how the biology and ClinVar concepts above fit together. This is the actual fixture used in the test suite (`tests/data/clinvar_vcv_12000.xml`).

### The Variant in Biology Terms

The **TSC2** gene sits on the `+` strand of chromosome 16 at cytogenetic location `16p13.3`. TSC2 encodes a protein that acts as a tumor suppressor; loss-of-function variants in this gene cause Tuberous sclerosis, a disease that produces benign tumors in multiple organs.

At position 2,070,571 on chromosome 16 (GRCh38 build), the reference base `G` is replaced by `A`. This is a **single-nucleotide variant (SNV)**. The codon change causes arginine (Arg) at protein position 611 to become glutamine (Gln) — a **missense** change. The same physical change is described at every level of HGVS notation:

| Level | Expression |
|-------|-----------|
| Genomic — GRCh38 | `NC_000016.10:g.2070571G>A` |
| Genomic — GRCh37 | `NC_000016.9:g.2120572G>A` |
| Coding (RefSeq transcript) | `NM_000548.4:c.1832G>A` |
| Protein (RefSeq) | `NP_000539.2:p.Arg611Gln` |
| Protein (UniProtKB) | `P49815:p.Arg611Gln` |

One physical change produces five different strings depending on which reference sequence is used. Because TSC2 undergoes alternative splicing, other transcripts of TSC2 would produce additional `c.` expressions for the same variant; only the canonical transcript is shown here.

### The ClinVar Record

This variant has VCV accession `VCV000012397` and has been assessed for multiple conditions, each with its own RCV accession:

| Condition | RCV accession | Classification | Review status |
|-----------|--------------|---------------|---------------|
| Tuberous sclerosis 2 | `RCV000013205` | Pathogenic | criteria provided, multiple submitters, no conflicts |
| Lymphangiomyomatosis | `RCV000055317` | Pathogenic | no assertion criteria provided |
| Hereditary cancer-predisposing syndrome | `RCV000491426` | Pathogenic | criteria provided, single submitter |
| Tuberous sclerosis syndrome | `RCV000042946` | not provided | no classification provided |

The strongest assessment — Tuberous sclerosis 2 — has 12 total submissions from 9 submitters, all agreeing the variant is pathogenic. The weaker assessments for other conditions have fewer or lower-quality submissions, which is reflected in their review status.

### XML Snippets

**Variant biology layer** — location, HGVS, and cross-references:

```xml
<SimpleAllele AlleleID="27436" VariationID="12397">
  <Location>
    <CytogeneticLocation>16p13.3</CytogeneticLocation>
    <SequenceLocation Assembly="GRCh38" Chr="16" Accession="NC_000016.10"
      start="2070571" stop="2070571"
      referenceAllele="G" alternateAllele="A"/>
  </Location>
  <HGVSlist>
    <HGVS Assembly="GRCh38" Type="genomic, top-level">
      <NucleotideExpression sequenceAccessionVersion="NC_000016.10" change="g.2070571G>A">
        <Expression>NC_000016.10:g.2070571G>A</Expression>
      </NucleotideExpression>
    </HGVS>
    <HGVS Type="coding">
      <NucleotideExpression sequenceAccessionVersion="NM_000548.4" change="c.1832G>A">
        <Expression>NM_000548.4:c.1832G>A</Expression>
      </NucleotideExpression>
      <ProteinExpression sequenceAccessionVersion="NP_000539.2" change="p.Arg611Gln">
        <Expression>NP_000539.2:p.Arg611Gln</Expression>
      </ProteinExpression>
      <MolecularConsequence ID="SO:0001583" Type="missense variant" DB="SO"/>
    </HGVS>
  </HGVSlist>
  <XRefList>
    <XRef Type="rs" ID="28934872" DB="dbSNP"/>
    <XRef Type="Allelic variant" ID="191092.0006" DB="OMIM"/>
  </XRefList>
</SimpleAllele>
```

`SO:0001583` is the Sequence Ontology term for missense variant. The `XRefList` links out to the dbSNP entry (`rs28934872`) and the OMIM allelic variant entry for this specific change.

**Clinical assertion layer** — one variant-condition pairing:

```xml
<RCVAccession Title="NM_000548.4(TSC2):c.1832G>A (p.Arg611Gln) AND Tuberous sclerosis 2"
              Accession="RCV000013205" Version="22">
  <ClassifiedConditionList>
    <ClassifiedCondition DB="MedGen" ID="C1860707">Tuberous sclerosis 2</ClassifiedCondition>
  </ClassifiedConditionList>
  <RCVClassifications>
    <GermlineClassification>
      <ReviewStatus>criteria provided, multiple submitters, no conflicts</ReviewStatus>
      <Description DateLastEvaluated="2018-06-05" SubmissionCount="6">Pathogenic</Description>
    </GermlineClassification>
  </RCVClassifications>
</RCVAccession>
```

The MedGen ID `C1860707` is the condition's identifier in the MedGen database. The `GermlineClassification` confirms this is an inherited (germline) variant. Six of the twelve submissions specifically addressed Tuberous sclerosis 2, all classifying the variant as pathogenic, last evaluated 2018-06-05.

---

## MetaPub ClinVar Component

> This section is for contributors working on the codebase. It assumes familiarity with the domain concepts above.

### Components

`ClinVarFetcher` is the retrieval layer. It queries NCBI using the E-utilities API and returns raw records.

`ClinVarVariant` is the parsing layer. It takes the XML returned by `ClinVarFetcher` and exposes the fields described in the domain model above as a structured Python object.

When debugging: a retrieval problem (wrong record, missing record, network error) belongs in `ClinVarFetcher`. A field extraction or normalization problem belongs in `ClinVarVariant`.

### Files

| File | Role |
|------|------|
| `metapub/metapub/clinvarfetcher.py` | Retrieval layer |
| `metapub/metapub/clinvarvariant.py` | XML parsing and in-memory representation |
| `metapub/tests/test_clinvar_fetcher.py` | Tests |
| `examples/clinvar_hello_world.py` | Runnable example |
| `clinvar-coverage.md` | Detailed coverage matrix |

**Suggested read order:** `clinvar_hello_world.py` → `clinvarfetcher.py` → `clinvarvariant.py` → tests → `clinvar-coverage.md`

### ClinVarFetcher Public API

`ClinVarFetcher` uses [NCBI E-utilities](https://www.ncbi.nlm.nih.gov/clinvar/docs/maintenance_use/#api) against `db=clinvar`. The four relevant operations are:
- `esearch`: search and return matching IDs
- `esummary`: fetch a lightweight summary record by ID
- `efetch`: fetch the full record by ID
- `elink`: follow cross-database links, e.g. ClinVar → PubMed

| Method | E-utility | Input | Returns |
|--------|-----------|-------|---------|
| `ids_by_gene(gene)` | `esearch` | gene symbol | **Entrez UIDs** |
| `ids_for_variant(hgvs)` | `esearch` | HGVS string | **Entrez UIDs** |
| `get_accession(id)` | `esummary` | Entrez UID | accession metadata |
| `variant(id, id_from='entrez')` | `efetch rettype=vcv` | Entrez UID (default) | `ClinVarVariant` |
| `variant(id, id_from='clinvar')` | `efetch rettype=vcv` | Variation ID | `ClinVarVariant` |
| `pmids_for_id(id)` | `elink` | Entrez UID | PubMed IDs |

**Key rule:** IDs from `ids_by_gene()` / `ids_for_variant()` are Entrez UIDs — pass them directly to `variant()` in the default `id_from='entrez'` mode. Use `id_from='clinvar'` only when you have a Variation ID from VCV XML.

### Common Contributor Pitfalls

**dbSNP XRef format inconsistency** — The same rsID appears in four different formats within real ClinVar XML, sometimes multiple formats in the same record (see [`clinvar_vcv_rsid_formats.manifest.txt`](metapub/tests/data/clinvar_vcv_rsid_formats.manifest.txt)):
```xml
<XRef Type="rs"       ID="1799945"   DB="dbSNP"/>  <!-- idiomatic -->
<XRef Type="rsNumber" ID="1799945"   DB="dbSNP"/>  <!-- non-standard Type -->
<XRef               ID="rs1799945"  DB="dbSNP"/>  <!-- "rs" prefix in the ID field -->
<XRef               ID="1799945"    DB="dbSNP"/>  <!-- bare number, no Type -->
```
Any code extracting dbSNP IDs must normalize across all four formats and deduplicate *after* normalization, not before — otherwise `"1799945"` and `"rs1799945"` survive dedup as different strings, then both normalize to the same value.

**`find()` vs `findall()` for complex variants** — For haplotype and genotype variant types, `SimpleAllele` elements are nested under a `Haplotype` or `Genotype` element inside `ClassifiedRecord`. Using `find('SimpleAllele')` returns only the first allele, silently dropping cross-references from all others. Always use `.//SimpleAllele/XRefList` (the `//` descendant axis) to collect xrefs from all constituent alleles. See [`clinvar_vcv_haplotype_kcnq2.manifest.txt`](metapub/tests/data/clinvar_vcv_haplotype_kcnq2.manifest.txt) for a real two-allele record that demonstrates the problem.

**VCV format vs old format** — The ClinVar XML format changed in April 2019. Before that, records used a `VariationReport` root element with `Allele` children. NCBI no longer serves this format via the API ([confirmed by fetching `rettype=variation`](metapub/tests/data/clinvar_old_format_minimal.manifest.txt)), but the codebase supports it for backwards compatibility with locally cached XML files from before the migration. The `_is_vcv_format` flag in `ClinVarVariant.__init__` controls which parsing path is used. See the [April 2019 NCBI web release notes](https://ftp.ncbi.nlm.nih.gov/pub/clinvar/release_notes/web_2.0_alpha/20190404WebRelease.pdf) for the original announcement.

### ClinVarVariant Parsed Fields

After retrieval, `ClinVarVariant` parses several identifier layers from the VCV XML:

| Field | Source | Meaning |
|-------|--------|---------|
| `variation_id` | VCV XML `VariationID` | ClinVar's own concept ID |
| `vcv_accession` | VCV XML accession field | Variation-centered accession |
| `associated_conditions` | condition sections of VCV XML | MedGen IDs, RCV accessions |
| `xrefs` | `SimpleAllele/XRefList` | allele-level cross-references (dbSNP, OMIM, UniProtKB, ClinGen) |
| `rsid` / `rsids` | `xrefs` | dbSNP variant ID(s) as bare numeric strings (e.g. `'28934872'`); `dbsnp_id` / `dbsnp_ids` are aliases |
| `omim_id` / `omim_ids` | `xrefs` | OMIM ID(s) |
| `orphanet_id` / `orphanet_ids` | `xrefs` | always `None` / `[]` on real records — Orphanet IDs are at the condition level, not in `SimpleAllele/XRefList` |
| `medgen_id` / `medgen_ids` | `xrefs` | always `None` / `[]` on real records — same reason; use `associated_conditions` for condition-level MedGen IDs |
