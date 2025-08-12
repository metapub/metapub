"""MDPI (Multidisciplinary Digital Publishing Institute) journals.

MDPI journals use DOI pattern 10.3390/... and are primarily available through PMC.
This module provides backup PDF access for when PMC is unavailable.

URL pattern: https://www.mdpi.com/{ISSN}/{volume}/{issue}/{article}/pdf
"""

# Template for MDPI backup PDF URLs
# The URL should be the resolved DOI URL + '/pdf'
mdpi_template = '{url}/pdf'

# MDPI journals from unknown publishers analysis
# DOI pattern: 10.3390/...
mdpi_journals = []  # Journal list moved to YAML configuration
