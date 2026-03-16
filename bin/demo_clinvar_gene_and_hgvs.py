"""Demo: ClinVar gene-based and HGVS-based lookups.

Shows ClinVarFetcher methods not covered by existing demos:
  - ids_by_gene(): find ClinVar variant IDs for a gene symbol
  - ids_for_variant(): find ClinVar IDs for an HGVS string
  - pmids_for_id(): find PubMed articles citing a ClinVar variant
  - pmids_for_hgvs(): find PubMed articles for an HGVS string

Usage:
    python demo_clinvar_gene_and_hgvs.py
    python demo_clinvar_gene_and_hgvs.py BRCA1
"""

import sys

from metapub import ClinVarFetcher

cvfetch = ClinVarFetcher()


def demo_ids_by_gene(gene):
    """Look up ClinVar variant IDs for a gene."""
    print(f'ClinVar variants for gene: {gene}')
    print('-' * 40)

    ids = cvfetch.ids_by_gene(gene)
    print(f'  Total variants found: {len(ids)}')
    if ids:
        print(f'  First 10 IDs: {ids[:10]}')

    # Also try with single_gene=True to filter multi-gene variants
    ids_single = cvfetch.ids_by_gene(gene, single_gene=True)
    print(f'  Single-gene variants: {len(ids_single)}')
    print()
    return ids


def demo_pmids_for_variant(variant_id):
    """Look up PubMed IDs associated with a ClinVar variant."""
    print(f'PubMed articles for ClinVar variant {variant_id}')
    print('-' * 40)

    pmids = cvfetch.pmids_for_id(variant_id)
    if pmids:
        print(f'  Found {len(pmids)} PubMed article(s): {pmids}')
    else:
        print(f'  No PubMed articles found')
    print()
    return pmids


def demo_hgvs_lookups(hgvs_text):
    """Look up ClinVar variants and PubMed articles by HGVS notation."""
    print(f'HGVS lookup: {hgvs_text}')
    print('-' * 40)

    # Find ClinVar IDs for this HGVS string
    ids = cvfetch.ids_for_variant(hgvs_text)
    print(f'  ClinVar IDs: {ids if ids else "none found"}')

    # Find associated PubMed articles via each variant ID
    # (pmids_for_hgvs has a known bug -- see issue #105 -- so we do it manually)
    all_pmids = []
    for vid in ids:
        all_pmids.extend(cvfetch.pmids_for_id(vid))
    print(f'  PubMed IDs: {all_pmids if all_pmids else "none found"}')
    print()


if __name__ == '__main__':
    gene = sys.argv[1] if len(sys.argv) > 1 else 'BRCA2'

    # 1. Find variants for a gene
    ids = demo_ids_by_gene(gene)

    # 2. Get PubMed articles for the first variant found
    if ids:
        demo_pmids_for_variant(ids[0])

    # 3. HGVS-based lookups
    demo_hgvs_lookups('NM_000059.4:c.9382C>T')  # BRCA2 variant
