from ...exceptions import AccessDenied, NoPDFLink
from .generic import verify_pdf_url

import re

def the_annualreviews_round(pma, verify=True, request_timeout=10, max_redirects=3):
    '''Annual Reviews Inc.: Direct PDF URL construction

    Evidence-based pattern from output/article_html/annualreviews/:
    Pattern: https://www.annualreviews.org/deliver/fulltext/{journal_abbrev}/{volume}/{issue}/{doi_suffix}.pdf

    DOI structure: 10.1146/annurev-{journal}-{date}-{id}
    Example: 10.1146/annurev-anchem-061622-012448 → anchem/17/1/annurev-anchem-061622-012448.pdf

    :param: pma (PubmedArticle)
    :param: verify (bool) [default: True]
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    '''
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for Annual Reviews journals - attempted: none')

    if not pma.doi.startswith('10.1146/'):
        raise NoPDFLink(f'INVALID: DOI does not match Annual Reviews pattern (10.1146/) - attempted: {pma.doi}')

    # Extract DOI suffix and journal abbreviation
    doi_suffix = pma.doi.replace('10.1146/', '')

    # Extract journal abbreviation from DOI pattern: annurev-{journal}-{date}-{id}
    match = re.match(r'annurev-([^-]+)-', doi_suffix)
    if not match:
        raise NoPDFLink(f'INVALID: Cannot extract journal abbreviation from DOI - attempted: {pma.doi}')

    journal_abbrev = match.group(1)

    # Get volume and issue (defaulting to 1 for most Annual Reviews)
    volume = pma.volume or "1"
    issue = pma.issue or "1"

    # Construct PDF URL using discovered pattern
    pdf_url = f"https://www.annualreviews.org/deliver/fulltext/{journal_abbrev}/{volume}/{issue}/{doi_suffix}.pdf"

    if verify:
        verify_pdf_url(pdf_url, request_timeout=request_timeout, max_redirects=max_redirects)

    return pdf_url
