# IOS Press
# 
# content.iospress.com
#
# IOS Press is an international publisher of scientific and technical books and journals
# based in Amsterdam, Netherlands. It specializes in computer science, artificial intelligence,
# biomedical sciences, health technologies, and other technical disciplines.
#
# URL Patterns:
#   - Article view: https://content.iospress.com/articles/[journal]/[DOI]
#   - PDF download: https://content.iospress.com/download/[journal]/[DOI]
#
# DOI Pattern:
#   - 10.3233/[JOURNAL]-[ID] (IOS Press DOI pattern)
#
# Notes:
#   - Many articles require subscription or institutional access
#   - Some articles are freely accessible (open access)
#   - Articles are indexed in PubMed with PMIDs across medical and technical fields
#   - Journal abbreviations are used in URLs

# URL format template - evidence-based pattern for the_doi_slide generic function
iospress_format = 'https://content.iospress.com/doi/pdf/{doi}?download=true'

# Complete list of IOS Press journals (54 total)
# NOTE: Using PubMed abbreviated journal names to match PMA data
iospress_journals = []  # Journal list moved to YAML configuration
