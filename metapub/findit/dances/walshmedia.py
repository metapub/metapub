from ...exceptions import *
from .generic import *


 #TODO: get rid of this dumb try-except jaw

 # also i'm not convinced any of this works

 # also this is just BAD CODE, CLAUDE, and this approach is bad.
 # we should not be trying tons of different URLs just to find one PDF.




def the_walshmedia_bora(pma, verify=True):
    """Dance function for Walsh Medical Media journals.

    Handles academic journals published by Walsh Medical Media at walshmedicalmedia.com.
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
            raise NoPDFLink(f'MISSING: DOI required for Walsh Medical Media access - Journal: {pma.journal}')

        # Try different URL construction approaches for Walsh Medical Media
        possible_urls = []

        # Try to construct article slugs from DOI
        doi_parts = pma.doi.split('/')
        if len(doi_parts) >= 2:
            article_id = doi_parts[-1]

            # Try different URL patterns
            possible_urls.extend([
                f'https://www.walshmedicalmedia.com/articles/{article_id}.pdf',
                f'https://www.walshmedicalmedia.com/open-access/{article_id}.pdf',
                f'https://www.walshmedicalmedia.com/abstract/{article_id}.pdf',
                f'https://walshmedicalmedia.com/articles/{article_id}.pdf',
                f'https://walshmedicalmedia.com/open-access/{article_id}.pdf'
            ])

        # Try generic patterns with full DOI
        possible_urls.extend([
            f'https://www.walshmedicalmedia.com/pdf/{pma.doi}.pdf',
            f'https://www.walshmedicalmedia.com/articles/{pma.doi}.pdf',
            f'https://walshmedicalmedia.com/pdf/{pma.doi}.pdf',
            f'https://www.walshmedicalmedia.com/abstract/{pma.doi}',
            f'https://www.walshmedicalmedia.com/open-access/{pma.doi}.pdf'
        ])


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
                                'access denied', 'purchase', 'institutional access'
                            ]
                            if any(indicator in page_text for indicator in paywall_indicators):
                                raise AccessDenied(f'PAYWALL: Walsh Medical Media article requires access - {pdf_url}')
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
            raise NoPDFLink(f'TXERROR: Could not access Walsh Medical Media article - attempted: {", ".join(possible_urls[:3])}')
        else:
            # Return first URL pattern without verification
            return possible_urls[0] if possible_urls else f'https://www.walshmedicalmedia.com/pdf/{pma.doi}.pdf'

    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: Walsh Media bora failed for {pma.journal}: {e} - DOI: {pma.doi}')

