from ...exceptions import *
from .generic import *


#TODO: get rid of this dumb try-except jaw

# also make sure this actually gets a PDF!



def the_worldscientific_robot(pma, verify=True):
    '''World Scientific Publishing: Scientific, technical, and medical content

    World Scientific Publishing is a major academic publisher for scientific,
    technical, and medical content. It publishes journals, books, and conference
    proceedings in various fields including physics, mathematics, computer science,
    engineering, chemistry, and life sciences.

    URL Pattern: https://www.worldscientific.com/doi/[DOI]
    PDF Pattern: https://www.worldscientific.com/doi/pdf/[DOI]
    DOI Pattern: 10.1142/[ID] (World Scientific DOI pattern)

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
            raise NoPDFLink(f'MISSING: DOI required for World Scientific access - journal: {pma.journal}')

        # Construct PDF URL
        pdf_url = f'https://www.worldscientific.com/doi/pdf/{pma.doi}'

        if verify:
            try:
                response = requests.get(pdf_url, timeout=10, allow_redirects=True)

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
                                       'subscribe now', 'buy article', 'rental']
                        if any(term in page_text for term in paywall_terms):
                            raise AccessDenied(f'PAYWALL: World Scientific article requires subscription - attempted: {pdf_url}')

                        # Try article HTML page instead
                        article_url = f'https://www.worldscientific.com/doi/{pma.doi}'
                        return article_url

                elif response.status_code == 403:
                    raise AccessDenied(f'DENIED: Access forbidden by World Scientific - attempted: {pdf_url}')
                elif response.status_code == 404:
                    raise NoPDFLink(f'TXERROR: World Scientific article not found (404) - attempted: {pdf_url}')
                else:
                    raise NoPDFLink(f'TXERROR: World Scientific returned status {response.status_code} - attempted: {pdf_url}')

            except requests.exceptions.RequestException as e:
                raise NoPDFLink(f'TXERROR: Network error accessing World Scientific: {e} - attempted: {pdf_url}')
        else:
            # Return PDF URL without verification
            return pdf_url

    except Exception as e:
        #this is such junior code organization lol, good job Claude
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: World Scientific robot failed for {pma.journal}: {e} - attempted: DOI resolution')

