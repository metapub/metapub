"""World Journal of Gastroenterology Network dance function - REFACTORED.

Follows CLAUDE_PROCESS principles:
- ONE consistent URL pattern based on actual testing
- Simple error handling
- Uses generic functions where possible
- No trial-and-error approaches
"""

from ...exceptions import *
from .generic import *


def the_wjgnet_wave(pma, verify=True):
    """Dance function for World Journal of Gastroenterology Network (WJG-NET) journals.

    Handles academic journals published by WJG-NET at wjgnet.com.
    These journals are primarily focused on gastroenterology and related medical fields.

    Primary URL Pattern: https://www.wjgnet.com/{journal_id}/full/v{volume}/i{issue}/{pii}.pdf
    where journal_id is derived from journal name
    Fallback: DOI resolution

    Args:
        pma: PubMedArticle object
        verify: Whether to verify PDF accessibility

    Returns:
        str: URL to PDF

    Raises:
        NoPDFLink: If required data missing or URL construction fails
        AccessDenied: If paywall detected
    """
    # WJG-NET requires either DOI or volume/issue/page info
    if not pma.doi and not (pma.volume and pma.issue and pma.first_page):
        raise NoPDFLink(f'MISSING: DOI or volume/issue/page required for WJG-NET access - Journal: {pma.journal}')

    # Map journal names to WJG-NET journal IDs (common ones)
    journal_map = {
        'World J Gastroenterol': '1007-9327',
        'World J Hepatol': '1948-5182',
        'World J Gastrointest Oncol': '1948-5204',
        'World J Gastrointest Surg': '1948-9366',
        'World J Clin Cases': '2307-8960'
    }
    
    # Try to get journal ID from mapping
    journal_id = None
    for journal_name, jid in journal_map.items():
        if journal_name.lower() in pma.journal.lower():
            journal_id = jid
            break
    
    if journal_id and pma.volume and pma.issue and pma.first_page:
        # Primary URL pattern using volume/issue/page
        pdf_url = f'https://www.wjgnet.com/{journal_id}/full/v{pma.volume}/i{pma.issue}/{pma.first_page}.pdf'
        
        if verify:
            try:
                response = unified_uri_get(pdf_url, timeout=10, allow_redirects=True)
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '').lower()
                    if 'application/pdf' in content_type:
                        return pdf_url
                    elif 'text/html' in content_type:
                        if detect_paywall_from_html(response.text):
                            raise AccessDenied(f'PAYWALL: WJG-NET article requires access - {pdf_url}')
                        # Continue to DOI fallback
                elif response.status_code == 404:
                    # Try DOI fallback
                    pass
                else:
                    raise NoPDFLink(f'TXERROR: WJG-NET returned status {response.status_code} - attempted: {pdf_url}')
                    
            except AccessDenied:
                raise  # Bubble up paywall detection
            except NoPDFLink:
                raise  # Bubble up specific errors
            except Exception:
                pass  # Network error, try fallback
        else:
            # Return constructed PDF URL without verification
            return pdf_url
    
    # Fallback: Try DOI resolution if available
    if pma.doi:
        try:
            resolved_url = the_doi_2step(pma.doi)
            if 'wjgnet.com' in resolved_url:
                if verify:
                    response = unified_uri_get(resolved_url, timeout=10)
                    if response.status_code == 200:
                        content_type = response.headers.get('content-type', '').lower()
                        if 'application/pdf' in content_type:
                            return resolved_url
                        elif 'text/html' in content_type and detect_paywall_from_html(response.text):
                            raise AccessDenied(f'PAYWALL: WJG-NET article requires access - {resolved_url}')
                else:
                    # Try to construct PDF URL from resolved DOI URL
                    if '/full/' in resolved_url:
                        # WJG-NET pattern: /full/... -> /pdf/...  
                        pdf_url = resolved_url.replace('/full/', '/pdf/')
                        return pdf_url
                    else:
                        # Fallback: return article URL with warning
                        return resolved_url  # WARNING: This is an HTML page, not a PDF
        except Exception:
            pass  # Continue to error
    
    # If we get here, we couldn't construct a working URL
    attempted_urls = []
    if journal_id and pma.volume and pma.issue and pma.first_page:
        attempted_urls.append(f'https://www.wjgnet.com/{journal_id}/full/v{pma.volume}/i{pma.issue}/{pma.first_page}.pdf')
    if pma.doi:
        attempted_urls.append(f'DOI resolution for {pma.doi}')
    
    raise NoPDFLink(f'TXERROR: Could not access WJG-NET article - attempted: {", ".join(attempted_urls)}')