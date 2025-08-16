"""Dance function for EurekaSelect (Bentham Science Publishers)."""

from ...exceptions import NoPDFLink, AccessDenied
from .generic import the_doi_2step, verify_pdf_url, unified_uri_get, COMMON_REQUEST_HEADERS
from lxml import html
import requests


def the_eureka_frug(pma, verify=True, request_timeout=10, max_redirects=3):
    """EurekaSelect - requires POST-based download (not compatible with FindIt URL model).

    IMPORTANT: EurekaSelect PDFs cannot be accessed via simple GET requests.
    They require a POST request with session-specific CSRF tokens and encrypted parameters.

    Evidence from HTML samples and user testing shows:
    - Direct PDF URLs (/article/{id}/pdf) consistently return HTTP 500 errors
    - "Download Article" button works via POST to https://www.eurekaselect.com/download_file
    - Required params: _token (CSRF), agree-flag=1, param (encrypted article data)

    To manually download EurekaSelect PDFs:
    1. Visit the article page: https://www.eurekaselect.com/article/{article_id}
    2. Click "Download Article" button
    3. Or programmatically: fetch page, extract form data, POST with session cookies

    Future consideration: Add a pdf_utils function that handles POST-based downloads
    with session management. Would need to extend FindIt model to support method="POST"
    and session requirements.
    """
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for EurekaSelect journals')

    # Step 1: Resolve DOI to article page
    try:
        article_url = the_doi_2step(pma.doi)
        response = unified_uri_get(article_url, timeout=request_timeout, max_redirects=max_redirects)
    except Exception as e:
        raise NoPDFLink(f'TXERROR: Could not resolve EurekaSelect DOI: {e}')

    if response.status_code != 200:
        raise NoPDFLink(f'TXERROR: Could not access EurekaSelect article page (HTTP {response.status_code})')

    if 'eurekaselect.com' not in response.url or '/article/' not in response.url:
        raise NoPDFLink(f'TXERROR: DOI does not resolve to EurekaSelect article - got {response.url}')

    # Extract article ID from resolved URL
    article_id = response.url.split('/article/')[-1].strip('/')

    # For EurekaSelect, we can only provide the article page URL and explain the limitation
    article_page_url = f"https://www.eurekaselect.com/article/{article_id}"

    # Throw informative error that includes the article URL but explains the limitation
    raise NoPDFLink(
        f'POSTONLY: EurekaSelect PDF requires POST request with session data - '
        f'cannot provide direct PDF URL. Visit article page and click "Download Article": '
        f'{article_page_url}'
    )

    # Note: The code below documents the actual POST process for future reference
    # but is unreachable due to the error above. This is intentional to maintain
    # FindIt's contract of returning only GET-able URLs.
    """
    # Step 2: Parse the page to find download form (DOCUMENTATION ONLY)
    tree = html.fromstring(response.content)

    # Find download form with PDF parameters
    forms = tree.xpath('//form[contains(@action, "download_file") and contains(@id, "download-form-pdf")]')
    if not forms:
        raise NoPDFLink('TXERROR: No PDF download form found on EurekaSelect page')

    form = forms[0]  # Use first PDF download form

    # Extract form parameters
    token = form.xpath('.//input[@name="_token"]/@value')
    param = form.xpath('.//input[@name="param"]/@value')

    if not token or not param:
        raise NoPDFLink('TXERROR: Missing required form parameters for EurekaSelect download')

    # Step 3: Submit POST request (requires session cookies)
    download_url = "https://www.eurekaselect.com/download_file"
    post_data = {
        '_token': token[0],
        'agree-flag': '1',
        'param': param[0]
    }

    headers = dict(COMMON_REQUEST_HEADERS)
    headers['Referer'] = response.url

    pdf_response = requests.post(
        download_url,
        data=post_data,
        cookies=response.cookies,
        headers=headers,
        timeout=30,
        allow_redirects=True
    )

    # This would get the PDF content, but we can't return a URL that works with GET
    """
