"""Dance function for AAAS (American Association for the Advancement of Science) journals."""

from urllib.parse import urlsplit
from lxml.html import HTMLParser
from lxml import etree
import os

from ...exceptions import AccessDenied, NoPDFLink
from .generic import unified_uri_get

AAAS_USERNAME = os.environ.get("AAAS_USERNAME", "set in env: AAAS_USERNAME and AAAS_PASSWORD")
AAAS_PASSWORD = os.environ.get("AAAS_PASSWORD", "")


def the_aaas_twist(pma, verify=True):
    '''Note: "verify" param recommended here (page navigation usually necessary).

         :param: pma (PubMedArticle object)
         :param: verify (bool) [default: True]
         :return: url (string)
         :raises: AccessDenied, NoPDFLink
    '''
    #try:
    #    pma = rectify_pma_for_vip_links(pma)
    #    pdfurl = aaas_format.format(ja=aaas_journals[pma.journal]['ja'], a=pma)
    #except NoPDFLink:
        # try the pmid-based approach
    baseurl = 'http://www.sciencemag.org/cgi/pmidlookup?view=long&pmid=%s' % pma.pmid
    res = unified_uri_get(baseurl)
    pdfurl = res.url.replace('.long', '.full') + '.pdf'

    if not verify:
        return pdfurl

    response = unified_uri_get(pdfurl)
    if response.status_code == 200 and 'pdf' in response.headers['content-type']:
        return response.url

    elif response.status_code == 200 and 'html' in response.headers['content-type']:
        tree = etree.fromstring(response.content, HTMLParser())

        if not 'Sign In' in tree.find('head/title').text:
            raise NoPDFLink('TXERROR: AAAS returned unexpected HTML response for url %s' % (pdfurl))
        else:
            # some items are acquirable via free account registration... but let's not mess with this just yet.
            raise NoPDFLink('DENIED: AAAS paper subscription-only or requires site registration (url: %s)' % pdfurl)

        form = tree.cssselect('form')[0]
        fbi = form.fields.get('form_build_id')

        baseurl = urlsplit(response.url)
        post_url = baseurl.scheme + '://' + baseurl.hostname + form.action

        payload = {'pass': AAAS_PASSWORD, 'name': AAAS_USERNAME,
                   'form_build_id': fbi, 'remember_me': 1}
        #print("SUBMITTING TO AAAS")
        #print(payload)

        response = requests.post(post_url, data=payload)
        if response.status_code == 403:
            return AccessDenied('DENIED: AAAS subscription-only paper (url: %s)')
        elif 'pdf' in response.headers['content-type']:
            return response.url
        elif 'html' in response.headers['content-type']:
            #if response.content.find('access-denied') > -1:
            raise NoPDFLink('DENIED: AAAS subscription-only paper (url: %s)' % pdfurl)
    else:
        raise NoPDFLink('TXERROR: AAAS returned %s for url %s' % (response.status_code, pdfurl))
