# Journal of Clinical Investigation (JCI)
# 
# jci.org
#
# JCI is a high-impact medical research journal that focuses on biomedical research.
# Articles are typically freely accessible after publication.
#
# URL Pattern:
#   - Article view: https://www.jci.org/articles/view/{pii}
#   - PDF download: http://www.jci.org/articles/view/{pii}/files/pdf
#
# PII Pattern:
#   - Numeric ID (e.g., 82041)
#   - Available in PubMed article metadata
#
# DOI Pattern:
#   - 10.1172/JCI{pii}
#
# Notes:
#   - Most JCI articles are freely accessible
#   - PII is essential for URL construction
#   - DOI can be used as fallback via dx.doi.org resolution

jci_format = 'http://www.jci.org/articles/view/{pii}/files/pdf'

jci_journals = []  # Journal list moved to YAML configuration
