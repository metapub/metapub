"""
OAText Publishing journal list.

OAText is an open access academic publisher specializing in medical, 
scientific, and healthcare journals. They publish peer-reviewed journals
across various medical and scientific disciplines.

URL format: https://www.oatext.com/[article-title].php
Alternative: https://oatext.com/pdf/[JOURNAL_CODE]-[VOLUME]-[ARTICLE_ID].pdf

DOI patterns: Various (need to determine specific patterns)
"""

# OAText journals from oatext.com cluster (41 journals)
oatext_journals = []  # Journal list moved to YAML configuration

# OAText URL format - will need to determine the exact pattern
oatext_format = 'https://www.oatext.com/pdf/{article_id}.pdf'