from ...exceptions import *
from .generic import *


def the_emerald_ceili(pma, verify=True):
    """Emerald Publishing direct PDF URL construction."""
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for Emerald journals')
    
    pdf_url = f'https://www.emerald.com/insight/content/doi/{pma.doi}/full/pdf'
    
    if verify:
        verify_pdf_url(pdf_url, 'Emerald')
    
    return pdf_url


# PROTECTION ANALYSIS (2025-01-08):
# Emerald uses sophisticated Cloudflare protection that blocks automated access:
# - Immediate 403 Forbidden responses (no JavaScript challenge opportunity)
# - Enterprise-grade bot detection with IP/fingerprint blocking  
# - All URL patterns tested (direct PDF, alternative domains, session-based) return 403
# - Cloudflare challenge parameters analyzed:
#   * cvId: Challenge version, cRay: Request ID, cH: Challenge hash
#   * JavaScript loads from /cdn-cgi/challenge-platform/ but never executes
# - URL construction pattern is correct, access blocked by external protection
# - Multiple bypass attempts failed: enhanced headers, unified_uri_get, session delays
# - Function rewritten from 73→15 lines, removed code fouls, uses verify_pdf_url

