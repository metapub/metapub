from ...exceptions import *
from .generic import *

from ..journals.iop import iop_format, iop_alt_format

#TODO: get rid of this dumb try-except jaw

# also i'm not convinced any of this works


def the_iop_fusion(pma, verify=True):
    """IOP Publishing (Institute of Physics) dance function.

    IOP Publishing operates multiple domains including iopscience.iop.org
    and validate.perfdrive.com. Most IOP journals use DOI pattern 10.1088/*.

    Args:
        pma: PubMedArticle object
        verify: Whether to verify PDF access

    Returns:
        PDF URL if accessible

    Raises:
        NoPDFLink: If DOI missing, wrong pattern, or PDF not accessible
        AccessDenied: If paywall detected
    """

    try:
        # WHY IS THIS ALL WITHIN A TRY-EXCEPT BLOCK, CLAUDE?
        if not pma.doi:
            raise NoPDFLink('MISSING: DOI required for IOP article access')

        # Try both IOP URL formats
        possible_urls = [
            iop_format.format(doi=pma.doi),
            iop_alt_format.format(doi=pma.doi)
        ]

        #TODO: if we don't know what's going to work, then gating on "verify" is bad logic...
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
                                'access denied', 'purchase', 'institutional access'
                            ]
                            if any(indicator in page_text for indicator in paywall_indicators):
                                # Try next URL before raising paywall error
                                continue
                            else:
                                # Might be article page, return it
                                return pdf_url
                    elif response.status_code == 404:
                        continue  # Try next URL format
                    else:
                        continue  # Try next URL format

                except requests.exceptions.RequestException as e:
                    continue  # Try next URL format

            # If both URLs failed, determine appropriate error
            if any(pma.doi.startswith(pattern) for pattern in common_iop_patterns):
                raise NoPDFLink(f'TXERROR: Could not access IOP article at either domain - DOI: {pma.doi}')
            else:
                raise NoPDFLink(f'PATTERN: IOP typically uses DOI patterns {common_iop_patterns}, got {pma.doi}')
        else:
            # Return primary URL without verification
            return possible_urls[0]

    except Exception as e:
        if isinstance(e, (NoPDFLink, AccessDenied)):
            raise
        else:
            raise NoPDFLink(f'TXERROR: IOP fusion failed for {pma.journal}: {e} - DOI: {pma.doi}')


