"""Thieme Medical Publishers journals.

Thieme is a German medical and scientific publisher with a long history of publishing
high-quality journals in medicine, health sciences, and related fields.

Their journals are hosted on thieme-connect.de and use DOI-based PDF access.

Based on investigation, their PDF access pattern is:
https://www.thieme-connect.de/products/ejournals/pdf/{doi}.pdf

DOI pattern: Thieme uses 10.1055 as their DOI prefix.
"""

# DOI-based template for Thieme Connect (evidence-driven pattern)
# Evidence from HTML samples shows http://www.thieme-connect.de pattern
thieme_doi_format = 'http://www.thieme-connect.de/products/ejournals/pdf/{doi}.pdf'


# Thieme journals from categorized analysis
# These journals showed up as associated with thieme-connect.de domain
thieme_journals = []  # Journal list moved to YAML configuration
