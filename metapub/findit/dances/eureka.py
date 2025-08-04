"""Bentham Science Publishers (EurekaSelect.com) dance function - REBUILT.

Follows CLAUDE_PROCESS principles:
- ONE consistent URL pattern based on actual testing
- Simple error handling
- Uses common paywall detection
- No trial-and-error approaches
"""

from ...exceptions import NoPDFLink, AccessDenied
from .generic import verify_pdf_url, detect_paywall_from_html, unified_uri_get

def the_eureka_frug(pma, verify=True):
    """Bentham Science Publishers dance using DOI resolution.
    
    Based on actual testing with PMIDs 38910487, 38879765, 32201485:
    - DOI resolves to https://www.eurekaselect.com/article/{article_id}
    - PDF URL pattern: https://www.eurekaselect.com/article/{article_id}/pdf
    - Expected result: HTTP 500 (server error) for PDF URLs
    - Publisher appears to have technical issues with PDF generation
    
    URL Pattern: DOI resolution → article page → PDF attempt (fails)
    
    Args:
        pma: PubMedArticle object
        verify: Whether to verify PDF accessibility
        
    Returns:
        str: URL to PDF (though access will likely fail)
        
    Raises:
        NoPDFLink: If DOI missing or technical issues
        AccessDenied: If paywall detected (rare - usually technical failure)
    """
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for Bentham Science article')
    
    # Step 1: Resolve DOI to get article URL
    doi_url = f'https://doi.org/{pma.doi}'
    
    if verify:
        try:
            response = unified_uri_get(doi_url, timeout=10, allow_redirects=True)
            
            if response.status_code != 200:
                raise NoPDFLink(f'TXERROR: DOI resolution failed with status {response.status_code} - {doi_url}')
            
            # Check if it resolves to eurekaselect.com
            if 'eurekaselect.com' not in response.url:
                raise NoPDFLink(f'TXERROR: DOI does not resolve to EurekaSelect - got {response.url}')
            
            # Extract article ID from resolved URL
            if '/article/' not in response.url:
                raise NoPDFLink(f'TXERROR: Unexpected EurekaSelect URL format - {response.url}')
            
            article_id = response.url.split('/article/')[-1]
            pdf_url = f'https://www.eurekaselect.com/article/{article_id}/pdf'
            
            # Test PDF URL - this typically returns HTTP 500
            pdf_response = unified_uri_get(pdf_url, timeout=10)
            
            if pdf_response.status_code == 200:
                content_type = pdf_response.headers.get('content-type', '').lower()
                if 'pdf' in content_type:
                    return pdf_url
                elif 'html' in content_type:
                    # Check for paywall (rare)
                    if detect_paywall_from_html(pdf_response.text):
                        raise AccessDenied(f'PAYWALL: Bentham Science article requires subscription - {pdf_url}')
                    else:
                        raise NoPDFLink(f'TXERROR: Bentham returned HTML instead of PDF - {pdf_url}')
            elif pdf_response.status_code == 500:
                # Common case - Bentham has technical issues with PDF generation
                raise NoPDFLink(f'TXERROR: Bentham Science PDF generation failed (HTTP 500) - {pdf_url}')
            elif pdf_response.status_code == 403:
                raise AccessDenied(f'DENIED: Access forbidden by Bentham Science - {pdf_url}')
            else:
                raise NoPDFLink(f'TXERROR: Bentham returned status {pdf_response.status_code} - {pdf_url}')
            
        except Exception as e:
            raise NoPDFLink(f'TXERROR: Network error accessing Bentham Science: {e}')
    
    else:
        # Without verification, construct the expected PDF URL pattern
        # Note: This will likely fail when accessed due to technical issues
        # But we return the correct URL format for consistency
        try:
            response = unified_uri_get(doi_url, timeout=10, allow_redirects=True)
            if 'eurekaselect.com' in response.url and '/article/' in response.url:
                article_id = response.url.split('/article/')[-1]
                return f'https://www.eurekaselect.com/article/{article_id}/pdf'
        except:
            pass
        
        # Fallback: return a constructed URL (won't work but follows expected pattern)
        raise NoPDFLink(f'TXERROR: Cannot construct Bentham Science URL without DOI resolution - {doi_url}')