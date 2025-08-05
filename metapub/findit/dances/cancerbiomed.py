from ...exceptions import NoPDFLink
from .generic import verify_pdf_url


def the_cancerbiomed_quickstep(pma, verify=True):
    """Cancer Biology & Medicine: Direct PDF URL construction from VIP data
    
    Cancer Biology & Medicine uses a consistent URL pattern for PDF downloads:
    https://www.cancerbiomed.org/content/cbm/{volume}/{issue}/{first_page}.full.pdf
    
    :param: pma (PubmedArticle)
    :param: verify (bool) [default: True]
    :return: url (string)
    :raises: NoPDFLink
    """
    # Check for required VIP data
    if not all([pma.volume, pma.issue, pma.first_page]):
        missing = []
        if not pma.volume: missing.append('volume')
        if not pma.issue: missing.append('issue') 
        if not pma.first_page: missing.append('first_page')
        raise NoPDFLink(f'MISSING: VIP data required for Cancer Biology & Medicine - missing: {", ".join(missing)}')

    # Construct PDF URL directly from VIP data
    pdf_url = f'https://www.cancerbiomed.org/content/cbm/{pma.volume}/{pma.issue}/{pma.first_page}.full.pdf'
    
    if verify:
        verify_pdf_url(pdf_url, 'Cancer Biology & Medicine')
    
    return pdf_url