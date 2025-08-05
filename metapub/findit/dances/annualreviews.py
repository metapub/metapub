
from ...exceptions import AccessDenied, NoPDFLink
from .generic import OK_STATUS_CODES, the_doi_2step, unified_uri_get

from lxml import html
from urllib.parse import urljoin

def the_annualreviews_round(pma, verify=True):
    '''Annual Reviews Inc.: Nonprofit publisher of comprehensive review articles

    Annual Reviews articles are hosted on annualreviews.org and typically accessible via DOI resolution.
    Founded in 1932, publishes review articles across various scientific disciplines.

    :param: pma (PubmedArticle)
    :param: verify (bool) [default: True]
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    '''
    try:
        # Check if DOI is available
        if not pma.doi:
            raise NoPDFLink('MISSING: DOI required for Annual Reviews journals - attempted: none')

        # Verify DOI pattern for Annual Reviews
        if not pma.doi.startswith('10.1146/'):
            raise NoPDFLink(f'INVALID: DOI does not match Annual Reviews pattern (10.1146/) - attempted: {pma.doi}')

        # Resolve DOI to get article URL
        article_url = the_doi_2step(pma.doi)

        if verify:
            try:
                response = unified_uri_get(article_url, timeout=30)

                if response.status_code in OK_STATUS_CODES:
                    page_text = response.text.lower()

                    # Look for PDF download links or indicators
                    if 'pdf' in page_text and ('download' in page_text or 'full text' in page_text or 'view pdf' in page_text):
                        # Try to find PDF link in the page
                        tree = html.fromstring(response.content)

                        # Look for PDF download links (Annual Reviews typically has direct PDF links)
                        pdf_links = tree.xpath('//a[contains(@href, ".pdf") or contains(text(), "PDF") or contains(@class, "pdf") or contains(@title, "PDF")]/@href')

                        if pdf_links:
                            pdf_url = pdf_links[0]
                            # Convert relative URL to absolute if needed
                            if pdf_url.startswith('/'):
                                pdf_url = urljoin(article_url, pdf_url)
                            return pdf_url

                    # Check for paywall/subscription indicators
                    paywall_terms = ['subscribe', 'sign in', 'log in', 'institutional access',
                                   'purchase', 'access denied', 'login required', 'subscription required',
                                   'register', 'institutional', 'purchase this article']
                    if any(term in page_text for term in paywall_terms):
                        raise AccessDenied(f'PAYWALL: Annual Reviews article requires subscription - attempted: {article_url}')

                    # If no PDF link found, this is an error in verify mode
                    raise NoPDFLink(f'TXERROR: No PDF link found on Annual Reviews page - attempted: {article_url}')

                elif response.status_code == 403:
                    raise AccessDenied(f'DENIED: Access forbidden by Annual Reviews - attempted: {article_url}')
                elif response.status_code == 404:
                    raise NoPDFLink(f'TXERROR: Annual Reviews article not found - attempted: {article_url}')
                else:
                    raise NoPDFLink(f'TXERROR: Annual Reviews returned status {response.status_code} - attempted: {article_url}')

            except Exception as e:
                raise NoPDFLink(f'TXERROR: Network error accessing Annual Reviews: {e} - attempted: {article_url}')
        else:
            # For Annual Reviews, try to construct PDF URL pattern without verification
            # Annual Reviews typically uses patterns like /doi/10.1146/... -> /doi/pdf/10.1146/...
            if 'annualreviews.org' in article_url:
                # Try common Annual Reviews PDF patterns
                if '/doi/' in article_url:
                    # Pattern: /doi/10.1146/... -> /doi/pdf/10.1146/...
                    pdf_url = article_url.replace('/doi/', '/doi/pdf/')
                    return pdf_url
                elif '/abs/' in article_url:
                    # Pattern: /abs/10.1146/... -> /pdf/10.1146/...
                    pdf_url = article_url.replace('/abs/', '/pdf/')
                    return pdf_url
            
            # Fallback: return article URL with warning that it's not a PDF
            # This preserves existing behavior while marking the issue
            return article_url  # WARNING: This is an HTML page, not a PDF

    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: Annual Reviews round failed for {pma.journal}: {e} - attempted: DOI resolution')

