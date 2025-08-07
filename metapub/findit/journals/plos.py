"""
PLOS (Public Library of Science) journal patterns and mappings.

PLOS publishes open access journals and provides perfect citation_pdf_url meta tags.
This makes PDF extraction extremely simple and reliable.

Evidence-based analysis from HTML samples (2025-08-07):
- Perfect citation_pdf_url meta tags in all samples
- Pattern: https://journals.plos.org/[journal]/article/file?id=[DOI]&type=printable
- DOI format: 10.1371/journal.[code] (consistent across all journals)
- No URL construction needed - direct meta tag extraction

Dance Function: the_plos_pogo
"""

# Publisher metadata
PUBLISHER_INFO = {
    'name': 'Public Library of Science',
    'dance_function': 'the_plos_pogo',
    'base_url': 'https://journals.plos.org',
    'identifier_type': 'doi'  # DOI-based format
}

# PLOS journals using DOI format (extracted from misc_doi.py)
plos_journals = [
    'J Data Mining Genomics Proteomics',
    'J Pet Environ Biotechnol',
    'PLoS Biol',
    'PLoS Clin Trials',
    'PLoS Comput Biol',
    'PLoS Genet',
    'PLoS Med',
    'PLoS Negl Trop Dis',
    'PLoS One',
    'PLoS Pathog',
]

# PLOS uses citation_pdf_url meta tag extraction - no template needed
# Evidence shows pattern: https://journals.plos.org/[journal]/article/file?id=[DOI]&type=printable