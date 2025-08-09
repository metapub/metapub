"""
Informa Healthcare journal patterns and mappings.

Informa Healthcare publishes medical and pharmaceutical journals using DOI-based URLs.
URL construction follows a standard pattern with DOI-based access.

URL Pattern: http://informahealthcare.com/doi/pdf/{DOI}
Dance Function: the_doi_slide
"""

# Informa Healthcare journals (extracted from misc_doi.py)
# Evidence-driven consolidation: Ann Hum Biol and Hemoglobin moved to Taylor & Francis
# Acta Oncol removed (uses medicaljournalssweden.se domain, not Informa Healthcare)
informa_journals = [
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