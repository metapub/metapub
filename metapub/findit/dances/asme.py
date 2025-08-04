from ...exceptions import *
from .generic import *

from ..journals.asme import asme_format

#TODO: get rid of this dumb try-except jaw

# also i'm not convinced any of this works


def the_asme_animal(pma, verify=True):
    """ASME (American Society of Mechanical Engineers) dance function.

    ASME publishes technical journals in mechanical engineering, biomechanical
    engineering, manufacturing, energy, and related fields through their
    Digital Collection platform.

    Args:
        pma: PubMedArticle object
        verify: Whether to verify PDF access

    Returns:
        PDF URL if accessible

    Raises:
        NoPDFLink: If DOI missing or PDF not accessible
        AccessDenied: If paywall detected
    """

    try:
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
                    response = requests.get(pdf_url, timeout=10, allow_redirects=True)

                    if response.ok:
                        # Check content type
                        content_type = response.headers.get('content-type', '').lower()
                        if 'application/pdf' in content_type:
                            return pdf_url
                        elif 'text/html' in content_type:
                            # Check for paywall indicators
                            page_text = response.text.lower()
                            paywall_indicators = [
                                'subscribe', 'subscription', 'login required',
                                'access denied', 'purchase', 'institutional access',
                                'sign in', 'member'
                            ]
                            if any(indicator in page_text for indicator in paywall_indicators):
                                raise AccessDenied(f'PAYWALL: ASME article requires subscription - {pdf_url}')
                            else:
                                # Might be article page, return it
                                return pdf_url
                    elif response.status_code == 404:
                        continue  # Try next URL format
                    else:
                        continue  # Try next URL format

                except requests.exceptions.RequestException:
                    continue  # Try next URL format

            # If all URLs failed
            if pma.doi.startswith('10.1115/'):
                raise NoPDFLink(f'TXERROR: Could not access ASME article - DOI: {pma.doi}')
            else:
                raise NoPDFLink(f'PATTERN: ASME typically uses DOI pattern 10.1115/*, got {pma.doi}')
        else:
            # Return first URL pattern without verification
            return possible_urls[0] if possible_urls else f'https://asmedigitalcollection.asme.org/article-pdf/{pma.doi}'

    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: ASME animal failed for {pma.journal}: {e} - DOI: {pma.doi}')


