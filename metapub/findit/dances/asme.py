from ...exceptions import *
from .generic import *

from ..registry import JournalRegistry

def the_asme_animal(pma, verify=True, request_timeout=10, max_redirects=3):
    """ASME (American Society of Mechanical Engineers) dance function.

    ASME publishes technical journals in mechanical engineering, biomechanical
    engineering, manufacturing, energy, and related fields through their
    Digital Collection platform.

    Includes CrossRef API fallback for blocked access.

    Args:
        pma: PubMedArticle object
        verify: Whether to verify PDF access

    Returns:
        PDF URL if accessible

    Raises:
        NoPDFLink: If DOI missing or PDF not accessible
        AccessDenied: If paywall detected
    """
    if not pma.doi:
        raise NoPDFLink('MISSING: doi needed for ASME article.')

    # Try CrossRef API first since ASME blocks automated access
    try:
        crossref_urls = get_crossref_pdf_links(pma.doi)
        if crossref_urls:
            # Use the first PDF URL from CrossRef
            return crossref_urls[0]
    except NoPDFLink:
        # Fall through to original approach if CrossRef fails
        pass

    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for ASME article access')

    # ASME typically uses 10.1115/* DOI pattern
    if not pma.doi.startswith('10.1115/'):
        # Still try to process, but note pattern mismatch
        pass

    # Get URL templates and journal parameters from registry
    registry = JournalRegistry()
    templates = registry.get_url_templates('asme')
    journal_params = registry.get_journal_parameters('asme', pma.journal)

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
                verify_pdf_url(pdf_url, 'ASME', request_timeout=request_timeout, max_redirects=max_redirects)
                return pdf_url
            except (NoPDFLink, AccessDenied):
                continue  # Try next URL format

        # If all URLs failed
        if pma.doi.startswith('10.1115/'):
            raise NoPDFLink(f'TXERROR: Could not access ASME article - DOI: {pma.doi}')
        else:
            raise NoPDFLink(f'PATTERN: ASME typically uses DOI pattern 10.1115/*, got {pma.doi}')
    else:
        # Return first URL pattern without verification
        return possible_urls[0] if possible_urls else f'https://asmedigitalcollection.asme.org/article-pdf/{pma.doi}'


