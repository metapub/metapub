from ...exceptions import *
from .generic import *


#TODO: get rid of this dumb try-except jaw

# also i'm not convinced any of this works


def the_uchicago_walk(pma, verify=True):
    '''University of Chicago Press: Academic journals across multiple disciplines

    The University of Chicago Press is one of the largest and oldest university presses
    in the United States. It publishes academic journals, books, and scholarly content
    across various disciplines including humanities, social sciences, education,
    biological sciences, and physical sciences.

    URL Pattern: https://www.journals.uchicago.edu/doi/[DOI]
    PDF Pattern: https://www.journals.uchicago.edu/doi/pdf/[DOI]
    DOI Pattern: 10.1086/[ID] (University of Chicago Press DOI pattern)

    Args:
        pma: PubMedArticle instance with DOI
        verify: Whether to verify PDF accessibility (default: True)

    Returns:
        PDF URL string if accessible

    Raises:
        NoPDFLink: If no DOI, wrong DOI pattern, or technical issues
        AccessDenied: If paywall detected
    '''
    try:
        # Check for required DOI
        if not pma.doi:
            raise NoPDFLink(f'MISSING: DOI required for University of Chicago Press access - journal: {pma.journal}')

        # Construct PDF URL
        pdf_url = f'https://www.journals.uchicago.edu/doi/pdf/{pma.doi}'

        if verify:
            try:
                response = unified_uri_get(pdf_url, timeout=10, allow_redirects=True)

                if response.ok:
                    # Check if we got actual PDF content
                    content_type = response.headers.get('content-type', '').lower()
                    if 'application/pdf' in content_type:
                        return pdf_url
                    elif 'text/html' in content_type:
                        # Check for paywall indicators in HTML response
                        page_text = response.text.lower()
                        paywall_terms = ['purchase', 'access denied', 'subscription required',
                                       'sign in', 'log in', 'member access', 'institutional access',
                                       'subscribe now', 'buy article', 'rent this article']
                        if any(term in page_text for term in paywall_terms):
                            raise AccessDenied(f'PAYWALL: University of Chicago Press article requires subscription - attempted: {pdf_url}')

                        # Try article HTML page instead
                        article_url = f'https://www.journals.uchicago.edu/doi/{pma.doi}'
                        return article_url

                elif response.status_code == 403:
                    raise AccessDenied(f'DENIED: Access forbidden by University of Chicago Press - attempted: {pdf_url}')
                elif response.status_code == 404:
                    raise NoPDFLink(f'TXERROR: University of Chicago Press article not found (404) - attempted: {pdf_url}')
                else:
                    raise NoPDFLink(f'TXERROR: University of Chicago Press returned status {response.status_code} - attempted: {pdf_url}')

            except Exception as e:
                raise NoPDFLink(f'TXERROR: Network error accessing University of Chicago Press: {e} - attempted: {pdf_url}')
        else:
            # Return PDF URL without verification
            return pdf_url

    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: University of Chicago Press walk failed for {pma.journal}: {e} - attempted: DOI resolution')


