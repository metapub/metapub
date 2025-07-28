#!/usr/bin/env python3
"""
NCBI Service Health Check Utility

A command-line tool to check the status of various NCBI services used by metapub.
Helps diagnose service outages and determine which endpoints are affected.

Usage:
    python ncbi_health_check.py          # Check all services
    python ncbi_health_check.py --quick  # Check only essential services
    python ncbi_health_check.py --json   # Output results as JSON
"""

import argparse
import json
import sys
import time
from dataclasses import dataclass
from typing import Dict, List, Optional

import requests
from lxml import etree

from .eutils_common import get_eutils_client
from .cache_utils import get_cache_path
from .config import API_KEY


@dataclass
class ServiceResult:
    """Result of checking a single NCBI service."""
    name: str
    url: str
    status: str  # 'up', 'down', 'slow', 'error'
    response_time: float
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    details: Optional[str] = None


class NCBIHealthChecker:
    """Health checker for NCBI services."""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        # Use existing eutils client with proper rate limiting and API key support
        cache_path = get_cache_path('ncbi_health_check.db')
        self.eutils_client = get_eutils_client(cache_path, cache=False)  # No cache for health checks
        self.services = {
            'efetch': {
                'name': 'EFetch (PubMed Articles)',
                'method': 'eutils',
                'eutils_method': 'efetch',
                'params': {'db': 'pubmed', 'id': '123456'},
                'essential': True
            },
            'esearch': {
                'name': 'ESearch (PubMed Search)',
                'method': 'eutils',
                'eutils_method': 'esearch',
                'params': {'db': 'pubmed', 'term': 'cancer[title]', 'retmax': '1'},
                'essential': True
            },
            'elink': {
                'name': 'ELink (Related Articles)',
                'method': 'eutils',
                'eutils_method': 'elink',
                'params': {'dbfrom': 'pubmed', 'db': 'pubmed', 'id': '123456'},
                'essential': True
            },
            'esummary': {
                'name': 'ESummary (Article Summaries)',
                'method': 'eutils',
                'eutils_method': 'esummary',
                'params': {'db': 'pubmed', 'id': '123456'},
                'essential': True
            },
            'einfo': {
                'name': 'EInfo (Database Info)',
                'method': 'eutils',
                'eutils_method': 'einfo',
                'params': {'db': 'pubmed'},
                'essential': False
            },
            'medgen_search': {
                'name': 'MedGen Search',
                'method': 'eutils',
                'eutils_method': 'esearch',
                'params': {'db': 'medgen', 'term': 'diabetes', 'retmax': '1'},
                'essential': False
            },
            'pmc_fetch': {
                'name': 'PMC Article Fetch',
                'method': 'eutils',
                'eutils_method': 'efetch',
                'params': {'db': 'pmc', 'id': '123456'},
                'essential': False
            },
            'books_search': {
                'name': 'NCBI Books Search',
                'method': 'eutils',
                'eutils_method': 'esearch',
                'params': {'db': 'books', 'term': 'genetics', 'retmax': '1'},
                'essential': False
            },
            'ncbi_main': {
                'name': 'NCBI Main Website',
                'method': 'http',
                'url': 'https://www.ncbi.nlm.nih.gov/',
                'essential': False
            }
        }

    def check_service(self, service_id: str, config: dict) -> ServiceResult:
        """Check a single NCBI service."""
        start_time = time.time()
        
        try:
            if config['method'] == 'eutils':
                # Use eutils client with built-in rate limiting and API key support
                eutils_method = getattr(self.eutils_client, config['eutils_method'])
                result = eutils_method(config['params'])
                
                response_time = time.time() - start_time
                
                # Check if we got valid XML response
                if result is None or len(result) == 0:
                    return ServiceResult(
                        name=config['name'],
                        url=f"eutils:{config['eutils_method']}",
                        status='down',
                        response_time=response_time,
                        error_message="Empty response from eutils"
                    )
                
                # Try to parse XML to ensure it's valid
                try:
                    root = etree.fromstring(result)
                    # Check for error messages in XML
                    error_elem = root.find('.//ERROR')
                    if error_elem is not None:
                        return ServiceResult(
                            name=config['name'],
                            url=f"eutils:{config['eutils_method']}",
                            status='error',
                            response_time=response_time,
                            error_message=f"API error: {error_elem.text}"
                        )
                except etree.XMLSyntaxError as e:
                    return ServiceResult(
                        name=config['name'],
                        url=f"eutils:{config['eutils_method']}",
                        status='error',
                        response_time=response_time,
                        error_message=f"Invalid XML response: {str(e)}"
                    )
                
                # Service is up
                status = 'slow' if response_time > 5.0 else 'up'
                api_key_status = " (with API key)" if API_KEY else " (no API key)"
                details = f"Response time: {response_time:.2f}s{api_key_status}"
                
                return ServiceResult(
                    name=config['name'],
                    url=f"eutils:{config['eutils_method']}",
                    status=status,
                    response_time=response_time,
                    status_code=200,  # eutils success
                    details=details
                )
                
            elif config['method'] == 'http':
                # Direct HTTP check for non-eutils services
                response = requests.get(
                    config['url'],
                    timeout=self.timeout,
                    headers={'User-Agent': 'metapub-health-check/1.0'}
                )
                
                response_time = time.time() - start_time
                
                if response.status_code >= 500:
                    return ServiceResult(
                        name=config['name'],
                        url=config['url'],
                        status='down',
                        response_time=response_time,
                        status_code=response.status_code,
                        error_message=f"Server error: {response.status_code} {response.reason}"
                    )
                
                if response.status_code >= 400:
                    return ServiceResult(
                        name=config['name'],
                        url=config['url'],
                        status='error',
                        response_time=response_time,
                        status_code=response.status_code,
                        error_message=f"Client error: {response.status_code} {response.reason}"
                    )
                
                # Service is up
                status = 'slow' if response_time > 5.0 else 'up'
                details = f"Response time: {response_time:.2f}s"
                
                return ServiceResult(
                    name=config['name'],
                    url=config['url'],
                    status=status,
                    response_time=response_time,
                    status_code=response.status_code,
                    details=details
                )
                
        except requests.exceptions.Timeout:
            return ServiceResult(
                name=config['name'],
                url=config.get('url', f"eutils:{config.get('eutils_method', 'unknown')}"),
                status='down',
                response_time=self.timeout,
                error_message=f"Timeout after {self.timeout}s"
            )
        except requests.exceptions.ConnectionError as e:
            return ServiceResult(
                name=config['name'],
                url=config.get('url', f"eutils:{config.get('eutils_method', 'unknown')}"),
                status='down',
                response_time=time.time() - start_time,
                error_message=f"Connection error: {str(e)}"
            )
        except Exception as e:
            return ServiceResult(
                name=config['name'],
                url=config.get('url', f"eutils:{config.get('eutils_method', 'unknown')}"),
                status='error',
                response_time=time.time() - start_time,
                error_message=f"Unexpected error: {str(e)}"
            )

    def check_all_services(self, quick: bool = False) -> List[ServiceResult]:
        """Check all services concurrently."""
        services_to_check = {
            k: v for k, v in self.services.items()
            if not quick or v.get('essential', False)
        }
        
        results = []
        
        # Use concurrent execution since eutils client handles rate limiting
        from concurrent.futures import ThreadPoolExecutor, as_completed
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_service = {
                executor.submit(self.check_service, service_id, config): service_id
                for service_id, config in services_to_check.items()
            }
            
            for future in as_completed(future_to_service):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    service_id = future_to_service[future]
                    config = services_to_check[service_id]
                    results.append(ServiceResult(
                        name=config['name'],
                        url=config['url'],
                        status='error',
                        response_time=0.0,
                        error_message=f"Check failed: {str(e)}"
                    ))
        
        return sorted(results, key=lambda x: x.name)


def print_status_icon(status: str) -> str:
    """Get emoji/icon for status."""
    icons = {
        'up': '✅',
        'slow': '🐌',
        'down': '❌',
        'error': '⚠️'
    }
    return icons.get(status, '❓')


def print_results(results: List[ServiceResult], show_details: bool = True):
    """Print results in human-readable format."""
    print("\n" + "="*80)
    print("🏥 NCBI SERVICE HEALTH CHECK REPORT")
    print("="*80)
    
    # Summary counts
    status_counts = {}
    for result in results:
        status_counts[result.status] = status_counts.get(result.status, 0) + 1
    
    print(f"\n📊 SUMMARY: {len(results)} services checked")
    for status, count in sorted(status_counts.items()):
        icon = print_status_icon(status)
        print(f"   {icon} {status.upper()}: {count}")
    
    # Detailed results
    print(f"\n📋 DETAILED RESULTS:")
    print("-" * 80)
    
    for result in results:
        icon = print_status_icon(result.status)
        print(f"{icon} {result.name}")
        print(f"   URL: {result.url}")
        print(f"   Status: {result.status.upper()}")
        
        if result.status_code:
            print(f"   HTTP: {result.status_code}")
        
        print(f"   Response Time: {result.response_time:.2f}s")
        
        if result.error_message:
            print(f"   Error: {result.error_message}")
        
        if result.details and show_details:
            print(f"   Details: {result.details}")
        
        print()
    
    # Overall assessment
    critical_down = any(r.status in ['down', 'error'] and 
                       r.name.startswith(('EFetch', 'ESearch')) 
                       for r in results)
    
    if critical_down:
        print("🚨 CRITICAL: Core PubMed services are down. Tests will likely fail.")
        print("   Consider using FORCE_NETWORK_TESTS=1 only if you need to debug specific issues.")
    elif any(r.status == 'down' for r in results):
        print("⚠️  WARNING: Some services are down, but core functionality may still work.")
    elif any(r.status == 'slow' for r in results):
        print("🐌 NOTICE: Some services are responding slowly. Tests may take longer.")
    else:
        print("✅ ALL GOOD: All services are responding normally.")
    
    print("\n" + "="*80)


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Check NCBI service health for metapub testing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ncbi_health_check.py              # Check all services
  python ncbi_health_check.py --quick      # Check only essential services  
  python ncbi_health_check.py --json       # JSON output for scripts
  python ncbi_health_check.py --timeout 30 # Longer timeout for slow networks
        """
    )
    
    parser.add_argument(
        '--quick', 
        action='store_true',
        help='Check only essential services (faster)'
    )
    parser.add_argument(
        '--json', 
        action='store_true',
        help='Output results as JSON'
    )
    parser.add_argument(
        '--timeout', 
        type=int, 
        default=10,
        help='Request timeout in seconds (default: 10)'
    )
    parser.add_argument(
        '--no-details',
        action='store_true', 
        help='Hide detailed information'
    )
    
    args = parser.parse_args()
    
    if not args.json:
        print("🔍 Checking NCBI service health...")
        if args.quick:
            print("   (Quick mode: essential services only)")
    
    checker = NCBIHealthChecker(timeout=args.timeout)
    results = checker.check_all_services(quick=args.quick)
    
    if args.json:
        # JSON output for programmatic use
        json_results = []
        for result in results:
            json_results.append({
                'name': result.name,
                'url': result.url,
                'status': result.status,
                'response_time': result.response_time,
                'status_code': result.status_code,
                'error_message': result.error_message,
                'details': result.details
            })
        
        output = {
            'timestamp': time.time(),
            'summary': {
                'total': len(results),
                'up': sum(1 for r in results if r.status == 'up'),
                'slow': sum(1 for r in results if r.status == 'slow'),
                'down': sum(1 for r in results if r.status == 'down'),
                'error': sum(1 for r in results if r.status == 'error')
            },
            'services': json_results
        }
        
        print(json.dumps(output, indent=2))
    else:
        print_results(results, show_details=not args.no_details)
    
    # Exit with appropriate code
    if any(r.status in ['down', 'error'] for r in results):
        sys.exit(1)  # Some services are down
    elif any(r.status == 'slow' for r in results):
        sys.exit(2)  # Some services are slow
    else:
        sys.exit(0)  # All good


if __name__ == '__main__':
    main()