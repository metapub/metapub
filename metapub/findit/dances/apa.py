"""APA (American Psychological Association) dance function.
"""

from ...exceptions import *
from .generic import *


def the_apa_dab(pma, verify=True):
    """Dance function for American Psychological Association (APA) journals.

    APA journals are hosted on PsycNET (psycnet.apa.org) with consistent pattern.
    Most articles require subscription access.

    Pattern: https://psycnet.apa.org/fulltext/{DOI}.pdf

    Args:
        pma: PubMedArticle object
        verify: Whether to verify PDF accessibility

    Returns:
        str: URL to PDF

    Raises:
        NoPDFLink: If DOI missing
        AccessDenied: If paywall detected
    """
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for APA journals - attempted: none')

    pdf_url = f'https://psycnet.apa.org/fulltext/{pma.doi}.pdf'

    if verify:
        if verify_pdf_url(pdf_url):
            return pdf_url
        else:
            raise AccessDenied(f'PAYWALL: APA article requires subscription - {pdf_url}')

    return pdf_url
