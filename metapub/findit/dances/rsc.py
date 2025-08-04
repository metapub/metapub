from ...exceptions import *
from .generic import *

# TODO: get rid of this awful try-except jaw
#
# move in-function imports to top

def the_rsc_reaction(pma, verify=True):
    '''Royal Society of Chemistry (RSC): Leading chemistry publisher

    RSC publishes over 50 journals covering all areas of chemistry and related fields.
    Founded in 1841, articles are hosted on pubs.rsc.org and accessible via DOI resolution.

    :param: pma (PubmedArticle)
    :param: verify (bool) [default: True]
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    '''
    try:
        # Check if DOI is available
        if not pma.doi:
            raise NoPDFLink('MISSING: DOI required for RSC journals - attempted: none')

        # Verify DOI pattern for RSC (should start with 10.1039/)
        if not pma.doi.startswith('10.1039/'):
            raise NoPDFLink(f'INVALID: DOI does not match RSC pattern (10.1039/) - attempted: {pma.doi}')

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
                        from lxml import html
                        tree = html.fromstring(response.content)

                        # Look for PDF download links (RSC typically has direct PDF access)
                        pdf_links = tree.xpath('//a[contains(@href, ".pdf") or contains(text(), "PDF") or contains(@class, "pdf") or contains(@title, "PDF")]/@href')

                        if pdf_links:
                            pdf_url = pdf_links[0]
                            # Convert relative URL to absolute if needed
                            if pdf_url.startswith('/'):
                                from urllib.parse import urljoin
                                pdf_url = urljoin(article_url, pdf_url)
                            return pdf_url

                    # Check for paywall/subscription indicators
                    paywall_terms = ['subscribe', 'sign in', 'log in', 'institutional access',
                                   'purchase', 'access denied', 'login required', 'subscription required',
                                   'register', 'institutional', 'purchase this article', 'member access']
                    if any(term in page_text for term in paywall_terms):
                        raise AccessDenied(f'PAYWALL: RSC article requires subscription - attempted: {article_url}')

                    # If no PDF link found but page accessible, return article URL
                    return article_url

                elif response.status_code == 403:
                    raise AccessDenied(f'DENIED: Access forbidden by RSC - attempted: {article_url}')
                elif response.status_code == 404:
                    raise NoPDFLink(f'TXERROR: RSC article not found - attempted: {article_url}')
                else:
                    raise NoPDFLink(f'TXERROR: RSC returned status {response.status_code} - attempted: {article_url}')

            except Exception as e:
                raise NoPDFLink(f'TXERROR: Network error accessing RSC: {e} - attempted: {article_url}')
        else:
            # Return DOI-resolved URL without verification
            return article_url

    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: RSC reaction failed for {pma.journal}: {e} - attempted: DOI resolution')

