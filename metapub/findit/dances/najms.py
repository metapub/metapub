"""Dance function for North American Journal of Medical Sciences."""

from urllib.parse import urljoin
from lxml.html import HTMLParser
from lxml import etree

from ...exceptions import AccessDenied, NoPDFLink
from .generic import verify_pdf_url


def the_najms_mazurka(pma, verify=True):
    '''Dance of the North Am J Med Sci, which should be largely free.

         :param: pma (PubMedArticle object)
         :param: verify (bool) [default: True]
         :return: url (string)
         :raises: AccessDenied, NoPDFLink
    '''
    #PDF link looks like this:
    #http://www.najms.org/downloadpdf.asp?issn=1947-2714;year=2015;volume=7;issue=6;spage=291;epage=294;aulast=Thawabi;type=2

    url_tmpl = 'http://www.najms.org/downloadpdf.asp?issn={issn};year={a.year};volume={a.volume};issue={a.issue};spage={a.first_page};epage={a.last_page};aulast={author1_lastname};type=2'
    if pma.doi:
        #starturl = the_doi_2step(pma.doi)
        starturl = url_tmpl.format(a=pma, author1_lastname=pma.author1_last_fm.split(' ')[0], issn=pma.doi.split('/')[1].split('.')[0])
    else:
        raise NoPDFLink('MISSING: pii, doi (doi lookup failed)')

    url = ''
    response = unified_uri_get(starturl)
    if response.ok:
        body = etree.fromstring(response.content, parser=HTMLParser()).find('body')
        href = body.findall('table/tr/td/p/a')[0].get('href')
        if href:
            url = urljoin('http://www.najms.org', href)
        else:
            raise NoPDFLink('TXERROR: NAJMS did not provide PDF link (or could not be parsed from page).')
    else:
        raise NoPDFLink('TXERROR: response from NAJMS website was %i' % response.status_code)

    if verify:
        verify_pdf_url(url, 'NAJMS')
    return url