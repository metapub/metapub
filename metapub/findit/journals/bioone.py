"""BioOne.org journals.

BioOne is a multi-publisher digital library platform that aggregates scholarly content
from biological, ecological, and environmental science publishers. Founded in 2000 as
a non-profit collaboration, BioOne serves as a content aggregator providing access to
journals from ~200+ societies and independent publishers in the life sciences.

The platform hosts journals with diverse DOI prefixes from different publishers,
but all content is accessible through complete.bioone.org. Since publishers vary,
DOI patterns include 10.1643/, 10.1645/, 10.1676/, and others.

URL pattern investigation shows DOI resolution to complete.bioone.org article pages.
Access models vary by publisher - some open access, some subscription-based.
BioOne focuses on content from small societies and non-commercial publishers.
"""

# DOI-based template for BioOne
# Since multiple publishers use this platform, we rely on DOI resolution
bioone_template = 'https://doi.org/{doi}'

# BioOne journals from categorized analysis
# These journals were identified from bioone.org domain in categorized_unknown_journals.txt
# Represents content from various biological science publishers hosted on the BioOne platform
bioone_journals = []  # Journal list moved to YAML configuration
