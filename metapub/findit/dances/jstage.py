"""Dance function for J-STAGE (Japan Science and Technology Information Aggregator, Electronic)."""

from ...exceptions import AccessDenied, NoPDFLink
from .generic import the_doi_2step, verify_pdf_url


def the_jstage_dive(pma, verify=True):
    '''  :param: pma (PubMedArticle object)
         :param: verify (bool) [default: True]
         :return: url (string)
         :raises: AccessDenied, NoPDFLink
    '''
    if pma.doi:
        url = the_doi_2step(pma.doi)
        res = unified_uri_get(url)
        if 'jstage' in res.url:
            url = res.url.replace('_article', '_pdf')
            pdfpos = url.find('_pdf')
            # remove everything after the "_pdf" part
            url = url[:pdfpos+4]
    else:
        raise NoPDFLink('MISSING: doi for dx.doi.org lookup to get jstage link')

    if verify:
        verify_pdf_url(url, 'jstage')
    return url