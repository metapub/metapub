from .generic import *
from ...exceptions import *


def the_sage_hula(pma, verify=True):
    '''SAGE Publications dance for modern journals.sagepub.com hosting.

    SAGE moved to a unified hosting platform using DOI-based URLs:
    https://journals.sagepub.com/doi/{DOI}

    For PDF access, we convert to:
    https://journals.sagepub.com/doi/pdf/{DOI}

    :param: pma (PubMedArticle object)
    :param: verify (bool) [default: True]
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    '''
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for SAGE journals - attempted: none')

    # SAGE uses DOI-based URLs on their unified platform
    pdf_url = f'https://journals.sagepub.com/doi/pdf/{pma.doi}'

    if not verify:
        return pdf_url

    # Verify the PDF URL works
    try:
        response = unified_uri_get(pdf_url, timeout=10)

        if response.status_code == 200:
            content_type = response.headers.get('content-type', '').lower()
            if 'pdf' in content_type:
                return response.url
            elif 'html' in content_type:
                # Check if we hit a paywall or access denied page
                page_text = response.text.lower()
                if any(term in page_text for term in ['access denied', 'paywall', 'subscribe', 'log in', 'sign in']):
                    raise AccessDenied('PAYWALL: SAGE article requires subscription')
                else:
                    raise NoPDFLink(f'TXERROR: SAGE returned HTML instead of PDF for {pdf_url}')
            else:
                raise NoPDFLink(f'TXERROR: Unexpected content type {content_type} from SAGE')

        elif response.status_code == 403:
            raise AccessDenied('DENIED: Access forbidden by SAGE')
        elif response.status_code == 404:
            raise NoPDFLink('NOTFOUND: Article not found on SAGE platform')
        else:
            raise NoPDFLink(f'TXERROR: SAGE returned status {response.status_code} for {pdf_url}')

    except Exception as e:
        raise NoPDFLink(f'TXERROR: Network error accessing SAGE: {e} - attempted: {pdf_url}')



