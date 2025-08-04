"""Dance function for DovePress (Dove Medical Press)."""

from lxml.html import HTMLParser
from lxml import etree

from ...exceptions import AccessDenied, NoPDFLink
from .generic import the_doi_2step, verify_pdf_url, unified_uri_get


def the_dovepress_peacock(pma, verify=True):
    '''DovePress (Dove Medical Press): Open access medical and scientific journals
    
    DovePress is an academic publisher of open-access peer-reviewed scientific and medical journals,
    acquired by Taylor & Francis Group in 2017. Most articles are freely accessible.
    
    URL Pattern: https://www.dovepress.com/[article-title]-peer-reviewed-fulltext-article-[JOURNAL_CODE]
    PDF Pattern: https://www.dovepress.com/article/download/[ARTICLE_ID]
    DOI Pattern: 10.2147/[JOURNAL_CODE].S[ID]
    
    Examples:
        37693885: IJN (International Journal of Nanomedicine) - DOI: 10.2147/IJN.S420748
        37736107: OPTH (Clinical Ophthalmology) - DOI: 10.2147/OPTH.S392665
    '''
    from ..journals.dovepress import dovepress_format
    
    # DovePress articles are typically accessed via DOI resolution to article page,
    # then PDF download link must be extracted from the article page
    if pma.doi:
        article_url = the_doi_2step(pma.doi)
        
        # Get the article page to extract PDF download link
        response = unified_uri_get(article_url)
        if not response.ok:
            raise NoPDFLink('TXERROR: DovePress article page returned status %i' % response.status_code)
        
        page_text = response.content
        pdf_url = None
        
        try:
            # Parse HTML to find PDF download link
            root = etree.fromstring(page_text, HTMLParser())
            
            # Look for PDF download link patterns
            # Pattern 1: Look for links containing "download"
            for elem in root.iter():
                if elem.tag == 'a':
                    href = elem.get('href', '')
                    text = (elem.text or '').lower()
                    
                    # Look for download links with "pdf" or "download" 
                    if ('download' in href and ('pdf' in text or 'article' in text)) or \
                       ('article/download/' in href):
                        # Convert relative URL to absolute URL
                        if href.startswith('/'):
                            pdf_url = 'https://www.dovepress.com' + href
                        elif href.startswith('article/'):
                            pdf_url = 'https://www.dovepress.com/' + href
                        else:
                            pdf_url = href
                        break
            
            # Pattern 2: Look for citation_pdf_url meta tag (fallback)
            if pdf_url is None:
                head = root.find('.//head')
                if head is not None:
                    for elem in head.findall('.//meta'):
                        if elem.get('name') == 'citation_pdf_url':
                            pdf_url = elem.get('content')
                            break
        
        except Exception as parse_error:
            raise NoPDFLink('TXERROR: Failed to parse DovePress article page: %s (See %s)' % (str(parse_error), article_url))
        
        if pdf_url:
            if verify:
                verify_pdf_url(pdf_url, 'DovePress')
            return pdf_url
        else:
            raise NoPDFLink('TXERROR: DovePress article page lacks PDF download link. (See %s)' % article_url)
    
    else:
        raise NoPDFLink('MISSING: doi needed for DovePress lookup.')