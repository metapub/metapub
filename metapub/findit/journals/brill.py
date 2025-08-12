"""Brill Academic Publishers (brill.com) journals.

Brill is a Dutch international academic publisher founded in 1683, specializing in
the humanities, international law, social sciences, and biology.
They publish over 600 journals and around 2000 new books and reference works annually.

Based on investigation, Brill uses DOI prefix 10.1163 for their publications.
Articles are hosted on brill.com with DOI-based access patterns.

URL pattern investigation shows DOI resolution to brill.com article pages.
Some content may be behind institutional paywalls but many articles have
open access or trial access available.
"""

# DOI-based template for Brill Academic Publishers
# Based on investigation showing DOI prefix 10.1163 redirects to brill.com
brill_template = 'https://doi.org/{doi}'

# Brill Academic Publishers journals from categorized analysis
# These journals were identified from brill.com domain in categorized_unknown_journals.txt
# Focused on humanities, social sciences, and biology journals published by Brill
brill_journals = []  # Journal list moved to YAML configuration
