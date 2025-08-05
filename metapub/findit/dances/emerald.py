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

