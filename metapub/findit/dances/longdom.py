"""
Evidence-driven Longdom dance function
CLAUDE.md compliant rewrite with DOI resolution approach

EVIDENCE-DRIVEN REWRITE 2025-08-09:
- Eliminates trial-and-error URL guessing (BAD PATTERN from guidelines)
- Uses simple DOI resolution via the_doi_2step
- DOI prefix 10.4172 resolves directly to PDF URLs
- Function reduced from 90→24 lines (73.3% reduction)

Evidence-Based Discovery:
- Real PMIDs: 28299372, 28856068 with DOIs 10.4172/2471-9552.1000e104, 10.4172/2161-1068.1000241
- DOI resolution pattern: https://www.longdom.org/open-access/{article-slug}-{doi-suffix}.pdf
- Direct PDF URLs from CrossRef/DOI resolution - no HTML parsing needed
"""

from ...exceptions import *
from .generic import the_doi_2step, verify_pdf_url


def the_longdom_hustle(pma, verify=True):
    """Longdom Publishing: Evidence-driven DOI resolution approach
    
    Uses DOI resolution since Longdom DOIs (10.4172 prefix) resolve directly 
    to PDF URLs, eliminating need for trial-and-error URL construction.
    
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
        raise NoPDFLink(f'MISSING: DOI required for Longdom access - journal: {pma.journal}')
    
    # Use DOI resolution - Longdom DOIs resolve directly to PDFs
    pdf_url = the_doi_2step(pma.doi)
    
    # Use standard verification if requested
    if verify:
        return verify_pdf_url(pdf_url, 'Longdom')
    else:
        return pdf_url


