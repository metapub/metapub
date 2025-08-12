"""Royal Society of Chemistry (RSC) Publishers (pubs.rsc.org) journals.

The Royal Society of Chemistry (RSC) is a learned society and professional body
for chemical scientists, founded in 1841. They publish over 50 journals covering
all areas of chemistry and related fields.

Based on investigation, RSC uses DOI prefix 10.1039 for their publications
hosted on pubs.rsc.org. Many RSC journals have open access articles or trial access.

URL pattern investigation shows DOI resolution to pubs.rsc.org article pages.
Some content may be behind institutional paywalls but many articles have
open access or are available through various access models.
"""

# DOI-based template for Royal Society of Chemistry
# Based on investigation showing DOI prefix 10.1039 redirects to pubs.rsc.org
rsc_template = 'https://doi.org/{doi}'

# Royal Society of Chemistry journals from categorized analysis
# These journals were identified from pubs.rsc.org domain in categorized_unknown_journals.txt
# Includes historical and current RSC publications across all chemistry fields
rsc_journals = []  # Journal list moved to YAML configuration
