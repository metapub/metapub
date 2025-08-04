"""Wolters Kluwer dance function."""

from lxml.html import HTMLParser
from lxml import etree
from ...exceptions import NoPDFLink
from .generic import rectify_pma_for_vip_links, unified_uri_get


# DO NOT REWRITE THIS SCRIPT, IT'S WORKING

def the_wolterskluwer_volta(pma, verify=True):
    '''  :param: pma (PubMedArticle object)
         :param: verify (bool) [default: True]
         :return: url
         :raises: AccessDenied, NoPDFLink
    '''
    doiurl = 'http://content.wkhealth.com/linkback/openurl?doi=%s'
    volissurl = 'http://content.wkhealth.com/linkback/openurl?issn={a.issn}&volume={a.volume}&issue={a.issue}&spage={a.first_page}'
    if pma.doi:
        baseurl = unified_uri_get(doiurl % pma.doi).url
    elif pma.issn:
        pma = rectify_pma_for_vip_links(pma)  #raises NoPDFLink if missing data
        baseurl = unified_uri_get(volissurl.format(a=pma)).url

    res = unified_uri_get(baseurl)
    tree = etree.fromstring(res.content, HTMLParser())
    try:
        item = tree.cssselect('li.ej-box-01-body-li-article-tools-pdf')[0]
    except IndexError:
        raise NoPDFLink('DENIED: wolterskluwer did not provide PDF link for this article')

    ahref = item.cssselect('a')[0]
    href = ahref.get('href')
    if href.startswith('/'):
        outurl = 'http://content.wkhealth.com' + href
    else:
        outurl = href

    if verify:
        try:
            response = unified_uri_get(outurl)
            if not response.ok:
                raise NoPDFLink('DENIED: wolterskluwer PDF link is not accessible')
        except Exception:
            raise NoPDFLink('TXERROR: network error verifying wolterskluwer PDF link')

    return outurl
