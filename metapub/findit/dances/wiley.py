"""Dance function for Wiley journals."""

from ...exceptions import AccessDenied, NoPDFLink
from .generic import verify_pdf_url


def the_wiley_shuffle(pma, verify=True):
    '''Wiley dance using evidence-driven patterns from HTML analysis.
    
    Primary pattern: Direct DOI-based PDF URL construction
    https://onlinelibrary.wiley.com/doi/epdf/{DOI}
    
    Evidence from wiley_example.txt shows clean URL pattern:
    - Regular: https://onlinelibrary.wiley.com/doi/10.1002/brb3.70665
    - PDF: https://onlinelibrary.wiley.com/doi/epdf/10.1002/brb3.70665
    
    Registry determines which journals use this dance function.
    
    :param: pma (PubMedArticle object)
    :param: verify (bool) [default: True]
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    '''
    
    if not pma.doi:
        raise NoPDFLink("MISSING: DOI required for Wiley PDF URL construction")
    
    # Evidence-based pattern: /doi/epdf/{DOI}
    pdf_url = f"https://onlinelibrary.wiley.com/doi/epdf/{pma.doi}"
    
    if verify:
        try:
            if verify_pdf_url(pdf_url):
                return pdf_url
            else:
                raise AccessDenied(f"PAYWALL: Wiley article requires subscription - {pdf_url}")
        except Exception:
            raise AccessDenied(f"PAYWALL: Wiley article requires subscription - {pdf_url}")
    else:
        return pdf_url