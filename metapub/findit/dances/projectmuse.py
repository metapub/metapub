"""Project MUSE dance function - REFACTORED.

Follows CLAUDE_PROCESS principles:
- ONE consistent URL pattern based on actual testing
- Simple error handling
- Uses generic functions where possible
- No trial-and-error approaches
"""

from ...exceptions import *
from .generic import *


def the_projectmuse_syrtos(pma, verify=True):
    """Dance function for Project MUSE journals.

    Handles academic journals published on Project MUSE platform at muse.jhu.edu.
    Project MUSE provides access to scholarly content primarily in humanities and social sciences.

    Primary URL Pattern: Constructed from DOI resolution
    Note: Project MUSE requires institutional access for most content

    Args:
        pma: PubMedArticle object
        verify: Whether to verify PDF accessibility

    Returns:
        str: URL to PDF

    Raises:
        NoPDFLink: If DOI missing or URL construction fails
        AccessDenied: If paywall detected (common for Project MUSE)
    """
    if not pma.doi:
        raise NoPDFLink(f'MISSING: DOI required for Project MUSE access - Journal: {pma.journal}')

    # Project MUSE uses DOI resolution to get to article pages
    # Direct PDF URLs are typically behind institutional access
    
    if verify:
        # Resolve DOI to get Project MUSE article URL
        try:
            article_url = the_doi_2step(pma.doi)
        except NoPDFLink as e:
            raise NoPDFLink(f'TXERROR: DOI resolution failed for Project MUSE: {e}')
        
        # Check if it resolved to Project MUSE
        if 'muse.jhu.edu' not in article_url:
            raise NoPDFLink(f'TXERROR: DOI did not resolve to Project MUSE - got: {article_url}')
        
        # Try to access the article page
        try:
            response = unified_uri_get(article_url, timeout=10, allow_redirects=True)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '').lower()
                if 'application/pdf' in content_type:
                    return response.url  # Redirected to PDF
                elif 'text/html' in content_type:
                    # Check for paywall (very common for Project MUSE)
                    if detect_paywall_from_html(response.text):
                        raise AccessDenied(f'PAYWALL: Project MUSE article requires institutional access - {article_url}')
                    else:
                        # Try to construct PDF URL from article URL
                        # Project MUSE pattern: /article/123456 -> /article/123456/pdf
                        if '/article/' in article_url:
                            pdf_url = article_url.rstrip('/') + '/pdf'
                            try:
                                pdf_response = unified_uri_get(pdf_url, timeout=10)
                                if pdf_response.status_code == 200:
                                    return pdf_url
                            except Exception:
                                pass
                        
                        raise NoPDFLink(f'TXERROR: Could not find PDF link on Project MUSE page - attempted: {article_url}')
            else:
                raise NoPDFLink(f'TXERROR: Project MUSE returned status {response.status_code} - attempted: {article_url}')
                
        except AccessDenied:
            raise  # Bubble up paywall detection
        except NoPDFLink:
            raise  # Bubble up specific errors
        except Exception as e:
            raise NoPDFLink(f'TXERROR: Network error accessing Project MUSE: {e} - attempted: {article_url}')
    
    else:
        # Without verification, try to construct likely PDF URL pattern
        try:
            article_url = the_doi_2step(pma.doi)
            if 'muse.jhu.edu' in article_url and '/article/' in article_url:
                # Try to construct PDF URL
                return article_url.rstrip('/') + '/pdf'
            else:
                # Fallback: return article URL with warning that it's not a PDF
                return article_url  # WARNING: This is an HTML page, not a PDF
        except Exception:
            raise NoPDFLink(f'TXERROR: Could not construct Project MUSE URL for DOI: {pma.doi}')