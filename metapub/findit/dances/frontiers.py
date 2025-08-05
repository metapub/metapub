"""Dance function for Frontiers Media journals - REFACTORED.

Follows CLAUDE_PROCESS principles:
- ONE consistent URL pattern based on actual testing
- Simple error handling
- Uses generic functions where possible
- No trial-and-error approaches
"""

from ...exceptions import *
from .generic import *


def the_frontiers_square(pma, verify=False):
    """Dance function for Frontiers Media journals.

    Handles open-access journals published by Frontiers Media at frontiersin.org.
    Frontiers is a major open-access publisher with transparent peer review and
    article-level metrics. Most content is freely accessible.

    Primary URL Pattern: https://www.frontiersin.org/articles/{doi}/pdf
    Fallback: DOI resolution for older content

    Args:
        pma: PubMedArticle object
        verify: Whether to verify PDF accessibility

    Returns:
        str: URL to PDF or article page

    Raises:
        NoPDFLink: If DOI missing or URL construction fails
        AccessDenied: If paywall detected (rare for Frontiers)
    """
    if not pma.doi:
        raise NoPDFLink(f'MISSING: DOI required for Frontiers access - Journal: {pma.journal}')

    # Primary URL pattern for Frontiers articles
    pdf_url = f'https://www.frontiersin.org/articles/{pma.doi}/pdf'
    
    if verify:
        try:
            if _try_frontiers_url(pdf_url):
                return pdf_url
        except Exception:
            pass  # Network error, try fallback
        
        # Fallback: Try DOI resolution for older articles
        try:
            resolved_url = the_doi_2step(pma.doi)
            if _try_frontiers_url(resolved_url):
                return resolved_url
        except NoPDFLink:
            pass  # Continue to error
        except Exception:
            pass  # Network error, continue to error
        
        raise NoPDFLink(f'TXERROR: Could not access Frontiers article - attempted: {pdf_url}')
    
    return pdf_url


def _try_frontiers_url(url):
    """Helper function to test a Frontiers URL.
    
    Args:
        url: URL to test
        
    Returns:
        bool: True if URL is accessible, False otherwise
        
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
        # Check for paywall (rare for Frontiers but possible)
        if detect_paywall_from_html(response.text):
            raise AccessDenied(f'PAYWALL: Frontiers article requires access - {url}')
        else:
            # Most Frontiers content is open access
            return True
    
    return False