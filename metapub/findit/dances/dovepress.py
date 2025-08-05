"""Dance function for DovePress (Dove Medical Press)."""

from lxml.html import HTMLParser
from lxml import etree

from ...exceptions import NoPDFLink
from .generic import the_doi_2step, verify_pdf_url, unified_uri_get


def the_dovepress_peacock(pma, verify=True):
    """DovePress - extract PDF URL from article download link."""
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for DovePress journals')
    
    article_url = the_doi_2step(pma.doi)
    response = unified_uri_get(article_url)
    
    if response.status_code != 200:
        raise NoPDFLink(f'TXERROR: Could not access DovePress article page (HTTP {response.status_code})')
    
    # Parse HTML to find PDF download link
    root = etree.fromstring(response.content, HTMLParser())
    
    # Look for article/download/ links
    for elem in root.iter():
        if elem.tag == 'a':
            href = elem.get('href', '')
            text = (elem.text or '').lower()
            
            if ('download' in href and ('pdf' in text or 'article' in text)) or 'article/download/' in href:
                # Convert relative URL to absolute URL
                if href.startswith('/'):
                    pdf_url = 'https://www.dovepress.com' + href
                elif href.startswith('article/'):
                    pdf_url = 'https://www.dovepress.com/' + href
                else:
                    pdf_url = href
                
                if verify:
                    verify_pdf_url(pdf_url, 'DovePress')
                
                return pdf_url
    
    # Fallback: Look for citation_pdf_url meta tag
    head = root.find('.//head')
    if head is not None:
        for elem in head.findall('.//meta'):
            if elem.get('name') == 'citation_pdf_url':
                pdf_url = elem.get('content')
                if verify:
                    verify_pdf_url(pdf_url, 'DovePress')
                return pdf_url
    
    raise NoPDFLink('MISSING: No PDF download link found in DovePress article HTML')