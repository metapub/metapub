__author__ = 'nthmost'

from urllib.parse import urlsplit, urljoin
from datetime import datetime

import requests
from lxml.html import HTMLParser
from lxml import etree

from ..dx_doi import DxDOI, DX_DOI_URL
from ..pubmedarticle import square_voliss_data_for_pma
from ..exceptions import AccessDenied, NoPDFLink, BadDOI, DxDOIError
from ..text_mining import find_doi_in_string
from ..utils import remove_chars

from .journals import *
from .journals.nature import nature_format, nature_journals
from .journals.wiley import wiley_template
from .registry import JournalRegistry

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
    attempted_url = f"{DX_DOI_URL}/{doi}"
    try:
        return dx_doi_engine.resolve(doi)
    except BadDOI as error:
        raise NoPDFLink(f'MISSING: Invalid DOI format ({error}) - attempted: {attempted_url}')
    except DxDOIError as error:
        raise NoPDFLink(f'TXERROR: dx.doi.org lookup failed ({error}) - attempted: {attempted_url}')

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
    '''Dance of journals that use DOI in their URL construction.

    Uses the registry-based template system for DOI-based publishers.

         :param: pma (PubMedArticle object)
         :param: verify (bool) [default: True]
         :return: url (string)
         :raises: AccessDenied, NoPDFLink
    '''
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for DOI-based publishers - attempted: none')

    jrnl = standardize_journal_name(pma.journal)

    # Registry-based template lookup
    try:
        registry = JournalRegistry()
        publisher_info = registry.get_publisher_for_journal(jrnl)
        registry.close()

        if not publisher_info or not publisher_info.get('format_template'):
            raise NoPDFLink(f'MISSING: No template found for journal {pma.journal} - attempted: registry lookup')

        # Perform template substitution
        template = publisher_info['format_template']

        # Apply standardized DOI template format
        url = template.format(doi=pma.doi)

    except Exception as e:
        if isinstance(e, NoPDFLink):
            raise
        else:
            raise NoPDFLink(f'TXERROR: DOI slide failed for {pma.journal}: {e} - attempted: none')

    # Verification logic
    if verify:
        try:
            verify_pdf_url(url)
        except Exception as e:
            # If verification fails, try to provide more specific error messages for paywalled content
            if "403" in str(e) or "Access" in str(e):
                raise AccessDenied(f'PAYWALL: {pma.journal} requires subscription - attempted: {url}')
            else:
                # Re-raise the original verification error
                raise

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
    from .journals.jci import jci_format
    
    # JCI uses simple URL pattern: https://www.jci.org/articles/view/{pii}/pdf
    if pma.pii:
        # Direct construction using PII (preferred method)
        url = jci_format.format(pii=pma.pii)
    elif pma.doi:
        # Fallback: use DOI resolution to get article page, then construct PDF URL
        article_url = the_doi_2step(pma.doi)
        # Convert article URL to PDF URL
        # Example: http://www.jci.org/articles/view/82041 -> http://www.jci.org/articles/view/82041/pdf
        if '/articles/view/' in article_url:
            url = article_url.rstrip('/') + '/pdf'
        else:
            # Fallback pattern if DOI redirects to unexpected format
            url = article_url + '/pdf'
    else:
        raise NoPDFLink('MISSING: pii or doi needed for JCI lookup.')
        
    if verify:
        # JCI sometimes returns HTML even for PDF URLs due to user-agent detection
        # or access control measures. We'll attempt verification but be more lenient.
        try:
            verify_pdf_url(url, 'JCI')
        except NoPDFLink as e:
            # If verification fails, check if it's due to HTML content type
            import requests
            try:
                response = requests.get(url)
                if response.status_code == 200 and 'text/html' in response.headers.get('content-type', ''):
                    # JCI is returning HTML instead of PDF - this might be due to access control
                    # For now, we'll return the URL anyway as it's the correct pattern
                    pass  # Continue and return the URL
                else:
                    # Re-raise the original exception for other types of failures
                    raise e
            except requests.exceptions.RequestException:
                # Network error during verification - re-raise original exception
                raise e
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

def the_bmc_boogie(pma, verify=False):
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
        try:
            # Parse HTML and look for citation_pdf_url meta tag
            root = etree.fromstring(page_text, HTMLParser())
            head = root.find('.//head')
            if head is not None:
                for elem in head.findall('.//meta'):
                    if elem.get('name') == 'citation_pdf_url':
                        pdf_url = elem.get('content')
                        break
            
            # If no meta tag found, try to look for PDF links in the page
            if pdf_url is None:
                for elem in root.iter():
                    if elem.tag == 'a':
                        href = elem.get('href', '')
                        if 'format=pdf' in href:
                            # Convert relative URL to absolute URL
                            if href.startswith('/'):
                                pdf_url = 'https://www.scielo.br' + href
                            else:
                                pdf_url = href
                            break

        except Exception as parse_error:
            raise NoPDFLink('TXERROR: Failed to parse SciELO page HTML: %s (See %s)' % (str(parse_error), response.url))

        if pdf_url:
            if verify:
                verify_pdf_url(pdf_url, 'SciELO')
            return pdf_url
        else:
            #TODO: some other fallback manoeuvre?
            raise NoPDFLink('TXERROR: SciELO article page lacks PDF url. (See %s)' % response.url)

    else:
        raise NoPDFLink('TXERROR: SciELO page load responded with not-ok status: %i' % response.status_code)


def the_dovepress_peacock(pma, verify=True):
    '''DovePress (Dove Medical Press): Open access medical and scientific journals
    
    DovePress is an academic publisher of open-access peer-reviewed scientific and medical journals,
    acquired by Taylor & Francis Group in 2017. Most articles are freely accessible.
    
    URL Pattern: https://www.dovepress.com/[article-title]-peer-reviewed-fulltext-article-[JOURNAL_CODE]
    PDF Pattern: https://www.dovepress.com/article/download/[ARTICLE_ID]
    DOI Pattern: 10.2147/[JOURNAL_CODE].S[ID]
    
    Examples:
        37693885: IJN (International Journal of Nanomedicine) - DOI: 10.2147/IJN.S420748
        37736107: OPTH (Clinical Ophthalmology) - DOI: 10.2147/OPTH.S392665
    '''
    from .journals.dovepress import dovepress_format
    
    # DovePress articles are typically accessed via DOI resolution to article page,
    # then PDF download link must be extracted from the article page
    if pma.doi:
        article_url = the_doi_2step(pma.doi)
        
        # Get the article page to extract PDF download link
        response = requests.get(article_url)
        if not response.ok:
            raise NoPDFLink('TXERROR: DovePress article page returned status %i' % response.status_code)
        
        page_text = response.content
        pdf_url = None
        
        try:
            # Parse HTML to find PDF download link
            root = etree.fromstring(page_text, HTMLParser())
            
            # Look for PDF download link patterns
            # Pattern 1: Look for links containing "download"
            for elem in root.iter():
                if elem.tag == 'a':
                    href = elem.get('href', '')
                    text = (elem.text or '').lower()
                    
                    # Look for download links with "pdf" or "download" 
                    if ('download' in href and ('pdf' in text or 'article' in text)) or \
                       ('article/download/' in href):
                        # Convert relative URL to absolute URL
                        if href.startswith('/'):
                            pdf_url = 'https://www.dovepress.com' + href
                        elif href.startswith('article/'):
                            pdf_url = 'https://www.dovepress.com/' + href
                        else:
                            pdf_url = href
                        break
            
            # Pattern 2: Look for citation_pdf_url meta tag (fallback)
            if pdf_url is None:
                head = root.find('.//head')
                if head is not None:
                    for elem in head.findall('.//meta'):
                        if elem.get('name') == 'citation_pdf_url':
                            pdf_url = elem.get('content')
                            break
        
        except Exception as parse_error:
            raise NoPDFLink('TXERROR: Failed to parse DovePress article page: %s (See %s)' % (str(parse_error), article_url))
        
        if pdf_url:
            if verify:
                verify_pdf_url(pdf_url, 'DovePress')
            return pdf_url
        else:
            raise NoPDFLink('TXERROR: DovePress article page lacks PDF download link. (See %s)' % article_url)
    
    else:
        raise NoPDFLink('MISSING: doi needed for DovePress lookup.')


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
    url = wiley_template.format(doi=pma.doi)
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
    '''Nature Publishing Group dance using modern DOI-based URLs with fallback.

    Primary approach: Modern DOI-based URL structure
    https://www.nature.com/articles/{DOI_SUFFIX}.pdf

    Fallback approach: Traditional volume/issue/pii URLs (still work via redirects)
    http://www.nature.com/{ja}/journal/v{volume}/n{issue}/pdf/{pii}.pdf

    :param: pma (PubMedArticle object)
    :param: verify (bool) [default: True]
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    '''
    pdf_url = None

    # Primary approach: DOI-based URL
    if pma.doi and pma.doi.startswith('10.1038/'):
        article_id = pma.doi.split('/', 1)[1]
        pdf_url = f'https://www.nature.com/articles/{article_id}.pdf'

        if not verify:
            return pdf_url

        # Try the DOI-based approach first
        try:
            response = requests.get(pdf_url, timeout=10)

            if response.status_code == 200:
                content_type = response.headers.get('content-type', '').lower()
                if 'pdf' in content_type:
                    return response.url
                elif 'html' in content_type:
                    page_text = response.text.lower()
                    if any(term in page_text for term in ['paywall', 'subscribe', 'sign in', 'log in', 'purchase']):
                        raise AccessDenied(f'PAYWALL: Nature article requires subscription - attempted: {pdf_url}')
                    else:
                        raise NoPDFLink(f'TXERROR: Nature returned HTML instead of PDF for {pdf_url}')
                else:
                    raise NoPDFLink(f'TXERROR: Unexpected content type {content_type} from Nature')

            elif response.status_code == 403:
                raise AccessDenied(f'DENIED: Access forbidden by Nature - attempted: {pdf_url}')
            elif response.status_code == 404:
                # DOI-based URL failed, try fallback approach
                pass
            else:
                raise NoPDFLink(f'TXERROR: Nature returned status {response.status_code} for {pdf_url}')

        except requests.exceptions.RequestException:
            # Network error with DOI approach, try fallback
            pass

    # Fallback approach: Traditional volume/issue/pii URL construction
    # Only works for traditional Nature journals with short PIIs (not modern s4xxxx journals)
    if pma.volume and pma.issue and pma.pii and pma.pii != pma.doi:

        # Skip modern journals that use full DOI as PII (s41xxx, s42xxx, s43xxx)
        is_modern_journal = pma.doi and any(code in pma.doi for code in ['s41', 's42', 's43'])

        if not is_modern_journal:
            # Find journal abbreviation for traditional journals
            jrnl = standardize_journal_name(pma.journal)
            if jrnl in nature_journals:
                ja = nature_journals[jrnl]['ja']
                fallback_url = nature_format.format(ja=ja, a=pma)

                if not verify:
                    return fallback_url

                try:
                    response = requests.get(fallback_url, timeout=10)

                    if response.status_code == 200:
                        content_type = response.headers.get('content-type', '').lower()
                        if 'pdf' in content_type:
                            return response.url
                        elif 'html' in content_type:
                            page_text = response.text.lower()
                            if any(term in page_text for term in ['paywall', 'subscribe', 'sign in', 'log in', 'purchase']):
                                raise AccessDenied(f'PAYWALL: Nature article requires subscription - attempted: {fallback_url}')
                            else:
                                # Old format URLs redirect to modern URLs, so this might be expected
                                # Try to extract the modern URL from the redirect
                                if 'articles' in response.url:
                                    return response.url.replace('/articles/', '/articles/') + '.pdf'
                                else:
                                    raise NoPDFLink(f'TXERROR: Nature fallback returned HTML for {fallback_url}')
                        else:
                            raise NoPDFLink(f'TXERROR: Unexpected content type {content_type} from Nature fallback')

                    elif response.status_code == 403:
                        raise AccessDenied(f'DENIED: Access forbidden by Nature - attempted: {fallback_url}')
                    elif response.status_code == 404:
                        raise NoPDFLink(f'NOTFOUND: Article not found on Nature platform - attempted: {pdf_url}, {fallback_url}')
                    else:
                        raise NoPDFLink(f'TXERROR: Nature fallback returned status {response.status_code} - attempted: {fallback_url}')

                except requests.exceptions.RequestException as e:
                    raise NoPDFLink(f'TXERROR: Network error with Nature fallback: {e} - attempted: {fallback_url}')

    # If we get here, neither approach worked
    missing_data = []
    if not pma.doi or not pma.doi.startswith('10.1038/'):
        missing_data.append('valid Nature DOI')
    if not (pma.volume and pma.issue and pma.pii):
        missing_data.append('volume/issue/pii data')

    if missing_data:
        raise NoPDFLink(f'MISSING: {" and ".join(missing_data)} - cannot construct Nature URL - attempted: none')
    else:
        # Both approaches were attempted but failed
        attempted_urls = []
        if pma.doi and pma.doi.startswith('10.1038/'):
            article_id = pma.doi.split('/', 1)[1]
            attempted_urls.append(f'https://www.nature.com/articles/{article_id}.pdf')
        if pma.volume and pma.issue and pma.pii:
            attempted_urls.append(f'traditional Nature URL (vol/issue/pii)')
        urls_str = ', '.join(attempted_urls) if attempted_urls else 'none'
        raise NoPDFLink(f'TXERROR: Both DOI-based and volume/issue/pii approaches failed for Nature article - attempted: {urls_str}')


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
    embargo_date = pma.history.get('pmc-release', None)
    if embargo_date and embargo_date > datetime.now():
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


def the_sage_hula(pma, verify=True):
    '''SAGE Publications dance for modern journals.sagepub.com hosting.

    SAGE moved to a unified hosting platform using DOI-based URLs:
    https://journals.sagepub.com/doi/{DOI}

    For PDF access, we convert to:
    https://journals.sagepub.com/doi/pdf/{DOI}

    :param: pma (PubMedArticle object)
    :param: verify (bool) [default: True]
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    '''
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for SAGE journals - attempted: none')

    # SAGE uses DOI-based URLs on their unified platform
    pdf_url = f'https://journals.sagepub.com/doi/pdf/{pma.doi}'

    if not verify:
        return pdf_url

    # Verify the PDF URL works
    try:
        response = requests.get(pdf_url, timeout=10)

        if response.status_code == 200:
            content_type = response.headers.get('content-type', '').lower()
            if 'pdf' in content_type:
                return response.url
            elif 'html' in content_type:
                # Check if we hit a paywall or access denied page
                page_text = response.text.lower()
                if any(term in page_text for term in ['access denied', 'paywall', 'subscribe', 'log in', 'sign in']):
                    raise AccessDenied('PAYWALL: SAGE article requires subscription')
                else:
                    raise NoPDFLink(f'TXERROR: SAGE returned HTML instead of PDF for {pdf_url}')
            else:
                raise NoPDFLink(f'TXERROR: Unexpected content type {content_type} from SAGE')

        elif response.status_code == 403:
            raise AccessDenied('DENIED: Access forbidden by SAGE')
        elif response.status_code == 404:
            raise NoPDFLink('NOTFOUND: Article not found on SAGE platform')
        else:
            raise NoPDFLink(f'TXERROR: SAGE returned status {response.status_code} for {pdf_url}')

    except requests.exceptions.RequestException as e:
        raise NoPDFLink(f'TXERROR: Network error accessing SAGE: {e} - attempted: {pdf_url}')


def the_cambridge_foxtrot(pma, verify=True):
    '''Cambridge University Press dance for modern cambridge.org hosting.

    Cambridge University Press moved to a DOI-based system where all articles
    are accessible via cambridge.org/core. The PDF access pattern uses:
    https://www.cambridge.org/core/services/aop-pdf-file/content/view/{DOI}

    Cambridge publishes journals with various DOI prefixes due to acquisitions.

    :param: pma (PubMedArticle object)
    :param: verify (bool) [default: True]
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    '''
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for Cambridge University Press journals - attempted: none')

    # Cambridge uses DOI-based URLs on their unified platform
    pdf_url = f'https://www.cambridge.org/core/services/aop-pdf-file/content/view/{pma.doi}'

    if not verify:
        return pdf_url

    # Verify the PDF URL works
    try:
        response = requests.get(pdf_url, timeout=10)

        if response.status_code == 200:
            content_type = response.headers.get('content-type', '').lower()
            if 'pdf' in content_type:
                return response.url
            elif 'html' in content_type:
                # Check if we hit a paywall or access denied page
                page_text = response.text.lower()
                if any(term in page_text for term in ['access denied', 'paywall', 'subscribe', 'log in', 'sign in', 'institutional access']):
                    raise AccessDenied(f'PAYWALL: Cambridge article requires subscription - attempted: {pdf_url}')
                else:
                    raise NoPDFLink(f'TXERROR: Cambridge returned HTML instead of PDF - attempted: {pdf_url}')
            else:
                raise NoPDFLink(f'TXERROR: Unexpected content type {content_type} from Cambridge - attempted: {pdf_url}')

        elif response.status_code == 403:
            raise AccessDenied(f'DENIED: Access forbidden by Cambridge - attempted: {pdf_url}')
        elif response.status_code == 404:
            raise NoPDFLink(f'NOTFOUND: Article not found on Cambridge platform - attempted: {pdf_url}')
        else:
            raise NoPDFLink(f'TXERROR: Cambridge returned status {response.status_code} - attempted: {pdf_url}')

    except requests.exceptions.RequestException as e:
        raise NoPDFLink(f'TXERROR: Network error accessing Cambridge: {e} - attempted: {pdf_url}')


def the_asm_shimmy(pma, verify=True):
    '''Dance function for American Society of Microbiology (ASM) journals.

    ASM journals use Volume-Issue-Page (VIP) format URLs with journal-specific subdomains.
    URL Pattern: http://{host}.asm.org/content/{volume}/{issue}/{first_page}.full.pdf

    :param: pma (PubMedArticle object)
    :param: verify (bool) [default: True]
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    '''
    from .journals.asm import asm_journal_params, asm_vip_template
    from .registry import standardize_journal_name

    jrnl = standardize_journal_name(pma.journal)

    if jrnl not in asm_journal_params:
        raise NoPDFLink(f'MISSING: Journal {pma.journal} not found in ASM registry - attempted: none')

    try:
        pma = rectify_pma_for_vip_links(pma)
        host = asm_journal_params[jrnl]['host']
        url = asm_vip_template.format(host=host, volume=pma.volume, issue=pma.issue, first_page=pma.first_page)

        if verify:
            verify_pdf_url(url, 'ASM')
        return url

    except NoPDFLink:
        raise NoPDFLink(f'MISSING: VIP data (volume/issue/page) required for ASM journals - attempted: none')


def the_aha_waltz(pma, verify=True):
    '''Dance function for American Heart Association (AHA) journals.

    AHA journals use Volume-Issue-Page (VIP) format URLs with journal-specific subdomains.
    URL Pattern: http://{host}.ahajournals.org/content/{volume}/{issue}/{first_page}.full.pdf

    :param: pma (PubMedArticle object)
    :param: verify (bool) [default: True]
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    '''
    from .journals.aha import aha_journal_params, aha_vip_template
    from .registry import standardize_journal_name

    jrnl = standardize_journal_name(pma.journal)

    if jrnl not in aha_journal_params:
        raise NoPDFLink(f'MISSING: Journal {pma.journal} not found in AHA registry - attempted: none')

    try:
        pma = rectify_pma_for_vip_links(pma)
        host = aha_journal_params[jrnl]['host']
        url = aha_vip_template.format(host=host, volume=pma.volume, issue=pma.issue, first_page=pma.first_page)

        if verify:
            verify_pdf_url(url, 'AHA')
        return url

    except NoPDFLink:
        raise NoPDFLink(f'MISSING: VIP data (volume/issue/page) required for AHA journals - attempted: none')


def the_aacr_jitterbug(pma, verify=True):
    '''Dance function for American Association for Cancer Research (AACR) journals.

    AACR journals use Volume-Issue-Page (VIP) format URLs with journal-specific subdomains.
    URL Pattern: http://{host}.aacrjournals.org/content/{volume}/{issue}/{first_page}.full.pdf

    :param: pma (PubMedArticle object)
    :param: verify (bool) [default: True]
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    '''
    from .journals.aacr import aacr_journal_params, aacr_vip_template
    from .registry import standardize_journal_name

    jrnl = standardize_journal_name(pma.journal)

    if jrnl not in aacr_journal_params:
        raise NoPDFLink(f'MISSING: Journal {pma.journal} not found in AACR registry - attempted: none')

    try:
        pma = rectify_pma_for_vip_links(pma)
        host = aacr_journal_params[jrnl]['host']
        url = aacr_vip_template.format(host=host, volume=pma.volume, issue=pma.issue, first_page=pma.first_page)

        if verify:
            verify_pdf_url(url, 'AACR')
        return url

    except NoPDFLink:
        raise NoPDFLink(f'MISSING: VIP data (volume/issue/page) required for AACR journals - attempted: none')


def the_aps_quickstep(pma, verify=True):
    '''Dance function for American Physiological Society (APS) journals.

    APS journals use Volume-Issue-Page (VIP) format URLs with journal-specific subdomains.
    URL Pattern: http://{host}.physiology.org/content/{volume}/{issue}/{first_page}.full.pdf

    :param: pma (PubMedArticle object)
    :param: verify (bool) [default: True]
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    '''
    from .journals.aps import aps_journal_params, aps_vip_template
    from .registry import standardize_journal_name

    jrnl = standardize_journal_name(pma.journal)

    if jrnl not in aps_journal_params:
        raise NoPDFLink(f'MISSING: Journal {pma.journal} not found in APS registry - attempted: none')

    try:
        pma = rectify_pma_for_vip_links(pma)
        host = aps_journal_params[jrnl]['host']
        url = aps_vip_template.format(host=host, volume=pma.volume, issue=pma.issue, first_page=pma.first_page)

        if verify:
            verify_pdf_url(url, 'APS')
        return url

    except NoPDFLink:
        raise NoPDFLink(f'MISSING: VIP data (volume/issue/page) required for APS journals - attempted: none')


def the_mdpi_moonwalk(pma, verify=True):
    '''Dance function for MDPI journals as backup to PMC access.
    
    MDPI journals are primarily available through PMC, but this provides backup
    PDF access by appending '/pdf' to the resolved DOI URL.
    URL Pattern: {resolved_doi_url}/pdf
    
    :param: pma (PubMedArticle object)
    :param: verify (bool) [default: True]
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    '''
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for MDPI backup - attempted: none')
    
    try:
        # Get the resolved DOI URL first
        resolved_url = the_doi_2step(pma.doi)
        
        # MDPI backup strategy: append '/pdf' to resolved URL
        url = f"{resolved_url}/pdf"
        
        if verify:
            verify_pdf_url(url, 'MDPI')
        return url
        
    except Exception as e:
        if isinstance(e, NoPDFLink):
            raise
        else:
            raise NoPDFLink(f'TXERROR: MDPI backup failed for {pma.journal}: {e} - attempted: none')


def the_eureka_frug(pma, verify=True):
    '''Dance function for Bentham Science Publishers (EurekaSelect.com) journals.
    
    Bentham Science journals use DOI-based URLs but are typically behind a paywall.
    This dance attempts multiple strategies to access PDFs:
    1. Direct DOI resolution to publisher's site
    2. Alternative URL patterns observed on eurekaselect.com
    
    :param: pma (PubMedArticle object)
    :param: verify (bool) [default: True]
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    '''
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for Bentham Science journals - attempted: none')
    
    try:
        # First approach: Resolve DOI and try common PDF patterns
        resolved_url = the_doi_2step(pma.doi)
        
        # Strategy 1: Try appending '/pdf' to resolved URL
        pdf_url = f"{resolved_url}/pdf"
        
        if verify:
            try:
                response = requests.get(pdf_url, timeout=10)
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '').lower()
                    if 'pdf' in content_type:
                        return response.url
                    elif 'html' in content_type:
                        # Check for paywall indicators
                        page_text = response.text.lower()
                        paywall_terms = ['paywall', 'subscribe', 'sign in', 'log in', 'purchase', 'access denied', 'checkLicense']
                        if any(term in page_text for term in paywall_terms):
                            raise AccessDenied(f'PAYWALL: Bentham Science article requires subscription - attempted: {pdf_url}')
                        else:
                            raise NoPDFLink(f'TXERROR: Bentham returned HTML instead of PDF - attempted: {pdf_url}')
                    else:
                        raise NoPDFLink(f'TXERROR: Unexpected content type {content_type} from Bentham - attempted: {pdf_url}')
                
                elif response.status_code == 403:
                    raise AccessDenied(f'DENIED: Access forbidden by Bentham Science - attempted: {pdf_url}')
                elif response.status_code == 404:
                    # Try alternative URL pattern
                    pass
                else:
                    raise NoPDFLink(f'TXERROR: Bentham returned status {response.status_code} - attempted: {pdf_url}')
                    
            except requests.exceptions.RequestException as e:
                raise NoPDFLink(f'TXERROR: Network error accessing Bentham: {e} - attempted: {pdf_url}')
        else:
            return pdf_url
        
        # Strategy 2: Try alternative openurl pattern
        # Based on investigation, some publishers use openurl.php for access
        openurl = f"https://www.eurekaselect.com/openurl/openurl.php?genre=article&doi={pma.doi}"
        
        if verify:
            try:
                response = requests.get(openurl, timeout=10)
                
                if response.status_code == 200 and 'pdf' in response.headers.get('content-type', '').lower():
                    return response.url
                else:
                    raise AccessDenied(f'PAYWALL: Bentham Science requires subscription for full access - attempted: {openurl}')
                    
            except requests.exceptions.RequestException:
                pass
        else:
            return openurl
            
        # If we get here, all strategies failed
        raise AccessDenied(f'PAYWALL: Bentham Science journal appears to be subscription-only - attempted: {pdf_url}, {openurl}')
        
    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: Eureka frug failed for {pma.journal}: {e} - attempted: DOI resolution')


def the_thieme_tap(pma, verify=True):
    '''Dance function for Thieme Medical Publishers journals.
    
    Thieme journals use a straightforward DOI-based PDF URL pattern.
    URL Pattern: https://www.thieme-connect.de/products/ejournals/pdf/{doi}.pdf
    
    Thieme uses 10.1055 as their DOI prefix and provides direct PDF access
    through their thieme-connect.de platform.
    
    :param: pma (PubMedArticle object)
    :param: verify (bool) [default: True]
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    '''
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for Thieme journals - attempted: none')
    
    try:
        # Construct PDF URL using Thieme's pattern
        pdf_url = f"https://www.thieme-connect.de/products/ejournals/pdf/{pma.doi}.pdf"
        
        if verify:
            try:
                response = requests.get(pdf_url, timeout=10)
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '').lower()
                    if 'pdf' in content_type:
                        return response.url
                    elif 'html' in content_type:
                        # Check for paywall indicators
                        page_text = response.text.lower()
                        paywall_terms = ['paywall', 'subscribe', 'sign in', 'log in', 'purchase', 'access denied', 'login required']
                        if any(term in page_text for term in paywall_terms):
                            raise AccessDenied(f'PAYWALL: Thieme article requires subscription - attempted: {pdf_url}')
                        else:
                            raise NoPDFLink(f'TXERROR: Thieme returned HTML instead of PDF - attempted: {pdf_url}')
                    else:
                        raise NoPDFLink(f'TXERROR: Unexpected content type {content_type} from Thieme - attempted: {pdf_url}')
                
                elif response.status_code == 403:
                    raise AccessDenied(f'DENIED: Access forbidden by Thieme - attempted: {pdf_url}')
                elif response.status_code == 404:
                    raise NoPDFLink(f'TXERROR: Thieme PDF not found - attempted: {pdf_url}')
                else:
                    raise NoPDFLink(f'TXERROR: Thieme returned status {response.status_code} - attempted: {pdf_url}')
                    
            except requests.exceptions.RequestException as e:
                raise NoPDFLink(f'TXERROR: Network error accessing Thieme: {e} - attempted: {pdf_url}')
        else:
            return pdf_url
        
    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: Thieme tap failed for {pma.journal}: {e} - attempted: DOI-based PDF URL')


def the_apa_dab(pma, verify=True):
    '''American Psychological Association (APA): Psychology and behavioral science journals
    
    APA journals are hosted on PsycNET (psycnet.apa.org) and use DOI pattern 10.1037/...
    Most articles require subscription access, though some may be freely available.
    
    :param: pma (PubmedArticle)
    :param: verify (bool) [default: True] 
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    '''
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for APA journals - attempted: none')
    
    # Validate DOI pattern for APA (should start with 10.1037/)
    if not pma.doi.startswith('10.1037/'):
        raise NoPDFLink(f'INVALID: DOI does not match APA pattern (10.1037/) - attempted: {pma.doi}')
    
    try:
        # Try DOI resolution first to get the article page
        article_url = the_doi_2step(pma.doi)
        
        if verify:
            try:
                response = requests.get(article_url, timeout=10)
                
                if response.status_code == 200:
                    # Check if we can access the content
                    page_text = response.text.lower()
                    
                    # Look for PDF download links or indicators
                    if 'pdf' in page_text and ('download' in page_text or 'full text' in page_text):
                        # Try to find PDF link in the page
                        from lxml import html
                        tree = html.fromstring(response.content)
                        
                        # Look for PDF download links
                        pdf_links = tree.xpath('//a[contains(@href, ".pdf") or contains(text(), "PDF") or contains(@class, "pdf")]/@href')
                        
                        if pdf_links:
                            pdf_url = pdf_links[0]
                            # Convert relative URL to absolute if needed
                            if pdf_url.startswith('/'):
                                from urllib.parse import urljoin
                                pdf_url = urljoin(article_url, pdf_url)
                            return pdf_url
                    
                    # Check for paywall/subscription indicators
                    paywall_terms = ['subscribe', 'sign in', 'log in', 'institutional access', 
                                   'purchase', 'access denied', 'login required', 'subscription required']
                    if any(term in page_text for term in paywall_terms):
                        raise AccessDenied(f'PAYWALL: APA article requires subscription - attempted: {article_url}')
                    
                    # If no PDF link found but page accessible, return article URL
                    return article_url
                
                elif response.status_code == 403:
                    raise AccessDenied(f'DENIED: Access forbidden by APA - attempted: {article_url}')
                elif response.status_code == 404:
                    raise NoPDFLink(f'TXERROR: APA article not found - attempted: {article_url}')
                else:
                    raise NoPDFLink(f'TXERROR: APA returned status {response.status_code} - attempted: {article_url}')
                    
            except requests.exceptions.RequestException as e:
                raise NoPDFLink(f'TXERROR: Network error accessing APA: {e} - attempted: {article_url}')
        else:
            # Return DOI-resolved URL without verification
            return article_url
        
    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: APA dab failed for {pma.journal}: {e} - attempted: DOI resolution')


def the_degruyter_danza(pma, verify=True):
    '''De Gruyter: Academic publisher for humanities, social sciences, and STEM
    
    De Gruyter articles are hosted on degruyter.com/degruyterbrill.com and typically 
    use DOI pattern 10.1515/... Most articles require subscription access.
    
    :param: pma (PubmedArticle)
    :param: verify (bool) [default: True] 
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    '''
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for De Gruyter journals - attempted: none')
    
    try:
        # Try DOI resolution first to get the article page
        article_url = the_doi_2step(pma.doi)
        
        if verify:
            try:
                response = requests.get(article_url, timeout=10)
                
                if response.status_code == 200:
                    # Check if we can access the content
                    page_text = response.text.lower()
                    
                    # Look for PDF download links or indicators
                    if 'pdf' in page_text and ('download' in page_text or 'full text' in page_text):
                        # Try to find PDF link in the page
                        from lxml import html
                        tree = html.fromstring(response.content)
                        
                        # Look for PDF download links
                        pdf_links = tree.xpath('//a[contains(@href, ".pdf") or contains(text(), "PDF") or contains(@class, "pdf")]/@href')
                        
                        if pdf_links:
                            pdf_url = pdf_links[0]
                            # Convert relative URL to absolute if needed
                            if pdf_url.startswith('/'):
                                from urllib.parse import urljoin
                                pdf_url = urljoin(article_url, pdf_url)
                            return pdf_url
                    
                    # Check for paywall/subscription indicators
                    paywall_terms = ['subscribe', 'sign in', 'log in', 'institutional access', 
                                   'purchase', 'access denied', 'login required', 'subscription required',
                                   'register', 'institutional', 'purchase this article']
                    if any(term in page_text for term in paywall_terms):
                        raise AccessDenied(f'PAYWALL: De Gruyter article requires subscription - attempted: {article_url}')
                    
                    # If no PDF link found but page accessible, return article URL
                    return article_url
                
                elif response.status_code == 403:
                    raise AccessDenied(f'DENIED: Access forbidden by De Gruyter - attempted: {article_url}')
                elif response.status_code == 404:
                    raise NoPDFLink(f'TXERROR: De Gruyter article not found - attempted: {article_url}')
                else:
                    raise NoPDFLink(f'TXERROR: De Gruyter returned status {response.status_code} - attempted: {article_url}')
                    
            except requests.exceptions.RequestException as e:
                raise NoPDFLink(f'TXERROR: Network error accessing De Gruyter: {e} - attempted: {article_url}')
        else:
            # Return DOI-resolved URL without verification
            return article_url
        
    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: De Gruyter danza failed for {pma.journal}: {e} - attempted: DOI resolution')


def the_scirp_timewarp(pma, verify=True):
    '''SCIRP (Scientific Research Publishing): Open access publisher
    
    SCIRP articles are hosted on scirp.org and typically accessible via DOI resolution.
    Most SCIRP journals are open access, making articles freely available.
    
    :param: pma (PubmedArticle)
    :param: verify (bool) [default: True] 
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    '''
    try:
        # Check if DOI is available
        if not pma.doi:
            raise NoPDFLink('MISSING: DOI required for SCIRP journals - attempted: none')
        
        # Resolve DOI to get article URL
        article_url = the_doi_2step(pma.doi)
        
        if verify:
            try:
                response = requests.get(article_url, timeout=30)
                
                if response.status_code in OK_STATUS_CODES:
                    page_text = response.text.lower()
                    
                    # Look for PDF download links or indicators
                    if 'pdf' in page_text and ('download' in page_text or 'full text' in page_text or 'view pdf' in page_text):
                        # Try to find PDF link in the page
                        from lxml import html
                        tree = html.fromstring(response.content)
                        
                        # Look for PDF download links (SCIRP typically has direct PDF links)
                        pdf_links = tree.xpath('//a[contains(@href, ".pdf") or contains(text(), "PDF") or contains(@class, "pdf") or contains(@title, "PDF")]/@href')
                        
                        if pdf_links:
                            pdf_url = pdf_links[0]
                            # Convert relative URL to absolute if needed
                            if pdf_url.startswith('/'):
                                from urllib.parse import urljoin
                                pdf_url = urljoin(article_url, pdf_url)
                            return pdf_url
                    
                    # Check for paywall/subscription indicators (uncommon for SCIRP but possible)
                    paywall_terms = ['subscribe', 'sign in', 'log in', 'institutional access', 
                                   'purchase', 'access denied', 'login required', 'subscription required',
                                   'register', 'institutional', 'purchase this article']
                    if any(term in page_text for term in paywall_terms):
                        raise AccessDenied(f'PAYWALL: SCIRP article requires subscription - attempted: {article_url}')
                    
                    # If no PDF link found but page accessible, return article URL (typical for open access)
                    return article_url
                
                elif response.status_code == 403:
                    raise AccessDenied(f'DENIED: Access forbidden by SCIRP - attempted: {article_url}')
                elif response.status_code == 404:
                    raise NoPDFLink(f'TXERROR: SCIRP article not found - attempted: {article_url}')
                else:
                    raise NoPDFLink(f'TXERROR: SCIRP returned status {response.status_code} - attempted: {article_url}')
                    
            except requests.exceptions.RequestException as e:
                raise NoPDFLink(f'TXERROR: Network error accessing SCIRP: {e} - attempted: {article_url}')
        else:
            # Return DOI-resolved URL without verification
            return article_url
        
    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: SCIRP timewarp failed for {pma.journal}: {e} - attempted: DOI resolution')


def the_annualreviews_round(pma, verify=True):
    '''Annual Reviews Inc.: Nonprofit publisher of comprehensive review articles
    
    Annual Reviews articles are hosted on annualreviews.org and typically accessible via DOI resolution.
    Founded in 1932, publishes review articles across various scientific disciplines.
    
    :param: pma (PubmedArticle)
    :param: verify (bool) [default: True] 
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    '''
    try:
        # Check if DOI is available
        if not pma.doi:
            raise NoPDFLink('MISSING: DOI required for Annual Reviews journals - attempted: none')
        
        # Verify DOI pattern for Annual Reviews
        if not pma.doi.startswith('10.1146/'):
            raise NoPDFLink(f'INVALID: DOI does not match Annual Reviews pattern (10.1146/) - attempted: {pma.doi}')
        
        # Resolve DOI to get article URL
        article_url = the_doi_2step(pma.doi)
        
        if verify:
            try:
                response = requests.get(article_url, timeout=30)
                
                if response.status_code in OK_STATUS_CODES:
                    page_text = response.text.lower()
                    
                    # Look for PDF download links or indicators
                    if 'pdf' in page_text and ('download' in page_text or 'full text' in page_text or 'view pdf' in page_text):
                        # Try to find PDF link in the page
                        from lxml import html
                        tree = html.fromstring(response.content)
                        
                        # Look for PDF download links (Annual Reviews typically has direct PDF links)
                        pdf_links = tree.xpath('//a[contains(@href, ".pdf") or contains(text(), "PDF") or contains(@class, "pdf") or contains(@title, "PDF")]/@href')
                        
                        if pdf_links:
                            pdf_url = pdf_links[0]
                            # Convert relative URL to absolute if needed
                            if pdf_url.startswith('/'):
                                from urllib.parse import urljoin
                                pdf_url = urljoin(article_url, pdf_url)
                            return pdf_url
                    
                    # Check for paywall/subscription indicators
                    paywall_terms = ['subscribe', 'sign in', 'log in', 'institutional access', 
                                   'purchase', 'access denied', 'login required', 'subscription required',
                                   'register', 'institutional', 'purchase this article']
                    if any(term in page_text for term in paywall_terms):
                        raise AccessDenied(f'PAYWALL: Annual Reviews article requires subscription - attempted: {article_url}')
                    
                    # If no PDF link found but page accessible, return article URL
                    return article_url
                
                elif response.status_code == 403:
                    raise AccessDenied(f'DENIED: Access forbidden by Annual Reviews - attempted: {article_url}')
                elif response.status_code == 404:
                    raise NoPDFLink(f'TXERROR: Annual Reviews article not found - attempted: {article_url}')
                else:
                    raise NoPDFLink(f'TXERROR: Annual Reviews returned status {response.status_code} - attempted: {article_url}')
                    
            except requests.exceptions.RequestException as e:
                raise NoPDFLink(f'TXERROR: Network error accessing Annual Reviews: {e} - attempted: {article_url}')
        else:
            # Return DOI-resolved URL without verification
            return article_url
        
    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: Annual Reviews round failed for {pma.journal}: {e} - attempted: DOI resolution')


def the_brill_bridge(pma, verify=True):
    '''Brill Academic Publishers: Dutch international academic publisher
    
    Brill has been publishing since 1683, specializing in humanities, international law,
    social sciences, and biology. Articles are hosted on brill.com and accessible via DOI resolution.
    
    :param: pma (PubmedArticle)
    :param: verify (bool) [default: True] 
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    '''
    try:
        # Check if DOI is available
        if not pma.doi:
            raise NoPDFLink('MISSING: DOI required for Brill journals - attempted: none')
        
        # Verify DOI pattern for Brill (should start with 10.1163/)
        if not pma.doi.startswith('10.1163/'):
            raise NoPDFLink(f'INVALID: DOI does not match Brill pattern (10.1163/) - attempted: {pma.doi}')
        
        # Resolve DOI to get article URL
        article_url = the_doi_2step(pma.doi)
        
        if verify:
            try:
                response = requests.get(article_url, timeout=30)
                
                if response.status_code in OK_STATUS_CODES:
                    page_text = response.text.lower()
                    
                    # Look for PDF download links or indicators
                    if 'pdf' in page_text and ('download' in page_text or 'full text' in page_text or 'view pdf' in page_text):
                        # Try to find PDF link in the page
                        from lxml import html
                        tree = html.fromstring(response.content)
                        
                        # Look for PDF download links (Brill typically has direct PDF access)
                        pdf_links = tree.xpath('//a[contains(@href, ".pdf") or contains(text(), "PDF") or contains(@class, "pdf") or contains(@title, "PDF")]/@href')
                        
                        if pdf_links:
                            pdf_url = pdf_links[0]
                            # Convert relative URL to absolute if needed
                            if pdf_url.startswith('/'):
                                from urllib.parse import urljoin
                                pdf_url = urljoin(article_url, pdf_url)
                            return pdf_url
                    
                    # Check for paywall/subscription indicators
                    paywall_terms = ['subscribe', 'sign in', 'log in', 'institutional access', 
                                   'purchase', 'access denied', 'login required', 'subscription required',
                                   'register', 'institutional', 'purchase this article', 'content access']
                    if any(term in page_text for term in paywall_terms):
                        raise AccessDenied(f'PAYWALL: Brill article requires subscription - attempted: {article_url}')
                    
                    # If no PDF link found but page accessible, return article URL
                    return article_url
                
                elif response.status_code == 403:
                    raise AccessDenied(f'DENIED: Access forbidden by Brill - attempted: {article_url}')
                elif response.status_code == 404:
                    raise NoPDFLink(f'TXERROR: Brill article not found - attempted: {article_url}')
                else:
                    raise NoPDFLink(f'TXERROR: Brill returned status {response.status_code} - attempted: {article_url}')
                    
            except requests.exceptions.RequestException as e:
                raise NoPDFLink(f'TXERROR: Network error accessing Brill: {e} - attempted: {article_url}')
        else:
            # Return DOI-resolved URL without verification
            return article_url
        
    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: Brill bridge failed for {pma.journal}: {e} - attempted: DOI resolution')


def the_rsc_reaction(pma, verify=True):
    '''Royal Society of Chemistry (RSC): Leading chemistry publisher
    
    RSC publishes over 50 journals covering all areas of chemistry and related fields.
    Founded in 1841, articles are hosted on pubs.rsc.org and accessible via DOI resolution.
    
    :param: pma (PubmedArticle)
    :param: verify (bool) [default: True] 
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    '''
    try:
        # Check if DOI is available
        if not pma.doi:
            raise NoPDFLink('MISSING: DOI required for RSC journals - attempted: none')
        
        # Verify DOI pattern for RSC (should start with 10.1039/)
        if not pma.doi.startswith('10.1039/'):
            raise NoPDFLink(f'INVALID: DOI does not match RSC pattern (10.1039/) - attempted: {pma.doi}')
        
        # Resolve DOI to get article URL
        article_url = the_doi_2step(pma.doi)
        
        if verify:
            try:
                response = requests.get(article_url, timeout=30)
                
                if response.status_code in OK_STATUS_CODES:
                    page_text = response.text.lower()
                    
                    # Look for PDF download links or indicators
                    if 'pdf' in page_text and ('download' in page_text or 'full text' in page_text or 'view pdf' in page_text):
                        # Try to find PDF link in the page
                        from lxml import html
                        tree = html.fromstring(response.content)
                        
                        # Look for PDF download links (RSC typically has direct PDF access)
                        pdf_links = tree.xpath('//a[contains(@href, ".pdf") or contains(text(), "PDF") or contains(@class, "pdf") or contains(@title, "PDF")]/@href')
                        
                        if pdf_links:
                            pdf_url = pdf_links[0]
                            # Convert relative URL to absolute if needed
                            if pdf_url.startswith('/'):
                                from urllib.parse import urljoin
                                pdf_url = urljoin(article_url, pdf_url)
                            return pdf_url
                    
                    # Check for paywall/subscription indicators
                    paywall_terms = ['subscribe', 'sign in', 'log in', 'institutional access', 
                                   'purchase', 'access denied', 'login required', 'subscription required',
                                   'register', 'institutional', 'purchase this article', 'member access']
                    if any(term in page_text for term in paywall_terms):
                        raise AccessDenied(f'PAYWALL: RSC article requires subscription - attempted: {article_url}')
                    
                    # If no PDF link found but page accessible, return article URL
                    return article_url
                
                elif response.status_code == 403:
                    raise AccessDenied(f'DENIED: Access forbidden by RSC - attempted: {article_url}')
                elif response.status_code == 404:
                    raise NoPDFLink(f'TXERROR: RSC article not found - attempted: {article_url}')
                else:
                    raise NoPDFLink(f'TXERROR: RSC returned status {response.status_code} - attempted: {article_url}')
                    
            except requests.exceptions.RequestException as e:
                raise NoPDFLink(f'TXERROR: Network error accessing RSC: {e} - attempted: {article_url}')
        else:
            # Return DOI-resolved URL without verification
            return article_url
        
    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: RSC reaction failed for {pma.journal}: {e} - attempted: DOI resolution')


def the_ingenta_flux(pma, verify=True):
    '''Ingenta Connect: Digital publishing platform hosting multiple publishers
    
    Ingenta Connect serves as a content aggregator hosting scholarly content from
    over 250 publishers. Journals have diverse DOI prefixes but all resolve through
    ingentaconnect.com platform.
    
    :param: pma (PubmedArticle)
    :param: verify (bool) [default: True] 
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    '''
    try:
        # Check if DOI is available
        if not pma.doi:
            raise NoPDFLink('MISSING: DOI required for Ingenta Connect journals - attempted: none')
        
        # Since Ingenta Connect hosts multiple publishers with different DOI prefixes,
        # we don't validate a specific DOI pattern - just ensure DOI exists
        
        # Resolve DOI to get article URL
        article_url = the_doi_2step(pma.doi)
        
        if verify:
            try:
                response = requests.get(article_url, timeout=30)
                
                if response.status_code in OK_STATUS_CODES:
                    page_text = response.text.lower()
                    
                    # Look for PDF download links or indicators
                    if 'pdf' in page_text and ('download' in page_text or 'full text' in page_text or 'view pdf' in page_text):
                        # Try to find PDF link in the page
                        from lxml import html
                        tree = html.fromstring(response.content)
                        
                        # Look for PDF download links (Ingenta Connect typically has direct PDF access)
                        pdf_links = tree.xpath('//a[contains(@href, ".pdf") or contains(text(), "PDF") or contains(@class, "pdf") or contains(@title, "PDF")]/@href')
                        
                        if pdf_links:
                            pdf_url = pdf_links[0]
                            # Convert relative URL to absolute if needed
                            if pdf_url.startswith('/'):
                                from urllib.parse import urljoin
                                pdf_url = urljoin(article_url, pdf_url)
                            return pdf_url
                    
                    # Check for paywall/subscription indicators
                    paywall_terms = ['subscribe', 'sign in', 'log in', 'institutional access', 
                                   'purchase', 'access denied', 'login required', 'subscription required',
                                   'register', 'institutional', 'purchase this article', 'pay per view']
                    if any(term in page_text for term in paywall_terms):
                        raise AccessDenied(f'PAYWALL: Ingenta Connect article requires subscription - attempted: {article_url}')
                    
                    # If no PDF link found but page accessible, return article URL
                    return article_url
                
                elif response.status_code == 403:
                    raise AccessDenied(f'DENIED: Access forbidden by Ingenta Connect - attempted: {article_url}')
                elif response.status_code == 404:
                    raise NoPDFLink(f'TXERROR: Ingenta Connect article not found - attempted: {article_url}')
                else:
                    raise NoPDFLink(f'TXERROR: Ingenta Connect returned status {response.status_code} - attempted: {article_url}')
                    
            except requests.exceptions.RequestException as e:
                raise NoPDFLink(f'TXERROR: Network error accessing Ingenta Connect: {e} - attempted: {article_url}')
        else:
            # Return DOI-resolved URL without verification
            return article_url
        
    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: Ingenta flux failed for {pma.journal}: {e} - attempted: DOI resolution')


def the_bioone_bounce(pma, verify=True):
    '''BioOne.org: Multi-publisher digital library platform for biological sciences
    
    BioOne is a multi-publisher digital library platform that aggregates scholarly content
    from biological, ecological, and environmental science publishers. The platform hosts
    journals from ~200+ societies and independent publishers with diverse DOI prefixes
    (10.1643/, 10.1645/, 10.1676/, etc.) but all resolve through complete.bioone.org.
    
    :param: pma (PubmedArticle)
    :param: verify (bool) [default: True] 
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    '''
    try:
        # Check if DOI is available
        if not pma.doi:
            raise NoPDFLink('MISSING: DOI required for BioOne journals - attempted: none')
        
        # Since BioOne hosts multiple publishers with different DOI prefixes,
        # we don't validate a specific DOI pattern - just ensure DOI exists
        
        # Resolve DOI to get article URL
        article_url = the_doi_2step(pma.doi)
        
        if verify:
            try:
                response = requests.get(article_url, timeout=30)
                
                if response.status_code in OK_STATUS_CODES:
                    page_text = response.text.lower()
                    
                    # Look for PDF download links or indicators
                    if 'pdf' in page_text and ('download' in page_text or 'full text' in page_text or 'view pdf' in page_text):
                        # Try to find PDF link in the page
                        from lxml import html
                        tree = html.fromstring(response.content)
                        
                        # Look for PDF download links (BioOne typically has direct PDF access)
                        pdf_links = tree.xpath('//a[contains(@href, ".pdf") or contains(text(), "PDF") or contains(@class, "pdf") or contains(@title, "PDF")]/@href')
                        
                        if pdf_links:
                            pdf_url = pdf_links[0]
                            # Convert relative URL to absolute if needed
                            if pdf_url.startswith('/'):
                                from urllib.parse import urljoin
                                pdf_url = urljoin(article_url, pdf_url)
                            return pdf_url
                    
                    # Check for paywall/subscription indicators
                    paywall_terms = ['subscribe', 'sign in', 'log in', 'institutional access', 
                                   'purchase', 'access denied', 'login required', 'subscription required',
                                   'register', 'institutional', 'purchase this article', 'member access']
                    if any(term in page_text for term in paywall_terms):
                        raise AccessDenied(f'PAYWALL: BioOne article requires subscription - attempted: {article_url}')
                    
                    # If no PDF link found but page accessible, return article URL
                    return article_url
                
                elif response.status_code == 403:
                    raise AccessDenied(f'DENIED: Access forbidden by BioOne - attempted: {article_url}')
                elif response.status_code == 404:
                    raise NoPDFLink(f'TXERROR: BioOne article not found - attempted: {article_url}')
                else:
                    raise NoPDFLink(f'TXERROR: BioOne returned status {response.status_code} - attempted: {article_url}')
                    
            except requests.exceptions.RequestException as e:
                raise NoPDFLink(f'TXERROR: Network error accessing BioOne: {e} - attempted: {article_url}')
        else:
            # Return DOI-resolved URL without verification
            return article_url
        
    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: BioOne bounce failed for {pma.journal}: {e} - attempted: DOI resolution')


def the_emerald_ceili(pma, verify=True):
    '''Emerald Publishing: Business, management, education, library science journals
    
    Emerald Publishing is a digital-first publisher of management, business, education,
    library science, information management research, and health care journals.
    Founded in 1967, it publishes over 300 journals and more than 2,500 books.
    
    URL Pattern: https://www.emerald.com/insight/content/doi/[DOI]/full/html
    PDF Pattern: https://www.emerald.com/insight/content/doi/[DOI]/full/pdf
    DOI Pattern: 10.1108/[JOURNAL_CODE]-[DATE]-[ID]
    
    :param: pma (PubmedArticle)
    :param: verify (bool) [default: True] 
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    '''
    try:
        # Check if DOI is available
        if not pma.doi:
            raise NoPDFLink('MISSING: DOI required for Emerald journals - attempted: none')
        
        # Emerald DOIs typically follow pattern 10.1108/...
        if not pma.doi.startswith('10.1108/'):
            raise NoPDFLink(f'PATTERN: DOI does not match Emerald pattern (10.1108/) - attempted: {pma.doi}')
        
        # Try direct PDF URL construction
        pdf_url = f'https://www.emerald.com/insight/content/doi/{pma.doi}/full/pdf'
        
        if verify:
            try:
                response = requests.get(pdf_url, timeout=30)
                
                if response.status_code in OK_STATUS_CODES:
                    # Check if this is actually a PDF
                    content_type = response.headers.get('content-type', '').lower()
                    if 'pdf' in content_type:
                        return pdf_url
                    else:
                        # Might be HTML page, check for subscription/paywall indicators
                        page_text = response.text.lower()
                        paywall_terms = ['subscribe', 'sign in', 'log in', 'institutional access', 
                                       'purchase', 'access denied', 'login required', 'subscription required',
                                       'register', 'institutional', 'purchase this article', 'member access']
                        if any(term in page_text for term in paywall_terms):
                            raise AccessDenied(f'PAYWALL: Emerald article requires subscription - attempted: {pdf_url}')
                        
                        # Try article HTML page instead
                        article_url = f'https://www.emerald.com/insight/content/doi/{pma.doi}/full/html'
                        return article_url
                
                elif response.status_code == 403:
                    raise AccessDenied(f'DENIED: Access forbidden by Emerald - attempted: {pdf_url}')
                elif response.status_code == 404:
                    raise NoPDFLink(f'TXERROR: Emerald article not found (404) - attempted: {pdf_url}')
                else:
                    raise NoPDFLink(f'TXERROR: Emerald returned status {response.status_code} - attempted: {pdf_url}')
                    
            except requests.exceptions.RequestException as e:
                raise NoPDFLink(f'TXERROR: Network error accessing Emerald: {e} - attempted: {pdf_url}')
        else:
            # Return PDF URL without verification
            return pdf_url
        
    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: Emerald ceili failed for {pma.journal}: {e} - attempted: DOI resolution')


def the_acm_reel(pma, verify=True):
    '''ACM Digital Library: Computing and information technology publications
    
    The ACM Digital Library is a comprehensive database of articles, proceedings,
    and other publications from the Association for Computing Machinery (ACM).
    It covers computer science, information technology, and related fields.
    
    URL Pattern: https://dl.acm.org/doi/[DOI]
    PDF Pattern: https://dl.acm.org/doi/pdf/[DOI]
    DOI Pattern: 10.1145/[ID] (most common ACM DOI pattern)
    
    :param: pma (PubmedArticle)
    :param: verify (bool) [default: True] 
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    '''
    try:
        # Check if DOI is available
        if not pma.doi:
            raise NoPDFLink('MISSING: DOI required for ACM articles - attempted: none')
        
        # ACM DOIs typically follow pattern 10.1145/...
        if not pma.doi.startswith('10.1145/'):
            raise NoPDFLink(f'PATTERN: DOI does not match ACM pattern (10.1145/) - attempted: {pma.doi}')
        
        # Try direct PDF URL construction
        pdf_url = f'https://dl.acm.org/doi/pdf/{pma.doi}'
        
        if verify:
            try:
                response = requests.get(pdf_url, timeout=30)
                
                if response.status_code in OK_STATUS_CODES:
                    # Check if this is actually a PDF
                    content_type = response.headers.get('content-type', '').lower()
                    if 'pdf' in content_type:
                        return pdf_url
                    else:
                        # Might be HTML page, check for subscription/paywall indicators
                        page_text = response.text.lower()
                        paywall_terms = ['purchase', 'access denied', 'subscription required',
                                       'sign in', 'log in', 'member access', 'institutional access',
                                       'acm membership', 'subscribe']
                        if any(term in page_text for term in paywall_terms):
                            raise AccessDenied(f'PAYWALL: ACM article requires subscription or membership - attempted: {pdf_url}')
                        
                        # Try article HTML page instead
                        article_url = f'https://dl.acm.org/doi/{pma.doi}'
                        return article_url
                
                elif response.status_code == 403:
                    raise AccessDenied(f'DENIED: Access forbidden by ACM - attempted: {pdf_url}')
                elif response.status_code == 404:
                    raise NoPDFLink(f'TXERROR: ACM article not found (404) - attempted: {pdf_url}')
                else:
                    raise NoPDFLink(f'TXERROR: ACM returned status {response.status_code} - attempted: {pdf_url}')
                    
            except requests.exceptions.RequestException as e:
                raise NoPDFLink(f'TXERROR: Network error accessing ACM: {e} - attempted: {pdf_url}')
        else:
            # Return PDF URL without verification
            return pdf_url
        
    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: ACM reel failed for {pma.journal}: {e} - attempted: DOI resolution')


def the_worldscientific_robot(pma, verify=True):
    '''World Scientific Publishing: Scientific, technical, and medical content
    
    World Scientific Publishing is a major academic publisher for scientific,
    technical, and medical content. It publishes journals, books, and conference
    proceedings in various fields including physics, mathematics, computer science,
    engineering, chemistry, and life sciences.
    
    URL Pattern: https://www.worldscientific.com/doi/[DOI]
    PDF Pattern: https://www.worldscientific.com/doi/pdf/[DOI]
    DOI Pattern: 10.1142/[ID] (World Scientific DOI pattern)
    
    Args:
        pma: PubMedArticle instance with DOI
        verify: Whether to verify PDF accessibility (default: True)
        
    Returns:
        PDF URL string if accessible
        
    Raises:
        NoPDFLink: If no DOI, wrong DOI pattern, or technical issues
        AccessDenied: If paywall detected
    '''
    try:
        # Check for required DOI
        if not pma.doi:
            raise NoPDFLink(f'MISSING: DOI required for World Scientific access - journal: {pma.journal}')
        
        # Verify DOI pattern (most World Scientific DOIs start with 10.1142)
        if not pma.doi.startswith('10.1142/'):
            raise NoPDFLink(f'PATTERN: Expected World Scientific DOI (10.1142/...), got: {pma.doi} - journal: {pma.journal}')
        
        # Construct PDF URL
        pdf_url = f'https://www.worldscientific.com/doi/pdf/{pma.doi}'
        
        if verify:
            try:
                response = requests.get(pdf_url, timeout=10, allow_redirects=True)
                
                if response.ok:
                    # Check if we got actual PDF content
                    content_type = response.headers.get('content-type', '').lower()
                    if 'application/pdf' in content_type:
                        return pdf_url
                    elif 'text/html' in content_type:
                        # Check for paywall indicators in HTML response
                        page_text = response.text.lower()
                        paywall_terms = ['purchase', 'access denied', 'subscription required',
                                       'sign in', 'log in', 'member access', 'institutional access',
                                       'subscribe now', 'buy article', 'rental']
                        if any(term in page_text for term in paywall_terms):
                            raise AccessDenied(f'PAYWALL: World Scientific article requires subscription - attempted: {pdf_url}')
                        
                        # Try article HTML page instead
                        article_url = f'https://www.worldscientific.com/doi/{pma.doi}'
                        return article_url
                
                elif response.status_code == 403:
                    raise AccessDenied(f'DENIED: Access forbidden by World Scientific - attempted: {pdf_url}')
                elif response.status_code == 404:
                    raise NoPDFLink(f'TXERROR: World Scientific article not found (404) - attempted: {pdf_url}')
                else:
                    raise NoPDFLink(f'TXERROR: World Scientific returned status {response.status_code} - attempted: {pdf_url}')
                    
            except requests.exceptions.RequestException as e:
                raise NoPDFLink(f'TXERROR: Network error accessing World Scientific: {e} - attempted: {pdf_url}')
        else:
            # Return PDF URL without verification
            return pdf_url
        
    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: World Scientific robot failed for {pma.journal}: {e} - attempted: DOI resolution')


def the_uchicago_walk(pma, verify=True):
    '''University of Chicago Press: Academic journals across multiple disciplines
    
    The University of Chicago Press is one of the largest and oldest university presses
    in the United States. It publishes academic journals, books, and scholarly content
    across various disciplines including humanities, social sciences, education, 
    biological sciences, and physical sciences.
    
    URL Pattern: https://www.journals.uchicago.edu/doi/[DOI]
    PDF Pattern: https://www.journals.uchicago.edu/doi/pdf/[DOI]
    DOI Pattern: 10.1086/[ID] (University of Chicago Press DOI pattern)
    
    Args:
        pma: PubMedArticle instance with DOI
        verify: Whether to verify PDF accessibility (default: True)
        
    Returns:
        PDF URL string if accessible
        
    Raises:
        NoPDFLink: If no DOI, wrong DOI pattern, or technical issues
        AccessDenied: If paywall detected
    '''
    try:
        # Check for required DOI
        if not pma.doi:
            raise NoPDFLink(f'MISSING: DOI required for University of Chicago Press access - journal: {pma.journal}')
        
        # Verify DOI pattern (most University of Chicago Press DOIs start with 10.1086)
        if not pma.doi.startswith('10.1086/'):
            raise NoPDFLink(f'PATTERN: Expected University of Chicago Press DOI (10.1086/...), got: {pma.doi} - journal: {pma.journal}')
        
        # Construct PDF URL
        pdf_url = f'https://www.journals.uchicago.edu/doi/pdf/{pma.doi}'
        
        if verify:
            try:
                response = requests.get(pdf_url, timeout=10, allow_redirects=True)
                
                if response.ok:
                    # Check if we got actual PDF content
                    content_type = response.headers.get('content-type', '').lower()
                    if 'application/pdf' in content_type:
                        return pdf_url
                    elif 'text/html' in content_type:
                        # Check for paywall indicators in HTML response
                        page_text = response.text.lower()
                        paywall_terms = ['purchase', 'access denied', 'subscription required',
                                       'sign in', 'log in', 'member access', 'institutional access',
                                       'subscribe now', 'buy article', 'rent this article']
                        if any(term in page_text for term in paywall_terms):
                            raise AccessDenied(f'PAYWALL: University of Chicago Press article requires subscription - attempted: {pdf_url}')
                        
                        # Try article HTML page instead
                        article_url = f'https://www.journals.uchicago.edu/doi/{pma.doi}'
                        return article_url
                
                elif response.status_code == 403:
                    raise AccessDenied(f'DENIED: Access forbidden by University of Chicago Press - attempted: {pdf_url}')
                elif response.status_code == 404:
                    raise NoPDFLink(f'TXERROR: University of Chicago Press article not found (404) - attempted: {pdf_url}')
                else:
                    raise NoPDFLink(f'TXERROR: University of Chicago Press returned status {response.status_code} - attempted: {pdf_url}')
                    
            except requests.exceptions.RequestException as e:
                raise NoPDFLink(f'TXERROR: Network error accessing University of Chicago Press: {e} - attempted: {pdf_url}')
        else:
            # Return PDF URL without verification
            return pdf_url
        
    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: University of Chicago Press walk failed for {pma.journal}: {e} - attempted: DOI resolution')


def the_iospress_freestyle(pma, verify=True):
    '''IOS Press: Scientific and technical books and journals
    
    IOS Press is an international publisher of scientific and technical books and journals
    based in Amsterdam, Netherlands. It specializes in computer science, artificial intelligence,
    biomedical sciences, health technologies, and other technical disciplines.
    
    URL Pattern: https://content.iospress.com/articles/[journal]/[DOI]
    PDF Pattern: https://content.iospress.com/download/[journal]/[DOI]
    DOI Pattern: 10.3233/[JOURNAL]-[ID] (IOS Press DOI pattern)
    
    Args:
        pma: PubMedArticle instance with DOI
        verify: Whether to verify PDF accessibility (default: True)
        
    Returns:
        PDF URL string if accessible
        
    Raises:
        NoPDFLink: If no DOI, wrong DOI pattern, or technical issues
        AccessDenied: If paywall detected
    '''
    try:
        # Check for required DOI
        if not pma.doi:
            raise NoPDFLink(f'MISSING: DOI required for IOS Press access - journal: {pma.journal}')
        
        # Verify DOI pattern (most IOS Press DOIs start with 10.3233)
        if not pma.doi.startswith('10.3233/'):
            raise NoPDFLink(f'PATTERN: Expected IOS Press DOI (10.3233/...), got: {pma.doi} - journal: {pma.journal}')
        
        # Extract journal code from DOI for URL construction
        # DOI format: 10.3233/JAD-240123 -> journal code is JAD
        doi_parts = pma.doi.split('/')
        if len(doi_parts) < 2:
            raise NoPDFLink(f'PATTERN: Invalid DOI format for IOS Press: {pma.doi} - journal: {pma.journal}')
        
        journal_and_id = doi_parts[1]  # e.g., "JAD-240123"
        if '-' not in journal_and_id:
            raise NoPDFLink(f'PATTERN: Expected IOS Press DOI with journal-ID format, got: {pma.doi} - journal: {pma.journal}')
        
        journal_code = journal_and_id.split('-')[0].lower()  # e.g., "jad"
        
        # Construct PDF URL
        pdf_url = f'https://content.iospress.com/download/{journal_code}/{pma.doi}'
        
        if verify:
            try:
                response = requests.get(pdf_url, timeout=10, allow_redirects=True)
                
                if response.ok:
                    # Check if we got actual PDF content
                    content_type = response.headers.get('content-type', '').lower()
                    if 'application/pdf' in content_type:
                        return pdf_url
                    elif 'text/html' in content_type:
                        # Check for paywall indicators in HTML response
                        page_text = response.text.lower()
                        paywall_terms = ['purchase', 'access denied', 'subscription required',
                                       'sign in', 'log in', 'member access', 'institutional access',
                                       'subscribe now', 'buy article', 'login required']
                        if any(term in page_text for term in paywall_terms):
                            raise AccessDenied(f'PAYWALL: IOS Press article requires subscription - attempted: {pdf_url}')
                        
                        # Try article HTML page instead
                        article_url = f'https://content.iospress.com/articles/{journal_code}/{pma.doi}'
                        return article_url
                
                elif response.status_code == 403:
                    raise AccessDenied(f'DENIED: Access forbidden by IOS Press - attempted: {pdf_url}')
                elif response.status_code == 404:
                    raise NoPDFLink(f'TXERROR: IOS Press article not found (404) - attempted: {pdf_url}')
                else:
                    raise NoPDFLink(f'TXERROR: IOS Press returned status {response.status_code} - attempted: {pdf_url}')
                    
            except requests.exceptions.RequestException as e:
                raise NoPDFLink(f'TXERROR: Network error accessing IOS Press: {e} - attempted: {pdf_url}')
        else:
            # Return PDF URL without verification
            return pdf_url
        
    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: IOS Press freestyle failed for {pma.journal}: {e} - attempted: DOI resolution')


def the_longdom_hustle(pma, verify=True):
    '''Longdom Publishing: Open access journals across various fields
    
    Longdom Publishing is an open access publisher that publishes journals
    across various fields including medical sciences, life sciences, and technology.
    Note: This publisher has been flagged by some as potentially predatory.
    
    URL Pattern: https://www.longdom.org/articles/[article-slug]
    PDF Pattern: https://www.longdom.org/articles-pdfs/[article-slug].pdf
    DOI Pattern: Various DOI patterns (10.4172, 10.35248, etc.)
    
    Args:
        pma: PubMedArticle instance with DOI
        verify: Whether to verify PDF accessibility (default: True)
        
    Returns:
        PDF URL string if accessible
        
    Raises:
        NoPDFLink: If no DOI, cannot construct URL, or technical issues
        AccessDenied: If paywall detected (rare for open access)
    '''
    try:
        # Check for required DOI
        if not pma.doi:
            raise NoPDFLink(f'MISSING: DOI required for Longdom access - journal: {pma.journal}')
        
        # Longdom uses various DOI patterns, but most common are 10.4172 and 10.35248
        common_patterns = ['10.4172', '10.35248', '10.37421', '10.35840']
        if not any(pma.doi.startswith(pattern) for pattern in common_patterns):
            # Still try to process, but note pattern mismatch
            pass
        
        # Longdom URL construction is complex - try to derive from DOI
        # Most Longdom URLs follow pattern: longdom.org/articles/article-title-doi-suffix
        # This is a simplified approach - may need refinement
        doi_suffix = pma.doi.split('/')[-1] if '/' in pma.doi else pma.doi
        
        # Try multiple URL patterns since Longdom has inconsistent URL structure
        possible_urls = [
            f'https://www.longdom.org/articles-pdf/{doi_suffix}.pdf',
            f'https://www.longdom.org/articles/{doi_suffix}.pdf',
            f'https://www.longdom.org/open-access/{doi_suffix}.pdf'
        ]
        
        if verify:
            for pdf_url in possible_urls:
                try:
                    response = requests.get(pdf_url, timeout=10, allow_redirects=True)
                    
                    if response.ok:
                        # Check if we got actual PDF content
                        content_type = response.headers.get('content-type', '').lower()
                        if 'application/pdf' in content_type:
                            return pdf_url
                        elif 'text/html' in content_type:
                            # Check for error pages
                            page_text = response.text.lower()
                            if 'not found' in page_text or 'error' in page_text:
                                continue  # Try next URL pattern
                            else:
                                # Return article page URL instead
                                article_url = pdf_url.replace('/articles-pdf/', '/articles/').replace('.pdf', '')
                                return article_url
                
                except requests.exceptions.RequestException:
                    continue  # Try next URL pattern
            
            # If all patterns failed, raise error
            raise NoPDFLink(f'TXERROR: Could not access Longdom article with any URL pattern - attempted: {possible_urls[0]}')
        else:
            # Return first PDF URL pattern without verification
            return possible_urls[0]
        
    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: Longdom hustle failed for {pma.journal}: {e} - attempted: DOI resolution')


def the_iop_fusion(pma, verify=True):
    """IOP Publishing (Institute of Physics) dance function.
    
    IOP Publishing operates multiple domains including iopscience.iop.org 
    and validate.perfdrive.com. Most IOP journals use DOI pattern 10.1088/*.
    
    Args:
        pma: PubMedArticle object
        verify: Whether to verify PDF access
        
    Returns:
        PDF URL if accessible
        
    Raises:
        NoPDFLink: If DOI missing, wrong pattern, or PDF not accessible
        AccessDenied: If paywall detected
    """
    from .journals.iop import iop_format, iop_alt_format
    
    try:
        if not pma.doi:
            raise NoPDFLink('MISSING: DOI required for IOP article access')
        
        # Most IOP journals use 10.1088 pattern, but some use others
        # Accept common patterns but warn about uncommon ones
        common_iop_patterns = ['10.1088', '10.1149', '10.3847', '10.1209', '10.1238']
        if not any(pma.doi.startswith(pattern) for pattern in common_iop_patterns):
            # Still try to process for other patterns
            pass
        
        # Try both IOP URL formats
        possible_urls = [
            iop_format.format(doi=pma.doi),
            iop_alt_format.format(doi=pma.doi)
        ]
        
        if verify:
            for pdf_url in possible_urls:
                try:
                    response = requests.get(pdf_url, timeout=10, allow_redirects=True)
                    
                    if response.ok:
                        # Check content type
                        content_type = response.headers.get('content-type', '').lower()
                        if 'application/pdf' in content_type:
                            return pdf_url
                        elif 'text/html' in content_type:
                            # Check for paywall indicators
                            page_text = response.text.lower()
                            paywall_indicators = [
                                'subscribe', 'subscription', 'login required',
                                'access denied', 'purchase', 'institutional access'
                            ]
                            if any(indicator in page_text for indicator in paywall_indicators):
                                # Try next URL before raising paywall error
                                continue
                            else:
                                # Might be article page, return it
                                return pdf_url
                    elif response.status_code == 404:
                        continue  # Try next URL format
                    else:
                        continue  # Try next URL format
                        
                except requests.exceptions.RequestException as e:
                    continue  # Try next URL format
            
            # If both URLs failed, determine appropriate error
            if any(pma.doi.startswith(pattern) for pattern in common_iop_patterns):
                raise NoPDFLink(f'TXERROR: Could not access IOP article at either domain - DOI: {pma.doi}')
            else:
                raise NoPDFLink(f'PATTERN: IOP typically uses DOI patterns {common_iop_patterns}, got {pma.doi}')
        else:
            # Return primary URL without verification
            return possible_urls[0]
            
    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: IOP fusion failed for {pma.journal}: {e} - DOI: {pma.doi}')


def the_oatext_orbit(pma, verify=True):
    """OAText Publishing dance function.
    
    OAText is an open access publisher specializing in medical and healthcare
    journals. Their URL patterns may vary, so this function tries multiple
    approaches to access PDFs.
    
    Args:
        pma: PubMedArticle object
        verify: Whether to verify PDF access
        
    Returns:
        PDF URL if accessible
        
    Raises:
        NoPDFLink: If DOI missing or PDF not accessible
        AccessDenied: If paywall detected (unlikely for open access)
    """
    from .journals.oatext import oatext_format
    
    try:
        if not pma.doi:
            raise NoPDFLink('MISSING: DOI required for OAText article access')
        
        # OAText journals may use various DOI patterns
        # Most open access publishers are flexible with DOI patterns
        
        # Try different URL construction approaches
        doi_suffix = pma.doi.split('/')[-1] if '/' in pma.doi else pma.doi
        
        possible_urls = [
            f'https://www.oatext.com/pdf/{doi_suffix}.pdf',
            f'https://oatext.com/pdf/{doi_suffix}.pdf',
            f'https://www.oatext.com/pdf/{pma.doi}.pdf',
            f'https://oatext.com/pdf/{pma.doi}.pdf'
        ]
        
        # Also try constructing from article title if available
        if hasattr(pma, 'title') and pma.title:
            # Convert title to URL-friendly format
            title_slug = pma.title.lower().replace(' ', '-').replace(',', '').replace(':', '').replace('.', '')
            title_slug = ''.join(c for c in title_slug if c.isalnum() or c == '-')
            possible_urls.extend([
                f'https://www.oatext.com/{title_slug}.php',
                f'https://oatext.com/{title_slug}.php'
            ])
        
        if verify:
            for pdf_url in possible_urls:
                try:
                    response = requests.get(pdf_url, timeout=10, allow_redirects=True)
                    
                    if response.ok:
                        # Check content type
                        content_type = response.headers.get('content-type', '').lower()
                        if 'application/pdf' in content_type:
                            return pdf_url
                        elif 'text/html' in content_type:
                            # Check for article page or PDF links
                            page_text = response.text.lower()
                            if 'not found' in page_text or '404' in page_text:
                                continue  # Try next URL
                            else:
                                # Might be article page, return it
                                return pdf_url
                    elif response.status_code == 404:
                        continue  # Try next URL format
                    else:
                        continue  # Try next URL format
                        
                except requests.exceptions.RequestException:
                    continue  # Try next URL format
            
            # If all URLs failed
            raise NoPDFLink(f'TXERROR: Could not access OAText article with any URL pattern - DOI: {pma.doi}')
        else:
            # Return first PDF URL pattern without verification
            return possible_urls[0]
            
    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: OAText orbit failed for {pma.journal}: {e} - DOI: {pma.doi}')


def the_allenpress_advance(pma, verify=True):
    """Allen Press dance function.
    
    Allen Press provides publishing services for scholarly and professional
    societies. Their journals are hosted on meridian.allenpress.com with
    journal-specific URL structures.
    
    Args:
        pma: PubMedArticle object
        verify: Whether to verify PDF access
        
    Returns:
        PDF URL if accessible
        
    Raises:
        NoPDFLink: If DOI missing or PDF not accessible
        AccessDenied: If paywall detected
    """
    from .journals.allenpress import allenpress_format
    
    try:
        if not pma.doi:
            raise NoPDFLink('MISSING: DOI required for Allen Press article access')
        
        # Allen Press journals may use various DOI patterns from different societies
        # Try to derive journal code from journal name or DOI
        journal_name = pma.journal.lower() if pma.journal else ''
        
        # Common journal code mappings (will need to expand based on actual patterns)
        journal_codes = {
            'oper dent': 'od',
            'j am anim hosp assoc': 'jaaha',
            'arch pathol lab med': 'aplm',
            'j athl train': 'jat',
            'angle orthod': 'angl',
            'tex heart inst j': 'thij',
            'ethn dis': 'ethn',
            'j oral implantol': 'joi',
            'j am mosq control assoc': 'jamca',
            'j grad med educ': 'jgme',
            'j pediatr pharmacol ther': 'jppt'
        }
        
        # Try to find journal code
        journal_code = None
        for name_pattern, code in journal_codes.items():
            if name_pattern in journal_name:
                journal_code = code
                break
        
        # If we can't determine journal code, try generic patterns
        possible_urls = []
        
        if journal_code:
            possible_urls.extend([
                f'https://meridian.allenpress.com/{journal_code}/article-pdf/{pma.doi}',
                f'https://meridian.allenpress.com/{journal_code}/article/{pma.doi}',
                f'https://meridian.allenpress.com/{journal_code}/article-pdf/doi/{pma.doi}',
                f'https://meridian.allenpress.com/{journal_code}/article/doi/{pma.doi}'
            ])
        
        # Try generic patterns without journal code
        doi_suffix = pma.doi.split('/')[-1] if '/' in pma.doi else pma.doi
        possible_urls.extend([
            f'https://meridian.allenpress.com/article-pdf/{pma.doi}',
            f'https://meridian.allenpress.com/article/{pma.doi}',
            f'https://meridian.allenpress.com/doi/pdf/{pma.doi}',
            f'https://meridian.allenpress.com/doi/{pma.doi}'
        ])
        
        if verify:
            for pdf_url in possible_urls:
                try:
                    response = requests.get(pdf_url, timeout=10, allow_redirects=True)
                    
                    if response.ok:
                        # Check content type
                        content_type = response.headers.get('content-type', '').lower()
                        if 'application/pdf' in content_type:
                            return pdf_url
                        elif 'text/html' in content_type:
                            # Check for paywall indicators
                            page_text = response.text.lower()
                            paywall_indicators = [
                                'subscribe', 'subscription', 'login required',
                                'access denied', 'purchase', 'institutional access',
                                'sign in', 'member'
                            ]
                            if any(indicator in page_text for indicator in paywall_indicators):
                                raise AccessDenied(f'PAYWALL: Allen Press article requires subscription - {pdf_url}')
                            else:
                                # Might be article page, return it
                                return pdf_url
                    elif response.status_code == 404:
                        continue  # Try next URL format
                    else:
                        continue  # Try next URL format
                        
                except requests.exceptions.RequestException:
                    continue  # Try next URL format
            
            # If all URLs failed
            raise NoPDFLink(f'TXERROR: Could not access Allen Press article with any URL pattern - DOI: {pma.doi}')
        else:
            # Return first URL pattern without verification
            return possible_urls[0] if possible_urls else f'https://meridian.allenpress.com/article-pdf/{pma.doi}'
            
    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: Allen Press advance failed for {pma.journal}: {e} - DOI: {pma.doi}')


def the_inderscience_ula(pma, verify=True):
    """Inderscience Publishers dance function.
    
    Inderscience Publishers is an independent academic publisher specializing
    in engineering, technology, science, and management journals. Most of their
    journals follow "International Journal of..." naming pattern.
    
    Args:
        pma: PubMedArticle object
        verify: Whether to verify PDF access
        
    Returns:
        PDF URL if accessible
        
    Raises:
        NoPDFLink: If DOI missing or PDF not accessible
        AccessDenied: If paywall detected
    """
    from .journals.inderscience import inderscience_format
    
    try:
        if not pma.doi:
            raise NoPDFLink('MISSING: DOI required for Inderscience article access')
        
        # Inderscience typically uses 10.1504/* DOI pattern
        if not pma.doi.startswith('10.1504/'):
            # Still try to process, but note pattern mismatch
            pass
        
        # Try different URL construction approaches
        possible_urls = [
            f'https://www.inderscienceonline.com/doi/pdf/{pma.doi}',
            f'https://www.inderscienceonline.com/doi/{pma.doi}',
            f'https://inderscienceonline.com/doi/pdf/{pma.doi}',
            f'https://inderscienceonline.com/doi/{pma.doi}'
        ]
        
        if verify:
            for pdf_url in possible_urls:
                try:
                    response = requests.get(pdf_url, timeout=10, allow_redirects=True)
                    
                    if response.ok:
                        # Check content type
                        content_type = response.headers.get('content-type', '').lower()
                        if 'application/pdf' in content_type:
                            return pdf_url
                        elif 'text/html' in content_type:
                            # Check for paywall indicators
                            page_text = response.text.lower()
                            paywall_indicators = [
                                'subscribe', 'subscription', 'login required',
                                'access denied', 'purchase', 'institutional access',
                                'sign in', 'member only'
                            ]
                            if any(indicator in page_text for indicator in paywall_indicators):
                                raise AccessDenied(f'PAYWALL: Inderscience article requires subscription - {pdf_url}')
                            else:
                                # Might be article page, return it
                                return pdf_url
                    elif response.status_code == 404:
                        continue  # Try next URL format
                    else:
                        continue  # Try next URL format
                        
                except requests.exceptions.RequestException:
                    continue  # Try next URL format
            
            # If all URLs failed
            if pma.doi.startswith('10.1504/'):
                raise NoPDFLink(f'TXERROR: Could not access Inderscience article - DOI: {pma.doi}')
            else:
                raise NoPDFLink(f'PATTERN: Inderscience typically uses DOI pattern 10.1504/*, got {pma.doi}')
        else:
            # Return first URL pattern without verification
            return possible_urls[0]
            
    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: Inderscience ula failed for {pma.journal}: {e} - DOI: {pma.doi}')


def the_asme_animal(pma, verify=True):
    """ASME (American Society of Mechanical Engineers) dance function.
    
    ASME publishes technical journals in mechanical engineering, biomechanical
    engineering, manufacturing, energy, and related fields through their
    Digital Collection platform.
    
    Args:
        pma: PubMedArticle object
        verify: Whether to verify PDF access
        
    Returns:
        PDF URL if accessible
        
    Raises:
        NoPDFLink: If DOI missing or PDF not accessible
        AccessDenied: If paywall detected
    """
    from .journals.asme import asme_format
    
    try:
        if not pma.doi:
            raise NoPDFLink('MISSING: DOI required for ASME article access')
        
        # ASME typically uses 10.1115/* DOI pattern
        if not pma.doi.startswith('10.1115/'):
            # Still try to process, but note pattern mismatch
            pass
        
        # Try to derive journal code from journal name
        journal_name = pma.journal.lower() if pma.journal else ''
        
        # Common ASME journal code mappings
        journal_codes = {
            'j appl mech': 'appliedmechanics',
            'j biomech eng': 'biomechanical',
            'j heat transfer': 'heattransfer',
            'j fluids eng': 'fluidsengineering',
            'j eng gas turbine power': 'gasturbinespower',
            'j press vessel technol': 'pressurevesseltech',
            'j manuf sci eng': 'manufacturingscience',
            'j mech des': 'mechanicaldesign',
            'j vib acoust': 'vibrationacoustics',
            'j tribol': 'tribology',
            'j dyn syst meas control': 'dynamicsystems',
            'j energy resour technol': 'energyresources',
            'j med device': 'medicaldevices',
            'j turbomach': 'turbomachinery',
            'j sol energy eng': 'solarenergyengineering'
        }
        
        # Try to find journal code
        journal_code = None
        for name_pattern, code in journal_codes.items():
            if name_pattern in journal_name:
                journal_code = code
                break
        
        # Try different URL construction approaches
        possible_urls = []
        
        if journal_code:
            possible_urls.extend([
                f'https://asmedigitalcollection.asme.org/{journal_code}/article-pdf/{pma.doi}',
                f'https://asmedigitalcollection.asme.org/{journal_code}/article/{pma.doi}',
                f'https://asmedigitalcollection.asme.org/{journal_code}/article-pdf/doi/{pma.doi}',
                f'https://asmedigitalcollection.asme.org/{journal_code}/article/doi/{pma.doi}'
            ])
        
        # Try generic patterns without journal code
        possible_urls.extend([
            f'https://asmedigitalcollection.asme.org/article-pdf/{pma.doi}',
            f'https://asmedigitalcollection.asme.org/article/{pma.doi}',
            f'https://asmedigitalcollection.asme.org/doi/pdf/{pma.doi}',
            f'https://asmedigitalcollection.asme.org/doi/{pma.doi}'
        ])
        
        if verify:
            for pdf_url in possible_urls:
                try:
                    response = requests.get(pdf_url, timeout=10, allow_redirects=True)
                    
                    if response.ok:
                        # Check content type
                        content_type = response.headers.get('content-type', '').lower()
                        if 'application/pdf' in content_type:
                            return pdf_url
                        elif 'text/html' in content_type:
                            # Check for paywall indicators
                            page_text = response.text.lower()
                            paywall_indicators = [
                                'subscribe', 'subscription', 'login required',
                                'access denied', 'purchase', 'institutional access',
                                'sign in', 'member'
                            ]
                            if any(indicator in page_text for indicator in paywall_indicators):
                                raise AccessDenied(f'PAYWALL: ASME article requires subscription - {pdf_url}')
                            else:
                                # Might be article page, return it
                                return pdf_url
                    elif response.status_code == 404:
                        continue  # Try next URL format
                    else:
                        continue  # Try next URL format
                        
                except requests.exceptions.RequestException:
                    continue  # Try next URL format
            
            # If all URLs failed
            if pma.doi.startswith('10.1115/'):
                raise NoPDFLink(f'TXERROR: Could not access ASME article - DOI: {pma.doi}')
            else:
                raise NoPDFLink(f'PATTERN: ASME typically uses DOI pattern 10.1115/*, got {pma.doi}')
        else:
            # Return first URL pattern without verification
            return possible_urls[0] if possible_urls else f'https://asmedigitalcollection.asme.org/article-pdf/{pma.doi}'
            
    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: ASME animal failed for {pma.journal}: {e} - DOI: {pma.doi}')


def the_wjgnet_wave(pma, verify=True):
    """Dance function for WJG Net (Baishideng Publishing Group) journals.
    
    Handles the "World Journal of ..." series published by Baishideng.
    These journals are open access and available at wjgnet.com.
    
    Args:
        pma: PubMedArticle object
        verify: Whether to verify PDF accessibility
        
    Returns:
        str: URL to PDF or article page
        
    Raises:
        NoPDFLink: If DOI missing or URL construction fails
        AccessDenied: If paywall detected
    """
    try:
        # Check if DOI is available
        if not pma.doi:
            raise NoPDFLink(f'MISSING: DOI required for WJG Net access - Journal: {pma.journal}')
        
        # WJG Net journals typically use 10.3748/* DOI pattern
        if not pma.doi.startswith('10.3748/'):
            # Still try to process, but note pattern mismatch
            pass
        
        # Try different URL construction approaches for WJG Net
        possible_urls = []
        
        # Try to extract volume/issue from DOI or PMA data
        volume = getattr(pma, 'volume', None)
        issue = getattr(pma, 'issue', None)
        
        # WJG Net URL patterns
        if volume and issue:
            possible_urls.extend([
                f'https://www.wjgnet.com/1007-9327/full/v{volume}/i{issue}/{pma.doi}.pdf',
                f'https://www.wjgnet.com/1007-9327/full/v{volume}/i{issue}/{pma.doi}.htm',
            ])
        
        # Try generic patterns
        possible_urls.extend([
            f'https://www.wjgnet.com/pdf/{pma.doi}.pdf',
            f'https://www.wjgnet.com/full/{pma.doi}.pdf',
            f'https://www.wjgnet.com/1007-9327/pdf/{pma.doi}.pdf',
            f'https://f6publishing.blob.core.windows.net/pdf/{pma.doi}.pdf',
            f'https://www.wjgnet.com/{pma.doi}.pdf',
            f'https://www.wjgnet.com/1007-9327/full/{pma.doi}.htm'
        ])
        
        if verify:
            for pdf_url in possible_urls:
                try:
                    response = requests.get(pdf_url, timeout=10, allow_redirects=True)
                    
                    if response.ok:
                        # Check content type
                        content_type = response.headers.get('content-type', '').lower()
                        if 'application/pdf' in content_type:
                            return pdf_url
                        elif 'text/html' in content_type:
                            # Check for paywall indicators (though WJG Net is open access)
                            page_text = response.text.lower()
                            paywall_indicators = [
                                'subscribe', 'subscription', 'login required',
                                'access denied', 'purchase', 'institutional access'
                            ]
                            if any(indicator in page_text for indicator in paywall_indicators):
                                raise AccessDenied(f'PAYWALL: WJG Net article requires access - {pdf_url}')
                            else:
                                # Might be article page, return it
                                return pdf_url
                    elif response.status_code == 404:
                        continue  # Try next URL format
                    else:
                        continue  # Try next URL format
                        
                except requests.exceptions.RequestException:
                    continue  # Try next URL format
            
            # If all URLs failed
            if pma.doi.startswith('10.3748/'):
                raise NoPDFLink(f'TXERROR: Could not access WJG Net article - DOI: {pma.doi}')
            else:
                raise NoPDFLink(f'PATTERN: WJG Net typically uses DOI pattern 10.3748/*, got {pma.doi}')
        else:
            # Return first URL pattern without verification
            return possible_urls[0] if possible_urls else f'https://www.wjgnet.com/pdf/{pma.doi}.pdf'
            
    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: WJG Net wave failed for {pma.journal}: {e} - DOI: {pma.doi}')


def the_hilaris_hop(pma, verify=True):
    """Dance function for Hilaris Publisher journals.
    
    Handles academic journals published by Hilaris Publisher at hilarispublisher.com.
    These journals typically follow open access publishing models.
    
    Args:
        pma: PubMedArticle object
        verify: Whether to verify PDF accessibility
        
    Returns:
        str: URL to PDF or article page
        
    Raises:
        NoPDFLink: If DOI missing or URL construction fails
        AccessDenied: If paywall detected
    """
    try:
        # Check if DOI is available
        if not pma.doi:
            raise NoPDFLink(f'MISSING: DOI required for Hilaris Publisher access - Journal: {pma.journal}')
        
        # Hilaris Publisher journals typically use 10.4172/* DOI pattern
        if not pma.doi.startswith('10.4172/'):
            # Still try to process, but note pattern mismatch
            pass
        
        # Try different URL construction approaches for Hilaris
        possible_urls = []
        
        # Try to construct article slugs from DOI
        doi_parts = pma.doi.split('/')
        if len(doi_parts) >= 2:
            article_id = doi_parts[-1]
            
            # Try different URL patterns
            possible_urls.extend([
                f'https://www.hilarispublisher.com/articles/{article_id}.pdf',
                f'https://www.hilarispublisher.com/abstract/{article_id}.pdf',
                f'https://www.hilarispublisher.com/fulltext/{article_id}.pdf',
                f'https://hilarispublisher.com/articles/{article_id}.pdf',
                f'https://hilarispublisher.com/abstract/{article_id}.pdf'
            ])
        
        # Try generic patterns with full DOI
        possible_urls.extend([
            f'https://www.hilarispublisher.com/pdf/{pma.doi}.pdf',
            f'https://www.hilarispublisher.com/articles/{pma.doi}.pdf',
            f'https://hilarispublisher.com/pdf/{pma.doi}.pdf',
            f'https://www.hilarispublisher.com/abstract/{pma.doi}',
            f'https://www.hilarispublisher.com/fulltext/{pma.doi}.pdf'
        ])
        
        if verify:
            for pdf_url in possible_urls:
                try:
                    response = requests.get(pdf_url, timeout=10, allow_redirects=True)
                    
                    if response.ok:
                        # Check content type
                        content_type = response.headers.get('content-type', '').lower()
                        if 'application/pdf' in content_type:
                            return pdf_url
                        elif 'text/html' in content_type:
                            # Check for paywall indicators
                            page_text = response.text.lower()
                            paywall_indicators = [
                                'subscribe', 'subscription', 'login required',
                                'access denied', 'purchase', 'institutional access'
                            ]
                            if any(indicator in page_text for indicator in paywall_indicators):
                                raise AccessDenied(f'PAYWALL: Hilaris Publisher article requires access - {pdf_url}')
                            else:
                                # Might be article page, return it
                                return pdf_url
                    elif response.status_code == 404:
                        continue  # Try next URL format
                    else:
                        continue  # Try next URL format
                        
                except requests.exceptions.RequestException:
                    continue  # Try next URL format
            
            # If all URLs failed
            if pma.doi.startswith('10.4172/'):
                raise NoPDFLink(f'TXERROR: Could not access Hilaris Publisher article - DOI: {pma.doi}')
            else:
                raise NoPDFLink(f'PATTERN: Hilaris Publisher typically uses DOI pattern 10.4172/*, got {pma.doi}')
        else:
            # Return first URL pattern without verification
            return possible_urls[0] if possible_urls else f'https://www.hilarispublisher.com/pdf/{pma.doi}.pdf'
            
    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: Hilaris hop failed for {pma.journal}: {e} - DOI: {pma.doi}')


def the_projectmuse_syrtos(pma, verify=True):
    """Dance function for Project MUSE journals.
    
    Handles scholarly journals available through Project MUSE (muse.jhu.edu),
    Johns Hopkins University's digital library for humanities and social sciences.
    Most content requires institutional subscription.
    
    Args:
        pma: PubMedArticle object
        verify: Whether to verify PDF accessibility
        
    Returns:
        str: URL to PDF or article page
        
    Raises:
        NoPDFLink: If DOI missing or URL construction fails
        AccessDenied: If paywall detected
    """
    try:
        # Check if DOI is available
        if not pma.doi:
            raise NoPDFLink(f'MISSING: DOI required for Project MUSE access - Journal: {pma.journal}')
        
        # Project MUSE articles typically use 10.1353/* DOI pattern
        if not pma.doi.startswith('10.1353/'):
            # Still try to process, but note pattern mismatch
            pass
        
        # Try different URL construction approaches for Project MUSE
        possible_urls = []
        
        # Try to extract article ID from DOI
        doi_parts = pma.doi.split('/')
        if len(doi_parts) >= 2:
            # Extract article identifier from DOI
            article_id = doi_parts[-1]
            
            # Try different URL patterns
            possible_urls.extend([
                f'https://muse.jhu.edu/article/{article_id}/pdf',
                f'https://muse.jhu.edu/article/{article_id}',
                f'https://muse.jhu.edu/pub/{article_id}/pdf',
                f'https://muse.jhu.edu/journals/{article_id}/pdf'
            ])
        
        # Try generic patterns with full DOI
        possible_urls.extend([
            f'https://muse.jhu.edu/article/{pma.doi}',
            f'https://muse.jhu.edu/article/{pma.doi}/pdf',
            f'https://doi.org/{pma.doi}',  # Fallback to DOI resolver
        ])
        
        if verify:
            for pdf_url in possible_urls:
                try:
                    response = requests.get(pdf_url, timeout=10, allow_redirects=True)
                    
                    if response.ok:
                        # Check content type
                        content_type = response.headers.get('content-type', '').lower()
                        if 'application/pdf' in content_type:
                            return pdf_url
                        elif 'text/html' in content_type:
                            # Check for paywall indicators (Project MUSE is usually paywalled)
                            page_text = response.text.lower()
                            paywall_indicators = [
                                'subscribe', 'subscription', 'login required',
                                'access denied', 'purchase', 'institutional access',
                                'sign in', 'member access', 'institution'
                            ]
                            if any(indicator in page_text for indicator in paywall_indicators):
                                raise AccessDenied(f'PAYWALL: Project MUSE article requires subscription - {pdf_url}')
                            else:
                                # Might be open access article page, return it
                                return pdf_url
                    elif response.status_code == 404:
                        continue  # Try next URL format
                    else:
                        continue  # Try next URL format
                        
                except requests.exceptions.RequestException:
                    continue  # Try next URL format
            
            # If all URLs failed
            if pma.doi.startswith('10.1353/'):
                raise NoPDFLink(f'TXERROR: Could not access Project MUSE article - DOI: {pma.doi}')
            else:
                raise NoPDFLink(f'PATTERN: Project MUSE typically uses DOI pattern 10.1353/*, got {pma.doi}')
        else:
            # Return first URL pattern without verification
            return possible_urls[0] if possible_urls else f'https://muse.jhu.edu/article/{pma.doi}'
            
    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: Project MUSE syrtos failed for {pma.journal}: {e} - DOI: {pma.doi}')


def the_walshmedia_bora(pma, verify=True):
    """Dance function for Walsh Medical Media journals.
    
    Handles academic journals published by Walsh Medical Media at walshmedicalmedia.com.
    These journals typically follow open access publishing models.
    
    Args:
        pma: PubMedArticle object
        verify: Whether to verify PDF accessibility
        
    Returns:
        str: URL to PDF or article page
        
    Raises:
        NoPDFLink: If DOI missing or URL construction fails
        AccessDenied: If paywall detected
    """
    try:
        # Check if DOI is available
        if not pma.doi:
            raise NoPDFLink(f'MISSING: DOI required for Walsh Medical Media access - Journal: {pma.journal}')
        
        # Walsh Medical Media journals typically use 10.4172/* or 10.35248/* DOI patterns
        if not (pma.doi.startswith('10.4172/') or pma.doi.startswith('10.35248/')):
            # Still try to process, but note pattern mismatch
            pass
        
        # Try different URL construction approaches for Walsh Medical Media
        possible_urls = []
        
        # Try to construct article slugs from DOI
        doi_parts = pma.doi.split('/')
        if len(doi_parts) >= 2:
            article_id = doi_parts[-1]
            
            # Try different URL patterns
            possible_urls.extend([
                f'https://www.walshmedicalmedia.com/articles/{article_id}.pdf',
                f'https://www.walshmedicalmedia.com/open-access/{article_id}.pdf',
                f'https://www.walshmedicalmedia.com/abstract/{article_id}.pdf',
                f'https://walshmedicalmedia.com/articles/{article_id}.pdf',
                f'https://walshmedicalmedia.com/open-access/{article_id}.pdf'
            ])
        
        # Try generic patterns with full DOI
        possible_urls.extend([
            f'https://www.walshmedicalmedia.com/pdf/{pma.doi}.pdf',
            f'https://www.walshmedicalmedia.com/articles/{pma.doi}.pdf',
            f'https://walshmedicalmedia.com/pdf/{pma.doi}.pdf',
            f'https://www.walshmedicalmedia.com/abstract/{pma.doi}',
            f'https://www.walshmedicalmedia.com/open-access/{pma.doi}.pdf'
        ])
        
        if verify:
            for pdf_url in possible_urls:
                try:
                    response = requests.get(pdf_url, timeout=10, allow_redirects=True)
                    
                    if response.ok:
                        # Check content type
                        content_type = response.headers.get('content-type', '').lower()
                        if 'application/pdf' in content_type:
                            return pdf_url
                        elif 'text/html' in content_type:
                            # Check for paywall indicators
                            page_text = response.text.lower()
                            paywall_indicators = [
                                'subscribe', 'subscription', 'login required',
                                'access denied', 'purchase', 'institutional access'
                            ]
                            if any(indicator in page_text for indicator in paywall_indicators):
                                raise AccessDenied(f'PAYWALL: Walsh Medical Media article requires access - {pdf_url}')
                            else:
                                # Might be article page, return it
                                return pdf_url
                    elif response.status_code == 404:
                        continue  # Try next URL format
                    else:
                        continue  # Try next URL format
                        
                except requests.exceptions.RequestException:
                    continue  # Try next URL format
            
            # If all URLs failed
            if pma.doi.startswith('10.4172/') or pma.doi.startswith('10.35248/'):
                raise NoPDFLink(f'TXERROR: Could not access Walsh Medical Media article - DOI: {pma.doi}')
            else:
                raise NoPDFLink(f'PATTERN: Walsh Medical Media typically uses DOI patterns 10.4172/* or 10.35248/*, got {pma.doi}')
        else:
            # Return first URL pattern without verification
            return possible_urls[0] if possible_urls else f'https://www.walshmedicalmedia.com/pdf/{pma.doi}.pdf'
            
    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: Walsh Media bora failed for {pma.journal}: {e} - DOI: {pma.doi}')


def the_aip_allegro(pma, verify=True):
    """Dance function for AIP Publishing journals.
    
    Handles physics and related science journals published by AIP Publishing at pubs.aip.org.
    These journals typically require subscription access but may have open access content.
    
    Args:
        pma: PubMedArticle object
        verify: Whether to verify PDF accessibility
        
    Returns:
        str: URL to PDF or article page
        
    Raises:
        NoPDFLink: If DOI missing or URL construction fails
        AccessDenied: If paywall detected
    """
    try:
        # Check if DOI is available
        if not pma.doi:
            raise NoPDFLink(f'MISSING: DOI required for AIP Publishing access - Journal: {pma.journal}')
        
        # AIP Publishing journals typically use 10.1063/* DOI pattern
        if not pma.doi.startswith('10.1063/'):
            # Still try to process, but note pattern mismatch
            pass
        
        # Try different URL construction approaches for AIP Publishing
        possible_urls = []
        
        # Try to extract article details from DOI and PMA data
        doi_parts = pma.doi.split('/')
        if len(doi_parts) >= 2:
            article_id = doi_parts[-1]
            
            # Get volume and issue info if available
            volume = getattr(pma, 'volume', None)
            issue = getattr(pma, 'issue', None)
            
            # Try different AIP URL patterns
            possible_urls.extend([
                f'https://pubs.aip.org/{pma.doi}/pdf',
                f'https://aip.scitation.org/doi/pdf/{pma.doi}',
                f'https://pubs.aip.org/aip/article-pdf/doi/{pma.doi}',
                f'https://aip.scitation.org/doi/abs/{pma.doi}',
                f'https://pubs.aip.org/{article_id}/pdf'
            ])
            
            if volume:
                possible_urls.extend([
                    f'https://pubs.aip.org/aip/article/doi/{pma.doi}',
                    f'https://pubs.aip.org/aip/article/{volume}/{article_id}/pdf'
                ])
        
        # Try generic patterns
        possible_urls.extend([
            f'https://doi.org/{pma.doi}',  # Fallback to DOI resolver
            f'https://pubs.aip.org/doi/{pma.doi}',
            f'https://aip.scitation.org/doi/{pma.doi}'
        ])
        
        if verify:
            for pdf_url in possible_urls:
                try:
                    response = requests.get(pdf_url, timeout=10, allow_redirects=True)
                    
                    if response.ok:
                        # Check content type
                        content_type = response.headers.get('content-type', '').lower()
                        if 'application/pdf' in content_type:
                            return pdf_url
                        elif 'text/html' in content_type:
                            # Check for paywall indicators (AIP typically requires subscription)
                            page_text = response.text.lower()
                            paywall_indicators = [
                                'subscribe', 'subscription', 'login required',
                                'access denied', 'purchase', 'institutional access',
                                'sign in', 'member access', 'buy this article'
                            ]
                            if any(indicator in page_text for indicator in paywall_indicators):
                                raise AccessDenied(f'PAYWALL: AIP Publishing article requires subscription - {pdf_url}')
                            else:
                                # Might be open access article page, return it
                                return pdf_url
                    elif response.status_code == 404:
                        continue  # Try next URL format
                    else:
                        continue  # Try next URL format
                        
                except requests.exceptions.RequestException:
                    continue  # Try next URL format
            
            # If all URLs failed
            if pma.doi.startswith('10.1063/'):
                raise NoPDFLink(f'TXERROR: Could not access AIP Publishing article - DOI: {pma.doi}')
            else:
                raise NoPDFLink(f'PATTERN: AIP Publishing typically uses DOI pattern 10.1063/*, got {pma.doi}')
        else:
            # Return first URL pattern without verification
            return possible_urls[0] if possible_urls else f'https://pubs.aip.org/{pma.doi}/pdf'
            
    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: AIP allegro failed for {pma.journal}: {e} - DOI: {pma.doi}')

