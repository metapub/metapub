"""Sciendo (De Gruyter) journal configuration for FindIt.

Sciendo is De Gruyter's open access publishing platform, launched in 2018.
It hosts a diverse collection of academic journals across multiple disciplines,
primarily from Eastern European and international publishers.

URL pattern: https://sciendo.com/article/{doi}
DOI patterns: Various (10.2478/*, 10.1515/*, etc.) due to publisher diversity
"""

# All Sciendo journals from cluster analysis
sciendo_journals = []  # Journal list moved to YAML configuration

# DOI-based format template (for the_doi_slide)
sciendo_doi_format = 'https://sciendo.com/pdf/{doi}'

