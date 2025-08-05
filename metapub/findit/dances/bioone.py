"""BioOne dance function - REFACTORED.

Follows CLAUDE_PROCESS principles:
- Simple error handling
- Uses generic functions where possible
- Focused try-except blocks
"""

from ...exceptions import *
from .generic import *

from lxml import html
from urllib.parse import urljoin


def the_bioone_bounce(pma, verify=True):
    '''BioOne.org: Multi-publisher digital library platform for biological sciences

    BioOne is a multi-publisher digital library platform that aggregates scholarly content
    from biological, ecological, and environmental science publishers. The platform hosts
    journals from ~200+ societies and independent publishers with diverse DOI prefixes
    (10.1643/, 10.1645/, 10.1676/, etc.) but all resolve through complete.bioone.org.

    :param: pma (PubmedArticle)
    :param: verify (bool) [default: True]
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    '''
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for BioOne journals - attempted: none')

    # Since BioOne hosts multiple publishers with different DOI prefixes,
    # we don't validate a specific DOI pattern - just ensure DOI exists

    # Resolve DOI to get article URL
    try:
        article_url = the_doi_2step(pma.doi)
    except NoPDFLink as e:
        raise NoPDFLink(f'TXERROR: BioOne DOI resolution failed: {e}')

    if not verify:
        # For BioOne, try to construct PDF URL pattern without verification
        # BioOne Complete typically uses patterns like /journals/.../articles/... -> /journals/.../pdf/...
        if 'complete.bioone.org' in article_url or 'bioone.org' in article_url:
            # Try common BioOne PDF patterns
            if '/journals/' in article_url and '/articles/' in article_url:
                # Pattern: /journals/.../articles/... -> /journals/.../pdf/...
                pdf_url = article_url.replace('/articles/', '/pdf/')
                return pdf_url
            elif '/articles/' in article_url:
                # Simpler pattern: add /pdf suffix
                pdf_url = article_url.rstrip('/') + '/pdf'
                return pdf_url
        
        # Fallback: return article URL with warning that it's not a PDF
        # This preserves existing behavior while marking the issue
        return article_url  # WARNING: This is an HTML page, not a PDF

    # Verify article accessibility and look for PDF links
    try:
        response = unified_uri_get(article_url, timeout=30)
    except Exception as e:
        raise NoPDFLink(f'TXERROR: Network error accessing BioOne: {e} - attempted: {article_url}')

    if response.status_code == 403:
        raise AccessDenied(f'DENIED: Access forbidden by BioOne - attempted: {article_url}')
    elif response.status_code == 404:
        raise NoPDFLink(f'TXERROR: BioOne article not found - attempted: {article_url}')
    elif response.status_code not in OK_STATUS_CODES:
        raise NoPDFLink(f'TXERROR: BioOne returned status {response.status_code} - attempted: {article_url}')

    # Check for paywall first
    if detect_paywall_from_html(response.text):
        raise AccessDenied(f'PAYWALL: BioOne article requires subscription - attempted: {article_url}')

    # Look for PDF download links
    try:
        pdf_url = _extract_bioone_pdf_link(response, article_url)
        if pdf_url:
            return pdf_url
    except Exception:
        pass  # If PDF extraction fails, continue to error

    # If no PDF link found, this is an error in verify mode
    raise NoPDFLink(f'TXERROR: No PDF link found on BioOne page - attempted: {article_url}')


def _extract_bioone_pdf_link(response, base_url):
    """Extract PDF download link from BioOne article page.
    
    Args:
        response: HTTP response object
        base_url: Base URL for resolving relative links
        
    Returns:
        str: PDF URL if found, None otherwise
    """
    page_text = response.text.lower()
    
    # Look for PDF indicators in the page
    if not ('pdf' in page_text and ('download' in page_text or 'full text' in page_text or 'view pdf' in page_text)):
        return None
        
    # Parse HTML to find PDF links
    tree = html.fromstring(response.content)
    
    # Look for PDF download links (BioOne typically has direct PDF access)
    pdf_links = tree.xpath('//a[contains(@href, ".pdf") or contains(text(), "PDF") or contains(@class, "pdf") or contains(@title, "PDF")]/@href')
    
    if pdf_links:
        pdf_url = pdf_links[0]
        # Convert relative URL to absolute if needed
        if pdf_url.startswith('/'):
            pdf_url = urljoin(base_url, pdf_url)
        return pdf_url
        
    return None