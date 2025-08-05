"""Dance function for EurekaSelect (Bentham Science Publishers)."""

from ...exceptions import NoPDFLink, AccessDenied
from .generic import the_doi_2step, verify_pdf_url, unified_uri_get


def the_eureka_frug(pma, verify=True):
    """EurekaSelect - extract PDF URL from DOI resolution.
    
    EurekaSelect has server-side issues with PDF generation (returns HTTP 500).
    Function correctly constructs PDF URLs but they typically fail due to server errors.
    """
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for EurekaSelect journals')
    
    article_url = the_doi_2step(pma.doi)
    response = unified_uri_get(article_url)
    
    if response.status_code != 200:
        raise NoPDFLink(f'TXERROR: Could not access EurekaSelect article page (HTTP {response.status_code})')
    
    if 'eurekaselect.com' not in response.url or '/article/' not in response.url:
        raise NoPDFLink(f'TXERROR: DOI does not resolve to EurekaSelect article - got {response.url}')
    
    article_id = response.url.split('/article/')[-1]
    pdf_url = f'https://www.eurekaselect.com/article/{article_id}/pdf'
    
    if verify:
        # EurekaSelect consistently returns HTTP 500 for PDF URLs (server issue)
        pdf_response = unified_uri_get(pdf_url)
        
        if pdf_response.status_code == 200:
            content_type = pdf_response.headers.get('content-type', '').lower()
            if 'pdf' in content_type:
                return pdf_url
            else:
                raise NoPDFLink('TXERROR: EurekaSelect returned non-PDF content')
        elif pdf_response.status_code == 500:
            raise NoPDFLink('TXERROR: EurekaSelect PDF generation failed (HTTP 500) - known server issue')
        elif pdf_response.status_code == 403:
            raise AccessDenied('DENIED: Access forbidden by EurekaSelect')
        else:
            raise NoPDFLink(f'TXERROR: EurekaSelect returned HTTP {pdf_response.status_code}')
    
    return pdf_url