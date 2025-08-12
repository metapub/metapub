"""Frontiers Media S.A. journal configuration for FindIt.

Frontiers is a major open-access academic publisher founded in 2007,
specializing in digital publishing across multiple disciplines.
Known for their innovative article-level metrics and transparent peer review.

URL pattern: https://www.frontiersin.org/articles/{doi}/full
DOI patterns: 10.3389/* (primary pattern for Frontiers)
"""

# All Frontiers journals from cluster analysis
frontiers_journals = []  # Journal list moved to YAML configuration

# URL format template for Frontiers articles
frontiers_format = "https://www.frontiersin.org/articles/{doi}/full"