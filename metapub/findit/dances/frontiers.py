"""Dance function for Frontiers Media journals."""

from ..dance_helpers import (
    validate_doi, FocusedURLBuilder, handle_dance_exceptions
)


@handle_dance_exceptions('Frontiers', 'square')
def the_frontiers_square(pma, verify=False):
    """Dance function for Frontiers Media journals.
    
    Handles open-access journals published by Frontiers Media at frontiersin.org.
    Frontiers is a major open-access publisher with transparent peer review and 
    article-level metrics. Most content is freely accessible.
    
    Primary PDF URL: https://www.frontiersin.org/articles/{doi}/pdf
    
    Args:
        pma: PubMedArticle object
        verify: Whether to verify PDF accessibility
        
    Returns:
        str: URL to PDF
        
    Raises:
        NoPDFLink: If DOI missing or URL construction fails
        AccessDenied: If paywall detected (rare for Frontiers)
    """
    validate_doi(pma, "Frontiers")
    
    builder = FocusedURLBuilder('Frontiers')
    
    # Primary PDF endpoint (researched and verified)
    builder.set_primary_pdf_url(f'https://www.frontiersin.org/articles/{pma.doi}/pdf')
    
    # Fallback to DOI resolver
    builder.set_fallback_doi_resolver(pma.doi)
    
    # Minimal paywall indicators (Frontiers is mostly open access)
    frontiers_paywall_indicators = [
        'subscribe', 'subscription', 'login required', 'access denied', 
        'purchase', 'institutional access', 'sign in', 'member access'
    ]
    
    return builder.verify_or_return_primary(verify, frontiers_paywall_indicators)