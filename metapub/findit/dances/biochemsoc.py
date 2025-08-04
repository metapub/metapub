from ...exceptions import AccessDenied, NoPDFLink
from .generic import the_doi_2step, standardize_journal_name


#TODO: PUT TESTS ON THIS ASAP

def the_biochemsoc_saunter(pma, verify=True):
    '''  :param: pma (PubMedArticle object)
         :param: verify (bool) [default: True]
         :return: url
         :raises: AccessDenied, NoPDFLink
    '''
    jrnl = standardize_journal_name(pma.journal)
    pma = rectify_pma_for_vip_links(pma)  #raises NoPDFLink if missing data
    host = biochemsoc_journals[jrnl]['host']
    url = biochemsoc_format.format(a=pma, host=host, ja=biochemsoc_journals[jrnl]['ja'])
    if verify:
        verify_pdf_url(url, 'biochemsoc')
    return url


