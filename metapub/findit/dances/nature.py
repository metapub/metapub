"""Dance function for Nature Publishing Group journals."""

import requests
from ...exceptions import AccessDenied, NoPDFLink
from .generic import *

# Import Nature-specific constants
from ..journals.nature import nature_format, nature_journals


def the_nature_ballet(pma, verify=True):
    '''Nature Publishing Group dance using modern DOI-based URLs with fallback.

    Primary approach: Modern DOI-based URL structure
    https://www.nature.com/articles/{DOI_SUFFIX}.pdf

    Fallback approach: Traditional volume/issue/pii URLs (still work via redirects)
    http://www.nature.com/{ja}/journal/v{volume}/n{issue}/pdf/{pii}.pdf

    :param: pma (PubMedArticle object)
    :param: verify (bool) [default: True]
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    '''
    pdf_url = None

    # Primary approach: DOI-based URL
    if pma.doi and pma.doi.startswith('10.1038/'):
        article_id = pma.doi.split('/', 1)[1]
        pdf_url = f'https://www.nature.com/articles/{article_id}.pdf'

        if not verify:
            return pdf_url

        # Try the DOI-based approach first
        try:
            response = requests.get(pdf_url, timeout=10)

            if response.status_code == 200:
                content_type = response.headers.get('content-type', '').lower()
                if 'pdf' in content_type:
                    return response.url
                elif 'html' in content_type:
                    page_text = response.text.lower()
                    if any(term in page_text for term in ['paywall', 'subscribe', 'sign in', 'log in', 'purchase']):
                        raise AccessDenied(f'PAYWALL: Nature article requires subscription - attempted: {pdf_url}')
                    else:
                        raise NoPDFLink(f'TXERROR: Nature returned HTML instead of PDF for {pdf_url}')
                else:
                    raise NoPDFLink(f'TXERROR: Unexpected content type {content_type} from Nature')

            elif response.status_code == 403:
                raise AccessDenied(f'DENIED: Access forbidden by Nature - attempted: {pdf_url}')
            elif response.status_code == 404:
                # DOI-based URL failed, try fallback approach
                pass
            else:
                raise NoPDFLink(f'TXERROR: Nature returned status {response.status_code} for {pdf_url}')

        except requests.exceptions.RequestException:
            # Network error with DOI approach, try fallback
            pass

    # Fallback approach: Traditional volume/issue/pii URL construction
    # Only works for traditional Nature journals with short PIIs (not modern s4xxxx journals)
    if pma.volume and pma.issue and pma.pii and pma.pii != pma.doi:

        # Skip modern journals that use full DOI as PII (s41xxx, s42xxx, s43xxx)
        is_modern_journal = pma.doi and any(code in pma.doi for code in ['s41', 's42', 's43'])

        if not is_modern_journal:
            # Find journal abbreviation for traditional journals
            jrnl = standardize_journal_name(pma.journal)
            if jrnl in nature_journals:
                ja = nature_journals[jrnl]['ja']
                fallback_url = nature_format.format(ja=ja, a=pma)

                if not verify:
                    return fallback_url

                try:
                    response = requests.get(fallback_url, timeout=10)

                    if response.status_code == 200:
                        content_type = response.headers.get('content-type', '').lower()
                        if 'pdf' in content_type:
                            return response.url
                        elif 'html' in content_type:
                            page_text = response.text.lower()
                            if any(term in page_text for term in ['paywall', 'subscribe', 'sign in', 'log in', 'purchase']):
                                raise AccessDenied(f'PAYWALL: Nature article requires subscription - attempted: {fallback_url}')
                            else:
                                # Old format URLs redirect to modern URLs, so this might be expected
                                # Try to extract the modern URL from the redirect
                                if 'articles' in response.url:
                                    return response.url.replace('/articles/', '/articles/') + '.pdf'
                                else:
                                    raise NoPDFLink(f'TXERROR: Nature fallback returned HTML for {fallback_url}')
                        else:
                            raise NoPDFLink(f'TXERROR: Unexpected content type {content_type} from Nature fallback')

                    elif response.status_code == 403:
                        raise AccessDenied(f'DENIED: Access forbidden by Nature - attempted: {fallback_url}')
                    elif response.status_code == 404:
                        raise NoPDFLink(f'NOTFOUND: Article not found on Nature platform - attempted: {pdf_url}, {fallback_url}')
                    else:
                        raise NoPDFLink(f'TXERROR: Nature fallback returned status {response.status_code} - attempted: {fallback_url}')

                except requests.exceptions.RequestException as e:
                    raise NoPDFLink(f'TXERROR: Network error with Nature fallback: {e} - attempted: {fallback_url}')

    # If we get here, neither approach worked
    missing_data = []
    if not pma.doi or not pma.doi.startswith('10.1038/'):
        missing_data.append('valid Nature DOI')
    if not (pma.volume and pma.issue and pma.pii):
        missing_data.append('volume/issue/pii data')

    if missing_data:
        raise NoPDFLink(f'MISSING: {" and ".join(missing_data)} - cannot construct Nature URL - attempted: none')
    else:
        # Both approaches were attempted but failed
        attempted_urls = []
        if pma.doi and pma.doi.startswith('10.1038/'):
            article_id = pma.doi.split('/', 1)[1]
            attempted_urls.append(f'https://www.nature.com/articles/{article_id}.pdf')
        if pma.volume and pma.issue and pma.pii:
            attempted_urls.append(f'traditional Nature URL (vol/issue/pii)')
        urls_str = ', '.join(attempted_urls) if attempted_urls else 'none'
        raise NoPDFLink(f'TXERROR: Both DOI-based and volume/issue/pii approaches failed for Nature article - attempted: {urls_str}')
