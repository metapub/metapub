
from ...exceptions import AccessDenied, NoPDFLink
from .generic import *


def the_acm_reel(pma, verify=True):
    '''ACM Digital Library: Computing and information technology publications

    The ACM Digital Library is a comprehensive database of articles, proceedings,
    and other publications from the Association for Computing Machinery (ACM).
    It covers computer science, information technology, and related fields.

    URL Pattern: https://dl.acm.org/doi/[DOI]
    PDF Pattern: https://dl.acm.org/doi/pdf/[DOI]
    DOI Pattern: 10.1145/[ID] (most common ACM DOI pattern)

    :param: pma (PubmedArticle)
    :param: verify (bool) [default: True]
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    '''
    try:
        # Check if DOI is available
        if not pma.doi:
            raise NoPDFLink('MISSING: DOI required for ACM articles - attempted: none')

        # ACM DOIs typically follow pattern 10.1145/...
        if not pma.doi.startswith('10.1145/'):
            raise NoPDFLink(f'PATTERN: DOI does not match ACM pattern (10.1145/) - attempted: {pma.doi}')

        # Try direct PDF URL construction
        pdf_url = f'https://dl.acm.org/doi/pdf/{pma.doi}'

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
                        paywall_terms = ['purchase', 'access denied', 'subscription required',
                                       'sign in', 'log in', 'member access', 'institutional access',
                                       'acm membership', 'subscribe']
                        if any(term in page_text for term in paywall_terms):
                            raise AccessDenied(f'PAYWALL: ACM article requires subscription or membership - attempted: {pdf_url}')

                        # If PDF access fails, this is an error in verify mode
                        raise NoPDFLink(f'TXERROR: No PDF access available for ACM article - attempted: {pdf_url}')

                elif response.status_code == 403:
                    raise AccessDenied(f'DENIED: Access forbidden by ACM - attempted: {pdf_url}')
                elif response.status_code == 404:
                    raise NoPDFLink(f'TXERROR: ACM article not found (404) - attempted: {pdf_url}')
                else:
                    raise NoPDFLink(f'TXERROR: ACM returned status {response.status_code} - attempted: {pdf_url}')

            except (AccessDenied, NoPDFLink):
                # Re-raise our own exceptions without wrapping
                raise
            except Exception as e:
                raise NoPDFLink(f'TXERROR: Network error accessing ACM: {e} - attempted: {pdf_url}')
        else:
            # Return PDF URL without verification
            return pdf_url

    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: ACM reel failed for {pma.journal}: {e} - attempted: DOI resolution')

