from ...exceptions import *
from .generic import *

from ..journals.aha import aha_journal_params, aha_vip_template

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

    if jrnl not in aha_journal_params:
        raise NoPDFLink(f'MISSING: Journal {pma.journal} not found in AHA registry - attempted: none')

    try:
        pma = rectify_pma_for_vip_links(pma)
        host = aha_journal_params[jrnl]['host']
        url = aha_vip_template.format(host=host, volume=pma.volume, issue=pma.issue, first_page=pma.first_page)

        if verify:
            verify_pdf_url(url, 'AHA', request_timeout=request_timeout, max_redirects=max_redirects)
        return url

    except NoPDFLink:
        raise NoPDFLink(f'MISSING: VIP data (volume/issue/page) required for AHA journals - attempted: none')

