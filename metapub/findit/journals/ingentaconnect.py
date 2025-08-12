"""Ingenta Connect (ingentaconnect.com) journals.

Ingenta Connect is a digital publishing platform that hosts scholarly content
from multiple publishers. Founded by Ingenta, it serves as a content aggregator
providing access to millions of articles from over 250 publishers.

The platform hosts journals with diverse DOI prefixes from different publishers,
but all content is accessible through ingentaconnect.com. Since publishers vary,
DOI patterns are diverse (10.3751/, 10.5588/, 10.1166/, etc.).

URL pattern investigation shows DOI resolution to ingentaconnect.com article pages.
Access models vary by publisher - some open access, some subscription-based.
"""

# DOI-based template for Ingenta Connect
# Since multiple publishers use this platform, we rely on DOI resolution
ingentaconnect_template = 'https://doi.org/{doi}'

# Ingenta Connect journals from categorized analysis
# These journals were identified from ingentaconnect.com domain in categorized_unknown_journals.txt
# Represents content from various publishers hosted on the Ingenta Connect platform
ingentaconnect_journals = []  # Journal list moved to YAML configuration
