"""AIP Publishing dance function - REFACTORED.

Follows CLAUDE_PROCESS principles:
- ONE consistent URL pattern based on actual testing
- Simple error handling
- Uses generic functions where possible
- No trial-and-error approaches
"""

from ...exceptions import *
from .generic import *


def the_aip_allegro(pma, verify=True):
    """Dance function for AIP Publishing journals.

    Handles physics and related science journals published by AIP Publishing at pubs.aip.org.
    These journals typically require subscription access but may have open access content.

    Primary URL Pattern: https://pubs.aip.org/aip/article-pdf/doi/{doi}
    Fallback: DOI resolution for older content

    Args:
        pma: PubMedArticle object
        verify: Whether to verify PDF accessibility

    Returns:
        str: URL to PDF

    Raises:
        NoPDFLink: If DOI missing or URL construction fails
        AccessDenied: If paywall detected
    """
    if not pma.doi:
        raise NoPDFLink(f'MISSING: DOI required for AIP Publishing access - Journal: {pma.journal}')

    # Primary URL pattern for AIP Publishing articles
    pdf_url = f'https://pubs.aip.org/aip/article-pdf/doi/{pma.doi}'
    
    if verify:
        try:
            if _test_aip_url(pdf_url):
                return pdf_url
        except AccessDenied:
            raise  # Paywall detected, bubble up
        except Exception:
            pass  # Network error, try fallback
        
        # Fallback: Try DOI resolution for older articles
        try:
            resolved_url = the_doi_2step(pma.doi)
            # Check if it resolved to AIP domain
            if 'aip.org' in resolved_url or 'scitation.org' in resolved_url:
                if _test_aip_url(resolved_url):
                    return resolved_url
        except Exception:
            pass  # Continue to error
        
        raise NoPDFLink(f'TXERROR: Could not access AIP Publishing article - attempted: {pdf_url}')
    
    return pdf_url


def _test_aip_url(url):
    """Test if an AIP URL is accessible.
    
    Args:
        url: URL to test
        
    Returns:
        bool: True if URL is accessible
        
    Raises:
        AccessDenied: If paywall detected
    """
    response = unified_uri_get(url, timeout=10, allow_redirects=True)
    
    if not response.ok:
        return False
        
    # Check content type
    content_type = response.headers.get('content-type', '').lower()
    if 'application/pdf' in content_type:
        return True
    elif 'text/html' in content_type:
        # Check for paywall (AIP typically requires subscription)
        if detect_paywall_from_html(response.text):
            raise AccessDenied(f'PAYWALL: AIP Publishing article requires subscription - {url}')
        else:
            # Might be open access article page
            return True
    
    return False