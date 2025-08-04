from ...exceptions import *
from .generic import *

def the_eureka_frug(pma, verify=True):
    '''Dance function for Bentham Science Publishers (EurekaSelect.com) journals.

    Bentham Science journals use DOI-based URLs but are typically behind a paywall.
    This dance attempts multiple strategies to access PDFs:
    1. Direct DOI resolution to publisher's site
    2. Alternative URL patterns observed on eurekaselect.com

    :param: pma (PubMedArticle object)
    :param: verify (bool) [default: True]
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    '''
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for Bentham Science journals - attempted: none')

    try:
        # First approach: Resolve DOI and try common PDF patterns
        resolved_url = the_doi_2step(pma.doi)

        # Strategy 1: Try appending '/pdf' to resolved URL
        pdf_url = f"{resolved_url}/pdf"

        if verify:
            try:
                response = requests.get(pdf_url, timeout=10)

                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '').lower()
                    if 'pdf' in content_type:
                        return response.url
                    elif 'html' in content_type:
                        # Check for paywall indicators
                        page_text = response.text.lower()
                        paywall_terms = ['paywall', 'subscribe', 'sign in', 'log in', 'purchase', 'access denied', 'checkLicense']
                        if any(term in page_text for term in paywall_terms):
                            raise AccessDenied(f'PAYWALL: Bentham Science article requires subscription - attempted: {pdf_url}')
                        else:
                            raise NoPDFLink(f'TXERROR: Bentham returned HTML instead of PDF - attempted: {pdf_url}')
                    else:
                        raise NoPDFLink(f'TXERROR: Unexpected content type {content_type} from Bentham - attempted: {pdf_url}')

                elif response.status_code == 403:
                    raise AccessDenied(f'DENIED: Access forbidden by Bentham Science - attempted: {pdf_url}')
                elif response.status_code == 404:
                    # Try alternative URL pattern
                    pass
                else:
                    raise NoPDFLink(f'TXERROR: Bentham returned status {response.status_code} - attempted: {pdf_url}')

            except requests.exceptions.RequestException as e:
                raise NoPDFLink(f'TXERROR: Network error accessing Bentham: {e} - attempted: {pdf_url}')
        else:
            return pdf_url

        # Strategy 2: Try alternative openurl pattern
        # Based on investigation, some publishers use openurl.php for access
        openurl = f"https://www.eurekaselect.com/openurl/openurl.php?genre=article&doi={pma.doi}"

        if verify:
            try:
                response = requests.get(openurl, timeout=10)

                if response.status_code == 200 and 'pdf' in response.headers.get('content-type', '').lower():
                    return response.url
                else:
                    raise AccessDenied(f'PAYWALL: Bentham Science requires subscription for full access - attempted: {openurl}')

            except requests.exceptions.RequestException:
                pass
        else:
            return openurl

        # If we get here, all strategies failed
        raise AccessDenied(f'PAYWALL: Bentham Science journal appears to be subscription-only - attempted: {pdf_url}, {openurl}')

    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: Eureka frug failed for {pma.journal}: {e} - attempted: DOI resolution')

