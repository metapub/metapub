"""AIP Publishing dance function."""

from ...exceptions import *
from .generic import *


#TODO: get rid of this dumb try-except jaw

# also i'm not convinced any of this works

# also this is just BAD CODE, CLAUDE, and this approach is bad.
# we should not be trying tons of different URLs just to find one PDF.



def the_aip_allegro(pma, verify=True):
    """Dance function for AIP Publishing journals.

    Handles physics and related science journals published by AIP Publishing at pubs.aip.org.
    These journals typically require subscription access but may have open access content.

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
            raise NoPDFLink(f'MISSING: DOI required for AIP Publishing access - Journal: {pma.journal}')

        # AIP Publishing journals use various DOI prefixes due to acquisitions and partnerships

        # Try different URL construction approaches for AIP Publishing
        possible_urls = []

        # Try to extract article details from DOI and PMA data
        doi_parts = pma.doi.split('/')
        if len(doi_parts) >= 2:
            article_id = doi_parts[-1]


            # Try different AIP URL patterns
            possible_urls.extend([
                f'https://pubs.aip.org/{pma.doi}/pdf',
                f'https://aip.scitation.org/doi/pdf/{pma.doi}',
                f'https://pubs.aip.org/aip/article-pdf/doi/{pma.doi}',
                f'https://aip.scitation.org/doi/abs/{pma.doi}',
                f'https://pubs.aip.org/{article_id}/pdf'
            ])

            if pma.volume:
                possible_urls.extend([
                    f'https://pubs.aip.org/aip/article/doi/{pma.doi}',
                    f'https://pubs.aip.org/aip/article/{pma.volume}/{article_id}/pdf'
                ])

        # Try generic patterns
        possible_urls.extend([
            f'https://doi.org/{pma.doi}',  # Fallback to DOI resolver
            f'https://pubs.aip.org/doi/{pma.doi}',
            f'https://aip.scitation.org/doi/{pma.doi}'
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
                            # Check for paywall indicators (AIP typically requires subscription)
                            page_text = response.text.lower()
                            paywall_indicators = [
                                'subscribe', 'subscription', 'login required',
                                'access denied', 'purchase', 'institutional access',
                                'sign in', 'member access', 'buy this article'
                            ]
                            if any(indicator in page_text for indicator in paywall_indicators):
                                raise AccessDenied(f'PAYWALL: AIP Publishing article requires subscription - {pdf_url}')
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
            raise NoPDFLink(f'TXERROR: Could not access AIP Publishing article - attempted: {", ".join(possible_urls[:3])}')
        else:
            # Return first URL pattern without verification
            return possible_urls[0] if possible_urls else f'https://pubs.aip.org/{pma.doi}/pdf'

    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: AIP allegro failed for {pma.journal}: {e} - DOI: {pma.doi}')

