from ...exceptions import *
from .generic import *


#TODO: get rid of this dumb try-except jaw


def the_iospress_freestyle(pma, verify=True):
    '''IOS Press: Scientific and technical books and journals

    IOS Press is an international publisher of scientific and technical books and journals
    based in Amsterdam, Netherlands. It specializes in computer science, artificial intelligence,
    biomedical sciences, health technologies, and other technical disciplines.

    URL Pattern: https://content.iospress.com/articles/[journal]/[DOI]
    PDF Pattern: https://content.iospress.com/download/[journal]/[DOI]
    DOI Pattern: 10.3233/[JOURNAL]-[ID] (IOS Press DOI pattern)

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
            raise NoPDFLink(f'MISSING: DOI required for IOS Press access - journal: {pma.journal}')

        # Verify DOI pattern (most IOS Press DOIs start with 10.3233)
        if not pma.doi.startswith('10.3233/'):
            raise NoPDFLink(f'PATTERN: Expected IOS Press DOI (10.3233/...), got: {pma.doi} - journal: {pma.journal}')

        # Extract journal code from DOI for URL construction
        # DOI format: 10.3233/JAD-240123 -> journal code is JAD
        doi_parts = pma.doi.split('/')
        if len(doi_parts) < 2:
            raise NoPDFLink(f'PATTERN: Invalid DOI format for IOS Press: {pma.doi} - journal: {pma.journal}')

        journal_and_id = doi_parts[1]  # e.g., "JAD-240123"
        if '-' not in journal_and_id:
            raise NoPDFLink(f'PATTERN: Expected IOS Press DOI with journal-ID format, got: {pma.doi} - journal: {pma.journal}')

        journal_code = journal_and_id.split('-')[0].lower()  # e.g., "jad"

        # Construct PDF URL
        pdf_url = f'https://content.iospress.com/download/{journal_code}/{pma.doi}'

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
                                       'subscribe now', 'buy article', 'login required']
                        if any(term in page_text for term in paywall_terms):
                            raise AccessDenied(f'PAYWALL: IOS Press article requires subscription - attempted: {pdf_url}')

                        # Try article HTML page instead
                        #TODO: learn how to construct a real PDF link without loading the page.
                        article_url = f'https://content.iospress.com/articles/{journal_code}/{pma.doi}'
                        return article_url

                elif response.status_code == 403:
                    raise AccessDenied(f'DENIED: Access forbidden by IOS Press - attempted: {pdf_url}')
                elif response.status_code == 404:
                    raise NoPDFLink(f'TXERROR: IOS Press article not found (404) - attempted: {pdf_url}')
                else:
                    raise NoPDFLink(f'TXERROR: IOS Press returned status {response.status_code} - attempted: {pdf_url}')

            except Exception as e:
                raise NoPDFLink(f'TXERROR: Network error accessing IOS Press: {e} - attempted: {pdf_url}')
        else:
            # Return PDF URL without verification
            return pdf_url

    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: IOS Press freestyle failed for {pma.journal}: {e} - attempted: DOI resolution')

