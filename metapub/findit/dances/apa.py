"""APA (American Psychological Association) dance function - REFACTORED.

Follows CLAUDE_PROCESS principles:
- Primary pattern based on DOI construction  
- Simple error handling
- Uses generic functions where possible
- No trial-and-error approaches
"""

from ...exceptions import *
from .generic import *

from lxml import html
from urllib.parse import urljoin


def the_apa_dab(pma, verify=True):
    """Dance function for American Psychological Association (APA) journals.

    Handles psychology and behavioral science journals published by APA.
    APA journals are hosted on PsycNET (psycnet.apa.org) and use DOI pattern 10.1037/...
    Most articles require subscription access, though some may be freely available.

    Primary Pattern: https://psycnet.apa.org/fulltext/{DOI}.pdf
    Fallback: DOI resolution to article page

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
        raise NoPDFLink('MISSING: DOI required for APA journals - attempted: none')

    # Verify DOI pattern for APA (should start with 10.1037/)
    if not pma.doi.startswith('10.1037/'):
        raise NoPDFLink(f'INVALID: DOI does not match APA pattern (10.1037/) - attempted: {pma.doi}')

    # Primary pattern: Direct PDF URL construction from DOI
    pdf_url = f'https://psycnet.apa.org/fulltext/{pma.doi}.pdf'
    
    if verify:
        try:
            response = unified_uri_get(pdf_url, timeout=10, allow_redirects=True)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '').lower()
                if 'application/pdf' in content_type:
                    return pdf_url
                elif 'text/html' in content_type:
                    # Check for paywall (common for APA)
                    if detect_paywall_from_html(response.text):
                        raise AccessDenied(f'PAYWALL: APA article requires subscription - {pdf_url}')
                    # If HTML returned, PDF URL didn't work, try fallback
            elif response.status_code == 404:
                # Primary pattern failed, try DOI resolution fallback
                pass
            else:
                raise NoPDFLink(f'TXERROR: APA returned status {response.status_code} - attempted: {pdf_url}')
                
        except AccessDenied:
            raise  # Bubble up paywall detection
        except NoPDFLink:
            raise  # Bubble up specific errors  
        except Exception:
            pass  # Network error, try fallback
        
        # Fallback: Try DOI resolution
        try:
            resolved_url = the_doi_2step(pma.doi)
            if 'psycnet.apa.org' in resolved_url:
                response = unified_uri_get(resolved_url, timeout=10)
                if response.status_code == 200:
                    if detect_paywall_from_html(response.text):
                        raise AccessDenied(f'PAYWALL: APA article requires subscription - {resolved_url}')
                    else:
                        # Try to extract PDF link from page
                        tree = html.fromstring(response.content)
                        pdf_links = tree.xpath('//a[contains(@href, ".pdf") or contains(text(), "PDF") or contains(@class, "pdf")]/@href')
                        if pdf_links:
                            pdf_link = pdf_links[0]
                            if pdf_link.startswith('/'):
                                pdf_link = urljoin(resolved_url, pdf_link)
                            return pdf_link
        except Exception:
            pass  # Continue to error
        
        raise NoPDFLink(f'TXERROR: Could not access APA article - attempted: {pdf_url}')
    
    else:
        # Return constructed PDF URL without verification
        return pdf_url