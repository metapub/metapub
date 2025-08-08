"""Royal Society of Chemistry dance function - EVIDENCE-DRIVEN REWRITE.

Based on analysis of 9 HTML samples, RSC provides 100% consistent citation_pdf_url 
meta tags with pattern: https://pubs.rsc.org/en/content/articlepdf/{year}/{journal}/{article_id}

Evidence: All samples (31712796, 32935693, 34533150, 34817495, 35014660, 
35699396, 38170905, 38651948, 39262316) have perfect citation_pdf_url metadata.

Follows DANCE_FUNCTION_GUIDELINES:
- Single method approach (no try-except blocks)
- Under 50 lines
- Uses citation_pdf_url extraction (most reliable)
- Clear error messages with prefixes
"""

import re
from ...exceptions import NoPDFLink, AccessDenied
from .generic import the_doi_2step, verify_pdf_url, unified_uri_get


def the_rsc_reaction(pma, verify=True):
    """Royal Society of Chemistry: Leading chemistry publisher with 50+ journals.
    
    Uses citation_pdf_url meta tag extraction - 100% reliable across all evidence samples.
    All RSC DOIs follow 10.1039/ prefix pattern with pubs.rsc.org hosting.

    Evidence from 9 HTML samples shows consistent pattern:
    https://pubs.rsc.org/en/content/articlepdf/{year}/{journal}/{article_id}

    :param pma: PubmedArticle with DOI required
    :param verify: PDF URL verification (default: True)
    :return: PDF URL string
    :raises: NoPDFLink, AccessDenied
    """
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for RSC journals')
    
    # Validate RSC DOI pattern (all evidence shows 10.1039/ prefix)
    if not pma.doi.startswith('10.1039/'):
        raise NoPDFLink(f'INVALID: DOI must start with 10.1039/ for RSC - got: {pma.doi}')
    
    # Get article HTML page via DOI resolution
    article_url = the_doi_2step(pma.doi)
    response = unified_uri_get(article_url)
    
    if response.status_code != 200:
        raise NoPDFLink(f'TXERROR: Could not access RSC article page (HTTP {response.status_code})')
    
    # Extract citation_pdf_url meta tag (evidence shows 100% reliability)
    pdf_match = re.search(r'<meta\s+content="([^"]+)"\s+name="citation_pdf_url"', response.text)
    if not pdf_match:
        raise NoPDFLink('MISSING: No citation_pdf_url found in RSC article HTML')
    
    pdf_url = pdf_match.group(1)
    
    # Verify PDF accessibility if requested
    if verify:
        verify_pdf_url(pdf_url, 'RSC')
    
    return pdf_url
