from ...exceptions import *
from .generic import *

def the_degruyter_danza(pma, verify=True):
    '''De Gruyter: Academic publisher for humanities, social sciences, and STEM

    De Gruyter articles are hosted on degruyter.com/degruyterbrill.com and typically
    use DOI pattern 10.1515/... Most articles require subscription access.

    :param: pma (PubmedArticle)
    :param: verify (bool) [default: True]
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    '''
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for De Gruyter journals - attempted: none')

    try:
        # Try DOI resolution first to get the article page
        article_url = the_doi_2step(pma.doi)

        if verify:
            try:
                response = unified_uri_get(article_url, timeout=10)

                if response.status_code == 200:
                    # Check if we can access the content
                    page_text = response.text.lower()

                    # Look for PDF download links or indicators
                    if 'pdf' in page_text and ('download' in page_text or 'full text' in page_text):
                        # Try to find PDF link in the page
                        from lxml import html
                        tree = html.fromstring(response.content)

                        # Look for PDF download links
                        pdf_links = tree.xpath('//a[contains(@href, ".pdf") or contains(text(), "PDF") or contains(@class, "pdf")]/@href')

                        if pdf_links:
                            pdf_url = pdf_links[0]
                            # Convert relative URL to absolute if needed
                            if pdf_url.startswith('/'):
                                from urllib.parse import urljoin
                                pdf_url = urljoin(article_url, pdf_url)
                            return pdf_url

                    # Check for paywall/subscription indicators
                    paywall_terms = ['subscribe', 'sign in', 'log in', 'institutional access',
                                   'purchase', 'access denied', 'login required', 'subscription required',
                                   'register', 'institutional', 'purchase this article']
                    if any(term in page_text for term in paywall_terms):
                        raise AccessDenied(f'PAYWALL: De Gruyter article requires subscription - attempted: {article_url}')

                    # If no PDF link found but page accessible, return article URL
                    return article_url

                elif response.status_code == 403:
                    raise AccessDenied(f'DENIED: Access forbidden by De Gruyter - attempted: {article_url}')
                elif response.status_code == 404:
                    raise NoPDFLink(f'TXERROR: De Gruyter article not found - attempted: {article_url}')
                else:
                    raise NoPDFLink(f'TXERROR: De Gruyter returned status {response.status_code} - attempted: {article_url}')

            except Exception as e:
                raise NoPDFLink(f'TXERROR: Network error accessing De Gruyter: {e} - attempted: {article_url}')
        else:
            # Return DOI-resolved URL without verification
            return article_url

    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: De Gruyter danza failed for {pma.journal}: {e} - attempted: DOI resolution')


