"""
Mary Ann Liebert Publishers journal patterns and mappings.

Liebert publishes biomedical journals using DOI-based URLs with a 
standardized format across all their publications.

URL Pattern: http://online.liebertpub.com/doi/pdf/{doi}
Dance Function: the_doi_slide
"""

# Publisher metadata
PUBLISHER_INFO = {
    'name': 'Mary Ann Liebert Publishers',
    'dance_function': 'the_doi_slide',
    'base_url': 'https://liebertpub.com',
    'url_pattern': 'http://online.liebertpub.com/doi/pdf/{doi}',
    'identifier_type': 'doi'  # DOI-based format
}

# Liebert journals using DOI format (extracted from misc_doi.py)
liebert_journals = [
    'AIDS Res Hum Retroviruses',
    'Antioxid Redox Signal',
    'Child Obes',
    'DNA Cell Biol',
    'Genet Test',
    'Genet Test Mol Biomarkers',
    'Thyroid',
    'Vector Borne Zoonotic Dis',
]

# DOI template for Liebert journals
liebert_template = 'http://online.liebertpub.com/doi/pdf/{doi}'