"""
Inderscience Publishers journal list.

Inderscience Publishers is an independent academic publisher of journals
in engineering, technology, science, and management. They publish over 
400 peer-reviewed journals, with many titles starting with "International
Journal of..."

URL format: https://www.inderscienceonline.com/doi/pdf/{doi}
Alternative: https://www.inderscienceonline.com/doi/{doi}

DOI patterns: Various (typically 10.1504/*)
"""

# Inderscience journals from inderscienceonline.com cluster (40 journals)
# INDERSCIENCE template
inderscience_template = 'https://www.inderscienceonline.com/doi/pdf/{doi}'

inderscience_journals = []  # Journal list moved to YAML configuration

# Inderscience URL format
inderscience_format = 'https://www.inderscienceonline.com/doi/pdf/{doi}'