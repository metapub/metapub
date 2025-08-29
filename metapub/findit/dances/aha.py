from ...exceptions import *
from .generic import *
from ..registry import JournalRegistry

def the_aha_waltz(pma, verify=True, request_timeout=10, max_redirects=3):
    '''Dance function for American Heart Association (AHA) journals.

    AHA journals use Volume-Issue-Page (VIP) format URLs with journal-specific subdomains.
    URL Pattern: http://{host}.ahajournals.org/content/{volume}/{issue}/{first_page}.full.pdf

    :param: pma (PubMedArticle object)
    :param: verify (bool) [default: True]
    :param: request_timeout (int) [default: 10]
    :param: max_redirects (int) [default: 3]
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    '''

    jrnl = standardize_journal_name(pma.journal)
    
    # Get configuration from registry - these MUST exist or it's a config bug
    registry = JournalRegistry()
    templates = registry.get_url_templates('aha')
    journal_params = registry.get_journal_parameters('aha', jrnl)
    
    # Use primary template - it MUST exist for this dance to be valid
    url_template = templates['primary'][0]['template']
    
    # Get host parameter - it MUST exist for VIP journals  
    host = journal_params['host']
    
    # Ensure we have VIP data
    pma = rectify_pma_for_vip_links(pma)
    
    # Construct URL
    url = url_template.format(host=host, volume=pma.volume, issue=pma.issue, first_page=pma.first_page)

    if verify:
        verify_pdf_url(url, 'AHA', request_timeout=request_timeout, max_redirects=max_redirects)
    return url

