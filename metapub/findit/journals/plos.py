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


# PLOS journals using DOI format (extracted from misc_doi.py)
plos_journals = []  # Journal list moved to YAML configuration

# PLOS uses citation_pdf_url meta tag extraction - no template needed
# Evidence shows pattern: https://journals.plos.org/[journal]/article/file?id=[DOI]&type=printable