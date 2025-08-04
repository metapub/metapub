"""Dance function for Wiley journals."""

from lxml.html import HTMLParser
from lxml import etree

from ...exceptions import AccessDenied, NoPDFLink
from .generic import verify_pdf_url, unified_uri_get

# Import Wiley-specific template
from ..journals.wiley import wiley_template


def the_wiley_shuffle(pma, verify=True):
    '''Returns a PDF link to an article from a Wiley-published journal.

    Note: Wiley sometimes buries PDF links in HTML pages we have to parse first.
    Turning off verification (verify=False) may return only a superficial link.

         :param: pma (PubMedArticle object)
         :param: verify (bool) [default: True]
         :return: url (string)
         :raises: AccessDenied, NoPDFLink
    '''
    url = wiley_template.format(doi=pma.doi)
    if not verify:
        return url

    # wiley sometimes buries PDF links in HTML pages we have to parse.
    res = unified_uri_get(url)
    if 'html' in res.headers['content-type']:
        if 'ACCESS DENIED' in res.text:
            raise AccessDenied('DENIED: Wiley E Publisher says no to %s' % res.url)

        tree = etree.fromstring(res.content, HTMLParser())

        #TODO: fix...?  no longer getting a head or a title...?
        #if tree.find('head/title').text.find('Not Found') > -1:
        #    raise NoPDFLink('TXERROR: Wiley says File Not found (%s)' % res.url)
        #elif tree.find('head/title').text.find('Maintenance') > -1:
        #    raise NoPDFLink('TXERROR: Wiley site under scheduled maintenance -- try again later (url was %s).' % res.url)
        iframe = tree.find('body/div/iframe')

        try:
            url = iframe.get('src')
        except AttributeError:
            # no iframe, give up (probably asking for a login at this point)
            raise AccessDenied('DENIED: Wiley E Publisher says no to %s' % res.url)
        verify_pdf_url(url, 'Wiley')
        return url

    elif 'pdf' in res.headers['content-type']:
        return res.url
    else:
        raise NoPDFLink('TXERROR: %s returned neither html nor pdf' % url)