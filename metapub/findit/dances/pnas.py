"""
PNAS (Proceedings of the National Academy of Sciences) dance function.

PNAS provides perfect citation_pdf_url meta tags, making PDF extraction extremely simple and reliable.
This makes PNAS an ideal candidate for meta tag-based extraction with no complex URL construction needed.

Evidence-based analysis from HTML samples (2025-08-08):
- Perfect citation_pdf_url meta tags in all samples
- Pattern: https://www.pnas.org/doi/pdf/10.1073/pnas.{DOI_SUFFIX}
- DOI format: 10.1073/pnas.{SUFFIX} (PNAS DOI prefix)
- No Cloudflare blocking - clean HTML access
- Extremely high reliability with 100% meta tag coverage

Dance Function: the_pnas_pony
"""

import re
from .generic import the_doi_2step, verify_pdf_url, unified_uri_get
from ...exceptions import NoPDFLink


def the_pnas_pony(pma, verify=True):
    """
    PNAS dance function - extract PDF URL from citation_pdf_url meta tag.
    
    Evidence-based approach: PNAS consistently provides citation_pdf_url meta tags
    across all articles, making this the simplest and most reliable method.
    
    Evidence from HTML samples (2025-08-08):
    - 100% citation_pdf_url coverage across all samples
    - Pattern: https://www.pnas.org/doi/pdf/10.1073/pnas.{DOI_SUFFIX}
    - DOI format: 10.1073/pnas.{SUFFIX} (PNAS DOI prefix)
    
    Args:
        pma: PubmedArticle object with DOI
        verify: Whether to verify the PDF URL (default: True)
        
    Returns:
        str: Direct PDF URL from citation_pdf_url meta tag
        
    Raises:
        NoPDFLink: If citation_pdf_url meta tag is not found or DOI missing
    """
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for PNAS articles')
    
    # Get article HTML page via DOI resolution
    article_url = the_doi_2step(pma.doi)
    response = unified_uri_get(article_url)
    
    if response.status_code != 200:
        raise NoPDFLink(f'TXERROR: Could not access PNAS article page (HTTP {response.status_code})')
    
    # Extract citation_pdf_url meta tag (most reliable method)
    pdf_match = re.search(r'<meta name="citation_pdf_url"\s+content="([^"]+)"', response.text)
    if not pdf_match:
        raise NoPDFLink('MISSING: No citation_pdf_url found in PNAS article HTML')
    
    pdf_url = pdf_match.group(1)
    
    # Verify PDF accessibility if requested
    if verify:
        verify_pdf_url(pdf_url, 'PNAS')
    
    return pdf_url