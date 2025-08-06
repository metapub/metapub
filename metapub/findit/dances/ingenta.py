"""Ingenta Connect dance function - REFACTORED.

Follows CLAUDE_PROCESS principles:
- Simple error handling
- Uses generic functions where possible
- Focused try-except blocks
"""

from ...exceptions import *
from .generic import *

from lxml import html
from urllib.parse import urljoin


#TODO: NO. THIS IS BAD.


def the_ingenta_flux(pma, verify=True):
    '''Ingenta Connect: Digital publishing platform hosting multiple publishers

    Ingenta Connect serves as a content aggregator hosting scholarly content from
    over 250 publishers. Journals have diverse DOI prefixes but all resolve through
    ingentaconnect.com platform.

    :param: pma (PubmedArticle)
    :param: verify (bool) [default: True]
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    '''
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for Ingenta Connect journals - attempted: none')

    # Since Ingenta Connect hosts multiple publishers with different DOI prefixes,
    # we don't validate a specific DOI pattern - just ensure DOI exists

    # Resolve DOI to get article URL
    try:
        article_url = the_doi_2step(pma.doi)
    except NoPDFLink as e:
        raise NoPDFLink(f'TXERROR: Ingenta Connect DOI resolution failed: {e}')

    if not verify:
        # For Ingenta Connect, try to construct PDF URL pattern without verification
        # Ingenta typically uses patterns like /content/... -> /contentone/... for PDFs
        if 'ingentaconnect.com' in article_url:
            # Try common Ingenta Connect PDF patterns
            if '/content/' in article_url and '?' not in article_url:
                # Pattern: /content/publisher/journal/... -> /contentone/publisher/journal/.../pdf
                pdf_url = article_url.replace('/content/', '/contentone/').rstrip('/') + '/pdf'
                return pdf_url
            elif '/content/' in article_url:
                # Add ?crawler=true&mimetype=application/pdf for PDF access
                separator = '&' if '?' in article_url else '?'
                pdf_url = article_url + separator + 'crawler=true&mimetype=application/pdf'
                return pdf_url

        # Fallback: return article URL with warning that it's not a PDF
        # This preserves existing behavior while marking the issue
        return article_url  # WARNING: This is an HTML page, not a PDF

    # Verify article accessibility and look for PDF links
    try:
        response = unified_uri_get(article_url, timeout=30)
    except Exception as e:
        raise NoPDFLink(f'TXERROR: Network error accessing Ingenta Connect: {e} - attempted: {article_url}')

    if response.status_code == 403:
        raise AccessDenied(f'DENIED: Access forbidden by Ingenta Connect - attempted: {article_url}')
    elif response.status_code == 404:
        raise NoPDFLink(f'TXERROR: Ingenta Connect article not found - attempted: {article_url}')
    elif response.status_code not in OK_STATUS_CODES:
        raise NoPDFLink(f'TXERROR: Ingenta Connect returned status {response.status_code} - attempted: {article_url}')

    # Check for paywall first
    if detect_paywall_from_html(response.text):
        raise AccessDenied(f'PAYWALL: Ingenta Connect article requires subscription - attempted: {article_url}')

    # Look for PDF download links
    try:
        pdf_url = _extract_ingenta_pdf_link(response, article_url)
        if pdf_url:
            return pdf_url
    except Exception:
        pass  # If PDF extraction fails, continue to error

    # If no PDF link found, this is an error in verify mode
    raise NoPDFLink(f'TXERROR: No PDF link found on Ingenta Connect page - attempted: {article_url}')


def _extract_ingenta_pdf_link(response, base_url):
    """Extract PDF download link from Ingenta Connect article page.

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

    # Look for PDF download links (Ingenta Connect typically has direct PDF access)
    pdf_links = tree.xpath('//a[contains(@href, ".pdf") or contains(text(), "PDF") or contains(@class, "pdf") or contains(@title, "PDF")]/@href')

    if pdf_links:
        pdf_url = pdf_links[0]
        # Convert relative URL to absolute if needed
        if pdf_url.startswith('/'):
            pdf_url = urljoin(base_url, pdf_url)
        return pdf_url

    return None
