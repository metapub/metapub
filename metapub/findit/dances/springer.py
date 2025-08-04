"""Dance function for Springer journals."""

from ...exceptions import AccessDenied, NoPDFLink
from .generic import the_doi_2step, verify_pdf_url


def the_springer_shag(pma, verify=True):
    '''  :param: pma (PubMedArticle object)
         :param: verify (bool) [default: True]
         :return: url
         :raises: AccessDenied, NoPDFLink
    '''
    # start: http://link.springer.com/article/10.1007%2Fs13238-015-0153-5
    # return: http://link.springer.com/content/pdf/10.1007%2Fs13238-015-0153-5.pdf
    if pma.doi:
        baseurl = the_doi_2step(pma.doi)
    else:
        raise NoPDFLink('MISSING: doi (doi lookup failed)')
    url = baseurl.replace('article', 'content/pdf') + '.pdf'

    if verify:
        verify_pdf_url(url, 'Springer')
    return url