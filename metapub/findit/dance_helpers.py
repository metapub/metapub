"""Helper functions for dance functions to reduce code duplication.

This module contains common patterns extracted from dance functions to make
them more concise and maintainable.
"""

import requests
from functools import wraps
from typing import List, Dict, Optional, Any, Callable
from urllib.parse import urljoin

from ..exceptions import AccessDenied, NoPDFLink


def validate_doi(pma, publisher_name: str) -> None:
    """Validate that PMA has a DOI, raise NoPDFLink if not.
    
    Args:
        pma: PubMedArticle object
        publisher_name: Name of publisher for error message
        
    Raises:
        NoPDFLink: If DOI is missing
    """
    if not pma.doi:
        raise NoPDFLink(f'MISSING: DOI required for {publisher_name} access - Journal: {pma.journal}')


def extract_doi_parts(doi: str) -> Dict[str, str]:
    """Extract common parts from DOI for URL construction.
    
    Args:
        doi: Digital Object Identifier
        
    Returns:
        Dict with keys: prefix, suffix, article_id, parts
    """
    parts = doi.split('/')
    return {
        'prefix': parts[0] if parts else '',
        'suffix': '/'.join(parts[1:]) if len(parts) > 1 else '',
        'article_id': parts[-1] if parts else '',
        'parts': parts
    }


def extract_pma_metadata(pma) -> Dict[str, Optional[str]]:
    """Extract common metadata from PMA object.
    
    Args:
        pma: PubMedArticle object
        
    Returns:
        Dict with volume, issue, year, etc.
    """
    return {
        'volume': getattr(pma, 'volume', None),
        'issue': getattr(pma, 'issue', None),
        'year': getattr(pma, 'year', None),
        'pages': getattr(pma, 'pages', None),
        'journal': getattr(pma, 'journal', None)
    }


def build_url_variants(base_domain: str, patterns: List[str], **kwargs) -> List[str]:
    """Build URL variants using base domain and patterns.
    
    Args:
        base_domain: Base domain (e.g., 'frontiersin.org')
        patterns: List of URL patterns with {} placeholders
        **kwargs: Values to substitute in patterns
        
    Returns:
        List of constructed URLs
    """
    urls = []
    
    for pattern in patterns:
        try:
            # Add https:// if not present
            if not base_domain.startswith(('http://', 'https://')):
                domain = f'https://www.{base_domain}' if not base_domain.startswith('www.') else f'https://{base_domain}'
            else:
                domain = base_domain
                
            # Build URL from pattern
            url_path = pattern.format(**kwargs)
            full_url = urljoin(domain.rstrip('/') + '/', url_path.lstrip('/'))
            urls.append(full_url)
        except KeyError:
            # Skip patterns that don't match available kwargs
            continue
    
    return urls


def build_article_id_urls(base_domain: str, article_id: str, patterns: List[str]) -> List[str]:
    """Build URLs using article ID extracted from DOI.
    
    Args:
        base_domain: Base domain
        article_id: Article ID (last part of DOI)
        patterns: URL patterns with {} for article_id
        
    Returns:
        List of URLs
    """
    return build_url_variants(base_domain, patterns, article_id=article_id)


def build_doi_urls(base_domain: str, doi: str, patterns: List[str]) -> List[str]:
    """Build URLs using full DOI.
    
    Args:
        base_domain: Base domain
        doi: Full DOI
        patterns: URL patterns with {} for DOI
        
    Returns:
        List of URLs
    """
    return build_url_variants(base_domain, patterns, doi=doi)


def build_volume_issue_urls(base_domain: str, volume: Optional[str], issue: Optional[str], 
                           doi: str, patterns: List[str]) -> List[str]:
    """Build URLs using volume and issue information.
    
    Args:
        base_domain: Base domain
        volume: Volume number
        issue: Issue number  
        doi: DOI for fallback
        patterns: URL patterns with {volume}, {issue}, {doi} placeholders
        
    Returns:
        List of URLs
    """
    if not volume:
        return []
        
    kwargs = {'volume': volume, 'doi': doi}
    if issue:
        kwargs['issue'] = issue
        
    return build_url_variants(base_domain, patterns, **kwargs)


def add_fallback_urls(urls: List[str], doi: str) -> None:
    """Add standard fallback URL patterns to existing list.
    
    Args:
        urls: Existing URL list to append to
        doi: DOI for fallback patterns
    """
    fallback_patterns = [
        f'https://doi.org/{doi}',
        f'https://dx.doi.org/{doi}'
    ]
    urls.extend(fallback_patterns)


DEFAULT_PAYWALL_INDICATORS = [
    'subscribe', 'subscription', 'login required', 'access denied', 
    'purchase', 'institutional access', 'sign in', 'member access',
    'buy this article', 'paywall', 'premium content'
]


def verify_url_access(urls: List[str], publisher_name: str, 
                     paywall_indicators: Optional[List[str]] = None,
                     timeout: int = 10) -> str:
    """Verify URL accessibility and return first working URL.
    
    Args:
        urls: List of URLs to try
        publisher_name: Publisher name for error messages
        paywall_indicators: Custom paywall detection terms
        timeout: Request timeout in seconds
        
    Returns:
        First accessible URL
        
    Raises:
        AccessDenied: If paywall detected
        NoPDFLink: If no URLs accessible
    """
    if paywall_indicators is None:
        paywall_indicators = DEFAULT_PAYWALL_INDICATORS
    
    for pdf_url in urls:
        try:
            response = requests.get(pdf_url, timeout=timeout, allow_redirects=True)
            
            if response.ok:
                # Check content type
                content_type = response.headers.get('content-type', '').lower()
                if 'application/pdf' in content_type:
                    return pdf_url
                elif 'text/html' in content_type:
                    # Check for paywall indicators
                    page_text = response.text.lower()
                    if any(indicator in page_text for indicator in paywall_indicators):
                        raise AccessDenied(f'PAYWALL: {publisher_name} article requires access - {pdf_url}')
                    else:
                        # Accessible HTML page, return it
                        return pdf_url
            elif response.status_code == 404:
                continue  # Try next URL
            else:
                continue  # Try next URL
                
        except requests.exceptions.RequestException:
            continue  # Try next URL
    
    # If all URLs failed
    attempted_urls = ', '.join(urls[:3])  # Show first 3 for brevity
    raise NoPDFLink(f'TXERROR: Could not access {publisher_name} article - attempted: {attempted_urls}')


def handle_dance_exceptions(publisher_name: str, dance_name: str):
    """Decorator to handle standard dance function exceptions.
    
    Args:
        publisher_name: Name of publisher
        dance_name: Name of dance (for error messages)
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(pma, verify=False, *args, **kwargs):
            try:
                return func(pma, verify, *args, **kwargs)
            except Exception as e:
                if isinstance(e, (NoPDFLink, AccessDenied)):
                    raise
                else:
                    journal = getattr(pma, 'journal', 'Unknown')
                    doi = getattr(pma, 'doi', 'Unknown')
                    raise NoPDFLink(f'TXERROR: {publisher_name} {dance_name} failed for {journal}: {e} - DOI: {doi}')
        return wrapper
    return decorator


class FocusedURLBuilder:
    """Focused URL builder that prioritizes primary PDF endpoints over shotgun approaches."""
    
    def __init__(self, publisher_name: str):
        self.publisher_name = publisher_name
        self.primary_url = None
        self.secondary_url = None
        self.fallback_url = None
    
    def set_primary_pdf_url(self, url: str) -> 'FocusedURLBuilder':
        """Set the primary PDF URL (this should be the researched, known-good PDF endpoint)."""
        self.primary_url = url
        return self
    
    def set_secondary_url(self, url: str, reason: str = "") -> 'FocusedURLBuilder':
        """Set optional secondary URL (only if we know it works, e.g., PMID-based lookup)."""
        self.secondary_url = url
        if reason:
            print(f"DEBUG: Secondary URL for {self.publisher_name}: {reason}")
        return self
    
    def set_fallback_doi_resolver(self, doi: str) -> 'FocusedURLBuilder':
        """Set DOI resolver as final fallback."""
        self.fallback_url = f'https://doi.org/{doi}'
        return self
    
    def get_urls_to_try(self) -> List[str]:
        """Get the focused list of URLs to try (1-3 URLs max)."""
        urls = []
        if self.primary_url:
            urls.append(self.primary_url)
        if self.secondary_url:
            urls.append(self.secondary_url)
        if self.fallback_url:
            urls.append(self.fallback_url)
        return urls
    
    def verify_or_return_primary(self, verify: bool, paywall_indicators: Optional[List[str]] = None) -> str:
        """Verify URLs in priority order, or return primary URL without verification."""
        if verify:
            urls = self.get_urls_to_try()
            if not urls:
                raise NoPDFLink(f'MISSING: No URLs configured for {self.publisher_name}')
            return verify_focused_url_access(urls, self.publisher_name, paywall_indicators)
        else:
            if not self.primary_url:
                raise NoPDFLink(f'MISSING: No primary URL configured for {self.publisher_name}')
            return self.primary_url


def verify_focused_url_access(urls: List[str], publisher_name: str, 
                             paywall_indicators: Optional[List[str]] = None,
                             timeout: int = 10) -> str:
    """Verify focused URL list (1-3 URLs max) and return first working PDF URL.
    
    This is the focused replacement for the shotgun verify_url_access approach.
    """
    if paywall_indicators is None:
        paywall_indicators = DEFAULT_PAYWALL_INDICATORS
    
    for i, pdf_url in enumerate(urls):
        url_type = "primary" if i == 0 else "secondary" if i == 1 else "fallback"
        
        try:
            response = requests.get(pdf_url, timeout=timeout, allow_redirects=True)
            
            if response.ok:
                # Check content type - we ONLY want PDFs
                content_type = response.headers.get('content-type', '').lower()
                if 'application/pdf' in content_type:
                    return pdf_url
                elif 'text/html' in content_type:
                    # HTML response - check if it's a paywall or just wrong URL
                    page_text = response.text.lower()
                    if any(indicator in page_text for indicator in paywall_indicators):
                        # This is a paywall, try next URL if available
                        if i + 1 < len(urls):
                            continue
                        else:
                            raise AccessDenied(f'PAYWALL: {publisher_name} article requires access - {pdf_url}')
                    else:
                        # HTML page but not paywalled - wrong URL, try next
                        if i + 1 < len(urls):
                            continue
                        else:
                            raise NoPDFLink(f'WRONGTYPE: {publisher_name} {url_type} URL returned HTML, not PDF - {pdf_url}')
                else:
                    # Some other content type, try next URL
                    if i + 1 < len(urls):
                        continue
                    else:
                        raise NoPDFLink(f'WRONGTYPE: {publisher_name} {url_type} URL returned {content_type}, not PDF - {pdf_url}')
            elif response.status_code == 404:
                # 404 - try next URL if available
                if i + 1 < len(urls):
                    continue
                else:
                    raise NoPDFLink(f'NOTFOUND: {publisher_name} {url_type} URL not found (404) - {pdf_url}')
            else:
                # Other HTTP error - try next URL if available
                if i + 1 < len(urls):
                    continue
                else:
                    raise NoPDFLink(f'HTTPERROR: {publisher_name} {url_type} URL failed ({response.status_code}) - {pdf_url}')
                
        except requests.exceptions.RequestException as e:
            # Network error - try next URL if available
            if i + 1 < len(urls):
                continue
            else:
                raise NoPDFLink(f'NETWORKERROR: {publisher_name} {url_type} URL network failure - {pdf_url}: {e}')
    
    # Should never reach here, but just in case
    raise NoPDFLink(f'TXERROR: All {publisher_name} URLs failed unexpectedly')


def create_focused_dance_function(publisher_name: str, primary_pdf_template: str, 
                                 secondary_template: str = None, secondary_reason: str = "",
                                 paywall_indicators: Optional[List[str]] = None):
    """Factory function to create focused dance functions with 1-2 precise URL templates.
    
    Args:
        publisher_name: Name of publisher
        primary_pdf_template: Primary PDF URL template (e.g., 'https://example.com/pdf/{doi}')
        secondary_template: Optional secondary URL template (e.g., 'https://example.com/pmid/{pmid}')
        secondary_reason: Explanation for why secondary exists (for debugging)
        paywall_indicators: Custom paywall indicators
        
    Returns:
        Focused dance function that tries 1-2 precise URLs
    """
    @handle_dance_exceptions(publisher_name, 'focused')
    def focused_dance_function(pma, verify=False):
        validate_doi(pma, publisher_name)
        
        doi_parts = extract_doi_parts(pma.doi)
        metadata = extract_pma_metadata(pma)
        
        builder = FocusedURLBuilder(publisher_name)
        
        # Build primary URL
        primary_url = primary_pdf_template.format(
            doi=pma.doi,
            article_id=doi_parts['article_id'],
            volume=metadata.get('volume', ''),
            issue=metadata.get('issue', ''),
            year=metadata.get('year', ''),
            pmid=getattr(pma, 'pmid', '')
        )
        builder.set_primary_pdf_url(primary_url)
        
        # Build secondary URL if provided
        if secondary_template:
            try:
                secondary_url = secondary_template.format(
                    doi=pma.doi,
                    article_id=doi_parts['article_id'],
                    volume=metadata.get('volume', ''),
                    issue=metadata.get('issue', ''),
                    year=metadata.get('year', ''),
                    pmid=getattr(pma, 'pmid', '')
                )
                builder.set_secondary_url(secondary_url, secondary_reason)
            except (KeyError, AttributeError):
                # If secondary template can't be filled, skip it
                pass
        
        # Always set DOI resolver as fallback
        builder.set_fallback_doi_resolver(pma.doi)
        
        return builder.verify_or_return_primary(verify, paywall_indicators)
    
    return focused_dance_function


def create_standard_dance_function(publisher_name: str, base_domain: str, 
                                 url_patterns: Dict[str, List[str]],
                                 paywall_indicators: Optional[List[str]] = None):
    """Factory function to create standard dance functions.
    
    Args:
        publisher_name: Name of publisher
        base_domain: Base domain for URLs
        url_patterns: Dict with keys like 'article_id', 'doi', 'volume_issue'
        paywall_indicators: Custom paywall indicators
        
    Returns:
        Dance function
    """
    @handle_dance_exceptions(publisher_name, 'dance')
    def dance_function(pma, verify=False):
        validate_doi(pma, publisher_name)
        
        doi_parts = extract_doi_parts(pma.doi)
        metadata = extract_pma_metadata(pma)
        
        builder = PublisherURLBuilder(base_domain, publisher_name)
        
        # Add different URL pattern types
        if 'article_id' in url_patterns:
            builder.add_article_id_patterns(url_patterns['article_id'], doi_parts['article_id'])
        
        if 'doi' in url_patterns:
            builder.add_doi_patterns(url_patterns['doi'], pma.doi)
            
        if 'volume_issue' in url_patterns and metadata['volume']:
            builder.add_volume_issue_patterns(url_patterns['volume_issue'], 
                                            metadata['volume'], metadata['issue'], pma.doi)
        
        builder.add_fallbacks(pma.doi)
        
        return builder.verify_or_return_first(verify, paywall_indicators)
    
    return dance_function