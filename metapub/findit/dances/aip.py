"""AIP Publishing dance function."""

import requests
from ...exceptions import AccessDenied, NoPDFLink
from ..dance_helpers import handle_dance_exceptions


@handle_dance_exceptions('AIP Publishing', 'allegro')
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
        
        # Get volume and issue info if available
        volume = getattr(pma, 'volume', None)
        issue = getattr(pma, 'issue', None)
        
        # Try different AIP URL patterns
        possible_urls.extend([
            f'https://pubs.aip.org/{pma.doi}/pdf',
            f'https://aip.scitation.org/doi/pdf/{pma.doi}',
            f'https://pubs.aip.org/aip/article-pdf/doi/{pma.doi}',
            f'https://aip.scitation.org/doi/abs/{pma.doi}',
            f'https://pubs.aip.org/{article_id}/pdf'
        ])
        
        if volume:
            possible_urls.extend([
                f'https://pubs.aip.org/aip/article/doi/{pma.doi}',
                f'https://pubs.aip.org/aip/article/{volume}/{article_id}/pdf'
            ])
    
    # Add DOI resolver as fallback
    possible_urls.extend([
        f'https://doi.org/{pma.doi}',
        f'https://dx.doi.org/{pma.doi}'
    ])
    
    # If not verifying, return the most likely URL
    if not verify:
        return possible_urls[0] if possible_urls else f'https://pubs.aip.org/{pma.doi}/pdf'
    
    # Try each URL until we find one that works
    for url in possible_urls:
        try:
            response = requests.get(url, timeout=10, allow_redirects=True)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '').lower()
                
                if 'application/pdf' in content_type:
                    return response.url
                elif 'text/html' in content_type:
                    # Check for paywall indicators
                    page_text = response.text.lower()
                    paywall_terms = ['subscribe', 'subscription', 'login required', 'access denied', 
                                   'purchase', 'institutional access', 'sign in']
                    
                    if any(term in page_text for term in paywall_terms):
                        continue  # Try next URL
                    else:
                        # Accessible HTML page, return it
                        return response.url
                        
            elif response.status_code in [301, 302, 307]:
                # Follow redirects to final URL
                return response.url
            elif response.status_code == 404:
                continue  # Try next URL
            else:
                continue  # Try next URL
                
        except requests.exceptions.RequestException:
            continue  # Try next URL
    
    # If all URLs failed
    attempted_urls = ', '.join(possible_urls[:3])  # Show first 3 for brevity
    raise NoPDFLink(f'TXERROR: Could not access AIP Publishing article - attempted: {attempted_urls}')