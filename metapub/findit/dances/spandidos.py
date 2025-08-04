import requests

from ...exceptions import AccessDenied, NoPDFLink
from .generic import the_doi_2step, verify_pdf_url

from .generic import standardize_journal_name, rectify_pma_for_vip_links

#TODO: PUT TESTS ON THIS ASAP


def the_spandidos_lambada(pma, verify=True):
    '''  :param: pma (PubMedArticle object)
         :param: verify (bool) [default: True]
         :return: url
         :raises: AccessDenied, NoPDFLink
    '''
    jrnl = standardize_journal_name(pma.journal)
    baseurl = None
    try:
        pma = rectify_pma_for_vip_links(pma)  #raises NoPDFLink if missing data
        url = spandidos_format.format(ja=spandidos_journals[jrnl]['ja'], a=pma)
    except NoPDFLink:
        # let doi2step exceptions fall to calling function
        if pma.doi:
            baseurl = the_doi_2step(pma.doi)
            url = baseurl + '/download'
        else:
            raise NoPDFLink('MISSING: vip, doi - volume and/or issue missing from PubMedArticle; doi lookup failed.')

    if verify:
        verify_pdf_url(url, 'Spandidos')
    return url


