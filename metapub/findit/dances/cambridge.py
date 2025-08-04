from .generic import *
from ...exceptions import *


def the_cambridge_foxtrot(pma, verify=True):
    '''Cambridge University Press dance for modern cambridge.org hosting.

    Cambridge University Press moved to a DOI-based system where all articles
    are accessible via cambridge.org/core. The PDF access pattern uses:
    https://www.cambridge.org/core/services/aop-pdf-file/content/view/{DOI}

    Cambridge publishes journals with various DOI prefixes due to acquisitions.

    :param: pma (PubMedArticle object)
    :param: verify (bool) [default: True]
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    '''
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for Cambridge University Press journals - attempted: none')

    # Cambridge uses DOI-based URLs on their unified platform
    pdf_url = f'https://www.cambridge.org/core/services/aop-pdf-file/content/view/{pma.doi}'

    if not verify:
        return pdf_url

    # Verify the PDF URL works
    try:
        response = requests.get(pdf_url, timeout=10)

        if response.status_code == 200:
            content_type = response.headers.get('content-type', '').lower()
            if 'pdf' in content_type:
                return response.url
            elif 'html' in content_type:
                # Check if we hit a paywall or access denied page
                page_text = response.text.lower()
                if any(term in page_text for term in ['access denied', 'paywall', 'subscribe', 'log in', 'sign in', 'institutional access']):
                    raise AccessDenied(f'PAYWALL: Cambridge article requires subscription - attempted: {pdf_url}')
                else:
                    raise NoPDFLink(f'TXERROR: Cambridge returned HTML instead of PDF - attempted: {pdf_url}')
            else:
                raise NoPDFLink(f'TXERROR: Unexpected content type {content_type} from Cambridge - attempted: {pdf_url}')

        elif response.status_code == 403:
            raise AccessDenied(f'DENIED: Access forbidden by Cambridge - attempted: {pdf_url}')
        elif response.status_code == 404:
            raise NoPDFLink(f'NOTFOUND: Article not found on Cambridge platform - attempted: {pdf_url}')
        else:
            raise NoPDFLink(f'TXERROR: Cambridge returned status {response.status_code} - attempted: {pdf_url}')

    except requests.exceptions.RequestException as e:
        raise NoPDFLink(f'TXERROR: Network error accessing Cambridge: {e} - attempted: {pdf_url}')


