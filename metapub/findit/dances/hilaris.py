from ...exceptions import *
from .generic import *


#TODO: get rid of this dumb try-except jaw

# also i'm not convinced any of this works

# also this is just BAD CODE, CLAUDE, and this approach is bad.
# we should not be trying tons of different URLs just to find one PDF.



def the_hilaris_hop(pma, verify=True):
    """Dance function for Hilaris Publisher journals.

    Handles academic journals published by Hilaris Publisher at hilarispublisher.com.
    These journals typically follow open access publishing models.

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
            raise NoPDFLink(f'MISSING: DOI required for Hilaris Publisher access - Journal: {pma.journal}')

        # Hilaris Publisher journals use various DOI prefixes due to acquisitions and partnerships

        # Try different URL construction approaches for Hilaris
        possible_urls = []

        # Try to construct article slugs from DOI
        doi_parts = pma.doi.split('/')
        if len(doi_parts) >= 2:
            article_id = doi_parts[-1]

            # Try different URL patterns
            possible_urls.extend([
                f'https://www.hilarispublisher.com/articles/{article_id}.pdf',
                f'https://www.hilarispublisher.com/abstract/{article_id}.pdf',
                f'https://www.hilarispublisher.com/fulltext/{article_id}.pdf',
                f'https://hilarispublisher.com/articles/{article_id}.pdf',
                f'https://hilarispublisher.com/abstract/{article_id}.pdf'
            ])

        # Try generic patterns with full DOI
        possible_urls.extend([
            f'https://www.hilarispublisher.com/pdf/{pma.doi}.pdf',
            f'https://www.hilarispublisher.com/articles/{pma.doi}.pdf',
            f'https://hilarispublisher.com/pdf/{pma.doi}.pdf',
            f'https://www.hilarispublisher.com/abstract/{pma.doi}',
            f'https://www.hilarispublisher.com/fulltext/{pma.doi}.pdf'
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
                            # Check for paywall indicators
                            page_text = response.text.lower()
                            paywall_indicators = [
                                'subscribe', 'subscription', 'login required',
                                'access denied', 'purchase', 'institutional access'
                            ]
                            if any(indicator in page_text for indicator in paywall_indicators):
                                raise AccessDenied(f'PAYWALL: Hilaris Publisher article requires access - {pdf_url}')
                            else:
                                # Might be article page, return it
                                return pdf_url
                    elif response.status_code == 404:
                        continue  # Try next URL format
                    else:
                        continue  # Try next URL format

                except Exception:
                    continue  # Try next URL format

            # If all URLs failed
            raise NoPDFLink(f'TXERROR: Could not access Hilaris Publisher article - attempted: {", ".join(possible_urls[:3])}')
        else:
            # Return first URL pattern without verification
            return possible_urls[0] if possible_urls else f'https://www.hilarispublisher.com/pdf/{pma.doi}.pdf'

    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: Hilaris hop failed for {pma.journal}: {e} - DOI: {pma.doi}')

