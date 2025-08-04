from ...exceptions import *
from .generic import *


def the_emerald_ceili(pma, verify=True):
    '''Emerald Publishing: Business, management, education, library science journals

    Emerald Publishing is a digital-first publisher of management, business, education,
    library science, information management research, and health care journals.
    Founded in 1967, it publishes over 300 journals and more than 2,500 books.

    URL Pattern: https://www.emerald.com/insight/content/doi/[DOI]/full/html
    PDF Pattern: https://www.emerald.com/insight/content/doi/[DOI]/full/pdf
    DOI Pattern: 10.1108/[JOURNAL_CODE]-[DATE]-[ID]

    :param: pma (PubmedArticle)
    :param: verify (bool) [default: True]
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    '''
    try:
        # Check if DOI is available
        if not pma.doi:
            raise NoPDFLink('MISSING: DOI required for Emerald journals - attempted: none')

        # Emerald DOIs typically follow pattern 10.1108/...
        if not pma.doi.startswith('10.1108/'):
            raise NoPDFLink(f'PATTERN: DOI does not match Emerald pattern (10.1108/) - attempted: {pma.doi}')

        # Try direct PDF URL construction
        pdf_url = f'https://www.emerald.com/insight/content/doi/{pma.doi}/full/pdf'

        if verify:
            try:
                response = unified_uri_get(pdf_url, timeout=30)

                if response.status_code in OK_STATUS_CODES:
                    # Check if this is actually a PDF
                    content_type = response.headers.get('content-type', '').lower()
                    if 'pdf' in content_type:
                        return pdf_url
                    else:
                        # Might be HTML page, check for subscription/paywall indicators
                        page_text = response.text.lower()
                        paywall_terms = ['subscribe', 'sign in', 'log in', 'institutional access',
                                       'purchase', 'access denied', 'login required', 'subscription required',
                                       'register', 'institutional', 'purchase this article', 'member access']
                        if any(term in page_text for term in paywall_terms):
                            raise AccessDenied(f'PAYWALL: Emerald article requires subscription - attempted: {pdf_url}')

                        # Try article HTML page instead
                        article_url = f'https://www.emerald.com/insight/content/doi/{pma.doi}/full/html'
                        return article_url

                elif response.status_code == 403:
                    raise AccessDenied(f'DENIED: Access forbidden by Emerald - attempted: {pdf_url}')
                elif response.status_code == 404:
                    raise NoPDFLink(f'TXERROR: Emerald article not found (404) - attempted: {pdf_url}')
                else:
                    raise NoPDFLink(f'TXERROR: Emerald returned status {response.status_code} - attempted: {pdf_url}')

            except Exception as e:
                raise NoPDFLink(f'TXERROR: Network error accessing Emerald: {e} - attempted: {pdf_url}')
        else:
            # Return PDF URL without verification
            return pdf_url

    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: Emerald ceili failed for {pma.journal}: {e} - attempted: DOI resolution')

