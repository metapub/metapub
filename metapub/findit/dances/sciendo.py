"""Dance function for Sciendo (De Gruyter) journals."""

from ..dance_helpers import (
    validate_doi, FocusedURLBuilder, handle_dance_exceptions
)


@handle_dance_exceptions('Sciendo', 'spiral')
def the_sciendo_spiral(pma, verify=False):
    """Dance function for Sciendo (De Gruyter) journals.
    
    Handles open access journals published on Sciendo platform (sciendo.com).
    Sciendo is De Gruyter's open access platform hosting diverse academic journals,
    primarily from Eastern European and international publishers.
    
    Primary PDF URL: https://sciendo.com/pdf/{doi}
    Secondary URL: https://sciendo.com/article/{doi} (may redirect to PDF)
    
    Args:
        pma: PubMedArticle object
        verify: Whether to verify PDF accessibility
        
    Returns:
        str: URL to PDF
        
    Raises:
        NoPDFLink: If DOI missing or URL construction fails
        AccessDenied: If paywall detected
    """
    validate_doi(pma, "Sciendo")
    
    builder = FocusedURLBuilder('Sciendo')
    
    # Primary PDF endpoint (educated guess - needs verification)
    builder.set_primary_pdf_url(f'https://sciendo.com/pdf/{pma.doi}')
    
    # Secondary: article page (may have PDF link or redirect)
    builder.set_secondary_url(f'https://sciendo.com/article/{pma.doi}', 
                             "Article page may redirect to PDF")
    
    # Fallback to DOI resolver
    builder.set_fallback_doi_resolver(pma.doi)
    
    # Sciendo paywall indicators (minimal since mostly open access)
    sciendo_paywall_indicators = [
        'subscribe', 'subscription', 'login required', 'access denied',
        'purchase', 'institutional access', 'sign in', 'member access',
        'paywall', 'premium content'
    ]
    
    return builder.verify_or_return_primary(verify, sciendo_paywall_indicators)