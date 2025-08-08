"""
NEJM (New England Journal of Medicine) journal configuration.

NEJM is the top medical journal with simple DOI-based PDF access.

Evidence-based analysis from HTML samples (2025-08-08):
- Direct DOI-based PDF URL construction: https://www.nejm.org/doi/pdf/{doi}
- DOI format: 10.1056/ prefix (consistent across all articles)
- No citation_pdf_url meta tags available
- Perfect for the_doi_slide generic function

Dance Function: the_doi_slide (generic DOI-based function)
"""

# Publisher metadata
PUBLISHER_INFO = {
    'name': 'New England Journal of Medicine',
    'dance_function': 'the_doi_slide',
    'base_url': 'https://www.nejm.org',
    'format_template': 'https://www.nejm.org/doi/pdf/{doi}',
    'identifier_type': 'doi'
}

# NEJM journal names
nejm_journals = [
    'N Engl J Med',
    'New England Journal of Medicine',
    'NEJM',
    'NEJM Evid',
    'NEJM Evidence',
    'NEJM Catalyst',
    'NEJM AI',
    'NEJM Journal Watch'
]