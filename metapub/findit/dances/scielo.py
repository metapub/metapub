"""SciELO dance function."""

from urllib.parse import urlparse
from lxml.html import HTMLParser
from lxml import etree
from ...exceptions import NoPDFLink
from .generic import the_doi_2step, verify_pdf_url, unified_uri_get


def the_scielo_chula(pma, verify=True, request_timeout=10, max_redirects=3):
    '''SciELO: The Scientific Electronic Library Online

    SciELO is an electronic library covering a selected collection of Brazilian
    scientific journals.

    Examples:
        23657305: pii = S0004-28032013000100035
            http://www.scielo.br/scielo.php?script=sci_arttext&pid=S0004-28032013000100035
            http://www.scielo.br/pdf/ag/v50n1/0004-2803-ag-50-01-35.pdf
    '''
    page_text = None
    article_url = None
    baseurl_pii = 'http://www.scielo.br/scielo.php?script=sci_arttext&pid=%s'
    if pma.pii:
        response = unified_uri_get(baseurl_pii % pma.pii, timeout=request_timeout, max_redirects=max_redirects)
        if response.ok:
            page_text = response.content
            article_url = response.url

    # If the PII URL didn't redirect to the new SciELO format (e.g. different CDN
    # behavior by geographic location), also try the DOI path which routes through
    # CrossRef and consistently resolves to the new /j/.../a/.../ URL format.
    if (page_text is None or (article_url and 'scielo.php' in article_url)) and pma.doi:
        doi_response = unified_uri_get(the_doi_2step(pma.doi), timeout=request_timeout, max_redirects=max_redirects)
        if doi_response.ok:
            page_text = doi_response.content
            article_url = doi_response.url
    elif page_text is None:
        raise NoPDFLink('MISSING: pii or doi needed for SciELO lookup.')

    if page_text:
        pdf_url = None
        try:
            # Parse HTML and look for citation_pdf_url meta tag
            root = etree.fromstring(page_text, HTMLParser())
            head = root.find('.//head')
            if head is not None:
                for elem in head.findall('.//meta'):
                    if elem.get('name') == 'citation_pdf_url':
                        pdf_url = elem.get('content')
                        break
            
            # If no meta tag found, try to look for PDF links in the page
            if pdf_url is None:
                for elem in root.iter():
                    if elem.tag == 'a':
                        href = elem.get('href', '')
                        if 'format=pdf' in href:
                            # Convert relative URL to absolute URL
                            if href.startswith('/'):
                                pdf_url = 'https://www.scielo.br' + href
                            else:
                                pdf_url = href
                            break

            # Fallback: construct PDF URL from new SciELO URL format
            # New format: /j/{journal}/a/{hash}/?lang=en -> append &format=pdf
            if pdf_url is None and article_url:
                parsed = urlparse(article_url)
                if '/j/' in parsed.path and '/a/' in parsed.path:
                    sep = '&' if '?' in article_url else '?'
                    pdf_url = article_url + sep + 'format=pdf'

        except (etree.XMLSyntaxError, etree.ParserError, AttributeError) as parse_error:
            raise NoPDFLink('TXERROR: Failed to parse SciELO article page: %s' % str(parse_error))
        
        if pdf_url:
            if verify:
                verify_pdf_url(pdf_url, 'SciELO', request_timeout=request_timeout, max_redirects=max_redirects)
            return pdf_url
        else:
            raise NoPDFLink('TXERROR: SciELO article page lacks PDF download link.')
    
    else:
        raise NoPDFLink('TXERROR: Could not retrieve SciELO article page.')