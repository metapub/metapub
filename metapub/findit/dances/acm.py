
from ...exceptions import AccessDenied, NoPDFLink
from .generic import *


def the_acm_reel(pma, verify=True, request_timeout=10, max_redirects=3):
    '''ACM Digital Library: Computing and information technology publications

    The ACM Digital Library is a comprehensive database of articles, proceedings,
    and other publications from the Association for Computing Machinery (ACM).
    It covers computer science, information technology, and related fields.

    URL Pattern: https://dl.acm.org/doi/[DOI]
    PDF Pattern: https://dl.acm.org/doi/pdf/[DOI]
    DOI Pattern: 10.1145/[ID] (most common ACM DOI pattern)

    :param: pma (PubmedArticle)
    :param: verify (bool) [default: True]
    :param: request_timeout (int) [default: 10]
    :param: max_redirects (int) [default: 3]
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    '''
    # Check if DOI is available
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for ACM articles - attempted: none')

    # Try direct PDF URL construction
    pdf_url = f'https://dl.acm.org/doi/pdf/{pma.doi}'

    if verify:
        verify_pdf_url(pdf_url, 'ACM', request_timeout=request_timeout, max_redirects=max_redirects)
    
    return pdf_url


