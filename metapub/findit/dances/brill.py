"""
Brill dance function.

PDF URL construction strategy:
- Resolve DOI via dx.doi.org to get the canonical article URL
- Derive PDF URL by replacing /view/journals/ with /downloadpdf/journals/
- This avoids scraping the article page entirely (which is behind AWS WAF)
- Falls back to HTML citation_pdf_url meta tag parsing if URL pattern doesn't match

URL pattern (consistent across all Brill journals):
  Article: https://brill.com/view/journals/{j}/{vol}/{iss}/article-p{page}_{id}.xml
  PDF:     https://brill.com/downloadpdf/journals/{j}/{vol}/{iss}/article-p{page}_{id}.xml
"""

import re
import requests
from .generic import the_doi_2step, verify_pdf_url, unified_uri_get
from ...exceptions import NoPDFLink, AccessDenied

BRILL_VIEW_PATH = '/view/journals/'
BRILL_PDF_PATH = '/downloadpdf/journals/'


def the_brill_bridge(pma, verify=True, request_timeout=10, max_redirects=3):
    """
    Brill dance function.

    Constructs the PDF URL from the DOI-resolved article URL without scraping
    the article page (which is behind AWS WAF bot protection).

    :param pma: PubMedArticle object
    :param verify: bool [default: True] - Verify PDF URL accessibility
    :return: PDF URL string
    :raises: NoPDFLink if DOI missing or URL construction fails
    :raises: AccessDenied if Brill WAF blocks verification
    """
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for Brill articles')

    article_url = the_doi_2step(pma.doi)

    if not article_url:
        raise NoPDFLink('MISSING: Could not resolve Brill DOI to article URL')

    # Derive PDF URL directly from article URL — no need to fetch the article page
    if BRILL_VIEW_PATH in article_url:
        pdf_url = article_url.replace(BRILL_VIEW_PATH, BRILL_PDF_PATH)
    else:
        # Fallback: fetch the page and look for citation_pdf_url meta tag
        pdf_url = _extract_pdf_url_from_page(article_url, request_timeout, max_redirects)

    if verify:
        try:
            verify_pdf_url(pdf_url, 'Brill', request_timeout=request_timeout, max_redirects=max_redirects)
        except Exception:
            # Fetch the page to check if it's a WAF block, for a clearer error
            try:
                response = unified_uri_get(article_url, timeout=request_timeout, max_redirects=max_redirects)
                if 'awswaf' in response.text or 'challenge.js' in response.text:
                    raise AccessDenied('DENIED: Brill is protected by AWS WAF bot detection (requires browser)')
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                pass
            raise

    return pdf_url


def _extract_pdf_url_from_page(article_url, request_timeout, max_redirects):
    """Fallback: fetch article page and extract citation_pdf_url meta tag."""
    try:
        response = unified_uri_get(article_url, timeout=request_timeout, max_redirects=max_redirects)
    except requests.exceptions.ConnectionError as e:
        raise NoPDFLink(f'TXERROR: Network error accessing Brill article: {e}')

    if response.status_code not in (200, 202, 301, 302, 307):
        raise NoPDFLink(f'TXERROR: Could not access Brill article page (HTTP {response.status_code})')

    if 'awswaf' in response.text or 'challenge.js' in response.text:
        raise AccessDenied('DENIED: Brill is protected by AWS WAF bot detection (requires browser)')

    pdf_match = re.search(r'<meta[^>]*name=["\']citation_pdf_url["\'][^>]*content=["\']([^"\']+)["\']',
                          response.text, re.IGNORECASE)
    if not pdf_match:
        raise NoPDFLink('MISSING: No PDF URL found via citation_pdf_url meta tag extraction')

    return pdf_match.group(1)
