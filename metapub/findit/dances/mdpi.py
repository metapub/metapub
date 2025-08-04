from ...exceptions import *
from .generic import *

def the_mdpi_moonwalk(pma, verify=True):
    '''Dance function for MDPI journals as backup to PMC access.

    MDPI journals are primarily available through PMC, but this provides backup
    PDF access by appending '/pdf' to the resolved DOI URL.
    URL Pattern: {resolved_doi_url}/pdf

    :param: pma (PubMedArticle object)
    :param: verify (bool) [default: True]
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    '''
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for MDPI backup - attempted: none')

    try:
        # Get the resolved DOI URL first
        resolved_url = the_doi_2step(pma.doi)

        # MDPI backup strategy: append '/pdf' to resolved URL
        url = f"{resolved_url}/pdf"

        if verify:
            verify_pdf_url(url, 'MDPI')
        return url

    except Exception as e:
        if isinstance(e, NoPDFLink):
            raise
        else:
            raise NoPDFLink(f'TXERROR: MDPI backup failed for {pma.journal}: {e} - attempted: none')


