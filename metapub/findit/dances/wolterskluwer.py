"""Wolters Kluwer dance function using CrossRef + URL construction hybrid approach."""

from ...exceptions import NoPDFLink
from ...crossref import CrossRefFetcher
from .generic import unified_uri_get


def the_wolterskluwer_volta(pma, verify=True):
    """Wolters Kluwer dance function - bypasses Cloudflare using CrossRef + URL construction.
    
    Uses CrossRef API to verify DOI existence, then constructs PDF URLs based on
    known Wolters Kluwer URL patterns. This hybrid approach avoids Cloudflare
    protection while leveraging publisher URL conventions.
    
    :param: pma (PubMedArticle object)
    :param: verify (bool) [default: True]
    :return: url
    :raises: NoPDFLink
    """
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for Wolters Kluwer CrossRef + URL construction')
    
    # Use CrossRef API to verify DOI exists and get canonical metadata
    try:
        cr_fetcher = CrossRefFetcher()
        work = cr_fetcher.article_by_doi(pma.doi)
        
        if not work:
            raise NoPDFLink('MISSING: CrossRef returned no metadata for this Wolters Kluwer DOI')
            
    except Exception as e:
        raise NoPDFLink(f'CROSSREF_ERROR: Failed to verify DOI via CrossRef API: {e}')
    
    # Construct PDF URLs based on DOI patterns discovered through evidence
    pdf_urls = []
    
    # Pattern 1: LWW/Ovid pattern for 10.1097/ DOIs (discovered in CrossRef analysis)
    if pma.doi.startswith('10.1097/'):
        # Extract DOI suffix after 10.1097/
        doi_suffix = pma.doi[8:]  # Remove '10.1097/' prefix
        lww_url = f'https://journals.lww.com/10.1097/{doi_suffix}'
        pdf_urls.append(lww_url)
        
        # Alternative Ovid pattern (found in CrossRef metadata)
        # Convert DOI to potential Ovid AN format
        ovid_url = f'http://Insights.ovid.com/crossref?an={doi_suffix}'
        pdf_urls.append(ovid_url)
    
    # Pattern 2: WK Health direct DOI pattern (legacy)
    wk_direct_url = f'http://content.wkhealth.com/linkback/openurl?doi={pma.doi}'
    pdf_urls.append(wk_direct_url)
    
    # Pattern 3: Generic DOI resolver as fallback
    doi_url = f'https://doi.org/{pma.doi}'
    pdf_urls.append(doi_url)
    
    # Test each constructed URL to find working PDF
    last_error = None
    for pdf_url in pdf_urls:
        if verify:
            try:
                response = unified_uri_get(pdf_url)
                if response.ok:
                    # Check if response looks like a PDF or valid article page
                    content_type = response.headers.get('content-type', '').lower()
                    if ('pdf' in content_type or 
                        'application/pdf' in content_type or
                        response.status_code == 200):  # Accept 200 OK for article pages
                        return pdf_url
                else:
                    last_error = f'HTTP {response.status_code} from {pdf_url}'
                    
            except Exception as e:
                last_error = f'Network error accessing {pdf_url}: {e}'
                continue
        else:
            # Return first constructed URL without verification
            return pdf_url
    
    # If all URLs failed, report the issue
    error_msg = f'BLOCKED: All Wolters Kluwer URL patterns failed for DOI {pma.doi}'
    if last_error:
        error_msg += f' (Last error: {last_error})'
    raise NoPDFLink(error_msg)
