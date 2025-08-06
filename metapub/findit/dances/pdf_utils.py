"""PDF-specific utilities for findit dance functions.

This module provides specialized functions for downloading and verifying PDFs
from various publishers, handling the unique requirements each may have.
"""

import requests
import ssl
import certifi
from typing import Tuple, Optional, Union
from urllib3.exceptions import InsecureRequestWarning
import warnings

from ...exceptions import NoPDFLink, AccessDenied


# Suppress SSL warnings when we need to disable verification
warnings.filterwarnings('ignore', category=InsecureRequestWarning)


def aggressive_pdf_get(url: str, timeout: int = 15, referrer: Optional[str] = None) -> Tuple[bool, bytes, int]:
    """
    Aggressively fetch PDF content with multiple fallback strategies.

    This function tries multiple approaches to download PDFs:
    1. Standard request with SSL verification
    2. Request without SSL verification (for publishers like SCIRP)
    3. Request with referrer header
    4. Request with different user-agent strings

    Args:
        url: PDF URL to fetch
        timeout: Request timeout in seconds
        referrer: Optional referrer URL to include in headers

    Returns:
        Tuple of (success: bool, content: bytes, status_code: int)
    """
    base_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/pdf,*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
    }

    if referrer:
        base_headers['Referer'] = referrer

    session = requests.Session()
    session.headers.update(base_headers)

    strategies = [
        # Strategy 1: Standard request with SSL verification
        {'verify': certifi.where(), 'name': 'Standard SSL'},
        # Strategy 2: No SSL verification (for publishers with SSL issues)
        {'verify': False, 'name': 'No SSL verification'},
    ]

    for strategy in strategies:
        try:
            response = session.get(url, timeout=timeout, allow_redirects=True, **{k: v for k, v in strategy.items() if k != 'name'})

            # Check if we got a successful response
            if response.status_code == 200:
                # Verify it's actually PDF content
                if response.content.startswith(b'%PDF'):
                    return True, response.content, response.status_code
                # Also check Content-Type header as fallback
                elif 'application/pdf' in response.headers.get('Content-Type', ''):
                    return True, response.content, response.status_code

            # If we got a non-200 response, continue to next strategy
            elif response.status_code in [403, 404, 500]:
                continue
            else:
                # Other status codes might indicate success for some publishers
                if response.content.startswith(b'%PDF'):
                    return True, response.content, response.status_code

        except (requests.exceptions.SSLError, ssl.SSLError):
            # SSL errors - continue to next strategy
            continue
        except requests.exceptions.RequestException:
            # Other request errors - continue to next strategy
            continue

    # All strategies failed
    return False, b'', 0



def extract_pdf_from_html(html_content: str, publisher_patterns: dict) -> Optional[str]:
    """
    Extract PDF URL from HTML using publisher-specific patterns.

    Args:
        html_content: Raw HTML content
        publisher_patterns: Dictionary of regex patterns to try, keyed by pattern name

    Returns:
        PDF URL if found, None otherwise

    Example:
        patterns = {
            'scirp_link_tag': r'<link rel="alternate" type="application/pdf"[^>]*href="([^"]+)"',
            'meta_citation': r'<meta name="citation_pdf_url" content="([^"]+)"',
            'meta_fulltext': r'<meta name="fulltext_pdf" content="([^"]+)"'
        }
    """
    import re

    for pattern_name, pattern in publisher_patterns.items():
        match = re.search(pattern, html_content)
        if match:
            pdf_url = match.group(1)
            # Convert protocol-relative URLs to https
            if pdf_url.startswith('//'):
                pdf_url = 'https:' + pdf_url
            return pdf_url

    return None


# Common PDF extraction patterns for different publishers
COMMON_PDF_PATTERNS = {
    'scirp': {
        'link_alternate': r'<link rel="alternate" type="application/pdf"[^>]*href="([^"]+)"',
        'meta_citation': r'<meta name="citation_pdf_url" content="([^"]+)"',
        'meta_fulltext': r'<meta name="fulltext_pdf" content="([^"]+)"'
    },
    'generic': {
        'meta_citation': r'<meta name="citation_pdf_url" content="([^"]+)"',
        'meta_dc_identifier': r'<meta name="DC\.identifier" content="([^"]*\.pdf[^"]*)"',
        'link_canonical_pdf': r'<link[^>]*rel="canonical"[^>]*href="([^"]*\.pdf[^"]*)"',
        'meta_fulltext': r'<meta name="fulltext_pdf" content="([^"]+)"'
    }
}


def get_publisher_pdf_patterns(publisher_name: str) -> dict:
    """
    Get PDF extraction patterns for a specific publisher.

    Args:
        publisher_name: Name of the publisher (lowercase)

    Returns:
        Dictionary of regex patterns for PDF extraction
    """
    return COMMON_PDF_PATTERNS.get(publisher_name.lower(), COMMON_PDF_PATTERNS['generic'])
