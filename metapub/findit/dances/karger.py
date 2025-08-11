import requests

from ...exceptions import AccessDenied, NoPDFLink
from ...text_mining import find_doi_in_string
from .generic import the_doi_2step, verify_pdf_url, get_crossref_pdf_links

#TODO: TESTS FOR THIS ASAP



def the_karger_conga(pma, verify=True):
    '''Karger dance function with CrossRef API fallback for blocked access.
    
         :param: pma (PubMedArticle object)
         :param: verify (bool) [default: True]
         :return: url
         :raises: AccessDenied, NoPDFLink
    '''
    if not pma.doi:
        raise NoPDFLink('MISSING: doi needed for Karger article.')

    # Try CrossRef API first since Karger blocks automated access
    try:
        crossref_urls = get_crossref_pdf_links(pma.doi)
        if crossref_urls:
            # Use the first PDF URL from CrossRef
            return crossref_urls[0]
    except NoPDFLink:
        # Fall through to original approach if CrossRef fails
        pass

    # Original approach (likely to be blocked by Cloudflare)
    if find_doi_in_string(pma.doi):
        kid = pma.doi.split('/')[1]
        if kid.isdigit():
            kid = str(int(kid))  # strips the zeroes that are padding the ID in the front.
    else:
        kid = pma.doi
        # sometimes the Karger ID was put in as the DOI (e.g. pmid 11509830)
        
    baseurl = 'http://www.karger.com/Article/FullText/%s' % kid
    # if it directs to an "Abstract", we prolly can't get the PDF. Try anyway.
    url = baseurl.replace('FullText', 'Pdf').replace('Abstract', 'Pdf')

    # Skip verification for blocked publishers 
    return url


