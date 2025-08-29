"""Ingenta Connect dance function - CLAUDE.md compliant rewrite.

Evidence-driven rewrite 2025-08-09:
- Uses simple DOI resolution + URL pattern transformation
- Follows CLAUDE.md guidelines: no huge try-except, let errors bubble up
- Uses standard verify_pdf_url for verification
- Simple, focused error handling
"""

from ...exceptions import NoPDFLink
from .generic import the_doi_2step, verify_pdf_url

def the_ingenta_flux(pma, verify=True, request_timeout=10, max_redirects=3):
    """Ingenta Connect dance using evidence-based DOI resolution pattern.

    Evidence from real PMIDs (38884108, 34707797):
    - DOI resolves to: https://www.ingentaconnect.com/content/...
    - PDF pattern: https://www.ingentaconnect.com/contentone/.../pdf
    - Simple transformation: /content/ → /contentone/ + /pdf

    Ingenta Connect is a digital publishing platform hosting content from 
    250+ publishers with diverse DOI prefixes, but consistent URL patterns.

    Examples:
    - PMID 38884108, DOI 10.5129/001041522x16222193902161
    - Resolves to: /content/cuny/cp/2022/.../art00007
    - PDF URL: /contentone/cuny/cp/2022/.../art00007/pdf

    Args:
        pma: PubMedArticle object
        verify: Whether to verify PDF accessibility

    Returns:
        str: Direct PDF URL

    Raises:
        NoPDFLink: If DOI missing or resolution fails
        AccessDenied: If paywall blocks access
    """
    if not pma.doi:
        raise NoPDFLink(f'MISSING: DOI required for Ingenta Connect access - attempted: none')

    # Resolve DOI to get article URL - let NoPDFLink bubble up from the_doi_2step
    article_url = the_doi_2step(pma.doi)
    
    # Verify it resolved to Ingenta Connect
    if 'ingentaconnect.com' not in article_url:
        raise NoPDFLink(f'INVALID: DOI did not resolve to Ingenta Connect domain - resolved to: {article_url}')
    
    # Apply evidence-based URL transformation: /content/ → /contentone/ + /pdf
    if '/content/' not in article_url:
        raise NoPDFLink(f'INVALID: Unexpected Ingenta Connect URL pattern - expected /content/ in: {article_url}')
    
    pdf_url = article_url.replace('/content/', '/contentone/').rstrip('/') + '/pdf'

    if verify:
        # Use standard verification - let AccessDenied bubble up naturally
        return verify_pdf_url(pdf_url, 'Ingenta Connect', request_timeout=request_timeout, max_redirects=max_redirects)

    return pdf_url
