"""Hilaris Publisher dance function - DOI RESOLUTION APPROACH.

EVIDENCE-DRIVEN REWRITE 2025-08-09:
- Uses DOI resolution which directly provides PDF URLs
- No HTML sample dependency - bypasses corrupted sample issue
- Single-method approach following DANCE_FUNCTION_GUIDELINES
- Simple error handling with verify_pdf_url integration
"""

from ...exceptions import *
from .generic import *


def the_hilaris_hop(pma, verify=True, request_timeout=10, max_redirects=3):
    """Dance function for Hilaris Publisher journals.

    EVIDENCE-DRIVEN APPROACH:
    DOI resolution for Hilaris articles (10.4172/ prefix) directly resolves to PDF URLs:
    https://www.hilarispublisher.com/open-access/{article-slug}-{doi-suffix}.pdf
    
    This approach bypasses the need for HTML sample analysis and works even when 
    HTML samples are corrupted or unavailable.

    Example:
    DOI: 10.4172/2161-0525.1000551
    Resolves to: https://www.hilarispublisher.com/open-access/environmental-toxins-...pdf

    Args:
        pma: PubMedArticle object
        verify: Whether to verify PDF accessibility

    Returns:
        str: Direct PDF URL

    Raises:
        NoPDFLink: If DOI missing or resolution fails
        AccessDenied: If paywall detected
    """
    if not pma.doi:
        raise NoPDFLink(f'MISSING: DOI required for Hilaris Publisher access - attempted: none')
    
    # Use DOI resolution to get direct PDF URL
    # This works because Hilaris DOIs resolve directly to PDF files
    pdf_url = the_doi_2step(pma.doi)
    
    # Verify it's actually a Hilaris URL
    if 'hilarispublisher.com' not in pdf_url.lower():
        raise NoPDFLink(f'INVALID: DOI did not resolve to Hilaris Publisher domain - resolved to: {pdf_url}')
    
    if verify:
        # Use standard verification - let AccessDenied bubble up naturally
        return verify_pdf_url(pdf_url, 'Hilaris Publisher', request_timeout=request_timeout, max_redirects=max_redirects)
    
    return pdf_url
