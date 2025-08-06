"""BioOne dance function using citation_pdf_url meta tag extraction."""

from .generic import the_vip_shake
from ...exceptions import NoPDFLink


def the_bioone_bounce(pma, verify=True):
    """BioOne dance - citation_pdf_url meta tag extraction.
    
    BioOne is a multi-publisher digital library platform for biological sciences
    that hosts journals from ~200+ societies and independent publishers. Despite 
    diverse DOI prefixes (10.1643/, 10.1645/, 10.1676/, 10.1647/, 10.7589/, etc.)
    all articles resolve through bioone.org with consistent citation_pdf_url metadata.
    
    Evidence from HTML samples shows 100% consistent citation_pdf_url patterns:
    - DOI: 10.1656/045.022.0311 → PDF: https://bioone.org/journals/.../10.1656/045.022.0311.pdf
    - DOI: 10.1647/20-00013 → PDF: https://bioone.org/journals/.../10.1647/20-00013.pdf
    - DOI: 10.13158/heia.24.2.2011.315 → PDF: https://bioone.org/journals/.../10.13158/heia.24.2.2011.315.pdf
    - DOI: 10.7589/JWD-D-23-00187 → PDF: https://bioone.org/journals/.../10.7589/JWD-D-23-00187.pdf
    
    TRUST THE REGISTRY: Function trusts that registry assigns BioOne articles correctly.
    Uses the_vip_shake for robust citation_pdf_url extraction with paywall detection.
    
    :param: pma (PubMedArticle object) 
    :param: verify (bool) [default: True]
    :return: url (str) - Direct PDF URL
    :raises: NoPDFLink, AccessDenied
    """
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for BioOne PDF access')
    
    # BioOne uses citation_pdf_url meta tags consistently across all publishers
    return the_vip_shake(pma, verify=verify)