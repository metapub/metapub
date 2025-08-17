from ...exceptions import *
from .generic import *

from ..registry import JournalRegistry


#TODO: get rid of this dumb try-except jaw

# also i'm not convinced any of this works

## Also THIS APPROACH IS BAD -- we shouldn't be guessing at patterns. we'll get banned.


def the_allenpress_advance(pma, verify=True, request_timeout=10, max_redirects=3):
    """Allen Press dance function.

    Allen Press provides publishing services for scholarly and professional
    societies. Their journals are hosted on meridian.allenpress.com with
    journal-specific URL structures.

    Args:
        pma: PubMedArticle object
        verify: Whether to verify PDF access
        request_timeout: HTTP request timeout in seconds
        max_redirects: Maximum redirects to follow

    Returns:
        PDF URL if accessible

    Raises:
        NoPDFLink: If DOI missing or PDF not accessible
        AccessDenied: If paywall detected
    """

    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for Allen Press article access')

    # Get URL templates and journal parameters from registry
    registry = JournalRegistry()
    templates = registry.get_url_templates('allenpress')
    journal_params = registry.get_journal_parameters('allenpress', pma.journal)
    
    possible_urls = []
    
    # Get journal abbreviation if available
    ja = None
    if journal_params and 'ja' in journal_params:
        ja = journal_params['ja']
    
    # Build URLs from templates
    all_template_groups = [templates['primary'], templates['secondary']]
    
    for template_group in all_template_groups:
        for template_info in template_group:
            template = template_info['template']
            required_params = template_info.get('requires_params', [])
            
            # Skip templates that require ja if we don't have it
            if 'ja' in required_params and not ja:
                continue
            
            try:
                if ja:
                    url = template.format(doi=pma.doi, ja=ja)
                else:
                    url = template.format(doi=pma.doi)
                possible_urls.append(url)
            except KeyError:
                # Template requires parameters we don't have
                continue

    if verify:
        for pdf_url in possible_urls:
            try:
                verify_pdf_url(pdf_url, 'Allen Press', request_timeout=request_timeout, max_redirects=max_redirects)
                return pdf_url
            except (NoPDFLink, AccessDenied):
                continue  # Try next URL format

        # If all URLs failed
        raise NoPDFLink(f'TXERROR: Could not access Allen Press article with any URL pattern - DOI: {pma.doi}')
    else:
        # Return first URL pattern without verification
        return possible_urls[0] if possible_urls else f'https://meridian.allenpress.com/article-pdf/{pma.doi}'




