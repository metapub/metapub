"""Dance function for Sciendo (De Gruyter) journals."""

from ...exceptions import *
from .generic import *

def the_sciendo_spiral(pma, verify=False):
    """Dance function for Sciendo (De Gruyter) journals.

    Handles open access journals published on Sciendo platform (sciendo.com).
    Sciendo is De Gruyter's open access platform hosting diverse academic journals,
    primarily from Eastern European and international publishers.

    Primary PDF URL: https://sciendo.com/pdf/{doi}
    Fallback: DOI resolution for archive.sciendo.com content

    Args:
        pma: PubMedArticle object
        verify: Whether to verify PDF accessibility

    Returns:
        str: URL to PDF

    Raises:
        NoPDFLink: If DOI missing or URL construction fails
        AccessDenied: If paywall detected
    """
    if not pma.doi:
        raise NoPDFLink("Sciendo dance requires DOI")

    # Primary URL pattern for modern Sciendo articles
    url = f"https://sciendo.com/pdf/{pma.doi}"

    # TODO: use dxdoi engine here. wtf is this
    if verify:
        if verify_pdf_url(url, "Sciendo"):
            return url

        # For older articles, the DOI might redirect to archive.sciendo.com
        # In that case, we should follow the DOI redirect
        doi_url = f"https://dx.doi.org/{pma.doi}"
        if verify_pdf_url(doi_url, "Sciendo"):
            # If the DOI resolves to a PDF, return that URL
            return doi_url

        raise NoPDFLink("Sciendo PDF not accessible for doi '%s'" % pma.doi)

    return url

