import requests
from ...exceptions import *
from .generic import *


def the_dustri_polka(pma, verify=True, request_timeout=10, max_redirects=3):
    """Dustri-Verlag dance function.
    
    Dustri-Verlag (www.dustri.com) is a German medical publisher that publishes
    journals in clinical nephrology, pharmacology, and neuropathology.
    
    ARCHITECTURAL LIMITATION: Dustri uses POST-only PDF downloads
    ========================================================
    
    Dustri articles use POST forms for PDF downloads:
    <form method="POST" action="/index.php?id=98&artId={artId}&doi={doi}&L=0">
        <input type="hidden" name="file" value="uploads/repository/{path}/{file}.pdf">
        <input type="submit" name="artDownloader" value="Free Full Text">
    </form>
    
    Since FindIt promises GET-able URLs, this function provides the article
    page URL where users can manually access PDFs when available.
    
    Mixed Access Model:
    - Some articles: Free full text via POST download
    - Some articles: Paywall ("Add to Cart" required)
    
    Args:
        pma: PubMedArticle object
        verify: Whether to verify access (optional)
        
    Returns:
        Article page URL (not direct PDF due to POST requirement)
        
    Raises:
        NoPDFLink: If DOI missing or POST-only access required
        AccessDenied: If article page accessible but paywall detected
    """
    
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for Dustri-Verlag article access')
    
    # Dustri DOI pattern: 10.5414/{journal_code}{article_id}
    if not pma.doi.startswith('10.5414/'):
        raise NoPDFLink('INVALID: DOI format not recognized for Dustri-Verlag')
    
    # Extract article ID from DOI (e.g., 10.5414/CN110175Intro -> extract artId from site)
    # Since artId is not directly derivable from DOI, we need to access the article page
    
    # Construct article page URL - this appears to be the pattern from evidence
    article_url = f"https://www.dustri.com/nc/article-response-page.html?doi={pma.doi}"
    
    if verify:
        try:
            response = unified_uri_get(article_url, timeout=10, allow_redirects=True)
            
            if not response.ok:
                raise NoPDFLink(f'TXERROR: Could not access Dustri article page - status {response.status_code}')
            
            page_content = response.text
            
            # Check if article has free PDF access (POST form with "Free Full Text")
            if 'name="artDownloader"' in page_content and 'Free Full Text' in page_content:
                # Article has free PDF but requires POST request
                raise NoPDFLink(f'POSTONLY: Dustri-Verlag PDF requires POST request - visit article page: {article_url}')
            
            # Check if article requires payment
            elif 'Add to Cart' in page_content or 'btnAddCart' in page_content:
                raise AccessDenied(f'PAYWALL: Dustri-Verlag article requires purchase - {article_url}')
            
            else:
                # Unknown access pattern
                raise NoPDFLink(f'TXERROR: Could not determine PDF access method for Dustri article - {article_url}')
                
        except (requests.exceptions.RequestException, requests.exceptions.ConnectionError,
                requests.exceptions.Timeout) as e:
            raise NoPDFLink(f'TXERROR: Network error accessing Dustri article page: {e}')
        except (AccessDenied, NoPDFLink):
            raise
    
    else:
        # Without verification, return article page URL with explanatory note
        raise NoPDFLink(f'POSTONLY: Dustri-Verlag PDFs require POST form submission - visit: {article_url}')