"""Dance function for ScienceDirect (Elsevier)."""

from ...exceptions import AccessDenied, NoPDFLink
from ...utils import remove_chars
from .generic import verify_pdf_url


def the_sciencedirect_disco(pma, verify=True, request_timeout=10, max_redirects=3):
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
                if verify_pdf_url(pdf_url, request_timeout=request_timeout, max_redirects=max_redirects):
                    return pdf_url
                else:
                    # Try alternate pattern without download parameter
                    alt_url = f'https://www.sciencedirect.com/science/article/pii/{clean_pii}/pdfft'
                    if verify_pdf_url(alt_url, request_timeout=request_timeout, max_redirects=max_redirects):
                        return alt_url
                    else:
                        raise AccessDenied(f'PAYWALL: ScienceDirect article requires subscription - {pdf_url}')
            except Exception:
                raise AccessDenied(f'PAYWALL: ScienceDirect article requires subscription - {pdf_url}')
        else:
            return pdf_url

    # Fallback: DOI-based backup strategies
    elif pma.doi:
        # Strategy 1: Try CrossRef API for PDF links
        try:
            from .generic import get_crossref_pdf_links
            crossref_urls = get_crossref_pdf_links(pma.doi)
            if crossref_urls:
                # Use the first PDF URL from CrossRef
                pdf_url = crossref_urls[0]
                if verify:
                    if verify_pdf_url(pdf_url, request_timeout=request_timeout, max_redirects=max_redirects):
                        return pdf_url
                else:
                    return pdf_url
        except Exception:
            pass  # Continue to next strategy
        
        # Strategy 2: DOI resolution to extract PII from ScienceDirect URLs
        try:
            from .generic import the_doi_2step
            import re
            
            resolved_url = the_doi_2step(pma.doi)
            if 'sciencedirect.com' in resolved_url or 'elsevier.com' in resolved_url:
                # Try to extract PII from URLs like:
                # https://www.sciencedirect.com/science/article/pii/S0964195596000358
                # https://www.sciencedirect.com/science/article/abs/pii/0305900696000025
                pii_match = re.search(r'/pii/([A-Z0-9\-]+)', resolved_url)
                if pii_match:
                    extracted_pii = pii_match.group(1)
                    # Clean and construct PDF URL
                    clean_pii = remove_chars(extracted_pii, '-()[]{}')
                    pdf_url = f'https://www.sciencedirect.com/science/article/pii/{clean_pii}/pdfft?isDTMRedir=true&download=true'
                    
                    if verify:
                        try:
                            if verify_pdf_url(pdf_url, request_timeout=request_timeout, max_redirects=max_redirects):
                                return pdf_url
                            else:
                                # Try alternate pattern
                                alt_url = f'https://www.sciencedirect.com/science/article/pii/{clean_pii}/pdfft'
                                if verify_pdf_url(alt_url, request_timeout=request_timeout, max_redirects=max_redirects):
                                    return alt_url
                        except Exception:
                            pass
                    else:
                        return pdf_url
        except Exception:
            pass  # Continue to final fallback
        
        # No more fallback strategies - maintain PDF URL contract
        
        # If all strategies fail
        raise NoPDFLink(f'MISSING: ScienceDirect article could not be accessed via DOI fallback - Journal: {pma.journal}')
