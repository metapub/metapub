from ...exceptions import *
from .generic import *

#TODO: get rid of this dumb try-except jaw

# also i'm not convinced any of this works



def the_longdom_hustle(pma, verify=True):
    '''Longdom Publishing: Open access journals across various fields

    Longdom Publishing is an open access publisher that publishes journals
    across various fields including medical sciences, life sciences, and technology.
    Note: This publisher has been flagged by some as potentially predatory.

    URL Pattern: https://www.longdom.org/articles/[article-slug]
    PDF Pattern: https://www.longdom.org/articles-pdfs/[article-slug].pdf
    DOI Pattern: Various DOI patterns (10.4172, 10.35248, etc.)

    Args:
        pma: PubMedArticle instance with DOI
        verify: Whether to verify PDF accessibility (default: True)

    Returns:
        PDF URL string if accessible

    Raises:
        NoPDFLink: If no DOI, cannot construct URL, or technical issues
        AccessDenied: If paywall detected (rare for open access)
    '''
    try:
        # Check for required DOI
        if not pma.doi:
            raise NoPDFLink(f'MISSING: DOI required for Longdom access - journal: {pma.journal}')

        # Longdom URL construction is complex - try to derive from DOI
        # Most Longdom URLs follow pattern: longdom.org/articles/article-title-doi-suffix
        # This is a simplified approach - may need refinement
        doi_suffix = pma.doi.split('/')[-1] if '/' in pma.doi else pma.doi

        # Try multiple URL patterns since Longdom has inconsistent URL structure
        possible_urls = [
            f'https://www.longdom.org/articles-pdf/{doi_suffix}.pdf',
            f'https://www.longdom.org/articles/{doi_suffix}.pdf',
            f'https://www.longdom.org/open-access/{doi_suffix}.pdf'
        ]


        # TODO: this logic makes no sense -- we're forced to verify if we don't know what the URL is,
        # so there's no use gating this.  We should experiment to see if there's "one URL format to
        #    rule them all" so we don't end up guessing multiple times (bad form).
        if verify:
            for pdf_url in possible_urls:
                try:
                    response = unified_uri_get(pdf_url, timeout=10, allow_redirects=True)

                    if response.ok:
                        # Check if we got actual PDF content
                        content_type = response.headers.get('content-type', '').lower()
                        if 'application/pdf' in content_type:
                            return pdf_url
                        elif 'text/html' in content_type:
                            # Check for error pages
                            page_text = response.text.lower()
                            if 'not found' in page_text or 'error' in page_text:
                                continue  # Try next URL pattern
                            else:
                                # Return article page URL instead
                                article_url = pdf_url.replace('/articles-pdf/', '/articles/').replace('.pdf', '')
                                return article_url

                except Exception:
                    continue  # Try next URL pattern

            # If all patterns failed, raise error
            raise NoPDFLink(f'TXERROR: Could not access Longdom article with any URL pattern - attempted: {possible_urls[0]}')
        else:
            # Return first PDF URL pattern without verification
            return possible_urls[0]

    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: Longdom hustle failed for {pma.journal}: {e} - attempted: DOI resolution')


