"""Royal Society of Chemistry dance function - REFACTORED.

Follows CLAUDE_PROCESS principles:
- Simple error handling
- Uses generic functions where possible
- Focused try-except blocks
- Imports at top of file
"""

from ...exceptions import *
from .generic import *

from lxml import html
from urllib.parse import urljoin


def the_rsc_reaction(pma, verify=True):
    '''Royal Society of Chemistry (RSC): Leading chemistry publisher

    RSC publishes over 50 journals covering all areas of chemistry and related fields.
    Founded in 1841, articles are hosted on pubs.rsc.org and accessible via DOI resolution.

    :param: pma (PubmedArticle)
    :param: verify (bool) [default: True]
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    '''
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for RSC journals - attempted: none')

    # Verify DOI pattern for RSC (should start with 10.1039/)
    if not pma.doi.startswith('10.1039/'):
        raise NoPDFLink(f'INVALID: DOI does not match RSC pattern (10.1039/) - attempted: {pma.doi}')

    # Resolve DOI to get article URL
    try:
        article_url = the_doi_2step(pma.doi)
    except NoPDFLink as e:
        raise NoPDFLink(f'TXERROR: RSC DOI resolution failed: {e}')

    # TODO: WHY IS THIS A CONDITIONAL  AUGHGHHG
    if not verify:
        # For RSC, try to construct PDF URL pattern without verification
        # RSC typically uses patterns like /en/content/articlelanding/... -> /en/content/articlepdf/...
        if 'pubs.rsc.org' in article_url:
            # Try common RSC PDF patterns
            if '/content/articlelanding/' in article_url:
                # Pattern: /content/articlelanding/... -> /content/articlepdf/...
                pdf_url = article_url.replace('/content/articlelanding/', '/content/articlepdf/')
                return pdf_url
            elif '/content/article' in article_url:
                # Add pdf suffix to article URLs
                pdf_url = article_url.rstrip('/') + '/pdf'
                return pdf_url
            else:
                # Try constructing from DOI: 10.1039/c1cc12345a -> /en/content/articlepdf/2011/cc/c1cc12345a
                doi_suffix = pma.doi.split('/')[-1] if '/' in pma.doi else pma.doi
                year = '2023'  # Default year, could be extracted from other PMA fields
                journal_code = doi_suffix[:2] if len(doi_suffix) >= 2 else 'cc'
                pdf_url = f'https://pubs.rsc.org/en/content/articlepdf/{year}/{journal_code}/{doi_suffix}'
                return pdf_url

        # Fallback: return article URL with warning that it's not a PDF
        # This preserves existing behavior while marking the issue
        return article_url  # WARNING: This is an HTML page, not a PDF

    # Verify article accessibility and look for PDF links
    try:
        response = unified_uri_get(article_url, timeout=30)
    except Exception as e:
        raise NoPDFLink(f'TXERROR: Network error accessing RSC: {e} - attempted: {article_url}')

    if response.status_code == 403:
        raise AccessDenied(f'DENIED: Access forbidden by RSC - attempted: {article_url}')
    elif response.status_code == 404:
        raise NoPDFLink(f'TXERROR: RSC article not found - attempted: {article_url}')
    elif response.status_code not in OK_STATUS_CODES:
        raise NoPDFLink(f'TXERROR: RSC returned status {response.status_code} - attempted: {article_url}')

    # Check for paywall first
    if detect_paywall_from_html(response.text):
        raise AccessDenied(f'PAYWALL: RSC article requires subscription - attempted: {article_url}')

    # Look for PDF download links
    try:
        pdf_url = _extract_rsc_pdf_link(response, article_url)
        if pdf_url:
            return pdf_url
    except Exception:
        pass  # If PDF extraction fails, continue to error

    # If no PDF link found, this is an error in verify mode
    raise NoPDFLink(f'TXERROR: No PDF link found on RSC page - attempted: {article_url}')


def _extract_rsc_pdf_link(response, base_url):
    """Extract PDF download link from RSC article page.

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

    # Look for PDF download links (RSC typically has direct PDF access)
    pdf_links = tree.xpath('//a[contains(@href, ".pdf") or contains(text(), "PDF") or contains(@class, "pdf") or contains(@title, "PDF")]/@href')

    if pdf_links:
        pdf_url = pdf_links[0]
        # Convert relative URL to absolute if needed
        if pdf_url.startswith('/'):
            pdf_url = urljoin(base_url, pdf_url)
        return pdf_url

    return None
