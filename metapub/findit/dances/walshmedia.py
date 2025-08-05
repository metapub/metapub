"""Walsh Medical Media dance function - REFACTORED.

Follows CLAUDE_PROCESS principles:
- ONE consistent URL pattern based on actual testing
- Simple error handling
- Uses generic functions where possible
- No trial-and-error approaches
"""

from ...exceptions import *
from .generic import *


def the_walshmedia_bora(pma, verify=True):
    """Dance function for Walsh Medical Media journals.

    Handles academic journals published by Walsh Medical Media at walshmedicalmedia.com.
    These journals typically follow open access publishing models.

    Primary URL Pattern: https://www.walshmedicalmedia.com/open-access/{article_id}.pdf
    where article_id is extracted from DOI
    Fallback: DOI resolution

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
        raise NoPDFLink(f'MISSING: DOI required for Walsh Medical Media access - Journal: {pma.journal}')

    # Extract article ID from DOI
    doi_parts = pma.doi.split('/')
    if len(doi_parts) < 2:
        raise NoPDFLink(f'INVALID: Cannot parse DOI for Walsh Medical Media - DOI: {pma.doi}')
    
    article_id = doi_parts[-1]
    
    # Primary URL pattern for Walsh Medical Media articles (open access pattern)
    pdf_url = f'https://www.walshmedicalmedia.com/open-access/{article_id}.pdf'
    
    if verify:
        try:
            response = unified_uri_get(pdf_url, timeout=10, allow_redirects=True)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '').lower()
                if 'application/pdf' in content_type:
                    return pdf_url
                elif 'text/html' in content_type:
                    # Check for paywall
                    if detect_paywall_from_html(response.text):
                        raise AccessDenied(f'PAYWALL: Walsh Medical Media article requires access - {pdf_url}')
                    else:
                        # If HTML returned, PDF URL didn't work
                        raise NoPDFLink(f'TXERROR: Walsh Medical Media returned HTML instead of PDF - attempted: {pdf_url}')
            elif response.status_code == 404:
                # Primary pattern failed, try DOI resolution as fallback
                pass
            else:
                raise NoPDFLink(f'TXERROR: Walsh Medical Media returned status {response.status_code} - attempted: {pdf_url}')
                
        except AccessDenied:
            raise  # Bubble up paywall detection
        except NoPDFLink:
            raise  # Bubble up specific errors
        except Exception:
            pass  # Network error, try fallback
        
        # Fallback: Try DOI resolution
        try:
            resolved_url = the_doi_2step(pma.doi)
            if 'walshmedicalmedia.com' in resolved_url:
                # If it resolved to Walsh domain, try to extract PDF URL
                response = unified_uri_get(resolved_url, timeout=10)
                if response.status_code == 200:
                    return resolved_url
        except Exception:
            pass  # Continue to error
        
        raise NoPDFLink(f'TXERROR: Could not access Walsh Medical Media article - attempted: {pdf_url}')
    
    # Return constructed PDF URL without verification
    return pdf_url