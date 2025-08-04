from .generic import *
from ...exceptions import *

from ..journals.asm import asm_journal_params, asm_vip_template

def the_asm_shimmy(pma, verify=True):
    '''Dance function for American Society of Microbiology (ASM) journals.

    ASM journals use Volume-Issue-Page (VIP) format URLs with journal-specific subdomains.
    URL Pattern: http://{host}.asm.org/content/{volume}/{issue}/{first_page}.full.pdf

    :param: pma (PubMedArticle object)
    :param: verify (bool) [default: True]
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    '''

    jrnl = standardize_journal_name(pma.journal)

    if jrnl not in asm_journal_params:
        raise NoPDFLink(f'MISSING: Journal {pma.journal} not found in ASM registry - attempted: none')

    try:
        pma = rectify_pma_for_vip_links(pma)
        host = asm_journal_params[jrnl]['host']
        url = asm_vip_template.format(host=host, volume=pma.volume, issue=pma.issue, first_page=pma.first_page)

        if verify:
            verify_pdf_url(url, 'ASM')
        return url

    except NoPDFLink:
        raise NoPDFLink(f'MISSING: VIP data (volume/issue/page) required for ASM journals - attempted: none')

