"""
Evidence-Based Dance Function for AAAS (American Association for the Advancement of Science).

Based on HTML analysis of Science journals, this function handles the complex
authentication requirements for Science/Science Advances articles.

Key findings from HTML evidence:
- No citation_pdf_url meta tags available  
- Main article PDFs require subscription access
- Only supplementary material PDFs freely available
- Modern science.org domains (updated from legacy sciencemag.org)
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


def the_aaas_twist(pma, verify=True):
    """
    AAAS dance function for Science journals with subscription handling.
    
    Evidence-based approach: AAAS requires complex authentication and doesn't
    provide citation_pdf_url meta tags. Must use PMID lookup -> redirect approach.
    
    :param pma: PubMedArticle object
    :param verify: bool [default: True] - Recommended for navigation handling
    :return: PDF URL string
    :raises: AccessDenied, NoPDFLink
    """
    if not pma.pmid:
        raise NoPDFLink('MISSING: PMID required for AAAS article lookup (journal: %s)' % getattr(pma, 'journal', 'Unknown'))
    
    # Use modern science.org PMID lookup (updated from legacy sciencemag.org)
    baseurl = 'https://www.science.org/cgi/pmidlookup?view=long&pmid=%s' % pma.pmid
    
    try:
        res = unified_uri_get(baseurl)
        # Convert article URL to PDF URL
        # From: https://www.science.org/doi/10.1126/sciadv.abl6449
        # To: https://www.science.org/doi/pdf/10.1126/sciadv.abl6449
        if '.long' in res.url:
            pdfurl = res.url.replace('.long', '.full') + '.pdf'
        elif '/doi/' in res.url:
            pdfurl = res.url.replace('/doi/', '/doi/pdf/')
        else:
            # Fallback: assume it's the full URL and append .pdf
            pdfurl = res.url + '.pdf'
    except Exception as e:
        raise NoPDFLink('ERROR: AAAS PMID lookup failed for %s: %s' % (pma.pmid, str(e)))

    if not verify:
        return pdfurl

    # Attempt PDF access with subscription handling
    try:
        response = unified_uri_get(pdfurl)
    except Exception as e:
        raise NoPDFLink('ERROR: AAAS PDF access failed for %s: %s' % (pdfurl, str(e)))

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
                return _attempt_aaas_authentication(tree, response, pdfurl)
            else:
                raise AccessDenied('DENIED: AAAS subscription required (url: %s). Set AAAS_USERNAME/AAAS_PASSWORD for authentication.' % pdfurl)
                
        except (etree.XMLSyntaxError, AttributeError) as e:
            raise NoPDFLink('ERROR: Failed to parse AAAS HTML response for %s: %s' % (pdfurl, str(e)))
    
    # Other HTTP errors
    else:
        raise NoPDFLink('ERROR: AAAS returned HTTP %s for %s' % (response.status_code, pdfurl))


def _attempt_aaas_authentication(tree, response, pdfurl):
    """
    Attempt AAAS authentication using credentials.
    
    :param tree: Parsed HTML tree
    :param response: Initial response object  
    :param pdfurl: Original PDF URL
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
        
        auth_response = requests.post(post_url, data=payload)
        
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
