from ...exceptions import *
from .generic import *

def the_thieme_tap(pma, verify=True):
    '''Dance function for Thieme Medical Publishers journals.

    Thieme journals use a straightforward DOI-based PDF URL pattern.
    URL Pattern: https://www.thieme-connect.de/products/ejournals/pdf/{doi}.pdf

    Thieme uses 10.1055 as their DOI prefix and provides direct PDF access
    through their thieme-connect.de platform.

    :param: pma (PubMedArticle object)
    :param: verify (bool) [default: True]
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    '''
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for Thieme journals - attempted: none')

    try:
        # Construct PDF URL using Thieme's pattern
        pdf_url = f"https://www.thieme-connect.de/products/ejournals/pdf/{pma.doi}.pdf"

        if verify:
            try:
                response = unified_uri_get(pdf_url, timeout=10)

                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '').lower()
                    if 'pdf' in content_type:
                        return response.url
                    elif 'html' in content_type:
                        # Check for paywall indicators
                        page_text = response.text.lower()
                        paywall_terms = ['paywall', 'subscribe', 'sign in', 'log in', 'purchase', 'access denied', 'login required']
                        if any(term in page_text for term in paywall_terms):
                            raise AccessDenied(f'PAYWALL: Thieme article requires subscription - attempted: {pdf_url}')
                        else:
                            raise NoPDFLink(f'TXERROR: Thieme returned HTML instead of PDF - attempted: {pdf_url}')
                    else:
                        raise NoPDFLink(f'TXERROR: Unexpected content type {content_type} from Thieme - attempted: {pdf_url}')

                elif response.status_code == 403:
                    raise AccessDenied(f'DENIED: Access forbidden by Thieme - attempted: {pdf_url}')
                elif response.status_code == 404:
                    raise NoPDFLink(f'TXERROR: Thieme PDF not found - attempted: {pdf_url}')
                else:
                    raise NoPDFLink(f'TXERROR: Thieme returned status {response.status_code} - attempted: {pdf_url}')

            except Exception as e:
                raise NoPDFLink(f'TXERROR: Network error accessing Thieme: {e} - attempted: {pdf_url}')
        else:
            return pdf_url

    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: Thieme tap failed for {pma.journal}: {e} - attempted: DOI-based PDF URL')

