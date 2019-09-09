__author__ = 'nthmost'

from urllib.parse import urlsplit, urljoin

import requests
from lxml.html import HTMLParser
from lxml import etree

from ..dx_doi import DxDOI, DX_DOI_URL
from ..pubmedarticle import square_voliss_data_for_pma
from ..exceptions import AccessDenied, NoPDFLink, BadDOI, DxDOIError
from ..text_mining import find_doi_in_string
from ..utils import remove_chars

from .journals import *

OK_STATUS_CODES = (200, 301, 302, 307)

#TODO: make configurable (somehow...)
AAAS_USERNAME = 'nthmost'
AAAS_PASSWORD = '434264'

dx_doi_engine = None
def _start_dx_doi_engine():
    global dx_doi_engine
    if dx_doi_engine is None:
        dx_doi_engine = DxDOI()

def the_doi_2step(doi):
    '''Given a doi, uses DxDOI lookup engine to source the publisher's 
            article URL for this doi.

    Args:
        doi (str): a Digital Object Identifier

    Returns:
        url (str): link to publisher's website as returned by dx.doi.org

    Raises:
        NoPDFLink if dx.doi.org lookup failed (see error.message)
    '''
    _start_dx_doi_engine()
    try:
        return dx_doi_engine.resolve(doi)
    except (BadDOI, DxDOIError) as error:
        raise NoPDFLink('%r' % error)

def standardize_journal_name(journal_name):
    '''Returns a "standardized" journal name with periods stripped out.'''
    return remove_chars(journal_name, '.')

def verify_pdf_url(pdfurl, publisher_name=''):
    res = requests.get(pdfurl)
    if res.status_code==401:
        raise NoPDFLink('DENIED: %s url (%s) requires login.' % (publisher_name, pdfurl))

    if not res.ok:
        raise NoPDFLink('TXERROR: %i status returned from %s url (%s)' % (res.status_code, 
                            publisher_name, pdfurl))

    if res.status_code in OK_STATUS_CODES and 'pdf' in res.headers['content-type']:
        return pdfurl
    else:
        raise NoPDFLink('DENIED: %s url (%s) did not result in a PDF' % (publisher_name, pdfurl))

def rectify_pma_for_vip_links(pma):
    '''takes a PubMedArticle object and "squares" the volume/issue/page info (sometimes there
    are weird characters in it, or sometimes the issue number is packed into the volume field,
    stuff like that).

    If volume, issue, and page data are all represented, return the PubMedArticle (possibly
    modified).

    If missing data, raise NoPDFLink('MISSING: vip...') 
    '''
    pma = square_voliss_data_for_pma(pma)
    if pma.volume and pma.first_page and pma.issue:
        return pma
    raise NoPDFLink('MISSING: vip (volume, issue, and/or first_page missing from PubMedArticle)')

def the_doi_slide(pma, verify=True):
    '''Dance of the miscellaneous journals that use DOI in their URL construction.

         :param: pma (PubMedArticle object)
         :param: verify (bool) [default: True]
         :return: url (string)
         :raises: AccessDenied, NoPDFLink
    '''
    jrnl = standardize_journal_name(pma.journal) 
    if pma.doi:
        url = simple_formats_doi[jrnl].format(a=pma)
    else:
        raise NoPDFLink('MISSING: doi (lookup failed)')

    if verify:
        verify_pdf_url(url)
    return url

def the_pmid_pogo(pma, verify=True):
    '''Dance of the miscellaneous journals that use PMID in their URL construction.

         :param: pma (PubMedArticle object)
         :param: verify (bool) [default: True]
         :return: url (string)
         :raises: AccessDenied, NoPDFLink
    '''
    jrnl = standardize_journal_name(pma.journal)
    url = simple_formats_pmid[jrnl].format(pmid=pma.pmid)

    if verify:
        verify_pdf_url(url)
    return url

def the_vip_shake(pma, verify=True):
    '''Dance of the miscellaneous journals that use volume-issue-page in their
        URL construction

         :param: pma (PubMedArticle object)
         :param: verify (bool) [default: True]
         :return: url (string)
         :raises: AccessDenied, NoPDFLink
    '''
    jrnl = standardize_journal_name(pma.journal)
    pma = rectify_pma_for_vip_links(pma)  #raises NoPDFLink if missing data.
    url = vip_format.format(host=vip_journals[jrnl]['host'], a=pma)

    if verify:
        verify_pdf_url(url)
    return url

def the_vip_nonstandard_shake(pma, verify=True):
    '''Dance of the miscellaneous journals that use volume-issue-page in their
        URL construction (but are a little different).

         :param: pma (PubMedArticle object)
         :param: verify (bool) [default: True]
         :return: url (string)
         :raises: AccessDenied, NoPDFLink
    '''
    jrnl = standardize_journal_name(pma.journal)
    pma = rectify_pma_for_vip_links(pma)  #raises NoPDFLink if missing data.
    url = vip_journals_nonstandard[jrnl].format(a=pma)

    if verify:
        verify_pdf_url(url)
    return url
 

def the_pii_polka(pma, verify=True):
    '''Dance of the miscellaneous journals that use a PII in their URL construction
        in their URL construction.

         :param: pma (PubMedArticle object)
         :param: verify (bool) [default: True]
         :return: url (string)
         :raises: AccessDenied, NoPDFLink
    '''
    jrnl = standardize_journal_name(pma.journal)
    if pma.pii:
        url = simple_formats_pii[jrnl].format(a=pma)
    else:
        raise NoPDFLink('MISSING: pii missing from PubMedArticle XML (pii format)')

    if url:
        res = requests.get(url)
        if res.text.find('Access Denial') > -1:
            raise AccessDenied('DENIED: Access Denied by ScienceDirect (%s)' % url)

    if verify:
        verify_pdf_url(url)
    return url


def the_jci_jig(pma, verify=True):
    '''Dance of the Journal of Clinical Investigation, which should be largely free.

         :param: pma (PubMedArticle object)
         :param: verify (bool) [default: True]
         :return: url (string)
         :raises: AccessDenied, NoPDFLink
    '''
    # approach: pii with dx.doi.org fallback to get pdf "view" page; scrape pdf download link.
    if pma.pii:
        starturl = doi_templates['jci'].format(a=pma)
    elif pma.doi:
        starturl = the_doi_2step(pma.doi)
        starturl = starturl + '/pdf'
    else:
        raise NoPDFLink('MISSING: pii, doi (doi lookup failed)')

    # Iter 1: do this until we see it stop working. (Iter 2: scrape download link from page.)
    url = starturl.replace('/pdf', '/version/1/pdf/render')
    if verify:
        verify_pdf_url(url, 'JCI')
    return url

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
    response = requests.get(starturl)
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
        res = requests.get(starturl)
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

def the_biomed_calypso(pma, verify=False):
    '''Note: verification turned off by default because BMC is an all-open-access publisher.

       (You may still like to use verify=True to make sure it's a valid link.)

         :param: pma (PubMedArticle object)
         :param: verify (bool) [default: False]
         :return: url (string)
         :raises: AccessDenied, NoPDFLink
    '''
    baseid = pma.doi if pma.doi else pma.pii
    if baseid:
        article_id = baseid.split('/')[1]
    else:
        raise NoPDFLink('MISSING: doi needed for BMC article')
    url = BMC_format.format(aid=article_id)
    if verify:
        verify_pdf_url(url, 'BMC')
    return url


def the_scielo_chula(pma, verify=True):
    '''SciELO: The Scientific Electronic Library Online

    SciELO is an electronic library covering a selected collection of Brazilian
    scientific journals.

    Examples:
        23657305: pii = S0004-28032013000100035
            http://www.scielo.br/scielo.php?script=sci_arttext&pid=S0004-28032013000100035
            http://www.scielo.br/pdf/ag/v50n1/0004-2803-ag-50-01-35.pdf
    '''
    page_text = None
    baseurl_pii = 'http://www.scielo.br/scielo.php?script=sci_arttext&pid=%s'
    if pma.pii:
        response = requests.get(baseurl_pii % pma.pii)
        if response.ok:
            page_text = response.content

    if page_text is None:
        if pma.doi:
            response = requests.get(the_doi_2step(pma.doi))
            if response.ok:
                page_text = response.content
        else:
            raise NoPDFLink('MISSING: pii or doi needed for SciELO lookup.')

    if page_text:
        pdf_url = None
        head = etree.fromstring(page_text, HTMLParser()).getchildren()[0]
        for elem in head.findall('meta'):
            if elem.get('name') == 'citation_pdf_url':
                pdf_url = elem.get('content')

        if pdf_url:
            if verify:
                verify_pdf_url(pdf_url)
            return pdf_url
        else:
            #TODO: some other fallback manoeuvre?
            raise NoPDFLink('TXERROR: SciELO article page lacks PDF url. (See %s)' % response.url)

    else:
        raise NoPDFLink('TXERROR: SciELO page load responded with not-ok status: %i' % response.status_code)


def the_aaas_tango(pma, verify=True):
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
    res = requests.get(baseurl)
    pdfurl = res.url.replace('.long', '.full') + '.pdf'

    if not verify:
        return pdfurl

    response = requests.get(pdfurl)
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
        print("SUBMITTING TO AAAS")
        print(payload)

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

def the_jama_dance(pma, verify=True):
    '''  :param: pma (PubMedArticle object)
         :param: verify (bool) [default: True]
         :return: url (string)
         :raises: AccessDenied, NoPDFLink
    '''
    if not pma.doi:
        raise NoPDFLink('MISSING: doi needed for JAMA article.')

    baseurl = the_doi_2step(pma.doi)
    res = requests.get(baseurl)
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

def the_jstage_dive(pma, verify=True):
    '''  :param: pma (PubMedArticle object)
         :param: verify (bool) [default: True]
         :return: url (string)
         :raises: AccessDenied, NoPDFLink
    '''
    if pma.doi:
        url = the_doi_2step(pma.doi)
        res = requests.get(url)
        if 'jstage' in res.url:
            url = res.url.replace('_article', '_pdf')
            pdfpos = url.find('_pdf')
            # remove everything after the "_pdf" part
            url = url[:pdfpos+4]
    else:
        raise NoPDFLink('MISSING: doi for dx.doi.org lookup to get jstage link')

    if verify:
        verify_pdf_url(url, 'jstage')
    return url


def the_wiley_shuffle(pma, verify=True):
    '''Returns a PDF link to an article from a Wiley-published journal.

    Note: Wiley sometimes buries PDF links in HTML pages we have to parse first.
    Turning off verification (verify=False) may return only a superficial link.
         
         :param: pma (PubMedArticle object)
         :param: verify (bool) [default: True]
         :return: url (string)
         :raises: AccessDenied, NoPDFLink
    '''
    url = doi_templates['wiley'].format(a=pma)
    if not verify:
        return url

    # wiley sometimes buries PDF links in HTML pages we have to parse.
    res = requests.get(url)
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


def the_lancet_tango(pma, verify=True):
    '''  :param: pma (PubMedArticle object)
         :param: verify (bool) [default: True]
         :return: url (string)
         :raises: AccessDenied, NoPDFLink
    '''
    url_template = doi_templates['lancet']
    jrnl = standardize_journal_name(pma.journal)

    if not pma.pii and pma.doi:
        pma.pii = pma.doi.split('/')[1]
    elif not pma.pii and not pma.doi:
        raise NoPDFLink('MISSING: pii, doi (doi lookup failed)')

    # if we got here, we should have a pii.
    url = url_template.format(a=pma, ja=lancet_journals[jrnl]['ja'])
    if verify:
        verify_pdf_url(url, 'Lancet')
    return url

def the_nature_ballet(pma, verify=True):
    '''  :param: pma (PubMedArticle object)
         :param: verify (bool) [default: True]
         :return: url (string)
         :raises: AccessDenied, NoPDFLink
    '''
    url = ''
    if pma.doi:
        try:
            starturl = the_doi_2step(pma.doi)
            url = starturl.replace('html', 'pdf').replace('abs', 'pdf').replace('full', 'pdf')
        except NoPDFLink:
            # alright, let's try the pii route.
            pass

    if url == '':
        if pma.pii:
            url = nature_format.format(a=pma, ja=nature_journals[standardize_journal_name(pma.journal)]['ja'])
        else:
            if pma.doi:
                raise NoPDFLink('MISSING: pii, TXERROR: dx.doi.org resolution failed for doi %s' % pma.doi)
            else:
                raise NoPDFLink('MISSING: pii, doi')

    if verify:
        verify_pdf_url(url, 'Nature')
    return url


PMC_PDF_URL = 'https://www.ncbi.nlm.nih.gov/pmc/articles/pmid/{a.pmid}/pdf'
EUROPEPMC_PDF_URL = 'http://europepmc.org/backend/ptpmcrender.fcgi?accid=PMC{a.pmc}&blobtype=pdf'
def the_pmc_twist(pma, verify=True, use_nih=False):
    '''Look up article in EuropePMC.org.  If not found there, fall back to NIH (if use_nih
    is True).

       Note: verification highly recommended. EuropePMC has most articles, but not everything.

         :param: pma (PubMedArticle object)
         :param: verify (bool) [default: True]
         :param: use_nih (bool) [default: False]
         :return: url
         :raises: NoPDFLink
    '''
    if pma.history.get('pmc-release', None):
        # marked "PAYWALL" here because FindIt will automatically retry such cached entries
        raise NoPDFLink('PAYWALL: pmc article in embargo until %s' % pma.history['pmc-release'].strftime('%Y-%m-%d'))

    url = EUROPEPMC_PDF_URL.format(a=pma)

    if not verify:
        return url

    try:
        verify_pdf_url(url, 'EuropePMC')
        return url

    except (NoPDFLink, AccessDenied):
        # Fallback to using NIH.gov if we're allowing it.        
        if use_nih:
            #   URL block might be discerned by grepping for this:
            #
            #   <div class="el-exception-reason">Bulk downloading of content by IP address [162.217...,</div>
            url = PMC_PDF_URL.format(a=pma)
            verify_pdf_url(url, 'NIH (EuropePMC fallback)')
            return url
    raise NoPDFLink('TXERROR: could not get PDF from EuropePMC.org and USE_NIH set to False')


def the_springer_shag(pma, verify=True):
    '''  :param: pma (PubMedArticle object)
         :param: verify (bool) [default: True]
         :return: url
         :raises: AccessDenied, NoPDFLink
    '''
    # start: http://link.springer.com/article/10.1007%2Fs13238-015-0153-5
    # return: http://link.springer.com/content/pdf/10.1007%2Fs13238-015-0153-5.pdf
    if pma.doi:
        baseurl = the_doi_2step(pma.doi)
    else:
        raise NoPDFLink('MISSING: doi (doi lookup failed)')
    url = baseurl.replace('article', 'content/pdf') + '.pdf'

    if verify:
        verify_pdf_url(url, 'Springer')
    return url

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


def the_spandidos_lambada(pma, verify=True):
    '''  :param: pma (PubMedArticle object)
         :param: verify (bool) [default: True]
         :return: url
         :raises: AccessDenied, NoPDFLink
    '''
    jrnl = standardize_journal_name(pma.journal)
    baseurl = None
    try:
        pma = rectify_pma_for_vip_links(pma)  #raises NoPDFLink if missing data
        url = spandidos_format.format(ja=spandidos_journals[jrnl]['ja'], a=pma)
    except NoPDFLink:
        # let doi2step exceptions fall to calling function
        if pma.doi:
            baseurl = the_doi_2step(pma.doi)
            url = baseurl + '/download'
        else:
            raise NoPDFLink('MISSING: vip, doi - volume and/or issue missing from PubMedArticle; doi lookup failed.')

    if verify:
        verify_pdf_url(url, 'Spandidos')
    return url


def the_wolterskluwer_volta(pma, verify=True):
    '''  :param: pma (PubMedArticle object)
         :param: verify (bool) [default: True]
         :return: url
         :raises: AccessDenied, NoPDFLink
    '''
    doiurl = 'http://content.wkhealth.com/linkback/openurl?doi=%s'
    volissurl = 'http://content.wkhealth.com/linkback/openurl?issn={a.issn}&volume={a.volume}&issue={a.issue}&spage={a.first_page}'
    if pma.doi:
        baseurl = requests.get(doiurl % pma.doi).url
    elif pma.issn:
        pma = rectify_pma_for_vip_links(pma)  #raises NoPDFLink if missing data
        baseurl = requests.get(volissurl.format(a=pma)).url
        
    res = requests.get(baseurl)
    tree = etree.fromstring(res.content, HTMLParser())
    try:
        item = tree.cssselect('li.ej-box-01-body-li-article-tools-pdf')[0]
    except IndexError:
        raise NoPDFLink('DENIED: wolterskluwer did not provide PDF link for this article')
    link = item.getchildren()[0]
    url = link.get('href')
    if verify:
        verify_pdf_url(url)
    return url


def the_biochemsoc_saunter(pma, verify=True):
    '''  :param: pma (PubMedArticle object)
         :param: verify (bool) [default: True]
         :return: url
         :raises: AccessDenied, NoPDFLink
    '''
    jrnl = standardize_journal_name(pma.journal)
    pma = rectify_pma_for_vip_links(pma)  #raises NoPDFLink if missing data 
    host = biochemsoc_journals[jrnl]['host']
    url = biochemsoc_format.format(a=pma, host=host, ja=biochemsoc_journals[jrnl]['ja'])
    if verify:
        verify_pdf_url(url, 'biochemsoc')
    return url

def the_cell_pogo(pma, verify=True):
    '''  :param: pma (PubMedArticle object)
         :param: verify (bool) [default: True]
         :return: url
         :raises: AccessDenied, NoPDFLink
    '''
    jrnl = standardize_journal_name(pma.journal)
    if pma.pii:
        # the front door
        url = cell_format.format(a=pma, ja=cell_journals[jrnl]['ja'],
                                     pii=remove_chars(pma.pii, '-()'))
        if verify:
            verify_pdf_url(url, 'Cell')
        return url
    else:
        # let the SD function raise Exceptions
        return the_sciencedirect_disco(pma, verify)

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

    html = requests.get(url)
    res = requests.get(url)
    if 'html' in res.headers['content-type']:
        from IPython import embed; embed()

    raise NoPDFLink('Not done writing the_endo_mambo! Stay tuned')

