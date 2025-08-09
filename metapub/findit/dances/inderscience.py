"""Inderscience Publishers dance function - CLAUDE.md compliant rewrite.

Evidence-driven rewrite 2025-08-09:
- Uses consistent DOI-based URL pattern discovered from real PMIDs
- Follows CLAUDE.md guidelines: no huge try-except, let errors bubble up
- Uses standard verify_pdf_url for verification
- Simple, focused error handling
"""

from ...exceptions import NoPDFLink
from .generic import verify_pdf_url

def the_inderscience_ula(pma, verify=True):
    """Inderscience Publishers dance using evidence-based DOI pattern.

    Evidence from real PMIDs (24084238, 24794070, 24449692):
    - DOI Pattern: 10.1504/* (Inderscience DOI prefix)
    - URL Pattern: https://www.inderscienceonline.com/doi/epdf/{doi}
    - Publisher Status: Protected by Cloudflare (access typically blocked)

    Examples:
    - PMID 24084238, DOI 10.1504/IJBRA.2013.056620
    - URL: https://www.inderscienceonline.com/doi/epdf/10.1504/IJBRA.2013.056620

    Args:
        pma: PubMedArticle object
        verify: Whether to verify PDF accessibility

    Returns:
        str: Direct PDF URL

    Raises:
        NoPDFLink: If DOI missing
        AccessDenied: If Cloudflare/paywall blocks access (common)
    """
    if not pma.doi:
        raise NoPDFLink(f'MISSING: DOI required for Inderscience Publishers access - attempted: none')

    # Construct PDF URL using evidence-based pattern
    pdf_url = f'https://www.inderscienceonline.com/doi/epdf/{pma.doi}'

    if verify:
        # Use standard verification - let AccessDenied bubble up naturally
        return verify_pdf_url(pdf_url, 'Inderscience Publishers')

    return pdf_url
