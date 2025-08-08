#!/usr/bin/env python3
"""
Utility script for checking URLs using metapub's unified_uri_get function.

This script uses the same HTTP client configuration that dance functions use,
including proper headers, SSL handling, and publisher-specific settings.
"""

import sys
import os

# Add metapub to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from metapub.findit.dances.generic import unified_uri_get


def check_url(url, timeout=15, show_content=False, max_content_chars=500):
    """Check a URL using unified_uri_get and display results.
    
    Args:
        url: URL to check
        timeout: Request timeout in seconds
        show_content: Whether to show response content preview
        max_content_chars: Maximum characters to show from content
    """
    print(f"Checking URL: {url}")
    print("=" * 60)
    
    try:
        response = unified_uri_get(url, timeout=timeout, allow_redirects=True)
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
        print(f"Content-Length: {len(response.content)} bytes")
        
        # Check if it's a PDF
        is_pdf = response.content.startswith(b'%PDF') if response.content else False
        content_type_pdf = 'application/pdf' in response.headers.get('content-type', '').lower()
        
        if is_pdf:
            print("✅ ACTUAL PDF CONTENT (starts with %PDF)")
        elif content_type_pdf:
            print("✅ PDF Content-Type header")
        else:
            print("❌ NOT PDF")
            
        # Show redirects if any
        if response.history:
            print(f"Redirects: {len(response.history)}")
            for i, redirect in enumerate(response.history, 1):
                print(f"  {i}. {redirect.status_code} -> {redirect.url}")
                
        # Show content preview if requested and not PDF
        if show_content and not is_pdf and response.text:
            print(f"\nContent Preview (first {max_content_chars} chars):")
            print("-" * 40)
            preview = response.text[:max_content_chars]
            if len(response.text) > max_content_chars:
                preview += "..."
            print(preview)
            
        return response
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None


def main():
    """Command line interface for checking URLs."""
    if len(sys.argv) < 2:
        print("Usage: python check_url.py <URL> [--content] [--timeout=15]")
        print("\nOptions:")
        print("  --content    Show content preview for non-PDF responses")
        print("  --timeout=N  Set request timeout (default: 15 seconds)")
        print("\nExamples:")
        print("  python scripts/check_url.py 'https://psycnet.apa.org/fulltext/10.1037/amp0000904.pdf'")
        print("  python scripts/check_url.py 'https://example.com' --content --timeout=30")
        sys.exit(1)
    
    url = sys.argv[1]
    show_content = '--content' in sys.argv
    
    # Parse timeout
    timeout = 15
    for arg in sys.argv:
        if arg.startswith('--timeout='):
            try:
                timeout = int(arg.split('=')[1])
            except (ValueError, IndexError):
                print("Invalid timeout value")
                sys.exit(1)
    
    response = check_url(url, timeout=timeout, show_content=show_content)
    
    if response:
        print(f"\n✅ Request completed with status {response.status_code}")
    else:
        print("\n❌ Request failed")
        sys.exit(1)


if __name__ == '__main__':
    main()