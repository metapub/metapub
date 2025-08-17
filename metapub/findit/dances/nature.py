"""Dance function for Nature Publishing Group journals."""

from ...exceptions import AccessDenied, NoPDFLink
from .generic import *

# Using registry-based approach for Nature journal configurations
from ..registry import JournalRegistry


def the_nature_ballet(pma, verify=True, request_timeout=10, max_redirects=3):
    '''Nature Publishing Group dance using evidence-driven patterns from HTML analysis.

    Primary approach: Direct DOI-based PDF URL construction
    https://www.nature.com/articles/{DOI_SUFFIX}.pdf

    Fallback approach: Canonical PDF link pattern (for older articles)
    https://www.nature.com/articles/{LEGACY_ID}.pdf

    Evidence from HTML samples shows 100% consistent /articles/{id}.pdf pattern.
    All modern Nature articles (s41xxx series) follow this structure.

    :param: pma (PubMedArticle object)
    :param: verify (bool) [default: True]
    :return: url (string)
    :raises: AccessDenied, NoPDFLink
    '''

    pdf_url = None
    attempted_urls = []

    # Strategy 1: Modern DOI-based URL construction for 10.1038 DOIs
    if pma.doi and pma.doi.startswith('10.1038/'):
        doi_suffix = pma.doi.split('10.1038/', 1)[1]
        pdf_url = f'https://www.nature.com/articles/{doi_suffix}.pdf'
        attempted_urls.append(pdf_url)

    # Strategy 2: Legacy volume/issue construction for older articles
    if not pdf_url and pma.volume and pma.issue and pma.first_page:
        registry = JournalRegistry()
        templates = registry.get_url_templates('nature')
        journal_params = registry.get_journal_parameters('nature', standardize_journal_name(pma.journal))

        # Get journal abbreviation - MUST exist for Nature legacy URLs
        ja = journal_params['ja']

        # Try journal-year-page pattern first
        if pma.year and pma.first_page and len(pma.first_page) <= 4:
            legacy_id = f"{ja}{str(pma.year)[-2:]}{pma.first_page}"
            pdf_url = f"https://www.nature.com/articles/{legacy_id}.pdf"
            attempted_urls.append(pdf_url)

        # Try legacy template patterns
        if not pdf_url:
            for template_info in templates['legacy']:
                template = template_info['template']
                required_params = template_info.get('requires_params', [])

                if all(hasattr(pma, param) or param == 'ja' for param in required_params):
                    try:
                        url = template.format(
                            ja=ja,
                            volume=pma.volume,
                            issue=pma.issue,
                            pii=pma.pii if hasattr(pma, 'pii') else pma.first_page
                        )
                        pdf_url = url
                        attempted_urls.append(pdf_url)
                        break
                    except (KeyError, AttributeError):
                        continue

    # No URL could be generated
    if not pdf_url:
        if pma.doi and pma.doi.startswith('10.1038/'):
            raise NoPDFLink("MISSING: Unable to construct Nature URL from DOI - attempted: none")
        else:
            raise NoPDFLink("MISSING: Need either Nature DOI (10.1038/*) or volume/issue/page data - attempted: none")

    # Single verification point
    if verify:
        verify_pdf_url(pdf_url, request_timeout=request_timeout, max_redirects=max_redirects)
    
    return pdf_url
