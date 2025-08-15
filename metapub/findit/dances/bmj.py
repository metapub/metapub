"""
BMJ (British Medical Journal) dance function.

Evidence-driven implementation based on HTML samples analysis.
Optimized approach: VIP URL construction first (saves page load), 
with citation_pdf_url meta tag extraction as reliable backup.

Pattern discovered from HTML samples:
- VIP pattern: https://[journal].bmj.com/content/{volume}/{issue}/{first_page}.full.pdf  
- Backup: citation_pdf_url meta tags (100% reliable when VIP fails)
- All DOIs use 10.1136/ prefix
- BMJ has comprehensive journal-to-host mapping available
"""

import re
from .generic import the_doi_2step, verify_pdf_url, unified_uri_get, standardize_journal_name, rectify_pma_for_vip_links
from ...exceptions import NoPDFLink


def the_bmj_bump(pma, verify=True, request_timeout=10, max_redirects=3):
    """
    BMJ dance function - VIP URL construction with meta tag extraction backup.
    
    Optimized two-stage approach:
    1. Try VIP URL construction (faster - no page load needed)
    2. Fall back to citation_pdf_url extraction if VIP fails
    
    :param pma: PubMedArticle object
    :param verify: bool [default: True] - Verify PDF URL accessibility
    :return: PDF URL string
    :raises: NoPDFLink if both methods fail or required data missing
    """
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for BMJ articles')
    
    # Import BMJ journal mappings
    from ..journals.bmj import bmj_journal_params
    
    # Stage 1: Try VIP URL construction (faster)
    try:
        jrnl = standardize_journal_name(pma.journal)
        if jrnl in bmj_journal_params:
            pma_vip = rectify_pma_for_vip_links(pma)  # Validates volume/issue/page
            host = bmj_journal_params[jrnl]['host']
            vip_url = f'https://{host}/content/{pma_vip.volume}/{pma_vip.issue}/{pma_vip.first_page}.full.pdf'
            
            if verify:
                verify_pdf_url(vip_url, 'BMJ', request_timeout=request_timeout, max_redirects=max_redirects)
            return vip_url
            
    except (NoPDFLink, KeyError):
        # VIP construction failed - fall back to meta tag extraction
        pass
    
    # Stage 2: Meta tag extraction backup (more reliable but requires page load)
    article_url = the_doi_2step(pma.doi)
    response = unified_uri_get(article_url, timeout=request_timeout, max_redirects=max_redirects)
    
    if response.status_code != 200:
        raise NoPDFLink(f'TXERROR: Could not access BMJ article page (HTTP {response.status_code})')
    
    pdf_match = re.search(r'<meta name="citation_pdf_url"\s+content="([^"]+)"', response.text)
    if not pdf_match:
        raise NoPDFLink('MISSING: No PDF URL found via VIP construction or meta tag extraction')
    
    pdf_url = pdf_match.group(1)
    
    if verify:
        verify_pdf_url(pdf_url, 'BMJ', request_timeout=request_timeout, max_redirects=max_redirects)
    
    return pdf_url