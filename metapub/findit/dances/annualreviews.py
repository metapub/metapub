from ...exceptions import AccessDenied, NoPDFLink
from .generic import verify_pdf_url

import re

def the_annualreviews_round(pma, verify=True, request_timeout=10, max_redirects=3):
    '''Annual Reviews Inc.: Direct PDF URL construction

    Evidence-based pattern from output/article_html/annualreviews/:
    Pattern: https://www.annualreviews.org/deliver/fulltext/{journal_abbrev}/{volume}/{issue}/{doi_suffix}.pdf

    Supports both modern and legacy DOI structures:
    - Modern: 10.1146/annurev-{journal}-{date}-{id}
      Example: 10.1146/annurev-anchem-061622-012448 → anchem/17/1/annurev-anchem-061622-012448.pdf
    - Legacy: 10.1146/annurev.{journal}.{volume}.{date}.{id}
      Example: 10.1146/annurev.ge.24.120190.001025 → ge/24/1/annurev.ge.24.120190.001025.pdf

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

    # Handle both modern and legacy DOI formats
    if doi_suffix.startswith('annurev-'):
        # Modern format: annurev-{journal}-{date}-{id}
        match = re.match(r'annurev-([^-]+)-', doi_suffix)
        if not match:
            raise NoPDFLink(f'INVALID: Cannot extract journal abbreviation from modern DOI format - attempted: {pma.doi}')
        journal_abbrev = match.group(1)
        # Use PMA volume/issue or defaults
        volume = pma.volume or "1"
        issue = pma.issue or "1"
        
    elif doi_suffix.startswith('annurev.'):
        # Legacy format: annurev.{journal}.{volume}.{date}.{id}
        parts = doi_suffix.split('.')
        if len(parts) < 3:
            raise NoPDFLink(f'INVALID: Cannot extract journal abbreviation from legacy DOI format - attempted: {pma.doi}')
        journal_abbrev = parts[1]  # Second part is journal abbreviation
        volume = parts[2] if len(parts) > 2 else (pma.volume or "1")  # Third part is volume
        issue = pma.issue or "1"  # Issue not in legacy DOI, use PMA or default
        
    else:
        raise NoPDFLink(f'INVALID: Cannot extract journal abbreviation from DOI - attempted: {pma.doi}')

    # Construct PDF URL using discovered pattern
    pdf_url = f"https://www.annualreviews.org/deliver/fulltext/{journal_abbrev}/{volume}/{issue}/{doi_suffix}.pdf"

    if verify:
        verify_pdf_url(pdf_url, request_timeout=request_timeout, max_redirects=max_redirects)

    return pdf_url
