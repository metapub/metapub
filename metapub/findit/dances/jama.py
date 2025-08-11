"""Dance function for JAMA (Journal of the American Medical Association)."""

from lxml.html import HTMLParser
from lxml import etree

from ...exceptions import AccessDenied, NoPDFLink
from .generic import the_doi_2step, verify_pdf_url, unified_uri_get, get_crossref_pdf_links


def the_jama_dance(pma, verify=True):
    '''JAMA dance function with CrossRef API fallback for blocked access.
    
         :param: pma (PubMedArticle object)
         :param: verify (bool) [default: True]
         :return: url (string)
         :raises: AccessDenied, NoPDFLink
    '''
    if not pma.doi:
        raise NoPDFLink('MISSING: doi needed for JAMA article.')

    # Try CrossRef API first since JAMA blocks automated access
    try:
        crossref_urls = get_crossref_pdf_links(pma.doi)
        if crossref_urls:
            # Use the first PDF URL from CrossRef
            pdfurl = crossref_urls[0]
            # Skip verification for blocked publishers
            return pdfurl
    except NoPDFLink:
        # Fall through to original approach if CrossRef fails
        pass

    # Original approach (likely to be blocked by Cloudflare)
    try:
        baseurl = the_doi_2step(pma.doi)
        res = unified_uri_get(baseurl)
        parser = HTMLParser()
        tree = etree.fromstring(res.content, parser)
        
        # Look for citation_pdf_url meta tag
        for item in tree.findall('head/meta'):
            if item.get('name') == 'citation_pdf_url':
                pdfurl = item.get('content')
                if verify:
                    # Skip verification since JAMA is typically blocked
                    pass
                return pdfurl
                
        # If no PDF meta tag found
        raise NoPDFLink('DENIED: JAMA did not provide PDF link in (%s).' % baseurl)
        
    except AccessDenied:
        # If blocked by Cloudflare, inform user
        raise NoPDFLink('BLOCKED: JAMA website blocks automated access - try CrossRef API fallback')