"""
American Thoracic Society (ATS) journal patterns and mappings.

ATS publishes respiratory medicine journals using DOI-based URLs 
with a standardized format.

URL Pattern: http://www.atsjournals.org/doi/pdf/{doi}
Dance Function: the_doi_slide
"""

# ATS journals using DOI format (extracted from misc_doi.py)
ats_journals = [
    'Am J Respir Cell Mol Biol',
    'Am J Respir Crit Care Med',
]

# DOI template for ATS journals
ats_template = 'http://www.atsjournals.org/doi/pdf/{doi}'