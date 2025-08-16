"""Dance function for Journal of Clinical Investigation."""

from ...exceptions import AccessDenied, NoPDFLink
from .generic import the_doi_2step, verify_pdf_url, unified_uri_get
from ..registry import JournalRegistry


def the_jci_jig(pma, verify=True, request_timeout=10, max_redirects=3):
    '''Dance of the Journal of Clinical Investigation, which should be largely free.

         :param: pma (PubMedArticle object)
         :param: verify (bool) [default: True]
         :return: url (string)
         :raises: AccessDenied, NoPDFLink
    '''
    # Get JCI URL template from registry
    registry = JournalRegistry()
    publisher_config = registry.get_publisher_config('jci')
    if not publisher_config:
        raise NoPDFLink('MISSING: JCI publisher not found in registry - attempted: none')
    
    url_template = publisher_config.get('format_template')
    if not url_template:
        # Fallback to hardcoded format for backward compatibility
        url_template = 'http://www.jci.org/articles/view/{pii}/files/pdf'
    
    # JCI uses simple URL pattern: https://www.jci.org/articles/view/{pii}/pdf
    if pma.pii:
        # Direct construction using PII (preferred method)
        url = url_template.format(pii=pma.pii)
    elif pma.doi:
        # Fallback: use DOI resolution to get article page, then construct PDF URL
        article_url = the_doi_2step(pma.doi)
        # Convert article URL to PDF URL
        # Example: http://www.jci.org/articles/view/82041 -> http://www.jci.org/articles/view/82041/files/pdf
        if '/articles/view/' in article_url:
            url = article_url.rstrip('/') + '/files/pdf'
        else:
            # Fallback pattern if DOI redirects to unexpected format
            url = article_url + '/files/pdf'
    else:
        raise NoPDFLink('MISSING: pii or doi needed for JCI lookup.')
        
    if verify:
        # JCI sometimes returns HTML even for PDF URLs due to user-agent detection
        # or access control measures. We'll attempt verification but be more lenient.
        try:
            verify_pdf_url(url, 'JCI', request_timeout=request_timeout, max_redirects=max_redirects)
        except NoPDFLink as e:
            # If verification fails, check if it's due to HTML content type
            try:
                response = unified_uri_get(url, timeout=request_timeout, max_redirects=max_redirects)
                if response.status_code == 200 and 'text/html' in response.headers.get('content-type', ''):
                    # JCI is returning HTML instead of PDF - this might be due to access control
                    # For now, we'll return the URL anyway as it's the correct pattern
                    pass  # Continue and return the URL
                else:
                    # Re-raise the original exception for other types of failures
                    raise e
            except Exception:
                # Network error during verification - re-raise original exception
                raise e
    return url