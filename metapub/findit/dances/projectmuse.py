"""
Project MUSE dance function.

PDF URL construction strategy:
- Resolve DOI via dx.doi.org
- If muse.jhu.edu redirects to /verify?url=..., extract the article path
  and construct the PDF URL directly (avoids the human-verification page)
- If DOI resolves to another domain (e.g. cambridge.org), fall back to
  fetching the page and extracting the citation_pdf_url meta tag

muse.jhu.edu verify redirect pattern (observed March 2026):
  DOI resolves to: https://muse.jhu.edu/verify?url=%2Farticle%2F{id}&r={rand}
  PDF URL:         https://muse.jhu.edu/article/{id}/pdf
"""

import re
from urllib.parse import urlparse, parse_qs, unquote
from .generic import the_doi_2step, verify_pdf_url, unified_uri_get
from ...exceptions import NoPDFLink, AccessDenied

MUSE_HOST = 'muse.jhu.edu'


def the_projectmuse_syrtos(pma, verify=True, request_timeout=10, max_redirects=3):
    """
    Project MUSE dance function.

    Constructs the PDF URL from the DOI-resolved URL. When muse.jhu.edu
    redirects through its /verify human-verification page, extracts the
    article ID and builds the PDF URL without fetching the blocked page.

    :param pma: PubMedArticle object
    :param verify: bool [default: True] - Verify PDF URL accessibility
    :return: PDF URL string
    :raises: NoPDFLink if DOI missing or URL construction fails
    :raises: AccessDenied if Project MUSE verification page blocks access
    """
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for Project MUSE articles')

    article_url = the_doi_2step(pma.doi)

    if not article_url:
        raise NoPDFLink('MISSING: Could not resolve Project MUSE DOI to article URL')

    parsed = urlparse(article_url)

    # muse.jhu.edu is serving human-verification redirects — extract article
    # path from the verify URL and construct PDF URL directly
    if parsed.netloc == MUSE_HOST and parsed.path == '/verify':
        params = parse_qs(parsed.query)
        article_path = unquote(params.get('url', [''])[0])
        if not article_path:
            raise NoPDFLink('MISSING: Could not extract article path from Project MUSE verify URL')
        pdf_url = f'https://{MUSE_HOST}{article_path}/pdf'

        if verify:
            response = unified_uri_get(pdf_url, timeout=request_timeout, max_redirects=max_redirects)
            if parsed.netloc == MUSE_HOST and 'verify' in response.url:
                raise AccessDenied('DENIED: Project MUSE requires human verification (bot protection)')
            verify_pdf_url(pdf_url, 'Project MUSE', request_timeout=request_timeout, max_redirects=max_redirects)

        return pdf_url

    # DOI resolved to a regular page (muse.jhu.edu article or another domain)
    # Fetch and extract citation_pdf_url meta tag
    response = unified_uri_get(article_url, timeout=request_timeout, max_redirects=max_redirects)

    if response.status_code not in (200, 301, 302, 307):
        raise NoPDFLink(f'TXERROR: Could not access Project MUSE article page (HTTP {response.status_code})')

    # Check if we got bounced to a verify page anyway (detect by page content)
    if 'Verification required' in response.text or 'verify_form' in response.text:
        raise AccessDenied('DENIED: Project MUSE requires human verification (bot protection)')

    pdf_match = re.search(r'<meta[^>]*name=["\']citation_pdf_url["\'][^>]*content=["\']([^"\']+)["\']',
                          response.text, re.IGNORECASE)

    if not pdf_match:
        raise NoPDFLink('MISSING: No PDF URL found via citation_pdf_url meta tag extraction')

    pdf_url = pdf_match.group(1)

    if verify:
        verify_pdf_url(pdf_url, 'Project MUSE', request_timeout=request_timeout, max_redirects=max_redirects)

    return pdf_url
