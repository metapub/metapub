# World Scientific Publishing
# 
# worldscientific.com
#
# World Scientific Publishing is a major academic publisher for scientific,
# technical, and medical content. It publishes journals, books, and conference
# proceedings in various fields including physics, mathematics, computer science,
# engineering, chemistry, and life sciences.
#
# URL Patterns:
#   - Article view: https://www.worldscientific.com/doi/[DOI]
#   - PDF download: https://www.worldscientific.com/doi/pdf/[DOI]
#
# DOI Pattern:
#   - 10.1142/[ID] (World Scientific DOI pattern)
#
# Notes:
#   - Many articles require subscription or institutional access
#   - Some articles are freely accessible (open access)
#   - Articles are indexed in PubMed with PMIDs for bio-computing and medical related content
#   - DOI resolution typically redirects to article pages

# URL format template - now used with the_doi_slide generic function
# Based on evidence from HTML samples: ?download=true parameter is consistently used
worldscientific_format = 'https://www.worldscientific.com/doi/pdf/{doi}?download=true'

# Complete list of World Scientific journals (60 total)
# NOTE: Using PubMed abbreviated journal names to match PMA data
worldscientific_journals = []  # Journal list moved to YAML configuration
