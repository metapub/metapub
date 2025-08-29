"""
Project MUSE dance function - evidence-driven rewrite.

Evidence-driven implementation based on HTML samples analysis showing
perfect citation_pdf_url meta tags in all samples.

Pattern discovered from HTML samples:
- citation_pdf_url meta tags: 100% reliable across all 3 samples
- URL pattern: https://muse.jhu.edu/pub/{id}/article/{article_id}/pdf
- Domain consistency: muse.jhu.edu (100% consistent)
- All samples from University of Nebraska Press but hosted on Project MUSE
- No blocking detected, clean HTML content throughout
"""

import re
from .generic import the_doi_2step, verify_pdf_url, unified_uri_get
from ...exceptions import NoPDFLink


def the_projectmuse_syrtos(pma, verify=True, request_timeout=10, max_redirects=3):
    """
    Project MUSE dance function - evidence-driven meta tag extraction.
    
    Based on evidence analysis of 3 HTML samples showing perfect citation_pdf_url 
    meta tags in all cases. Simple and reliable approach.
    
    :param pma: PubMedArticle object  
    :param verify: bool [default: True] - Verify PDF URL accessibility
    :return: PDF URL string
    :raises: NoPDFLink if DOI missing or meta tag extraction fails
    """
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for Project MUSE articles')
    
    # Step 1: Resolve DOI to get Project MUSE article URL
    article_url = the_doi_2step(pma.doi)
    
    # Step 2: Fetch article page HTML
    response = unified_uri_get(article_url, timeout=request_timeout, max_redirects=max_redirects)
    
    if response.status_code not in (200, 301, 302, 307):
        raise NoPDFLink(f'TXERROR: Could not access Project MUSE article page (HTTP {response.status_code})')
    
    # Step 3: Extract citation_pdf_url meta tag (evidence-based approach)
    pdf_match = re.search(r'<meta[^>]*name=["\']citation_pdf_url["\'][^>]*content=["\']([^"\']+)["\']', 
                         response.text, re.IGNORECASE)
    
    if not pdf_match:
        raise NoPDFLink('MISSING: No PDF URL found via citation_pdf_url meta tag extraction')
    
    pdf_url = pdf_match.group(1)
    
    if verify:
        verify_pdf_url(pdf_url, 'Project MUSE', request_timeout=request_timeout, max_redirects=max_redirects)
    
    return pdf_url
