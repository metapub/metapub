"""
American Thoracic Society (ATS) journal patterns and mappings.

ATS publishes respiratory medicine journals using DOI-based URLs 
with a standardized format.

URL Pattern: http://www.atsjournals.org/doi/pdf/{doi}
Dance Function: the_doi_slide
"""

# Publisher metadata
PUBLISHER_INFO = {
    'name': 'American Thoracic Society',
    'dance_function': 'the_doi_slide',
    'base_url': 'https://atsjournals.org',
    'url_pattern': 'http://www.atsjournals.org/doi/pdf/{doi}',
    'identifier_type': 'doi'  # DOI-based format
}

# ATS journals using DOI format (extracted from misc_doi.py)
ats_journals = [
    'Am J Respir Cell Mol Biol',
    'Am J Respir Crit Care Med',
]

# DOI template for ATS journals
ats_template = 'http://www.atsjournals.org/doi/pdf/{doi}'