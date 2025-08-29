"""
PLOS (Public Library of Science) dance function.

Evidence-driven implementation based on HTML samples analysis.
PLOS provides perfect citation_pdf_url meta tags, making this extremely simple.

Pattern discovered from HTML samples:
- citation_pdf_url: https://journals.plos.org/[journal]/article/file?id=[DOI]&type=printable
- All DOIs use 10.1371/journal.[code] format
- 100% consistent across all samples

This function reduces logical complication by directly extracting the 
citation_pdf_url meta tag from the article HTML page.
"""

import re
from .generic import the_doi_2step, verify_pdf_url, unified_uri_get
from ...exceptions import NoPDFLink


def the_plos_pogo(pma, verify=True, request_timeout=10, max_redirects=3):
    """
    PLOS dance function - extract PDF URL from citation_pdf_url meta tag.
    
    Evidence-based approach: PLOS consistently provides citation_pdf_url meta tags
    across all journals, making this the simplest and most reliable method.
    
    :param pma: PubMedArticle object
    :param verify: bool [default: True] - Verify PDF URL accessibility
    :return: PDF URL string
    :raises: NoPDFLink if citation_pdf_url not found or DOI missing
    """
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for PLOS articles')
    
    # Get article HTML page via DOI resolution
    article_url = the_doi_2step(pma.doi)
    response = unified_uri_get(article_url, timeout=request_timeout, max_redirects=max_redirects)
    
    if response.status_code != 200:
        raise NoPDFLink(f'TXERROR: Could not access PLOS article page (HTTP {response.status_code})')
    
    # Extract citation_pdf_url meta tag (most reliable method)
    pdf_match = re.search(r'<meta name="citation_pdf_url"\s+content="([^"]+)"', response.text)
    if not pdf_match:
        raise NoPDFLink('MISSING: No citation_pdf_url found in PLOS article HTML')
    
    pdf_url = pdf_match.group(1)
    
    # Verify PDF accessibility if requested
    if verify:
        verify_pdf_url(pdf_url, 'PLOS', request_timeout=request_timeout, max_redirects=max_redirects)
    
    return pdf_url