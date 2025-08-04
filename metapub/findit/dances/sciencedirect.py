"""Dance function for ScienceDirect (Elsevier)."""

from lxml.html import HTMLParser
from lxml import etree

from ...exceptions import AccessDenied, NoPDFLink
from ...utils import remove_chars
from .generic import the_doi_2step

# Import ScienceDirect-specific URL template
from ..journals.sciencedirect import sciencedirect_url


def the_sciencedirect_disco(pma, verify=True):
    '''Note: verify=True required to find link.  Parameter supplied only for unity
       with other dances.

         :param: pma (PubMedArticle object)
         :param: verify (bool) [default: True]
         :return: url (string)
         :raises: AccessDenied, NoPDFLink
    '''
    #we're looking for a url that looks like this:
    #http://www.sciencedirect.com/science/article/pii/S0022283601953379/pdfft?md5=07db9e1b612f64ea74872842e34316a5&pid=1-s2.0-S0022283601953379-main.pdf

    starturl = None
    if pma.pii:
        starturl = sciencedirect_url.format(piit=remove_chars(pma.pii, '-()'))
    elif pma.doi:
        starturl = the_doi_2step(pma.doi)

    if starturl == None:
        raise NoPDFLink('MISSING: pii, doi (doi lookup failed)')

    try:
        res = unified_uri_get(starturl)
    except requests.exceptions.TooManyRedirects:
        raise NoPDFLink('TXERROR: ScienceDirect TooManyRedirects: cannot reach %s via %s' %
                        (pma.journal, starturl))

    tree = etree.fromstring(res.content, HTMLParser())
    try:
        div = tree.cssselect('div.icon_pdf')[0]
    except IndexError:
        raise NoPDFLink('DENIED: ScienceDirect did not provide pdf link (probably paywalled)')
    url = div.cssselect('a')[0].get('href')
    if 'pdf' in url:
        return url
    else:
        # give up, it's probably a "shopping cart" link.
        raise NoPDFLink('DENIED: ScienceDirect did not provide pdf link (probably paywalled)')