"""Dance function for OAText Publishing."""

import re
from urllib.parse import urljoin

from ...exceptions import NoPDFLink, AccessDenied
from .generic import verify_pdf_url, unified_uri_get, the_doi_2step


def the_oatext_orbit(pma, verify=True):
    """OAText dance - resolve DOI then extract PDF link from article page.
    
    OAText is an open access publisher that uses DOI resolution to article pages,
    with PDF links embedded in the page HTML. Evidence from HTML samples shows
    consistent pattern: <a href="pdf/JOURNAL-VOLUME-ARTICLE.pdf" target="_blank">
    
    Evidence-driven analysis:
    - DOI 10.15761/JSIN.1000229 → article page → pdf/JSIN-6-229.pdf
    - DOI 10.15761/JSIN.1000228 → article page → pdf/JSIN-6-228.pdf
    
    Strategy: Use DOI resolution to get article page, then parse PDF link.
    
    :param: pma (PubMedArticle object)
    :param: verify (bool) [default: True]
    :return: url (str) - Direct PDF URL
    :raises: NoPDFLink
    """
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for OAText PDF access')
    
    # Step 1: Resolve DOI to get article page
    article_url = the_doi_2step(pma.doi)
    
    # Step 2: Fetch article page and extract PDF link
    response = unified_uri_get(article_url)
    if not response.ok:
        raise NoPDFLink(f'TXERROR: Could not fetch OAText article page - Status: {response.status_code}')
    
    # Step 3: Extract PDF link using regex pattern from evidence
    # Pattern: href="pdf/JOURNAL-VOLUME-ARTICLE.pdf" target="_blank"
    pdf_pattern = r'href="(pdf/[^"]+\.pdf)"[^>]*target="_blank"'
    matches = re.search(pdf_pattern, response.text, re.IGNORECASE)
    
    if not matches:
        raise NoPDFLink('TXERROR: Could not find PDF link in OAText article page')
    
    # Step 4: Construct full PDF URL
    pdf_path = matches.group(1)
    pdf_url = urljoin(article_url, pdf_path)
    
    if verify:
        verify_pdf_url(pdf_url, 'OAText')
    
    return pdf_url

