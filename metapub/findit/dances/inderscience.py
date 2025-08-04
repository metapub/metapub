from ...exceptions import *
from .generic import *

from ..journals.inderscience import inderscience_format

 #TODO: get rid of this dumb try-except jaw

 # also i'm not convinced any of this works


# ALSO THIS IS JUST BAD CODE -- we shouldn't be trying different "possible URL"s, we'll get banned.
# and it's just bad code overall, Claude.  huge try-except blocks containing long if-then blocks
# are really bad form.  :(



def the_inderscience_ula(pma, verify=True):
    """Inderscience Publishers dance function.

    Inderscience Publishers is an independent academic publisher specializing
    in engineering, technology, science, and management journals. Most of their
    journals follow "International Journal of..." naming pattern.

    Args:
        pma: PubMedArticle object
        verify: Whether to verify PDF access

    Returns:
        PDF URL if accessible

    Raises:
        NoPDFLink: If DOI missing or PDF not accessible
        AccessDenied: If paywall detected
    """

    try:
        if not pma.doi:
            raise NoPDFLink('MISSING: DOI required for Inderscience article access')

        # Inderscience typically uses 10.1504/* DOI pattern
        if not pma.doi.startswith('10.1504/'):
            # Still try to process, but note pattern mismatch
            pass

        # Try different URL construction approaches
        possible_urls = [
            f'https://www.inderscienceonline.com/doi/pdf/{pma.doi}',
            f'https://www.inderscienceonline.com/doi/{pma.doi}',
            f'https://inderscienceonline.com/doi/pdf/{pma.doi}',
            f'https://inderscienceonline.com/doi/{pma.doi}'
        ]

        if verify:
            for pdf_url in possible_urls:
                try:
                    response = requests.get(pdf_url, timeout=10, allow_redirects=True)

                    if response.ok:
                        # Check content type
                        content_type = response.headers.get('content-type', '').lower()
                        if 'application/pdf' in content_type:
                            return pdf_url
                        elif 'text/html' in content_type:
                            # Check for paywall indicators
                            page_text = response.text.lower()
                            paywall_indicators = [
                                'subscribe', 'subscription', 'login required',
                                'access denied', 'purchase', 'institutional access',
                                'sign in', 'member only'
                            ]
                            if any(indicator in page_text for indicator in paywall_indicators):
                                raise AccessDenied(f'PAYWALL: Inderscience article requires subscription - {pdf_url}')
                            else:
                                # Might be article page, return it
                                return pdf_url
                    elif response.status_code == 404:
                        continue  # Try next URL format
                    else:
                        continue  # Try next URL format

                except requests.exceptions.RequestException:
                    continue  # Try next URL format

            # If all URLs failed
            if pma.doi.startswith('10.1504/'):
                raise NoPDFLink(f'TXERROR: Could not access Inderscience article - DOI: {pma.doi}')
            else:
                raise NoPDFLink(f'PATTERN: Inderscience typically uses DOI pattern 10.1504/*, got {pma.doi}')
        else:
            # Return first URL pattern without verification
            return possible_urls[0]

    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: Inderscience ula failed for {pma.journal}: {e} - DOI: {pma.doi}')



