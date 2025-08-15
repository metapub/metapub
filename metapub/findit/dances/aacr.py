from ...exceptions import *
from .generic import *

from ..journals.aacr import aacr_journal_params, aacr_vip_template

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

    if jrnl not in aacr_journal_params:
        raise NoPDFLink(f'MISSING: Journal {pma.journal} not found in AACR registry - attempted: none')

    try:
        pma = rectify_pma_for_vip_links(pma)
        host = aacr_journal_params[jrnl]['host']
        url = aacr_vip_template.format(host=host, volume=pma.volume, issue=pma.issue, first_page=pma.first_page)

        if verify:
            verify_pdf_url(url, 'AACR', request_timeout=request_timeout, max_redirects=max_redirects)
        return url

    except NoPDFLink:
        raise NoPDFLink(f'MISSING: VIP data (volume/issue/page) required for AACR journals - attempted: none')


