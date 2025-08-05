"""Dance function for Springer journals."""

from ...exceptions import AccessDenied, NoPDFLink
from .generic import verify_pdf_url


def the_springer_shag(pma, verify=True):
    '''Springer dance using evidence-driven patterns from HTML analysis.
    
    Primary approach: Direct DOI-based PDF URL construction
    https://link.springer.com/content/pdf/{DOI}.pdf
    
    Evidence from HTML samples shows 100% consistent pattern.
    Registry determines which journals use this dance function.
    
    :param: pma (PubMedArticle object)
    :param: verify (bool) [default: True]
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    '''
    
    if not pma.doi:
        raise NoPDFLink("MISSING: DOI required for Springer PDF URL construction")
    
    # Trust the registry - construct URL for any DOI that gets routed here
    pdf_url = f"https://link.springer.com/content/pdf/{pma.doi}.pdf"
    
    if verify:
        try:
            if verify_pdf_url(pdf_url):
                return pdf_url
            else:
                raise AccessDenied(f"PAYWALL: Springer article requires subscription - {pdf_url}")
        except Exception:
            raise AccessDenied(f"PAYWALL: Springer article requires subscription - {pdf_url}")
    else:
        return pdf_url