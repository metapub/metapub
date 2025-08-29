"""Oxford Academic dance function using CrossRef API integration."""

from ...crossref import CrossRefFetcher
from ...exceptions import NoPDFLink


def the_oxford_academic_foxtrot(pma, verify=True, request_timeout=10, max_redirects=3):
    """Oxford Academic dance function - uses CrossRef API to bypass Cloudflare protection.
    
    Oxford Academic (academic.oup.com) blocks direct HTML scraping with Cloudflare protection.
    This function uses CrossRef API to get PDF URLs directly from metadata.
    
    Supports journals with DOI prefix 10.1210/ (Endocrine Society) and other Oxford Academic
    publications that provide PDF metadata through CrossRef.
    
    :param pma: PubMedArticle object with DOI
    :param verify: bool - verification skipped due to Cloudflare protection  
    :return: str - PDF URL from CrossRef metadata
    :raises: NoPDFLink for missing DOI or no PDF links in metadata
    """
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for Oxford Academic CrossRef lookup')
    
    # Get work metadata from CrossRef
    cr_fetcher = CrossRefFetcher()
    work = cr_fetcher.article_by_doi(pma.doi)
    
    if not work or not work.link:
        raise NoPDFLink(f'MISSING: No CrossRef metadata or links for DOI: {pma.doi}')
    
    # Find PDF URLs from Oxford Academic
    pdf_urls = []
    for link in work.link:
        url = link.get('URL', '')
        content_type = link.get('content-type', '')
        content_version = link.get('content-version', '')
        
        # Check if this is a PDF link from Oxford Academic
        is_oxford_pdf = (
            'academic.oup.com' in url and
            ('pdf' in content_type.lower() or 'pdf' in url.lower())
        )
        
        if is_oxford_pdf:
            # Prioritize Version of Record (vor) over Author Manuscript (am)
            priority = 1 if content_version == 'vor' else 0
            pdf_urls.append((priority, url))
    
    if not pdf_urls:
        raise NoPDFLink(f'MISSING: No Oxford Academic PDF URLs in CrossRef metadata for DOI: {pma.doi}')
    
    # Return highest priority PDF URL
    pdf_urls.sort(key=lambda x: x[0], reverse=True)
    return pdf_urls[0][1]