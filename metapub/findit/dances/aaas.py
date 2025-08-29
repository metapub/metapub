"""
Evidence-Based Dance Function for AAAS (American Association for the Advancement of Science).

Based on HTML analysis of Science journals from 2025-01-08, this function uses
the correct URL patterns discovered in actual AAAS article pages.

Key findings from HTML evidence (samples from output/article_html/aaas/):
- No citation_pdf_url meta tags available  
- PDF links use pattern: /doi/reader/{DOI} (not /doi/pdf/)
- Articles show: <a href="/doi/reader/10.1126/sciadv.abl6449" aria-label="PDF">
- All PDFs require subscription access (403 Forbidden)
- Open access articles only available via PMC fallback
- Modern science.org domains (updated from legacy sciencemag.org)

Evidence-based URL construction: https://www.science.org/doi/reader/{DOI}
"""

from urllib.parse import urlsplit
from lxml.html import HTMLParser
from lxml import etree
import os
import requests

from ...exceptions import AccessDenied, NoPDFLink
from .generic import unified_uri_get

AAAS_USERNAME = os.environ.get("AAAS_USERNAME", "set in env: AAAS_USERNAME and AAAS_PASSWORD")
AAAS_PASSWORD = os.environ.get("AAAS_PASSWORD", "")


def the_aaas_twist(pma, verify=True, request_timeout=10, max_redirects=3):
    """
    AAAS dance function for Science journals with evidence-based URL construction.
    
    Evidence-based approach: HTML samples show AAAS uses /doi/reader/{DOI} pattern
    for PDF access. Falls back to PMID lookup if DOI unavailable.
    
    :param pma: PubMedArticle object
    :param verify: bool [default: True] - Recommended for navigation handling
    :param request_timeout: int [default: 10] - HTTP request timeout in seconds
    :param max_redirects: int [default: 3] - Maximum redirects to follow
    :return: PDF URL string
    :raises: AccessDenied, NoPDFLink
    """
    
    # Primary approach: Direct DOI-based URL construction (evidence-based)
    if pma.doi:
        # Evidence from HTML samples: AAAS uses /doi/reader/ pattern for PDFs
        pdfurl = 'https://www.science.org/doi/reader/%s' % pma.doi
    
    # Fallback: PMID lookup approach (legacy)
    elif pma.pmid:
        baseurl = 'https://www.science.org/cgi/pmidlookup?view=long&pmid=%s' % pma.pmid
        
        try:
            res = unified_uri_get(baseurl, timeout=request_timeout, max_redirects=max_redirects)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout,
                requests.exceptions.RequestException) as e:
            raise NoPDFLink('TXERROR: AAAS PMID lookup failed for %s: %s' % (pma.pmid, str(e)))
        
        # Convert article URL to reader URL (evidence-based pattern)
        if '/doi/' in res.url:
            # Extract DOI from redirected URL and construct reader URL
            doi_part = res.url.split('/doi/')[-1]
            pdfurl = 'https://www.science.org/doi/reader/%s' % doi_part
        else:
            # Fallback: assume it's the full URL and use reader pattern
            pdfurl = res.url.replace('/doi/', '/doi/reader/')
    
    else:
        raise NoPDFLink('MISSING: Either DOI or PMID required for AAAS article lookup (journal: %s)' % getattr(pma, 'journal', 'Unknown'))

    if not verify:
        return pdfurl

    # Attempt PDF access with subscription handling
    try:
        response = unified_uri_get(pdfurl, timeout=request_timeout, max_redirects=max_redirects)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout,
            requests.exceptions.RequestException) as e:
        raise NoPDFLink('TXERROR: AAAS PDF access failed for %s: %s' % (pdfurl, str(e)))

    # Success: Direct PDF access
    if response.status_code == 200 and 'pdf' in response.headers.get('content-type', '').lower():
        return response.url

    # Paywall detected: HTML response indicates subscription required
    elif response.status_code == 200 and 'html' in response.headers.get('content-type', '').lower():
        try:
            tree = etree.fromstring(response.content, HTMLParser())
            title_element = tree.find('head/title')
            title_text = title_element.text if title_element is not None else ""
            
            # Check for sign-in requirement
            if 'Sign In' not in title_text:
                raise NoPDFLink('TXERROR: AAAS returned unexpected HTML for %s (title: %s)' % (pdfurl, title_text[:100]))
            
            # Subscription required - attempt authentication if credentials provided
            if AAAS_USERNAME and AAAS_PASSWORD and 'set in env:' not in AAAS_USERNAME:
                return _attempt_aaas_authentication(tree, response, pdfurl, request_timeout, max_redirects)
            else:
                raise AccessDenied('DENIED: AAAS subscription required (url: %s). Set AAAS_USERNAME/AAAS_PASSWORD for authentication.' % pdfurl)
                
        except (etree.XMLSyntaxError, AttributeError) as e:
            raise NoPDFLink('ERROR: Failed to parse AAAS HTML response for %s: %s' % (pdfurl, str(e)))
    
    # Other HTTP errors
    else:
        raise NoPDFLink('ERROR: AAAS returned HTTP %s for %s' % (response.status_code, pdfurl))


def _attempt_aaas_authentication(tree, response, pdfurl, request_timeout, max_redirects):
    """
    Attempt AAAS authentication using credentials.
    
    :param tree: Parsed HTML tree
    :param response: Initial response object  
    :param pdfurl: Original PDF URL
    :param request_timeout: HTTP request timeout in seconds
    :param max_redirects: Maximum redirects to follow
    :return: Authenticated PDF URL
    :raises: AccessDenied, NoPDFLink
    """
    try:
        # Find authentication form
        forms = tree.cssselect('form')
        if not forms:
            raise NoPDFLink('ERROR: No authentication form found on AAAS page')
            
        form = forms[0]
        form_build_id = form.fields.get('form_build_id', '')
        
        # Construct authentication URL
        baseurl = urlsplit(response.url)
        post_url = f"{baseurl.scheme}://{baseurl.hostname}{form.action}"
        
        # Submit authentication
        payload = {
            'pass': AAAS_PASSWORD,
            'name': AAAS_USERNAME,
            'form_build_id': form_build_id,
            'remember_me': 1
        }
        
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=0)
        adapter.max_retries.redirect = max_redirects
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        auth_response = session.post(post_url, data=payload, timeout=request_timeout)
        
        # Handle authentication response
        if auth_response.status_code == 403:
            raise AccessDenied('DENIED: AAAS authentication failed (invalid credentials for %s)' % pdfurl)
        elif 'pdf' in auth_response.headers.get('content-type', '').lower():
            return auth_response.url
        elif 'html' in auth_response.headers.get('content-type', '').lower():
            # Check for access denied in content
            if b'access-denied' in auth_response.content.lower():
                raise AccessDenied('DENIED: AAAS subscription insufficient for %s' % pdfurl)
            else:
                raise NoPDFLink('ERROR: AAAS authentication succeeded but PDF not accessible for %s' % pdfurl)
        else:
            raise NoPDFLink('ERROR: AAAS authentication returned unexpected response for %s' % pdfurl)
            
    except requests.RequestException as e:
        raise NoPDFLink('ERROR: AAAS authentication request failed for %s: %s' % (pdfurl, str(e)))
    except (AttributeError, KeyError) as e:
        raise NoPDFLink('ERROR: AAAS authentication form parsing failed for %s: %s' % (pdfurl, str(e)))
