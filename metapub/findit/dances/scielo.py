"""SciELO dance function."""

from lxml.html import HTMLParser
from lxml import etree
from ...exceptions import NoPDFLink
from .generic import the_doi_2step, verify_pdf_url


def the_scielo_chula(pma, verify=True):
    '''SciELO: The Scientific Electronic Library Online

    SciELO is an electronic library covering a selected collection of Brazilian
    scientific journals.

    Examples:
        23657305: pii = S0004-28032013000100035
            http://www.scielo.br/scielo.php?script=sci_arttext&pid=S0004-28032013000100035
            http://www.scielo.br/pdf/ag/v50n1/0004-2803-ag-50-01-35.pdf
    '''
    page_text = None
    baseurl_pii = 'http://www.scielo.br/scielo.php?script=sci_arttext&pid=%s'
    if pma.pii:
        response = unified_uri_get(baseurl_pii % pma.pii)
        if response.ok:
            page_text = response.content

    if page_text is None:
        if pma.doi:
            response = unified_uri_get(the_doi_2step(pma.doi))
            if response.ok:
                page_text = response.content
        else:
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
        
        except Exception as parse_error:
            raise NoPDFLink('TXERROR: Failed to parse SciELO article page: %s' % str(parse_error))
        
        if pdf_url:
            if verify:
                verify_pdf_url(pdf_url, 'SciELO')
            return pdf_url
        else:
            raise NoPDFLink('TXERROR: SciELO article page lacks PDF download link.')
    
    else:
        raise NoPDFLink('TXERROR: Could not retrieve SciELO article page.')