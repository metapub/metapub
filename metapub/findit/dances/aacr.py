from ...exceptions import *
from .generic import *
from ..registry import JournalRegistry

def the_aacr_jitterbug(pma, verify=True, request_timeout=10, max_redirects=3):
    '''Dance function for American Association for Cancer Research (AACR) journals.

    AACR journals use Volume-Issue-Page (VIP) format URLs with journal-specific subdomains.
    URL Pattern: http://{host}.aacrjournals.org/content/{volume}/{issue}/{first_page}.full.pdf

    :param: pma (PubMedArticle object)
    :param: verify (bool) [default: True]
    :param: request_timeout (int) [default: 10]
    :param: max_redirects (int) [default: 3]
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    '''

    jrnl = standardize_journal_name(pma.journal)
    
    # Initialize registry
    registry = JournalRegistry()
    
    # Get publisher config from registry
    publisher_config = registry.get_publisher_config('Aacr')
    if not publisher_config:
        raise NoPDFLink(f'MISSING: AACR publisher not found in registry - attempted: none')
    
    # Get URL template from config
    url_template = publisher_config.get('format_template')
    if not url_template:
        config_data = publisher_config.get('config_data', {})
        url_patterns = config_data.get('url_patterns', {})
        url_template = url_patterns.get('primary_template')
    
    if not url_template:
        raise NoPDFLink(f'MISSING: No URL template found for AACR in registry - attempted: none')

    # Get journal parameters from registry
    journal_params = registry.get_journal_params(jrnl)
    if not journal_params:
        raise NoPDFLink(f'MISSING: Journal {pma.journal} not found in AACR registry - attempted: none')

    try:
        pma = rectify_pma_for_vip_links(pma)
        
        # Extract host parameter from journal params
        host = journal_params.get('host')
        if not host:
            raise NoPDFLink(f'MISSING: Host parameter not found for journal {pma.journal} - attempted: none')
        
        url = url_template.format(host=host, volume=pma.volume, issue=pma.issue, first_page=pma.first_page)

        if verify:
            verify_pdf_url(url, 'AACR', request_timeout=request_timeout, max_redirects=max_redirects)
        return url

    except NoPDFLink:
        raise NoPDFLink(f'MISSING: VIP data (volume/issue/page) required for AACR journals - attempted: none')


