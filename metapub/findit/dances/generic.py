"""Generic and framework dance functions.

This module contains dance functions that are not specific to individual publishers
but provide general framework functionality like DOI resolution, VIP-based URLs,
PII-based URLs, etc.
"""

from urllib.parse import urlsplit, urljoin
from datetime import datetime
import requests

from ...dx_doi import DxDOI, DX_DOI_URL
from ...pubmedarticle import square_voliss_data_for_pma
from ...exceptions import AccessDenied, NoPDFLink, BadDOI, DxDOIError
from ...text_mining import find_doi_in_string
from ...utils import remove_chars

from ..journals import (
    simple_formats_pmid, vip_format, vip_journals, vip_journals_nonstandard,
    simple_formats_pii, BMC_format
)
from ..registry import JournalRegistry

OK_STATUS_CODES = (200, 301, 302, 307)


# Enhanced browser headers optimized for Cloudflare bypass
# Based on testing that successfully unlocked University of Chicago Press
# We're not scraping, we're just checking something exists.
COMMON_REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
    "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"macOS"',
}

# Common paywall detection terms
PAYWALL_TERMS = [
    'paywall', 'subscribe', 'subscription', 'sign in', 'log in',
    'login required', 'access denied', 'purchase', 'institutional access',
    'member access', 'subscribe now', 'buy article', 'rent this article',
    'subscription required', 'checkLicense', 'member only', 'institution'
]


def unified_uri_get(uri, timeout=10, allow_redirects=True, params={},
                    headers=COMMON_REQUEST_HEADERS):
    response = requests.get(uri, headers=headers, allow_redirects=allow_redirects,
                            timeout=timeout, params=params)
    return response

def detect_paywall_from_html(html_content, publisher_name=''):
    """Detect if HTML content indicates a paywall.

    Args:
        html_content: HTML response text
        publisher_name: Optional publisher name for error messages

    Returns:
        bool: True if paywall detected, False otherwise
    """
    page_text = html_content.lower()
    return any(term in page_text for term in PAYWALL_TERMS)

# PMC URL constants
PMC_PDF_URL = 'https://www.ncbi.nlm.nih.gov/pmc/articles/pmid/{a.pmid}/pdf'
EUROPEPMC_PDF_URL = 'http://europepmc.org/backend/ptpmcrender.fcgi?accid=PMC{a.pmc}&blobtype=pdf'

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


def verify_pdf_url(pdfurl, publisher_name='', referrer=None):
    """
    Enhanced PDF URL verification with robust handling for various publisher quirks.
    
    This function tries multiple strategies to verify PDF accessibility:
    1. Standard request with SSL verification
    2. Request without SSL verification (for publishers with SSL issues like SCIRP)
    3. Validates actual PDF content, not just headers
    
    Args:
        pdfurl: PDF URL to verify
        publisher_name: Publisher name for error messages (default: '')
        referrer: Optional referrer URL for requests (default: None)
        
    Returns:
        The verified URL if successful
        
    Raises:
        NoPDFLink: If PDF cannot be accessed or verified
        AccessDenied: If access requires authentication (401) or is forbidden (403)
    """
    import ssl
    import certifi
    from urllib3.exceptions import InsecureRequestWarning
    import warnings
    
    # Suppress SSL warnings when we need to disable verification
    warnings.filterwarnings('ignore', category=InsecureRequestWarning)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/pdf,*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
    }
    
    if referrer:
        headers['Referer'] = referrer

    session = requests.Session()
    session.headers.update(headers)

    strategies = [
        # Strategy 1: Standard request with SSL verification
        {'verify': certifi.where(), 'name': 'Standard SSL'},
        # Strategy 2: No SSL verification (for publishers with SSL issues)
        {'verify': False, 'name': 'No SSL verification'},
    ]
    
    last_status_code = 0
    
    for strategy in strategies:
        try:
            response = session.get(pdfurl, timeout=15, allow_redirects=True, 
                                 **{k: v for k, v in strategy.items() if k != 'name'})
            
            last_status_code = response.status_code
            
            # Handle specific status codes
            if response.status_code == 401:
                raise AccessDenied('DENIED: %s url (%s) requires login.' % (publisher_name, pdfurl))
            elif response.status_code == 403:
                # Try next strategy for 403 - might be SSL issue
                continue
            elif response.status_code == 404:
                raise NoPDFLink('MISSING: %s url (%s) not found.' % (publisher_name, pdfurl))
            elif response.status_code == 200:
                # Verify it's actually PDF content
                if response.content.startswith(b'%PDF'):
                    return pdfurl
                # Also check Content-Type header as fallback
                elif 'application/pdf' in response.headers.get('Content-Type', ''):
                    return pdfurl
                # Check old way for backward compatibility
                elif 'pdf' in response.headers.get('content-type', '').lower():
                    return pdfurl
                else:
                    raise NoPDFLink('DENIED: %s url (%s) did not result in a PDF' % (publisher_name, pdfurl))
            elif response.status_code in OK_STATUS_CODES:
                # Handle redirects - if we got redirected and it's a PDF, accept it
                if (response.content.startswith(b'%PDF') or 
                    'application/pdf' in response.headers.get('Content-Type', '') or
                    'pdf' in response.headers.get('content-type', '').lower()):
                    return pdfurl
                else:
                    continue  # Try next strategy
            else:
                # Other status codes - try next strategy
                continue
                    
        except (requests.exceptions.SSLError, ssl.SSLError):
            # SSL errors - continue to next strategy
            continue
        except requests.exceptions.RequestException:
            # Other request errors - continue to next strategy
            continue
    
    # All strategies failed - raise appropriate error based on last status code
    if last_status_code == 403:
        raise AccessDenied('DENIED: %s url (%s) access forbidden.' % (publisher_name, pdfurl))
    elif last_status_code > 0:
        raise NoPDFLink('TXERROR: %i status returned from %s url (%s)' % (last_status_code, publisher_name, pdfurl))
    else:
        raise NoPDFLink('TXERROR: Could not access %s url (%s)' % (publisher_name, pdfurl))


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
