"""Dance function for JAMA (Journal of the American Medical Association)."""

from lxml.html import HTMLParser
from lxml import etree

from ...exceptions import AccessDenied, NoPDFLink
from .generic import the_doi_2step, verify_pdf_url


def the_jama_dance(pma, verify=True):
    '''  :param: pma (PubMedArticle object)
         :param: verify (bool) [default: True]
         :return: url (string)
         :raises: AccessDenied, NoPDFLink
    '''
    if not pma.doi:
        raise NoPDFLink('MISSING: doi needed for JAMA article.')

    baseurl = the_doi_2step(pma.doi)
    res = unified_uri_get(baseurl)
    parser = HTMLParser()
    tree = etree.fromstring(res.content, parser)
    # we're looking for a meta tag like this:
    # <meta name="citation_pdf_url" content="http://archneur.jamanetwork.com/data/Journals/NEUR/13776/NOC40008.pdf" />
    for item in tree.findall('head/meta'):
        if item.get('name') == 'citation_pdf_url':
            pdfurl = item.get('content')
        else:
            raise NoPDFLink('DENIED: JAMA did not provide PDF link in (%s).' % baseurl)
    if verify:
        #TODO: form navigation
        verify_pdf_url(pdfurl, 'JAMA')
    return pdfurl