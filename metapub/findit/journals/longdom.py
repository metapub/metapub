# Longdom Publishing
# 
# longdom.org
#
# Longdom Publishing is an open access publisher that publishes journals
# across various fields including medical sciences, life sciences, and technology.
# Note: This publisher has been flagged by some as potentially predatory.
#
# URL Patterns:
#   - Article view: https://www.longdom.org/articles/[article-slug]
#   - PDF download: https://www.longdom.org/articles-pdfs/[article-slug].pdf
#
# DOI Pattern:
#   - Various DOI patterns (10.4172, 10.35248, etc.)
#
# Notes:
#   - Many articles are open access
#   - Articles are indexed in PubMed with PMIDs
#   - Publisher has been subject to criticism regarding editorial practices
#   - Included here for completeness as articles appear in PubMed

# URL format template - will be used in the dance function
longdom_format = 'https://www.longdom.org/articles-pdfs/{article_slug}.pdf'

# Complete list of Longdom journals (47 total)
# NOTE: Using PubMed abbreviated journal names to match PMA data
longdom_journals = []  # Journal list moved to YAML configuration
