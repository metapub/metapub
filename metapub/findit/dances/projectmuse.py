from ...exceptions import *
from .generic import *


#TODO: get rid of this dumb try-except jaw

# also i'm not convinced any of this works

# also this is just BAD CODE, CLAUDE, and this approach is bad.
# we should not be trying tons of different URLs just to find one PDF.


def the_projectmuse_syrtos(pma, verify=True):
    """Dance function for Project MUSE journals.

    Handles scholarly journals available through Project MUSE (muse.jhu.edu),
    Johns Hopkins University's digital library for humanities and social sciences.
    Most content requires institutional subscription.

    Args:
        pma: PubMedArticle object
        verify: Whether to verify PDF accessibility

    Returns:
        str: URL to PDF or article page

    Raises:
        NoPDFLink: If DOI missing or URL construction fails
        AccessDenied: If paywall detected
    """
    try:
        # Check if DOI is available
        if not pma.doi:
            raise NoPDFLink(f'MISSING: DOI required for Project MUSE access - Journal: {pma.journal}')

        # Project MUSE articles use various DOI prefixes due to acquisitions and partnerships

        # Try different URL construction approaches for Project MUSE
        possible_urls = []

        # Try to extract article ID from DOI
        doi_parts = pma.doi.split('/')
        if len(doi_parts) >= 2:
            # Extract article identifier from DOI
            article_id = doi_parts[-1]

            # Try different URL patterns
            possible_urls.extend([
                f'https://muse.jhu.edu/article/{article_id}/pdf',
                f'https://muse.jhu.edu/article/{article_id}',
                f'https://muse.jhu.edu/pub/{article_id}/pdf',
                f'https://muse.jhu.edu/journals/{article_id}/pdf'
            ])

        # Try generic patterns with full DOI
        possible_urls.extend([
            f'https://muse.jhu.edu/article/{pma.doi}',
            f'https://muse.jhu.edu/article/{pma.doi}/pdf',
            f'https://doi.org/{pma.doi}',  # Fallback to DOI resolver
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
                            # Check for paywall indicators (Project MUSE is usually paywalled)
                            page_text = response.text.lower()
                            paywall_indicators = [
                                'subscribe', 'subscription', 'login required',
                                'access denied', 'purchase', 'institutional access',
                                'sign in', 'member access', 'institution'
                            ]
                            if any(indicator in page_text for indicator in paywall_indicators):
                                raise AccessDenied(f'PAYWALL: Project MUSE article requires subscription - {pdf_url}')
                            else:
                                # Might be open access article page, return it
                                return pdf_url
                    elif response.status_code == 404:
                        continue  # Try next URL format
                    else:
                        continue  # Try next URL format

                except Exception:
                    continue  # Try next URL format

            # If all URLs failed
            raise NoPDFLink(f'TXERROR: Could not access Project MUSE article - attempted: {", ".join(possible_urls[:3])}')
        else:
            # Return first URL pattern without verification
            return possible_urls[0] if possible_urls else f'https://muse.jhu.edu/article/{pma.doi}'

    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: Project MUSE syrtos failed for {pma.journal}: {e} - DOI: {pma.doi}')


