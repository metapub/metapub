import re
from ...exceptions import NoPDFLink, AccessDenied
from .generic import the_doi_2step, unified_uri_get, verify_pdf_url


def the_scirp_timewarp(pma, verify=True, request_timeout=10, max_redirects=3):
    """SCIRP (Scientific Research Publishing): Open access publisher backup for PMC
    
    SCIRP articles use consistent PDF link patterns in their HTML pages.
    This dance extracts PDF URLs using the reliable <link rel="alternate"> pattern.
    
    :param: pma (PubmedArticle)
    :param: verify (bool) [default: True]
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    """
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for SCIRP journals')

    # Get the article page HTML
    article_url = the_doi_2step(pma.doi)
    response = unified_uri_get(article_url, timeout=request_timeout, max_redirects=max_redirects)
    
    if response.status_code != 200:
        raise NoPDFLink(f'TXERROR: Could not access SCIRP article page (HTTP {response.status_code})')

    # Extract PDF URL using the reliable pattern we discovered
    # SCIRP always puts PDF link in: <link rel="alternate" type="application/pdf" href="...">
    pdf_pattern = r'<link rel="alternate" type="application/pdf"[^>]*href="([^"]+)"'
    match = re.search(pdf_pattern, response.text)
    
    if not match:
        raise NoPDFLink('MISSING: No PDF link found in SCIRP article HTML')
    
    pdf_url = match.group(1)
    
    # Convert protocol-relative URL to https
    if pdf_url.startswith('//'):
        pdf_url = 'https:' + pdf_url
    
    if verify:
        verify_pdf_url(pdf_url, 'SCIRP', referrer=article_url, request_timeout=request_timeout, max_redirects=max_redirects)
    
    return pdf_url



