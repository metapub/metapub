from ...exceptions import AccessDenied, NoPDFLink
from .generic import verify_pdf_url

def the_thieme_tap(pma, verify=True):
    '''Thieme Medical Publishers: Direct PDF URL construction
    
    Evidence from output/article_html/thieme_medical_publishers/:
    Pattern: http://www.thieme-connect.de/products/ejournals/pdf/{DOI}.pdf
    
    Perfect consistency: 10/10 samples show exact DOI → PDF URL pattern.
    All Thieme DOIs use 10.1055/ prefix with various suffixes (s-, a-, etc.).
    
    Example: DOI 10.1055/s-0034-1387804 → http://www.thieme-connect.de/products/ejournals/pdf/10.1055/s-0034-1387804.pdf
    
    :param: pma (PubmedArticle)
    :param: verify (bool) [default: True] 
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    '''
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for Thieme journals - attempted: none')

    if not pma.doi.startswith('10.1055/'):
        raise NoPDFLink(f'INVALID: DOI does not match Thieme pattern (10.1055/) - attempted: {pma.doi}')

    # Construct PDF URL using evidence-based pattern
    pdf_url = f"http://www.thieme-connect.de/products/ejournals/pdf/{pma.doi}.pdf"

    if verify:
        if verify_pdf_url(pdf_url):
            return pdf_url
        else:
            raise AccessDenied(f'PAYWALL: Thieme PDF requires subscription - attempted: {pdf_url}')

    return pdf_url