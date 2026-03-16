"""Demo: advanced PubMed query features.

Shows pmids_for_query() capabilities beyond basic keyword search:
  - MeSH term filtering (mesh, mesh_major)
  - Title and abstract search (title, abstract)
  - Date range filtering (since, until, year)
  - PMC-only results (pmc_only)
  - Affiliation search
  - Combining freeform queries with field-specific kwargs

The existing demo_get_pmids_for_query.py covers basic journal/author/volume
searches. This demo focuses on the more advanced options.

Usage:
    python demo_advanced_pubmed_query.py
"""

from metapub import PubMedFetcher
from metapub.eutils_compat import EutilsRequestError

fetch = PubMedFetcher()


def show_results(description, pmids, max_show=5):
    print(f'{description}')
    print(f'  Found {len(pmids)} result(s)')
    if pmids:
        print(f'  First {min(max_show, len(pmids))}: {pmids[:max_show]}')
    print()


def try_query(description, *args, **kwargs):
    """Run a query and handle transient NCBI errors gracefully."""
    try:
        pmids = fetch.pmids_for_query(*args, **kwargs)
        show_results(description, pmids)
        return pmids
    except EutilsRequestError as e:
        print(f'{description}')
        print(f'  NCBI service error (transient): {type(e).__name__}')
        print()
        return []


# 1. MeSH major topic heading
try_query('MeSH major topic "Breast Neoplasms" in 2023 (max 10):',
          mesh_major='Breast Neoplasms', year=2023, retmax=10)

# 2. Title-word search
try_query('Title contains "CRISPR" in 2024 (max 10):',
          title='CRISPR', year=2024, retmax=10)

# 3. Title/abstract combined search
try_query('Title/abstract "machine learning radiology", 2023-2024 (max 10):',
          abstract='machine learning radiology', since='2023', until='2024', retmax=10)

# 4. Freeform query with exact phrase matching
try_query('Exact phrase: "liquid biopsy" AND "non-small cell lung cancer" (2023):',
          '"liquid biopsy" AND "non-small cell lung cancer"', retmax=10, year=2023)

# 5. PMC-only results (open access articles)
try_query('MeSH "Alzheimer Disease" in PMC only (2024, max 10):',
          mesh='Alzheimer Disease', pmc_only=True, year=2024, retmax=10)

# 6. Affiliation search
try_query('Affiliation "Harvard Medical School" + title "genomics" since 2023:',
          affiliation='Harvard Medical School', title='genomics', since='2023', retmax=10)

# 7. Language filter
try_query('MeSH "Diabetes Mellitus" in French (2023):',
          mesh='Diabetes Mellitus', language='fre', year=2023, retmax=10)

# 8. Pagination: get second page of results
print('Pagination demo: MeSH "Neoplasms" 2024')
try:
    pmids_page1 = fetch.pmids_for_query(mesh='Neoplasms', year=2024, retmax=5, retstart=0)
    pmids_page2 = fetch.pmids_for_query(mesh='Neoplasms', year=2024, retmax=5, retstart=5)
    print(f'  Page 1 (0-4): {pmids_page1}')
    print(f'  Page 2 (5-9): {pmids_page2}')
    overlap = set(pmids_page1) & set(pmids_page2)
    print(f'  Overlap: {len(overlap)} (should be 0)')
except EutilsRequestError as e:
    print(f'  NCBI service error (transient): {type(e).__name__}')
print()

# 9. Combining freeform query with kwargs
try_query('Freeform "cancer immunotherapy" + journal Nature since 2023:',
          'cancer immunotherapy', journal='Nature', since='2023', retmax=10)
