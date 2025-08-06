from ...exceptions import *
from .generic import *

from lxml import html
from urllib.parse import urljoin

#TODO: get rid of this horrible try-except jaw
#
# also i'm not convinced this really works

def the_brill_bridge(pma, verify=True):
    '''Brill Academic Publishers: Dutch international academic publisher

    Brill has been publishing since 1683, specializing in humanities, international law,
    social sciences, and biology. Articles are hosted on brill.com and accessible via DOI resolution.

    :param: pma (PubmedArticle)
    :param: verify (bool) [default: True]
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    '''
    try:
        # Check if DOI is available
        if not pma.doi:
            raise NoPDFLink('MISSING: DOI required for Brill journals - attempted: none')

        # Verify DOI pattern for Brill (should start with 10.1163/)
        if not pma.doi.startswith('10.1163/'):
            raise NoPDFLink(f'INVALID: DOI does not match Brill pattern (10.1163/) - attempted: {pma.doi}')

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

                        # Look for PDF download links (Brill typically has direct PDF access)
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
                                   'register', 'institutional', 'purchase this article', 'content access']
                    if any(term in page_text for term in paywall_terms):
                        raise AccessDenied(f'PAYWALL: Brill article requires subscription - attempted: {article_url}')

                    # If no PDF link found, this is an error in verify mode
                    raise NoPDFLink(f'TXERROR: No PDF link found on Brill page - attempted: {article_url}')

                elif response.status_code == 403:
                    raise AccessDenied(f'DENIED: Access forbidden by Brill - attempted: {article_url}')
                elif response.status_code == 404:
                    raise NoPDFLink(f'TXERROR: Brill article not found - attempted: {article_url}')
                else:
                    raise NoPDFLink(f'TXERROR: Brill returned status {response.status_code} - attempted: {article_url}')

            except Exception as e:
                raise NoPDFLink(f'TXERROR: Network error accessing Brill: {e} - attempted: {article_url}')
        else:
            # For Brill, try to construct PDF URL pattern without verification
            # Brill typically uses patterns like /view/journals/... -> /downloadpdf/journals/...
            if 'brill.com' in article_url:
                # Try common Brill PDF patterns
                if '/view/journals/' in article_url:
                    # Pattern: /view/journals/... -> /downloadpdf/journals/...
                    pdf_url = article_url.replace('/view/journals/', '/downloadpdf/journals/')
                    return pdf_url
                elif '/abstract/' in article_url:
                    # Pattern: /abstract/... -> /pdf/...
                    pdf_url = article_url.replace('/abstract/', '/pdf/')
                    return pdf_url
                else:
                    # Try adding /pdf suffix to DOI-based URLs
                    pdf_url = article_url.rstrip('/') + '/pdf'
                    return pdf_url

            # Fallback: return article URL with warning that it's not a PDF
            # This preserves existing behavior while marking the issue
            return article_url  # WARNING: This is an HTML page, not a PDF

    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: Brill bridge failed for {pma.journal}: {e} - attempted: DOI resolution')


