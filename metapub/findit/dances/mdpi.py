"""MDPI dance function using direct URL construction from DOI patterns."""

from ...exceptions import NoPDFLink


def the_mdpi_moonwalk(pma, verify=True):
    """MDPI dance - direct PDF URL construction from DOI.
    
    MDPI uses a consistent URL pattern where DOI 10.3390/journal[volume][issue][article]
    maps to PDF URL /{journal_id}/{volume}/{issue}/{article}/pdf
    
    Pattern discovered from evidence:
    - DOI: 10.3390/cardiogenetics11030017
    - URL: /2035-8148/11/3/17/pdf
    - DOI: 10.3390/metabo14040228  
    - URL: /2218-1989/14/4/228/pdf
    
    The challenge is mapping journal names to their numeric IDs.
    Since direct DOI resolution works well for MDPI, this function
    uses enhanced DOI resolution with '/pdf' appended.
    
    :param: pma (PubMedArticle object)
    :param: verify (bool) [default: True]
    :return: url (str) - Direct PDF URL
    :raises: NoPDFLink
    """
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for MDPI PDF access')
    
    if not pma.doi.startswith('10.3390/'):
        raise NoPDFLink('MISSING: Not an MDPI DOI (expected 10.3390/)')
    
    # MDPI strategy: resolve DOI and append /pdf
    # This works because MDPI DOIs resolve to their article pages
    # and the PDF pattern is consistent
    try:
        from .generic import the_doi_2step
        resolved_url = the_doi_2step(pma.doi)
        pdf_url = f"{resolved_url}/pdf"
        
        if verify:
            from .generic import verify_pdf_url
            verify_pdf_url(pdf_url, 'MDPI')
            
        return pdf_url
        
    except Exception as e:
        if isinstance(e, NoPDFLink):
            raise
        raise NoPDFLink(f'MISSING: MDPI PDF construction failed for {pma.journal}: {str(e)}')
