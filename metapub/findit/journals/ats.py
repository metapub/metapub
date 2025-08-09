"""
American Thoracic Society (ATS) journal patterns and mappings.

ATS publishes respiratory medicine journals using DOI-based URLs 
with a standardized format.

URL Pattern: https://www.thoracic.org/doi/pdf/{doi}?download=true
Dance Function: the_doi_slide

Evidence-Based Update: 2025-08-09
- Updated from legacy atsjournals.org to current thoracic.org domain
- Added ?download=true parameter for direct PDF downloads
- Enforced HTTPS instead of HTTP
- Pattern discovered through evidence-driven analysis of HTML samples
"""

# ATS journals using DOI format (evidence-based expansion)
ats_journals = [
    'Am J Respir Cell Mol Biol',
    'Am J Respir Crit Care Med',
    'Ann Am Thorac Soc',
    'Proc Am Thorac Soc',
]

# DOI template for ATS journals (updated based on evidence)
ats_template = 'https://www.thoracic.org/doi/pdf/{doi}?download=true'