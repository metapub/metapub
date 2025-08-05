"""Dance function for ScienceDirect (Elsevier)."""

from ...exceptions import AccessDenied, NoPDFLink
from ...utils import remove_chars
from .generic import verify_pdf_url


def the_sciencedirect_disco(pma, verify=True):
    '''ScienceDirect (Elsevier) dance using direct PDF URL construction.
    
    Primary approach: Direct PDF URL from PII
    Pattern: https://www.sciencedirect.com/science/article/pii/{clean_pii}/pdfft?isDTMRedir=true&download=true
    
    ScienceDirect is one of the largest academic publishers, including:
    - Elsevier journals
    - Cell Press journals  
    - Lancet journals
    - And thousands of others
    
    Most articles have a PII (Publisher Item Identifier) which is used to construct URLs.
    PIIs need to be cleaned by removing hyphens, parentheses, etc.
    
    :param: pma (PubMedArticle object)
    :param: verify (bool) [default: True]
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    '''
    
    if not pma.pii and not pma.doi:
        raise NoPDFLink('MISSING: PII or DOI required for ScienceDirect access')
    
    # Primary method: Use PII if available
    if pma.pii:
        # Clean PII - remove hyphens, parentheses, and other special chars
        clean_pii = remove_chars(pma.pii, '-()[]{}')
        
        # Direct PDF URL pattern
        pdf_url = f'https://www.sciencedirect.com/science/article/pii/{clean_pii}/pdfft?isDTMRedir=true&download=true'
        
        if verify:
            try:
                if verify_pdf_url(pdf_url):
                    return pdf_url
                else:
                    # Try alternate pattern without download parameter
                    alt_url = f'https://www.sciencedirect.com/science/article/pii/{clean_pii}/pdfft'
                    if verify_pdf_url(alt_url):
                        return alt_url
                    else:
                        raise AccessDenied(f'PAYWALL: ScienceDirect article requires subscription - {pdf_url}')
            except Exception:
                raise AccessDenied(f'PAYWALL: ScienceDirect article requires subscription - {pdf_url}')
        else:
            return pdf_url
    
    # Fallback: Try DOI-based URL
    elif pma.doi:
        # For DOI-only articles, we need to construct a different URL
        # Pattern: https://www.sciencedirect.com/science/article/abs/pii/SXXXXXXXXX
        # But without PII, we can't construct the full URL reliably
        raise NoPDFLink(f'MISSING: PII required for ScienceDirect PDF access (DOI alone insufficient) - Journal: {pma.journal}')