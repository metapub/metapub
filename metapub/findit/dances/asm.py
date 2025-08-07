from .generic import *
from ...exceptions import *

def the_asm_shimmy(pma, verify=True):
    '''Evidence-based dance function for American Society of Microbiology (ASM) journals.

    **EVIDENCE-DRIVEN REWRITE (2025-08-07)**
    Based on analysis of 5 HTML samples showing 100% consistency with modern 
    /doi/reader/ pattern. ASM has modernized from legacy VIP approach.

    Modern Pattern: https://journals.asm.org/doi/reader/{DOI}
    Evidence: All 5 samples (PMIDs: 35856662, 36598232, 38329942, 38591913, 39382274)
    
    Legacy Pattern: http://{host}.asm.org/content/{volume}/{issue}/{page}.full.pdf
    Status: Deprecated - no longer found in HTML samples

    Benefits:
    - No journal name mapping required
    - No VIP metadata dependencies  
    - Direct DOI-based URL construction
    - Eliminates complex journal standardization
    - Follows DANCE_FUNCTION_GUIDELINES

    :param: pma (PubMedArticle object)
    :param: verify (bool) [default: True] 
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    '''

    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for ASM modern reader URLs - attempted: none')

    # Modern ASM uses centralized reader URLs (evidence from 5/5 HTML samples)
    url = f'https://journals.asm.org/doi/reader/{pma.doi}'

    if verify:
        verify_pdf_url(url, 'ASM')
    
    return url