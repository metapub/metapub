from .generic import *
from ...exceptions import *


def the_endo_mambo(pma, verify=True):
    '''  :param: pma (PubMedArticle object)
         :param: verify (bool) [default: True]
         :return: url
         :raises: AccessDenied, NoPDFLink
    '''
    # use dxdoi to get the URL. Load the article page. Scrape for PDF link, which will contain
    #   a unique key and (probably) isn't usable again after a few minutes.
    jrnl = standardize_journal_name(pma.journal)
    if pma.doi:
        url = the_doi_2step(pma.doi)
    else:
        raise NoPDFLink('MISSING: doi (doi lookup failed)')


    ## TODO: THIS CLEARLY DOESN'T WORK, NEED TO REPLACE:
    #html = unified_uri_get(url)
    #res = unified_uri_get(url)
    #if 'html' in res.headers['content-type']:
    #    from IPython import embed; embed()

    raise NoPDFLink('Not done writing the_endo_mambo! Stay tuned')


