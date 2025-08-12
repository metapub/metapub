# ACM Digital Library
# 
# dl.acm.org
#
# The ACM Digital Library is a comprehensive database of articles, proceedings,
# and other publications from the Association for Computing Machinery (ACM).
# It covers computer science, information technology, and related fields.
#
# URL Pattern:
#   - Article view: https://dl.acm.org/doi/[DOI]
#   - PDF download: https://dl.acm.org/doi/pdf/[DOI]
#
# DOI Pattern:
#   - 10.1145/[ID] (most common ACM DOI pattern)
#
# Notes:
#   - Many articles require ACM membership or institutional access
#   - Some articles are freely accessible (open access)
#   - Articles are indexed in PubMed with PMIDs for bio-computing related content
#   - DOI resolution typically redirects to article pages

# URL format template - will be used in the dance function
acm_format = 'https://dl.acm.org/doi/pdf/{doi}'

# Complete list of ACM journals and proceedings (133 total)
# NOTE: Using PubMed abbreviated journal names to match PMA data
acm_journals = []  # Journal list moved to YAML configuration
