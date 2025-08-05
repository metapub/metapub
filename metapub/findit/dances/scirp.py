from ...exceptions import *
from .generic import *

from lxml import html
from urllib.parse import urljoin


#TODO: get rid of this dumb try-except jaw

# also i'm not convinced any of this works

def the_scirp_timewarp(pma, verify=True):
    '''SCIRP (Scientific Research Publishing): Open access publisher

    SCIRP articles are hosted on scirp.org and typically accessible via DOI resolution.
    Most SCIRP journals are open access, making articles freely available.

    :param: pma (PubmedArticle)
    :param: verify (bool) [default: True]
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    '''
    try:
        # Check if DOI is available
        if not pma.doi:
            raise NoPDFLink('MISSING: DOI required for SCIRP journals - attempted: none')

        # Resolve DOI to get article URL
        article_url = the_doi_2step(pma.doi)

        if verify:
            try:
                response = unified_uri_get(article_url, timeout=30)

                if response.status_code in OK_STATUS_CODES:
                    page_text = response.text.lower()

                    # Look for PDF download links or indicators
                    if 'pdf' in page_text and ('download' in page_text or 'full text' in page_text or 'view pdf' in page_text):
                        # Try to find PDF link in the page
                        tree = html.fromstring(response.content)

                        # Look for PDF download links (SCIRP typically has direct PDF links)
                        pdf_links = tree.xpath('//a[contains(@href, ".pdf") or contains(text(), "PDF") or contains(@class, "pdf") or contains(@title, "PDF")]/@href')

                        if pdf_links:
                            pdf_url = pdf_links[0]
                            # Convert relative URL to absolute if needed
                            if pdf_url.startswith('/'):
                                pdf_url = urljoin(article_url, pdf_url)
                            return pdf_url

                    # Check for paywall/subscription indicators (uncommon for SCIRP but possible)
                    paywall_terms = ['subscribe', 'sign in', 'log in', 'institutional access',
                                   'purchase', 'access denied', 'login required', 'subscription required',
                                   'register', 'institutional', 'purchase this article']
                    if any(term in page_text for term in paywall_terms):
                        raise AccessDenied(f'PAYWALL: SCIRP article requires subscription - attempted: {article_url}')

                    # If no PDF link found, this is an error in verify mode
                    raise NoPDFLink(f'TXERROR: No PDF link found on SCIRP page - attempted: {article_url}')

                elif response.status_code == 403:
                    raise AccessDenied(f'DENIED: Access forbidden by SCIRP - attempted: {article_url}')
                elif response.status_code == 404:
                    raise NoPDFLink(f'TXERROR: SCIRP article not found - attempted: {article_url}')
                else:
                    raise NoPDFLink(f'TXERROR: SCIRP returned status {response.status_code} - attempted: {article_url}')

            except Exception as e:
                raise NoPDFLink(f'TXERROR: Network error accessing SCIRP: {e} - attempted: {article_url}')
        else:
            # For SCIRP, try to construct PDF URL pattern without verification
            # SCIRP typically uses patterns like /Html/1-1234567.html -> /Html/pdf/1-1234567.pdf
            if 'scirp.org' in article_url:
                # Try common SCIRP PDF patterns
                if '/Html/' in article_url and article_url.endswith('.html'):
                    # Pattern: /Html/1-1234567.html -> /Html/pdf/1-1234567.pdf
                    pdf_url = article_url.replace('/Html/', '/Html/pdf/').replace('.html', '.pdf')
                    return pdf_url
                elif '/journal/' in article_url:
                    # Alternative pattern based on DOI
                    doi_suffix = pma.doi.split('/')[-1] if '/' in pma.doi else pma.doi
                    return f'https://www.scirp.org/pdf/{doi_suffix}.pdf'
            
            # Fallback: return article URL with warning that it's not a PDF
            # This preserves existing behavior while marking the issue
            return article_url  # WARNING: This is an HTML page, not a PDF

    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: SCIRP timewarp failed for {pma.journal}: {e} - attempted: DOI resolution')



