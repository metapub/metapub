"""
Taylor & Francis journal patterns and mappings.

Taylor & Francis publishes a vast array of academic journals across multiple disciplines
using DOI-based URLs through their tandfonline.com platform.

URL Pattern: https://www.tandfonline.com/doi/epdf/{DOI}?needAccess=true
Dance Function: the_doi_slide

Evidence-driven pattern discovered from HTML sample analysis:
- All samples showed consistent /doi/epdf/{DOI}?needAccess=true pattern
- HTTPS required (not HTTP)
- needAccess=true parameter required for access
"""

# Template for Taylor & Francis DOI-based URLs (evidence-driven pattern)
taylor_francis_template = 'https://www.tandfonline.com/doi/epdf/{doi}?needAccess=true'

# Taylor & Francis journals (extracted from misc_doi.py)
# Note: This is a comprehensive list of 1,687 journals across multiple disciplines
taylor_francis_journals = []  # Journal list moved to YAML configuration
