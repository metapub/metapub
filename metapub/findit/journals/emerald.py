# Emerald Publishing
# 
# emerald.com
#
# Emerald Publishing is a digital-first publisher of management, business,
# education, library science, information management research, and health care journals.
# Founded in 1967, it publishes over 300 journals and more than 2,500 books.
#
# URL Pattern:
#   - Article view: https://www.emerald.com/insight/content/doi/[DOI]/full/html
#   - PDF download: https://www.emerald.com/insight/content/doi/[DOI]/full/pdf
#
# DOI Pattern:
#   - 10.1108/[JOURNAL_CODE]-[DATE]-[ID]
#
# Notes:
#   - Many articles are behind paywall but some are open access
#   - Articles are indexed in PubMed with PMIDs
#   - DOI resolution typically redirects to article pages
#   - PDF access requires subscription or institutional access

# URL format template - will be used in the dance function
emerald_format = 'https://www.emerald.com/insight/content/doi/{doi}/full/pdf'

# Complete list of Emerald journals (68 total)
# NOTE: Using PubMed abbreviated journal names to match PMA data
emerald_journals = []  # Journal list moved to YAML configuration
