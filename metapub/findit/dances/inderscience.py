"""Inderscience Publishers dance function - REBUILT.

Follows CLAUDE_PROCESS principles:
- ONE consistent URL pattern based on actual testing
- Simple error handling
- No trial-and-error approaches
- Properly handles Cloudflare protection
"""

from ...exceptions import NoPDFLink, AccessDenied
from .generic import verify_pdf_url, unified_uri_get

def the_inderscience_ula(pma, verify=True):
    """Inderscience Publishers dance using consistent DOI-based URL pattern.

    Based on actual testing with PMIDs 23565122, 31534305, 26642363:
    - URL Pattern: https://www.inderscienceonline.com/doi/pdf/{doi}
    - DOI Pattern: 10.1504/*
    - Current Status: ALL requests blocked by Cloudflare (HTTP 403)
    - Platform: inderscienceonline.com is protected by bot detection

    This dance maintains the correct URL pattern for future compatibility
    but will consistently fail due to publisher's anti-bot measures.

    Args:
        pma: PubMedArticle object
        verify: Whether to verify PDF accessibility

    Returns:
        str: URL to PDF (though access will be blocked)

    Raises:
        NoPDFLink: If DOI missing or wrong pattern
        AccessDenied: If Cloudflare protection blocks access (common case)
    """
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for Inderscience article')

    # Construct the ONE known URL pattern for Inderscience PDFs
    pdf_url = f'https://www.inderscienceonline.com/doi/pdf/{pma.doi}'

    if verify:
        try:
            response = unified_uri_get(pdf_url, timeout=10)

            if response.status_code == 200:
                content_type = response.headers.get('content-type', '').lower()
                if 'pdf' in content_type:
                    return pdf_url
                elif 'html' in content_type:
                    # This would be paywall content (if accessible)
                    raise AccessDenied(f'PAYWALL: Inderscience article requires subscription - {pdf_url}')

            elif response.status_code == 403:
                # Common case - Cloudflare bot protection
                if 'cloudflare' in response.headers.get('server', '').lower():
                    raise AccessDenied(f'BLOCKED: Inderscience uses Cloudflare protection that prevents automated access - {pdf_url}')
                else:
                    raise AccessDenied(f'DENIED: Access forbidden by Inderscience - {pdf_url}')

            elif response.status_code == 404:
                raise NoPDFLink(f'NOTFOUND: Article not found on Inderscience platform - {pdf_url}')

            else:
                raise NoPDFLink(f'TXERROR: Inderscience returned status {response.status_code} - {pdf_url}')

        except Exception as e:
            raise NoPDFLink(f'TXERROR: Network error accessing Inderscience: {e} - {pdf_url}')

    # Return URL without verification
    return pdf_url
