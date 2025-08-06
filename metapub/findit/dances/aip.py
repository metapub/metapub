"""AIP Publishing dance function using direct URL construction from DOI patterns."""

from .generic import verify_pdf_url
from ...exceptions import NoPDFLink


def the_aip_allegro(pma, verify=True):
    """AIP Publishing dance - direct PDF URL construction from DOI.
    
    AIP Publishing (pubs.aip.org) hosts physics and related science journals.
    **BLOCKED BY CLOUDFLARE**: HTML samples show Cloudflare protection blocking access.
    
    Pattern based on AIP URL structure:
    - DOI: 10.1063/1.5093924 → PDF: https://pubs.aip.org/aip/article-pdf/doi/10.1063/1.5093924
    - DOI: 10.1063/5.0026818 → PDF: https://pubs.aip.org/aip/article-pdf/doi/10.1063/5.0026818
    
    TRUST THE REGISTRY: Function trusts that registry assigns AIP articles correctly.
    The function constructs correct URLs but verification may fail due to Cloudflare bot protection.
    
    :param: pma (PubMedArticle object)
    :param: verify (bool) [default: True]
    :return: url (str) - Direct PDF URL
    :raises: NoPDFLink
    """
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for AIP Publishing PDF access')
    
    # AIP Publishing uses direct DOI-based PDF URLs
    pdf_url = f'https://pubs.aip.org/aip/article-pdf/doi/{pma.doi}'
    
    if verify:
        verify_pdf_url(pdf_url, 'AIP')
        
    return pdf_url