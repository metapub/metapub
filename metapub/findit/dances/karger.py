import requests

from ...exceptions import AccessDenied, NoPDFLink
from .generic import the_doi_2step, verify_pdf_url

#TODO: TESTS FOR THIS ASAP



def the_karger_conga(pma, verify=True):
    '''  :param: pma (PubMedArticle object)
         :param: verify (bool) [default: True]
         :return: url
         :raises: AccessDenied, NoPDFLink
    '''
    # example: 23970213.  doi = 10.1159/000351538
    #       http://www.karger.com/Article/FullText/351538
    #       http://www.karger.com/Article/Pdf/351538

    if pma.doi:
        if find_doi_in_string(pma.doi):
            kid = pma.doi.split('/')[1]
            if kid.isdigit():
                kid = str(int(kid))     # strips the zeroes that are padding the ID in the front.
        else:
            kid = pma.doi
            # sometimes the Karger ID was put in as the DOI (e.g. pmid 11509830)
        baseurl = 'http://www.karger.com/Article/FullText/%s' % kid
    else:
        raise NoPDFLink('MISSING: doi (doi lookup failed)')
    # if it directs to an "Abstract", we prolly can't get the PDF. Try anyway.
    url = baseurl.replace('FullText', 'Pdf').replace('Abstract', 'Pdf')

    if verify:
        verify_pdf_url(url, 'Karger')
    return url


