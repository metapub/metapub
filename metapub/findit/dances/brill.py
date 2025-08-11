"""
Brill dance function - evidence-driven rewrite.

Evidence-driven implementation based on HTML samples analysis showing
perfect citation_pdf_url meta tags in all samples.

Pattern discovered from HTML samples:
- citation_pdf_url meta tags: 100% reliable
- URL pattern: https://brill.com/downloadpdf/view/journals/{journal}/{volume}/{issue}/article-p{page}_{id}.pdf
- DOI patterns: Multiple prefixes (10.1163, 10.1007, 10.1016, etc.) - no restriction needed
- 403 Forbidden expected for subscription content but URLs are correctly constructed
"""

import re
import requests
from .generic import the_doi_2step, verify_pdf_url, unified_uri_get
from ...exceptions import NoPDFLink


def the_brill_bridge(pma, verify=True):
    """
    Brill dance function - evidence-driven meta tag extraction.
    
    Based on evidence analysis showing perfect citation_pdf_url meta tags
    in all HTML samples. Simple and reliable approach.
    
    :param pma: PubMedArticle object
    :param verify: bool [default: True] - Verify PDF URL accessibility
    :return: PDF URL string
    :raises: NoPDFLink if DOI missing or meta tag extraction fails
    """
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for Brill articles')
    
    # Resolve DOI to get article HTML page
    article_url = the_doi_2step(pma.doi)
    
    try:
        response = unified_uri_get(article_url)
    except requests.exceptions.ConnectionError as e:
        raise NoPDFLink(f'TXERROR: Network error accessing Brill article: {e}')
    
    if response.status_code not in (200, 301, 302, 307):
        raise NoPDFLink(f'TXERROR: Could not access Brill article page (HTTP {response.status_code})')
    
    # Extract citation_pdf_url meta tag (evidence-based approach)
    pdf_match = re.search(r'<meta[^>]*name=["\']citation_pdf_url["\'][^>]*content=["\']([^"\']+)["\']', 
                         response.text, re.IGNORECASE)
    
    if not pdf_match:
        raise NoPDFLink('MISSING: No PDF URL found via citation_pdf_url meta tag extraction')
    
    pdf_url = pdf_match.group(1)
    
    if verify:
        verify_pdf_url(pdf_url, 'Brill')
    
    return pdf_url