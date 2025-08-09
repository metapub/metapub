"""
Evidence-driven Walsh Medical Media dance function
CLAUDE.md compliant rewrite with DOI resolution approach

EVIDENCE-DRIVEN REWRITE 2025-08-09:
- Eliminates trial-and-error URL guessing (BAD PATTERN from guidelines)  
- Uses simple DOI resolution via the_doi_2step
- Walsh Medical Media DOIs resolve directly to PDF URLs with article slugs
- Function reduced from 90→24 lines (73.3% reduction)

Evidence-Based Discovery:
- Real PMID: 29226023 with DOI 10.4172/2161-1122.1000448
- DOI resolution: https://www.walshmedicalmedia.com/open-access/evaluating-the-whitening-and-microstructural-effects-of-a-novel-whitening-strip-on-porcelain-and-composite-dental-materials-2161-1122-1000449.pdf
- Direct PDF access from DOI resolution - no HTML parsing or URL construction needed
"""

from ...exceptions import *
from .generic import the_doi_2step, verify_pdf_url


def the_walshmedia_bora(pma, verify=True):
    """Walsh Medical Media: Evidence-driven DOI resolution approach
    
    Uses DOI resolution since Walsh Medical Media DOIs resolve directly 
    to PDF URLs with meaningful article slugs, eliminating need for 
    trial-and-error URL construction.
    
    Args:
        pma: PubMedArticle instance with DOI
        verify: Whether to verify PDF accessibility (default: True)
        
    Returns:
        PDF URL string if accessible
        
    Raises:
        NoPDFLink: If no DOI available  
        AccessDenied: If paywall detected during verification
    """
    # Check for required DOI
    if not pma.doi:
        raise NoPDFLink(f'MISSING: DOI required for Walsh Medical Media access - journal: {pma.journal}')
    
    # Use DOI resolution - Walsh Medical Media DOIs resolve directly to PDFs
    pdf_url = the_doi_2step(pma.doi)
    
    # Use standard verification if requested
    if verify:
        return verify_pdf_url(pdf_url, 'Walsh Medical Media')
    else:
        return pdf_url