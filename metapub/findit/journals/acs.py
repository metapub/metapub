"""
American Chemical Society (ACS) journal patterns and mappings.

ACS publishes chemistry and chemical engineering journals using DOI-based URLs.
All ACS journals follow a consistent DOI-based PDF access pattern.

URL Pattern: https://pubs.acs.org/doi/pdf/{DOI}
Dance Function: the_doi_slide

Evidence-based analysis from HTML samples (2025-08-07):
- Consistent pattern across all samples: /doi/pdf/{DOI}?ref=article_openPDF
- All DOIs use 10.1021/ prefix (ACS DOI prefix)
- HTTPS enforced (HTTP redirects with 301)
- Cloudflare protection may block verification but URL construction works
"""


# Template for ACS DOI-based URLs
acs_template = 'https://pubs.acs.org/doi/pdf/{doi}'

# American Chemical Society journals (extracted from misc_doi.py)
acs_journals = []  # Journal list moved to YAML configuration
