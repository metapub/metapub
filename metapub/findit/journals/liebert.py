"""
Mary Ann Liebert Publishers journal patterns and mappings.

Liebert publishes biomedical journals using DOI-based URLs with a 
standardized format across all their publications.

URL Pattern: https://www.liebertpub.com/doi/pdf/{doi}?download=true
Dance Function: the_doi_slide
DOI Prefix: 10.1089

Evidence-driven update 2025-08-09: Updated domain from legacy online.liebertpub.com
to modern www.liebertpub.com with HTTPS and download parameter based on analysis
of 5/8 accessible HTML samples showing consistent pattern.
"""

# Liebert journals using DOI format (expanded from unknown publishers analysis)
liebert_journals = []  # Journal list moved to YAML configuration

# DOI template for Liebert journals (evidence-driven update 2025-08-09)
# Updated from legacy http://online.liebertpub.com to modern HTTPS domain with download parameter
# Pattern discovered from 5/8 HTML samples showing consistent /doi/pdf/ + ?download=true
liebert_template = 'https://www.liebertpub.com/doi/pdf/{doi}?download=true'