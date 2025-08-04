from ...exceptions import *
from .generic import *

#TODO: get rid of this dumb try-except jaw

# also i'm not convinced any of this works

# also this is just BAD CODE, CLAUDE, and this approach is bad.
# we should not be trying tons of different URLs just to find one PDF.


def the_wjgnet_wave(pma, verify=True):
    """Dance function for WJG Net (Baishideng Publishing Group) journals.

    Handles the "World Journal of ..." series published by Baishideng.
    These journals are open access and available at wjgnet.com.

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
            raise NoPDFLink(f'MISSING: DOI required for WJG Net access - Journal: {pma.journal}')

        # WJG Net journals use various DOI prefixes due to acquisitions and partnerships

        # Try different URL construction approaches for WJG Net
        possible_urls = []

        # Try to extract volume/issue from DOI or PMA data
        volume = getattr(pma, 'volume', None)
        issue = getattr(pma, 'issue', None)

        # WJG Net URL patterns
        if volume and issue:
            possible_urls.extend([
                f'https://www.wjgnet.com/1007-9327/full/v{volume}/i{issue}/{pma.doi}.pdf',
                f'https://www.wjgnet.com/1007-9327/full/v{volume}/i{issue}/{pma.doi}.htm',
            ])

        # Try generic patterns
        possible_urls.extend([
            f'https://www.wjgnet.com/pdf/{pma.doi}.pdf',
            f'https://www.wjgnet.com/full/{pma.doi}.pdf',
            f'https://www.wjgnet.com/1007-9327/pdf/{pma.doi}.pdf',
            f'https://f6publishing.blob.core.windows.net/pdf/{pma.doi}.pdf',
            f'https://www.wjgnet.com/{pma.doi}.pdf',
            f'https://www.wjgnet.com/1007-9327/full/{pma.doi}.htm'
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
                            # Check for paywall indicators (though WJG Net is open access)
                            page_text = response.text.lower()
                            paywall_indicators = [
                                'subscribe', 'subscription', 'login required',
                                'access denied', 'purchase', 'institutional access'
                            ]
                            if any(indicator in page_text for indicator in paywall_indicators):
                                raise AccessDenied(f'PAYWALL: WJG Net article requires access - {pdf_url}')
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
            raise NoPDFLink(f'TXERROR: Could not access WJG Net article - attempted: {", ".join(possible_urls[:3])}')
        else:
            # Return first URL pattern without verification
            return possible_urls[0] if possible_urls else f'https://www.wjgnet.com/pdf/{pma.doi}.pdf'

    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: WJG Net wave failed for {pma.journal}: {e} - DOI: {pma.doi}')

