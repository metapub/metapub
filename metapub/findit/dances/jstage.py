"""J-STAGE dance function - OPTIMIZED COMPLEXITY HIERARCHY.

Follows optimal complexity hierarchy to minimize network requests:
1. DOI resolution to get article URL (minimal network request)
2. Primary: URL manipulation (_article → _pdf) - no page loading
3. Fallback: HTML parsing for citation_pdf_url - only when needed

Evidence: All samples (31588070, 34334504, 38028269) show consistent patterns.
URL pattern: https://www.jstage.jst.go.jp/article/{journal}/{volume}/{issue}/{volume}_{article_id}/_pdf

This approach tries simplest method first, falls back to reliable method only when necessary.
"""

import re
from ...exceptions import NoPDFLink, AccessDenied
from .generic import the_doi_2step, verify_pdf_url, unified_uri_get


def the_jstage_dive(pma, verify=True, request_timeout=10, max_redirects=3):
    """J-STAGE: Japan Science and Technology Information Aggregator, Electronic.
    
    Optimized approach: Try DOI resolution to get article URL first (minimal network request),
    then try URL manipulation, fallback to HTML parsing only if needed.
    
    Primary method: DOI resolution + URL manipulation (fast)
    Fallback method: HTML parsing for citation_pdf_url (reliable)

    :param pma: PubmedArticle with DOI required
    :param verify: PDF URL verification (default: True)
    :return: PDF URL string
    :raises: NoPDFLink, AccessDenied
    """
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for J-STAGE articles')
    
    # Get article page URL via DOI resolution (minimal network request)
    article_url = the_doi_2step(pma.doi)
    
    # Verify this resolves to J-STAGE without loading content
    if 'jstage.jst.go.jp' not in article_url:
        raise NoPDFLink('INVALID: DOI does not resolve to J-STAGE platform')
    
    # Primary method: Try URL manipulation without loading page content
    pdf_url = None
    if '_article' in article_url:
        # Simple URL manipulation: _article → _pdf
        pdf_url = article_url.replace('_article', '_pdf')
        # Clean up any query parameters after _pdf
        pdf_pos = pdf_url.find('_pdf')
        if pdf_pos != -1:
            pdf_url = pdf_url[:pdf_pos + 4]  # Keep up to and including "_pdf"
    
    # If URL manipulation didn't work, fall back to loading page content
    if pdf_url is None:
        response = unified_uri_get(article_url, timeout=request_timeout, max_redirects=max_redirects)
        
        if response.status_code != 200:
            raise NoPDFLink(f'TXERROR: Could not access J-STAGE article page (HTTP {response.status_code})')
        
        # Extract citation_pdf_url from HTML
        pdf_match = re.search(r'<meta\s+name="citation_pdf_url"\s+content="([^"]+)"', response.text)
        if not pdf_match:
            raise NoPDFLink('MISSING: No PDF URL found (URL manipulation failed and no citation_pdf_url)')
        pdf_url = pdf_match.group(1)
    
    # Verify PDF accessibility if requested
    if verify:
        verify_pdf_url(pdf_url, 'J-STAGE', request_timeout=request_timeout, max_redirects=max_redirects)
    
    return pdf_url