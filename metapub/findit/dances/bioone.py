 from ...exceptions import *
 from .generic import *

 from lxml import html
 from urllib.parse import urljoin


 #TODO: get rid of this dumb try-except jaw

 # also i'm not convinced any of this works


def the_bioone_bounce(pma, verify=True):
    '''BioOne.org: Multi-publisher digital library platform for biological sciences

    BioOne is a multi-publisher digital library platform that aggregates scholarly content
    from biological, ecological, and environmental science publishers. The platform hosts
    journals from ~200+ societies and independent publishers with diverse DOI prefixes
    (10.1643/, 10.1645/, 10.1676/, etc.) but all resolve through complete.bioone.org.

    :param: pma (PubmedArticle)
    :param: verify (bool) [default: True]
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    '''
    try:
        # Check if DOI is available
        if not pma.doi:
            raise NoPDFLink('MISSING: DOI required for BioOne journals - attempted: none')

        # Since BioOne hosts multiple publishers with different DOI prefixes,
        # we don't validate a specific DOI pattern - just ensure DOI exists

        # Resolve DOI to get article URL
        article_url = the_doi_2step(pma.doi)

        if verify:
            try:
                response = requests.get(article_url, timeout=30)

                if response.status_code in OK_STATUS_CODES:
                    page_text = response.text.lower()

                    # Look for PDF download links or indicators
                    if 'pdf' in page_text and ('download' in page_text or 'full text' in page_text or 'view pdf' in page_text):
                        # Try to find PDF link in the page
                        tree = html.fromstring(response.content)

                        # Look for PDF download links (BioOne typically has direct PDF access)
                        pdf_links = tree.xpath('//a[contains(@href, ".pdf") or contains(text(), "PDF") or contains(@class, "pdf") or contains(@title, "PDF")]/@href')

                        if pdf_links:
                            pdf_url = pdf_links[0]
                            # Convert relative URL to absolute if needed
                            if pdf_url.startswith('/'):
                                pdf_url = urljoin(article_url, pdf_url)
                            return pdf_url

                    # Check for paywall/subscription indicators
                    paywall_terms = ['subscribe', 'sign in', 'log in', 'institutional access',
                                   'purchase', 'access denied', 'login required', 'subscription required',
                                   'register', 'institutional', 'purchase this article', 'member access']
                    if any(term in page_text for term in paywall_terms):
                        raise AccessDenied(f'PAYWALL: BioOne article requires subscription - attempted: {article_url}')

                    # If no PDF link found but page accessible, return article URL
                    return article_url

                elif response.status_code == 403:
                    raise AccessDenied(f'DENIED: Access forbidden by BioOne - attempted: {article_url}')
                elif response.status_code == 404:
                    raise NoPDFLink(f'TXERROR: BioOne article not found - attempted: {article_url}')
                else:
                    raise NoPDFLink(f'TXERROR: BioOne returned status {response.status_code} - attempted: {article_url}')

            except requests.exceptions.RequestException as e:
                raise NoPDFLink(f'TXERROR: Network error accessing BioOne: {e} - attempted: {article_url}')
        else:
            # Return DOI-resolved URL without verification
            return article_url

    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: BioOne bounce failed for {pma.journal}: {e} - attempted: DOI resolution')

