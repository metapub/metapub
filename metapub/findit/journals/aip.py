"""AIP Publishing journal data.

This module contains journal data for AIP Publishing (American Institute of Physics),
which publishes physics and related science journals through pubs.aip.org.
"""

aip_journals = []  # Journal list moved to YAML configuration

aip_format = 'https://pubs.aip.org/aip/{journal}/{article}/{volume}/{article_id}/pdf'

# DOI-based template for AIP (for the_doi_slide)
aip_doi_format = 'https://pubs.aip.org/aip/article-pdf/doi/{doi}'