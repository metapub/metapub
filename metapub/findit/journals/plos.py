"""
PLOS (Public Library of Science) journal patterns and mappings.

PLOS publishes open access journals using DOI-based URLs with a 
specialized format for PDF retrieval.

URL Pattern: http://www.plosone.org/article/fetchObject.action?uri=info:doi/{doi}&representation=PDF
Dance Function: the_doi_slide
"""

# Publisher metadata
PUBLISHER_INFO = {
    'name': 'Public Library of Science',
    'dance_function': 'the_doi_slide',
    'base_url': 'https://plos.org',
    'url_pattern': 'http://www.plosone.org/article/fetchObject.action?uri=info:doi/{doi}&representation=PDF',
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

# DOI template for PLOS journals
plos_template = 'http://www.plosone.org/article/fetchObject.action?uri=info:doi/{doi}&representation=PDF'