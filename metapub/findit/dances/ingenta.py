from ...exceptions import *
from .generic import *

from lxml import html
from urllib.parse import urljoin


#TODO: get rid of this dumb try-except jaw

# also i'm not convinced any of this works


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
    try:
        # Check if DOI is available
        if not pma.doi:
            raise NoPDFLink('MISSING: DOI required for Ingenta Connect journals - attempted: none')

        # Since Ingenta Connect hosts multiple publishers with different DOI prefixes,
        # we don't validate a specific DOI pattern - just ensure DOI exists

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

                        # Look for PDF download links (Ingenta Connect typically has direct PDF access)
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
                                   'register', 'institutional', 'purchase this article', 'pay per view']
                    if any(term in page_text for term in paywall_terms):
                        raise AccessDenied(f'PAYWALL: Ingenta Connect article requires subscription - attempted: {article_url}')

                    # If no PDF link found but page accessible, return article URL
                    return article_url

                elif response.status_code == 403:
                    raise AccessDenied(f'DENIED: Access forbidden by Ingenta Connect - attempted: {article_url}')
                elif response.status_code == 404:
                    raise NoPDFLink(f'TXERROR: Ingenta Connect article not found - attempted: {article_url}')
                else:
                    raise NoPDFLink(f'TXERROR: Ingenta Connect returned status {response.status_code} - attempted: {article_url}')

            except Exception as e:
                raise NoPDFLink(f'TXERROR: Network error accessing Ingenta Connect: {e} - attempted: {article_url}')
        else:
            # Return DOI-resolved URL without verification
            return article_url

    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: Ingenta flux failed for {pma.journal}: {e} - attempted: DOI resolution')

