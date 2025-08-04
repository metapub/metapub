from ...exceptions import *
from .generic import *
from ..journals.aps import aps_journal_params, aps_vip_template


def the_aps_quickstep(pma, verify=True):
    '''Dance function for American Physiological Society (APS) journals.

    APS journals use Volume-Issue-Page (VIP) format URLs with journal-specific subdomains.
    URL Pattern: http://{host}.physiology.org/content/{volume}/{issue}/{first_page}.full.pdf

    :param: pma (PubMedArticle object)
    :param: verify (bool) [default: True]
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    '''

    jrnl = standardize_journal_name(pma.journal)

    if jrnl not in aps_journal_params:
        raise NoPDFLink(f'MISSING: Journal {pma.journal} not found in APS registry - attempted: none')

    try:
        pma = rectify_pma_for_vip_links(pma)
        host = aps_journal_params[jrnl]['host']
        url = aps_vip_template.format(host=host, volume=pma.volume, issue=pma.issue, first_page=pma.first_page)

        if verify:
            verify_pdf_url(url, 'APS')
        return url

    except NoPDFLink:
        raise NoPDFLink(f'MISSING: VIP data (volume/issue/page) required for APS journals - attempted: none')


