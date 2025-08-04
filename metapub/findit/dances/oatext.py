from ...exceptions import *
from .generic import *

from ..journals.oatext import oatext_format

#TODO: get rid of this dumb try-except jaw

# also i'm not convinced any of this works



def the_oatext_orbit(pma, verify=True):
    """OAText Publishing dance function.

    OAText is an open access publisher specializing in medical and healthcare
    journals. Their URL patterns may vary, so this function tries multiple
    approaches to access PDFs.

    Args:
        pma: PubMedArticle object
        verify: Whether to verify PDF access

    Returns:
        PDF URL if accessible

    Raises:
        NoPDFLink: If DOI missing or PDF not accessible
        AccessDenied: If paywall detected (unlikely for open access)
    """

    try:
        if not pma.doi:
            raise NoPDFLink('MISSING: DOI required for OAText article access')

        # OAText journals may use various DOI patterns
        # Most open access publishers are flexible with DOI patterns

        # Try different URL construction approaches
        doi_suffix = pma.doi.split('/')[-1] if '/' in pma.doi else pma.doi

        possible_urls = [
            f'https://www.oatext.com/pdf/{doi_suffix}.pdf',
            f'https://oatext.com/pdf/{doi_suffix}.pdf',
            f'https://www.oatext.com/pdf/{pma.doi}.pdf',
            f'https://oatext.com/pdf/{pma.doi}.pdf'
        ]

        # Also try constructing from article title if available
        if hasattr(pma, 'title') and pma.title:
            # Convert title to URL-friendly format
            title_slug = pma.title.lower().replace(' ', '-').replace(',', '').replace(':', '').replace('.', '')
            title_slug = ''.join(c for c in title_slug if c.isalnum() or c == '-')
            possible_urls.extend([
                f'https://www.oatext.com/{title_slug}.php',
                f'https://oatext.com/{title_slug}.php'
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
                            # Check for article page or PDF links
                            page_text = response.text.lower()
                            if 'not found' in page_text or '404' in page_text:
                                continue  # Try next URL
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
            raise NoPDFLink(f'TXERROR: Could not access OAText article with any URL pattern - DOI: {pma.doi}')
        else:
            # Return first PDF URL pattern without verification
            return possible_urls[0]

    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: OAText orbit failed for {pma.journal}: {e} - DOI: {pma.doi}')

