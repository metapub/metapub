"""
Informa Healthcare journal patterns and mappings.

Informa Healthcare publishes medical and pharmaceutical journals using DOI-based URLs.
URL construction follows a standard pattern with DOI-based access.

URL Pattern: http://informahealthcare.com/doi/pdf/{DOI}
Dance Function: the_template_dance
"""

# Publisher metadata
PUBLISHER_INFO = {
    'name': 'Informa Healthcare',
    'dance_function': 'the_template_dance',
    'base_url': 'http://informahealthcare.com',
    'url_pattern': 'http://informahealthcare.com/doi/pdf/{doi}',
    'identifier_type': 'doi'
}

# Informa Healthcare journals (extracted from misc_doi.py)
informa_journals = [
    'Acta Oncol',
    'Ann Hum Biol',
    'Hemoglobin',
    'J Matern Fetal Neonatal Med',
    'Ophthalmic Genet',
    'Platelets',
    'Ren Fail',
    'Scand J Rheumatol',
    'Scand J Urol Nephrol',
    'Xenobiotica',
]

# URL template for Informa Healthcare journals
informa_template = 'http://informahealthcare.com/doi/pdf/{doi}'