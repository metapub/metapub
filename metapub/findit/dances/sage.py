"""SAGE Publications dance function using evidence-driven /doi/reader/ pattern."""

from .generic import verify_pdf_url
from ...exceptions import NoPDFLink


def the_sage_hula(pma, verify=True):
    """SAGE Publications dance - uses /doi/reader/ for PDF/EPUB access.

    Evidence from HTML samples shows SAGE uses:
    - Article pages: https://journals.sagepub.com/doi/full/{DOI}
    - PDF/EPUB access: https://journals.sagepub.com/doi/reader/{DOI}

    Pattern discovered from samples:
    - DOI: 10.1177/0048393118767084 → PDF: /doi/reader/10.1177/0048393118767084
    - DOI: 10.1177/00405736221132863 → PDF: /doi/reader/10.1177/00405736221132863

    This pattern is consistent across all SAGE journals using their unified platform.

    :param: pma (PubMedArticle object)
    :param: verify (bool) [default: True]
    :return: url (str) - PDF/EPUB reader URL
    :raises: NoPDFLink
    """
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for SAGE Publications PDF access')

    # SAGE uses /doi/reader/ pattern for PDF/EPUB access
    # This provides their unified reader interface with PDF download options
    pdf_url = f'https://journals.sagepub.com/doi/reader/{pma.doi}'

    if verify:
        verify_pdf_url(pdf_url, 'SAGE')

    return pdf_url


