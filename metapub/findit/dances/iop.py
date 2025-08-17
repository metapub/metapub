from ...exceptions import *
from .generic import *

# Using registry-based approach for URL templates
from ..registry import JournalRegistry


def the_iop_fusion(pma, verify=True, request_timeout=10, max_redirects=3):
    """IOP Publishing (Institute of Physics) dance function.

    IOP Publishing operates multiple domains including iopscience.iop.org
    and validate.perfdrive.com. Most IOP journals use DOI pattern 10.1088/*.

    Includes CrossRef API fallback for blocked access.

    Args:
        pma: PubMedArticle object
        verify: Whether to verify PDF access

    Returns:
        PDF URL if accessible

    Raises:
        NoPDFLink: If DOI missing, wrong pattern, or PDF not accessible
        AccessDenied: If paywall detected
    """
    if not pma.doi:
        raise NoPDFLink('MISSING: doi needed for IOP article.')

    # Try CrossRef API first since IOP blocks automated access
    try:
        crossref_urls = get_crossref_pdf_links(pma.doi)
        if crossref_urls:
            # Use the first PDF URL from CrossRef
            return crossref_urls[0]
    except NoPDFLink:
        # Fall through to original approach if CrossRef fails
        pass

    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for IOP article access')

    # Get URL templates from registry
    registry = JournalRegistry()
    templates = registry.get_url_templates('iop')
    
    possible_urls = []
    
    # Add primary template
    for template_info in templates['primary']:
        url = template_info['template'].format(doi=pma.doi)
        possible_urls.append(url)
    
    # Add secondary templates  
    for template_info in templates['secondary']:
        url = template_info['template'].format(doi=pma.doi)
        possible_urls.append(url)

    #TODO: if we don't know what's going to work, then gating on "verify" is bad logic...
    if verify:
        for pdf_url in possible_urls:
            try:
                response = unified_uri_get(pdf_url, timeout=request_timeout, max_redirects=max_redirects)

                if response.ok:
                    # Check content type
                    content_type = response.headers.get('content-type', '').lower()
                    if 'application/pdf' in content_type:
                        return pdf_url
                    elif 'text/html' in content_type:
                        # Check for paywall indicators
                        page_text = response.text.lower()
                        paywall_indicators = [
                            'subscribe', 'subscription', 'login required',
                            'access denied', 'purchase', 'institutional access'
                        ]
                        if any(indicator in page_text for indicator in paywall_indicators):
                            # Try next URL before raising paywall error
                            continue
                        else:
                            # Might be article page, return it
                            return pdf_url
                elif response.status_code == 404:
                    continue  # Try next URL format
                else:
                    continue  # Try next URL format

            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout,
                    requests.exceptions.RequestException) as e:
                continue  # Try next URL format due to network error

        # If both URLs failed, determine appropriate error
        common_iop_patterns = ['10.1088/', '10.1209/']  # Common IOP DOI patterns
        if any(pma.doi.startswith(pattern) for pattern in common_iop_patterns):
            raise NoPDFLink(f'TXERROR: Could not access IOP article at either domain - DOI: {pma.doi}')
        else:
            raise NoPDFLink(f'PATTERN: IOP typically uses DOI patterns {common_iop_patterns}, got {pma.doi}')
    else:
        # Return primary URL without verification
        return possible_urls[0]


