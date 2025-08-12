# University of Chicago Press
# 
# journals.uchicago.edu
#
# The University of Chicago Press is one of the largest and oldest university presses
# in the United States. It publishes academic journals, books, and scholarly content
# across various disciplines including humanities, social sciences, education, 
# biological sciences, and physical sciences.
#
# URL Patterns:
#   - Article view: https://www.journals.uchicago.edu/doi/[DOI]
#   - PDF download: https://www.journals.uchicago.edu/doi/pdf/[DOI]
#
# DOI Pattern:
#   - 10.1086/[ID] (University of Chicago Press DOI pattern)
#
# Notes:
#   - Many articles require subscription or institutional access
#   - Some articles are freely accessible (open access)
#   - Articles are indexed in PubMed with PMIDs across multiple disciplines
#   - DOI resolution typically redirects to article pages

# URL format template - now used with the_doi_slide generic function
# Based on evidence from HTML samples: /doi/epdf/ and /doi/pdf/ both work,
# using /doi/pdf/ as primary pattern
uchicago_format = 'https://www.journals.uchicago.edu/doi/pdf/{doi}'

# Complete list of University of Chicago Press journals (59 total)
# NOTE: Using PubMed abbreviated journal names to match PMA data
uchicago_journals = []  # Journal list moved to YAML configuration
