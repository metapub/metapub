import re
from .generic import *
from ...exceptions import *


def the_cambridge_foxtrot(pma, verify=True, request_timeout=10, max_redirects=3):
    """Cambridge University Press - extract PDF URL from citation_pdf_url meta tag."""
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for Cambridge journals')
    
    article_url = the_doi_2step(pma.doi)
    response = unified_uri_get(article_url, timeout=request_timeout, max_redirects=max_redirects)
    
    if response.status_code != 200:
        raise NoPDFLink(f'TXERROR: Could not access Cambridge article page (HTTP {response.status_code})')
    
    pdf_match = re.search(r'<meta name="citation_pdf_url"\s+content="([^"]+)"', response.text)
    if not pdf_match:
        raise NoPDFLink('MISSING: No citation_pdf_url found in Cambridge article HTML')
    
    pdf_url = pdf_match.group(1)
    
    if verify:
        verify_pdf_url(pdf_url, 'Cambridge', request_timeout=request_timeout, max_redirects=max_redirects)
    
    return pdf_url


