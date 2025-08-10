"""
Schattauer publisher configuration.

Evidence-driven implementation: Schattauer journals run on Thieme's platform
(thieme-connect.de) and use standard DOI-based PDF URLs with the_doi_slide generic function.

Based on HTML samples analysis showing consistent citation_pdf_url meta tags
and DOI pattern 10.1055/a-XXXX-XXXX.
"""

# Schattauer journals (run on Thieme platform)
schattauer_journals = [
    'Thromb Haemost',
]

# Uses Thieme's platform template
schattauer_template = 'http://www.thieme-connect.de/products/ejournals/pdf/{doi}.pdf'