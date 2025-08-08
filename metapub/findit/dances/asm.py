from .generic import *
from ...exceptions import *

def the_asm_shimmy(pma, verify=True):
    '''Evidence-based dance function for American Society of Microbiology (ASM) journals.

    **EVIDENCE-DRIVEN PDF PATTERN UPDATE (2025-08-08)**
    Updated based on re-analysis of HTML samples showing direct PDF download links.
    ASM has modernized from legacy VIP approach to DOI-based PDF downloads.

    PDF Download Pattern: https://journals.asm.org/doi/pdf/{DOI}?download=true
    Evidence: All samples show consistent PDF download buttons with this pattern
    
    Reader Pattern: https://journals.asm.org/doi/reader/{DOI} (HTML view, not PDF)
    Legacy Pattern: http://{host}.asm.org/content/{volume}/{issue}/{page}.full.pdf (deprecated)

    Contract Compliance: Returns direct PDF URLs as required by DANCE_FUNCTION_GUIDELINES.
    "Function must return PDF link, nothing else (e.g. no article page as a runner-up!)"

    Benefits:
    - Direct PDF download URLs (not reader interface)
    - No journal name mapping required
    - No VIP metadata dependencies  
    - DOI-based URL construction only
    - Follows FindIt contract properly

    :param: pma (PubMedArticle object)
    :param: verify (bool) [default: True] 
    :return: url (string) - Direct PDF URL
    :raises: AccessDenied, NoPDFLink
    '''

    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for ASM PDF downloads - attempted: none')

    # ASM PDF download pattern (evidence from HTML samples analysis)
    # NOTE: Reader URLs (https://journals.asm.org/doi/reader/{doi}) were working as of ~2025-08-06
    # but PDF URLs are preferred per DANCE_FUNCTION_GUIDELINES (return PDF link, not article page)
    url = f'https://journals.asm.org/doi/pdf/{pma.doi}?download=true'

    if verify:
        verify_pdf_url(url, 'ASM')
    
    return url