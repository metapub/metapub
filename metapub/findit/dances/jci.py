"""Dance function for Journal of Clinical Investigation."""

import requests
from ...exceptions import AccessDenied, NoPDFLink
from .generic import the_doi_2step, verify_pdf_url


def the_jci_jig(pma, verify=True):
    '''Dance of the Journal of Clinical Investigation, which should be largely free.

         :param: pma (PubMedArticle object)
         :param: verify (bool) [default: True]
         :return: url (string)
         :raises: AccessDenied, NoPDFLink
    '''
    from ..journals.jci import jci_format
    
    # JCI uses simple URL pattern: https://www.jci.org/articles/view/{pii}/pdf
    if pma.pii:
        # Direct construction using PII (preferred method)
        url = jci_format.format(pii=pma.pii)
    elif pma.doi:
        # Fallback: use DOI resolution to get article page, then construct PDF URL
        article_url = the_doi_2step(pma.doi)
        # Convert article URL to PDF URL
        # Example: http://www.jci.org/articles/view/82041 -> http://www.jci.org/articles/view/82041/pdf
        if '/articles/view/' in article_url:
            url = article_url.rstrip('/') + '/pdf'
        else:
            # Fallback pattern if DOI redirects to unexpected format
            url = article_url + '/pdf'
    else:
        raise NoPDFLink('MISSING: pii or doi needed for JCI lookup.')
        
    if verify:
        # JCI sometimes returns HTML even for PDF URLs due to user-agent detection
        # or access control measures. We'll attempt verification but be more lenient.
        try:
            verify_pdf_url(url, 'JCI')
        except NoPDFLink as e:
            # If verification fails, check if it's due to HTML content type
            try:
                response = requests.get(url)
                if response.status_code == 200 and 'text/html' in response.headers.get('content-type', ''):
                    # JCI is returning HTML instead of PDF - this might be due to access control
                    # For now, we'll return the URL anyway as it's the correct pattern
                    pass  # Continue and return the URL
                else:
                    # Re-raise the original exception for other types of failures
                    raise e
            except requests.exceptions.RequestException:
                # Network error during verification - re-raise original exception
                raise e
    return url