"""Dance function for Frontiers Media journals."""

from ...exceptions import *
from .generic import *


#TODO: get rid of this dumb try-except jaw

# also i'm not convinced any of this works

# also this is just BAD CODE, CLAUDE, and this approach is bad.
# we should not be trying tons of different URLs just to find one PDF.


def the_frontiers_square(pma, verify=False):
    """Dance function for Frontiers Media journals.

    Handles open-access journals published by Frontiers Media at frontiersin.org.
    Frontiers is a major open-access publisher with transparent peer review and
    article-level metrics. Most content is freely accessible.

    Args:
        pma: PubMedArticle object
        verify: Whether to verify PDF accessibility

    Returns:
        str: URL to PDF or article page

    Raises:
        NoPDFLink: If DOI missing or URL construction fails
        AccessDenied: If paywall detected (rare for Frontiers)
    """
    try:
        # Check if DOI is available
        if not pma.doi:
            raise NoPDFLink(f'MISSING: DOI required for Frontiers access - Journal: {pma.journal}')

        # Frontiers journals use various DOI prefixes due to acquisitions and partnerships

        # Try different URL construction approaches for Frontiers
        possible_urls = []

        # Try to extract article details from DOI
        doi_parts = pma.doi.split('/')
        if len(doi_parts) >= 2:
            article_id = doi_parts[-1]

            # Try different Frontiers URL patterns
            possible_urls.extend([
                f'https://www.frontiersin.org/articles/{pma.doi}/full',
                f'https://www.frontiersin.org/articles/{pma.doi}/pdf',
                f'https://journal.frontiersin.org/article/{pma.doi}/full',
                f'https://www.frontiersin.org/article/{pma.doi}/pdf',
                f'https://www.frontiersin.org/journals/article/{pma.doi}',
                f'https://frontiersin.org/articles/{pma.doi}/full'
            ])

        # Try generic patterns
        possible_urls.extend([
            f'https://doi.org/{pma.doi}',  # Fallback to DOI resolver
            f'https://www.frontiersin.org/journals/{pma.doi}',
            f'https://journal.frontiersin.org/{pma.doi}'
        ])

        if verify:
            for pdf_url in possible_urls:
                try:
                    response = unified_uri_get(pdf_url, timeout=10, allow_redirects=True)

                    if response.ok:
                        # Check content type
                        content_type = response.headers.get('content-type', '').lower()
                        if 'application/pdf' in content_type:
                            return pdf_url
                        elif 'text/html' in content_type:
                            # Check for paywall indicators (rare for Frontiers)
                            page_text = response.text.lower()
                            paywall_indicators = [
                                'subscribe', 'subscription', 'login required',
                                'access denied', 'purchase', 'institutional access',
                                'sign in', 'member access'
                            ]
                            if any(indicator in page_text for indicator in paywall_indicators):
                                raise AccessDenied(f'PAYWALL: Frontiers article requires access - {pdf_url}')
                            else:
                                # Most Frontiers content is open access, return article page
                                return pdf_url
                    elif response.status_code == 404:
                        continue  # Try next URL format
                    else:
                        continue  # Try next URL format

                except Exception:
                    continue  # Try next URL format

            # If all URLs failed
            raise NoPDFLink(f'TXERROR: Could not access Frontiers article - attempted: {", ".join(possible_urls[:3])}')
        else:
            # Return first URL pattern without verification
            return possible_urls[0] if possible_urls else f'https://www.frontiersin.org/articles/{pma.doi}/full'

    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: Frontiers square failed for {pma.journal}: {e} - DOI: {pma.doi}')

