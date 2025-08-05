from ...exceptions import NoPDFLink
from .generic import verify_pdf_url


def the_spandidos_lambada(pma, verify=True):
    """Spandidos Publications: Direct PDF URL construction from DOI
    
    Spandidos uses a consistent URL pattern for PDF downloads:
    http://www.spandidos-publications.com/{DOI}/download
    
    :param: pma (PubmedArticle)
    :param: verify (bool) [default: True]
    :return: url (string)
    :raises: NoPDFLink
    """
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for Spandidos journals')

    # Construct PDF URL directly from DOI
    pdf_url = f'http://www.spandidos-publications.com/{pma.doi}/download'
    
    if verify:
        verify_pdf_url(pdf_url, 'Spandidos')
    
    return pdf_url


