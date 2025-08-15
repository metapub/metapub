"""Dance function for WJGNet (World Journal of Gastroenterology Network)."""

import re

from ...exceptions import NoPDFLink, AccessDenied  
from .generic import verify_pdf_url, unified_uri_get, the_doi_2step


def the_wjgnet_wave(pma, verify=True, request_timeout=10, max_redirects=3):
    """WJGNet dance - resolve DOI then extract PDF link from article page.
    
    WJGNet uses a two-tier system where article pages are on wjgnet.com
    and PDF downloads are served by f6publishing.com with dynamic URLs.
    Evidence from HTML samples shows consistent patterns:
    
    - DOI resolution: 10.5495/wjcid.v10.i1.14 → wjgnet.com article page
    - PDF extraction: "Full Article with Cover (PDF)" or "Full Article (PDF)" 
    - PDF URLs: f6publishing.com/forms/main/DownLoadFile.aspx with encrypted FilePath
    
    Evidence-driven patterns discovered from 5 HTML samples:
    - All have DOI metadata available
    - All have f6publishing.com PDF download links
    - TypeId=1 (Full Article with Cover) or TypeId=22 (Full Article) both work
    
    Strategy: Use DOI resolution to get article page, then extract PDF link.
    
    :param: pma (PubMedArticle object)
    :param: verify (bool) [default: True]
    :return: url (str) - Direct PDF download URL
    :raises: NoPDFLink
    """
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for WJGNet PDF access')
    
    # Step 1: Resolve DOI to get article page
    article_url = the_doi_2step(pma.doi)
    
    # Step 2: Fetch article page and extract PDF link
    response = unified_uri_get(article_url, timeout=request_timeout, max_redirects=max_redirects)
    if not response.ok:
        raise NoPDFLink(f'TXERROR: Could not fetch WJGNet article page - Status: {response.status_code}')
    
    # Step 3: Extract PDF link using regex pattern from evidence
    # Pattern matches both "Full Article (PDF)" and "Full Article with Cover (PDF)"
    pdf_pattern = r'href="(https://www\.f6publishing\.com/forms/main/DownLoadFile\.aspx[^"]*)"[^>]*>Full Article[^<]*\(PDF\)'
    matches = re.search(pdf_pattern, response.text, re.IGNORECASE)
    
    if not matches:
        raise NoPDFLink('TXERROR: Could not find PDF link in WJGNet article page')
    
    # Step 4: Get the PDF URL (it's already complete)
    pdf_url = matches.group(1)
    
    # HTML entities in URLs are already decoded by the regex match
    # Convert &amp; back to & if needed
    pdf_url = pdf_url.replace('&amp;', '&')
    
    if verify:
        verify_pdf_url(pdf_url, 'WJGNet', request_timeout=request_timeout, max_redirects=max_redirects)
    
    return pdf_url