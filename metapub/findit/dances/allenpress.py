from ...exceptions import *
from .generic import *

from ..journals.allenpress import allenpress_format


#TODO: get rid of this dumb try-except jaw

# also i'm not convinced any of this works

## Also THIS APPROACH IS BAD -- we shouldn't be guessing at patterns. we'll get banned.


def the_allenpress_advance(pma, verify=True, request_timeout=10, max_redirects=3):
    """Allen Press dance function.

    Allen Press provides publishing services for scholarly and professional
    societies. Their journals are hosted on meridian.allenpress.com with
    journal-specific URL structures.

    Args:
        pma: PubMedArticle object
        verify: Whether to verify PDF access
        request_timeout: HTTP request timeout in seconds
        max_redirects: Maximum redirects to follow

    Returns:
        PDF URL if accessible

    Raises:
        NoPDFLink: If DOI missing or PDF not accessible
        AccessDenied: If paywall detected
    """

    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for Allen Press article access')

    # Allen Press journals may use various DOI patterns from different societies
    # Try to derive journal code from journal name or DOI
    journal_name = pma.journal.lower() if pma.journal else ''

    # Common journal code mappings (will need to expand based on actual patterns)
    journal_codes = {
        'oper dent': 'od',
        'j am anim hosp assoc': 'jaaha',
        'arch pathol lab med': 'aplm',
        'j athl train': 'jat',
        'angle orthod': 'angl',
        'tex heart inst j': 'thij',
        'ethn dis': 'ethn',
        'j oral implantol': 'joi',
        'j am mosq control assoc': 'jamca',
        'j grad med educ': 'jgme',
        'j pediatr pharmacol ther': 'jppt'
    }

    # Try to find journal code
    journal_code = None
    for name_pattern, code in journal_codes.items():
        if name_pattern in journal_name:
            journal_code = code
            break

    # If we can't determine journal code, try generic patterns
    possible_urls = []

    if journal_code:
        possible_urls.extend([
            f'https://meridian.allenpress.com/{journal_code}/article-pdf/{pma.doi}',
            f'https://meridian.allenpress.com/{journal_code}/article/{pma.doi}',
            f'https://meridian.allenpress.com/{journal_code}/article-pdf/doi/{pma.doi}',
            f'https://meridian.allenpress.com/{journal_code}/article/doi/{pma.doi}'
        ])

    # Try generic patterns without journal code
    doi_suffix = pma.doi.split('/')[-1] if '/' in pma.doi else pma.doi
    possible_urls.extend([
        f'https://meridian.allenpress.com/article-pdf/{pma.doi}',
        f'https://meridian.allenpress.com/article/{pma.doi}',
        f'https://meridian.allenpress.com/doi/pdf/{pma.doi}',
        f'https://meridian.allenpress.com/doi/{pma.doi}'
    ])

    if verify:
        for pdf_url in possible_urls:
            try:
                verify_pdf_url(pdf_url, 'Allen Press', request_timeout=request_timeout, max_redirects=max_redirects)
                return pdf_url
            except (NoPDFLink, AccessDenied):
                continue  # Try next URL format

        # If all URLs failed
        raise NoPDFLink(f'TXERROR: Could not access Allen Press article with any URL pattern - DOI: {pma.doi}')
    else:
        # Return first URL pattern without verification
        return possible_urls[0] if possible_urls else f'https://meridian.allenpress.com/article-pdf/{pma.doi}'




