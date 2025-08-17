from ...exceptions import *
from .generic import *

from ..journals.asme import asme_format

#TODO: get rid of this dumb try-except jaw

# also i'm not convinced any of this works


def the_asme_animal(pma, verify=True, request_timeout=10, max_redirects=3):
    """ASME (American Society of Mechanical Engineers) dance function.

    ASME publishes technical journals in mechanical engineering, biomechanical
    engineering, manufacturing, energy, and related fields through their
    Digital Collection platform.
    
    Includes CrossRef API fallback for blocked access.

    Args:
        pma: PubMedArticle object
        verify: Whether to verify PDF access

    Returns:
        PDF URL if accessible

    Raises:
        NoPDFLink: If DOI missing or PDF not accessible
        AccessDenied: If paywall detected
    """
    if not pma.doi:
        raise NoPDFLink('MISSING: doi needed for ASME article.')

    # Try CrossRef API first since ASME blocks automated access
    try:
        crossref_urls = get_crossref_pdf_links(pma.doi)
        if crossref_urls:
            # Use the first PDF URL from CrossRef
            return crossref_urls[0]
    except NoPDFLink:
        # Fall through to original approach if CrossRef fails
        pass

    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for ASME article access')

    # ASME typically uses 10.1115/* DOI pattern
    if not pma.doi.startswith('10.1115/'):
        # Still try to process, but note pattern mismatch
        pass

    # Try to derive journal code from journal name
    journal_name = pma.journal.lower() if pma.journal else ''


    # TODO: actually find the ASME journal code mappings, this is a stupid approach.
    # Common ASME journal code mappings
    journal_codes = {
        'j appl mech': 'appliedmechanics',
        'j biomech eng': 'biomechanical',
        'j heat transfer': 'heattransfer',
        'j fluids eng': 'fluidsengineering',
        'j eng gas turbine power': 'gasturbinespower',
        'j press vessel technol': 'pressurevesseltech',
        'j manuf sci eng': 'manufacturingscience',
        'j mech des': 'mechanicaldesign',
        'j vib acoust': 'vibrationacoustics',
        'j tribol': 'tribology',
        'j dyn syst meas control': 'dynamicsystems',
        'j energy resour technol': 'energyresources',
        'j med device': 'medicaldevices',
        'j turbomach': 'turbomachinery',
        'j sol energy eng': 'solarenergyengineering'
    }

    # Try to find journal code
    journal_code = None
    for name_pattern, code in journal_codes.items():
        if name_pattern in journal_name:
            journal_code = code
            break

    # Try different URL construction approaches
    possible_urls = []

    if journal_code:
        possible_urls.extend([
            f'https://asmedigitalcollection.asme.org/{journal_code}/article-pdf/{pma.doi}',
            f'https://asmedigitalcollection.asme.org/{journal_code}/article/{pma.doi}',
            f'https://asmedigitalcollection.asme.org/{journal_code}/article-pdf/doi/{pma.doi}',
            f'https://asmedigitalcollection.asme.org/{journal_code}/article/doi/{pma.doi}'
        ])

    # Try generic patterns without journal code
    possible_urls.extend([
        f'https://asmedigitalcollection.asme.org/article-pdf/{pma.doi}',
        f'https://asmedigitalcollection.asme.org/article/{pma.doi}',
        f'https://asmedigitalcollection.asme.org/doi/pdf/{pma.doi}',
        f'https://asmedigitalcollection.asme.org/doi/{pma.doi}'
    ])

    if verify:
        for pdf_url in possible_urls:
            try:
                verify_pdf_url(pdf_url, 'ASME', request_timeout=request_timeout, max_redirects=max_redirects)
                return pdf_url
            except (NoPDFLink, AccessDenied):
                continue  # Try next URL format

        # If all URLs failed
        if pma.doi.startswith('10.1115/'):
            raise NoPDFLink(f'TXERROR: Could not access ASME article - DOI: {pma.doi}')
        else:
            raise NoPDFLink(f'PATTERN: ASME typically uses DOI pattern 10.1115/*, got {pma.doi}')
    else:
        # Return first URL pattern without verification
        return possible_urls[0] if possible_urls else f'https://asmedigitalcollection.asme.org/article-pdf/{pma.doi}'



