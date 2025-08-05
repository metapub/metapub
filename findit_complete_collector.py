#!/usr/bin/env python3
"""
Complete findit data collector - 100% coverage of supported publishers.
Uses the PUBLISHER_CONFIGS directly to avoid registry auto-population delays.
Aggressive HTML fetching that bypasses access restrictions.
"""

import os
import sys
import csv
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from metapub import PubMedFetcher
from metapub.dx_doi import DxDOI
from metapub.findit.dances.generic import unified_uri_get

# Import publisher configs directly
from metapub.findit.migrate_journals import PUBLISHER_CONFIGS


def should_skip_publisher(config: Dict) -> bool:
    """Skip publishers using vip_shake, doi_2step methods and open access."""
    dance_function = config['dance_function']
    name = config['name'].lower()

    # Skip vip_shake and doi_slide methods
    if dance_function in ['the_vip_shake', 'the_doi_slide']:
        return True

    # Skip fully open-access publishers per user request
    skip_names = [
        'public library of science',  # PLoS
        'bmc',                       # BMC
    ]

    for skip_name in skip_names:
        if skip_name in name:
            return True

    return False


def get_pmids_for_publisher(publisher_name: str, count: int = 5, min_year: int = 2000) -> List[str]:
    """Get PMIDs for a publisher from data directories.
    
    Args:
        publisher_name: Name of the publisher
        count: Number of PMIDs to return
        min_year: Minimum publication year to consider (default: 2000)
    """
    pmids = []

    # Map publisher names to file patterns
    name_mappings = {
        'springer': ['springer', 'bmc'],
        'nature': ['nature'],
        'wiley': ['wiley'],
        'sciencedirect': ['sciencedirect'],
        'cambridge university press': ['cambridge'],
        'karger': ['karger'],
        'sage publications': ['sage'],
        'american association for cancer research': ['aacrjournals'],
        'american heart association': ['ahajournals'],
        'cancer biology & medicine': ['cancerbiomed'],
        'mdpi': ['mdpi'],
        'dovepress': ['dovepress'],
        'frontiers': ['frontiers'],
    }

    # Check publishers_clean directory first
    publishers_dir = Path("output/publishers_clean")
    name_lower = publisher_name.lower()

    for txt_file in publishers_dir.glob("*.txt"):
        if txt_file.name in ["DOISerbia.txt", "JSTOR.txt", "Unknown_PMIDs.txt"]:
            continue

        file_base = txt_file.stem.replace("_PMIDs", "").lower().replace("_", " ")

        # Check direct matches or mapped names
        matches = name_mappings.get(name_lower, [name_lower])
        if any(match in file_base or file_base in match for match in matches):
            with open(txt_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        pmids.append(line)
            break

    # If not found, do comprehensive journal cluster search
    if not pmids:
        clusters_dir = Path("output/journal_clusters_todo")
        
        # Comprehensive domain mappings for ALL publishers
        domain_mappings = {
            'american association for cancer research': ['aacrjournals'],
            'american heart association': ['ahajournals'],
            'cancer biology & medicine': ['cancerbiomed'],
            'jama': ['jamanetwork'],
            'dovepress': ['dovepress'],
            'mdpi': ['mdpi'],
            'frontiers': ['frontiersin', 'kids.frontiersin'],
            'nature': ['nature'],
            'springer': ['springer'],
            'wiley': ['wiley'],
            'sage publications': ['sage'],
            'eurekaselect': ['eurekaselect.com'],
            'apa': ['psycnet', 'apa'],
            'iop': ['iopscience', 'iop'],
            'scirp': ['scirp'],
            'annualreviews': ['annualreviews.org'],
            'brill': ['brill.com'],
            'rsc': ['rsc'],
            'ingentaconnect': ['ingentaconnect'],
            'bioone': ['bioone.org'],
            'emerald': ['emerald.com'],
            'acm': ['dl.acm.org', 'dl.acm', 'acm'],
            'worldscientific': ['worldscientific.com', 'worldscientific'],
            'uchicago': ['uchicago.edu', 'uchicago'],
            'iospress': ['iospress'],
            'longdom': ['longdom.org', 'longdom'],
            'oatext': ['oatext.com', 'oatext'],
            'allenpress': ['allenpress'],
            'inderscience': ['inderscience.com', 'inderscience'],
            'asme': ['asmedigitalcollection', 'asme'],
            'wjgnet': ['wjgnet.com', 'wjgnet'],
            'hilaris': ['hilarispublisher.com', 'hilaris'],
            'projectmuse': ['muse.jhu.edu', 'muse.jhu', 'projectmuse'],
            'walshmedia': ['walshmedicalmedia.com', 'walshmedia'],
            'aip': ['aip.scitation.org', 'aip'],
            'sciendo': ['sciendo'],
            'najms': ['najms.com', 'najms'],
            'degruyter': ['degruyter'],
            'dustri': ['dustri'],
            'schattauer': ['schattauer.de', 'schattauer'],
            'thieme medical publishers': ['thieme'],
            'jci': ['jci.org', 'jci'],
            'cell': ['cell.com', 'cell'],
            'endo': ['endocrine.org', 'endocrine'],
            'lancet': ['thelancet.com', 'lancet'],
            'scielo': ['scielo.org', 'scielo.br', 'scielo'],
            'spandidos': ['spandidos'],
            'wolterskluwer': ['lww'],
            'biochemsoc': ['biochemsoc.org', 'portlandpress.com', 'biochemsoc'],
            'aaas': ['science.org', 'science'],
            'jstage': ['jstage'],
            'karger': ['karger.com', 'karger'],
            'sciencedirect': ['sciencedirect.com', 'sciencedirect'],
            'asce': ['ascelibrary.org', 'ascelibrary'],
            'siam': ['epubs.siam.org', 'siam'],
        }
        
        # First try exact domain matches
        search_domains = domain_mappings.get(name_lower, [])
        
        # If no exact match, try fuzzy matching with publisher name parts
        if not search_domains:
            name_parts = name_lower.replace('university press', '').replace('publishing', '').replace('publishers', '').strip().split()
            search_domains = [part for part in name_parts if len(part) > 3]  # Skip short words like "the", "of"
        
        # Search through all journal cluster files
        found_match = False
        
        # First try exact filename matches
        for search_domain in search_domains:
            exact_file = clusters_dir / f"{search_domain}.json"
            if exact_file.exists() and not exact_file.name.startswith("_"):
                try:
                    with open(exact_file, 'r') as f:
                        data = json.load(f)
                    
                    if isinstance(data, list):
                        continue
                        
                    for journal in data.get("journals", []):
                        pmids.extend(journal.get("pmids", []))
                    found_match = True
                    print(f"    Found {len(pmids)} PMIDs in {exact_file.name}")
                    break
                        
                except (json.JSONDecodeError, KeyError, TypeError):
                    continue
        
        # If no exact match, try fuzzy matching
        if not found_match:
            for json_file in clusters_dir.glob("*.json"):
                if json_file.name.startswith("_"):
                    continue
                    
                domain = json_file.stem.lower()
                
                # Check if any search domain matches this file's domain
                domain_match = False
                for search_domain in search_domains:
                    if search_domain in domain or domain in search_domain:
                        domain_match = True
                        break
                
                if domain_match:
                    try:
                        with open(json_file, 'r') as f:
                            data = json.load(f)
                    
                        if isinstance(data, list):
                            continue
                            
                        for journal in data.get("journals", []):
                            pmids.extend(journal.get("pmids", []))
                        found_match = True
                        print(f"    Found {len(pmids)} PMIDs in {json_file.name}")
                        break
                            
                    except (json.JSONDecodeError, KeyError, TypeError):
                        continue

    # Select diverse PMIDs, preferring newer ones that are more likely to have DOIs
    if len(pmids) <= count:
        # Sort by PMID (descending) to prioritize newer articles
        return sorted(pmids, key=int, reverse=True)

    # Sort numerically (descending) for temporal ordering - newer PMIDs first
    sorted_pmids = sorted(pmids, key=int, reverse=True)

    # For recent articles, take the newest ones
    # Older PMIDs (< 15000000, roughly pre-2005) are more likely to lack DOIs
    recent_pmids = [p for p in sorted_pmids if int(p) >= 15000000]
    older_pmids = [p for p in sorted_pmids if int(p) < 15000000]

    selected = []
    
    # Prefer recent PMIDs
    if len(recent_pmids) >= count:
        # Take evenly spaced recent PMIDs
        step = max(1, len(recent_pmids) // count)
        for i in range(count):
            idx = min(i * step, len(recent_pmids) - 1)
            selected.append(recent_pmids[idx])
    else:
        # Take all recent PMIDs and fill with older ones
        selected.extend(recent_pmids)
        remaining = count - len(recent_pmids)
        if older_pmids and remaining > 0:
            # Add some older PMIDs if needed
            step = max(1, len(older_pmids) // remaining)
            for i in range(remaining):
                idx = min(i * step, len(older_pmids) - 1)
                selected.append(older_pmids[idx])

    return selected[:count]


def fetch_html_aggressively(url: str, timeout: int = 15) -> Tuple[bool, str, int]:
    """Fetch HTML content aggressively, bypassing access restrictions."""
    import requests
    import ssl
    import certifi

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0',
    }

    session = requests.Session()
    session.headers.update(headers)

    try:
        # First try with unified_uri_get (respects existing patterns)
        try:
            result = unified_uri_get(url, timeout=timeout)
            if result and result.text and len(result.text) > 100:
                status_code = getattr(result, 'status_code', 200)
                return True, result.text, status_code
        except:
            pass

        # Try with proper SSL verification first
        try:
            response = session.get(url, timeout=timeout, allow_redirects=True, verify=certifi.where())
            
            # Accept any response that looks like HTML
            text = response.text
            if text and len(text) > 100:
                # Look for HTML indicators
                text_lower = text.lower()[:2000]
                if any(indicator in text_lower for indicator in ['<html', '<!doctype', '<title>', '<head>', '<body>']):
                    return True, text, response.status_code
            return False, "", response.status_code
        except (requests.exceptions.SSLError, ssl.SSLError):
            # If SSL verification fails, try without verification as fallback
            try:
                response = session.get(url, timeout=timeout, allow_redirects=True, verify=False)
                
                text = response.text
                if text and len(text) > 100:
                    text_lower = text.lower()[:2000]
                    if any(indicator in text_lower for indicator in ['<html', '<!doctype', '<title>', '<head>', '<body>']):
                        return True, text, response.status_code
                return False, "", response.status_code
            except Exception as e:
                return False, "", 0
        except Exception as e:
            # Any other error, try without verification
            try:
                response = session.get(url, timeout=timeout, allow_redirects=True, verify=False)
                
                text = response.text
                if text and len(text) > 100:
                    text_lower = text.lower()[:2000]
                    if any(indicator in text_lower for indicator in ['<html', '<!doctype', '<title>', '<head>', '<body>']):
                        return True, text, response.status_code
                return False, "", response.status_code
            except Exception as e:
                return False, "", 0

        return False, "", 0

    except Exception as e:
        return False, "", 0


def process_pmid_aggressive(pmid: str, publisher_name: str, fetch: PubMedFetcher, dx_doi: DxDOI) -> Tuple[str, str, str, bool, str, int]:
    """Process a single PMID with aggressive HTML fetching."""
    try:
        art = fetch.article_by_pmid(pmid)
        if not art.doi:
            print(f"    {pmid}: ⚠️  No DOI available")
            return pmid, "", "", False, "", 0

        # Resolve DOI to article URL
        article_url = dx_doi.resolve(art.doi)
        if not article_url:
            return pmid, art.doi, "", False, "", 0

        # Check if HTML file already exists and determine if we should skip
        safe_publisher = "".join(c for c in publisher_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_publisher = safe_publisher.replace(' ', '_').lower()
        html_dir = Path(f"output/article_html/{safe_publisher}")
        html_file = html_dir / f"{pmid}.html"
        html_filename = f"{safe_publisher}/{pmid}.html"

        # Check if file exists and is non-empty (indicates successful previous download)
        if html_file.exists() and html_file.stat().st_size > 1000:
            print(f"    {pmid}: ⏭️  (already downloaded)")
            return pmid, art.doi, article_url, True, html_filename, 200

        # Fetch HTML aggressively
        success, html_content, status_code = fetch_html_aggressively(article_url)

        if success and html_content:
            # Save HTML file
            html_dir.mkdir(parents=True, exist_ok=True)
            
            with open(html_file, 'w', encoding='utf-8', errors='ignore') as f:
                f.write(html_content)
        else:
            html_filename = ""

        return pmid, art.doi, article_url, success, html_filename, status_code

    except Exception as e:
        return pmid, "", "", False, "", 0


def main():
    """Main execution function."""
    print("Starting COMPLETE findit publisher coverage collection...")
    print("Targeting ALL supported publishers with aggressive HTML fetching...")

    # Initialize services
    fetch = PubMedFetcher()
    dx_doi = DxDOI()

    # Filter publishers from configs
    target_publishers = [p for p in PUBLISHER_CONFIGS if not should_skip_publisher(p)]
    skipped_count = len(PUBLISHER_CONFIGS) - len(target_publishers)

    print(f"Total publishers in registry: {len(PUBLISHER_CONFIGS)}")
    print(f"Targeting: {len(target_publishers)} publishers")
    print(f"Skipped: {skipped_count} (vip_shake, doi_slide methods + open access)")

    # Show what we're targeting
    print("\nTargeted publishers:")
    for p in target_publishers:
        print(f"  - {p['name']} ({p['dance_function']})")

    # Prepare output
    results = []
    output_file = Path("output/findit_complete_coverage_results.csv")

    total_processed = 0
    total_successful = 0

    print("\nStarting collection...")

    # Process each publisher
    for i, config in enumerate(target_publishers, 1):
        pub_name = config['name']
        dance_func = config['dance_function']

        print(f"\n[{i}/{len(target_publishers)}] {pub_name}")
        print(f"  Dance: {dance_func}")

        # Get PMIDs for this publisher
        pmids = get_pmids_for_publisher(pub_name, count=5)

        if not pmids:
            print(f"  ⚠️  No PMIDs found for {pub_name}")
            continue

        print(f"  Processing {len(pmids)} PMIDs...")

        # Process each PMID
        publisher_success = 0
        for pmid in pmids:
            row = process_pmid_aggressive(pmid, pub_name, fetch, dx_doi)
            results.append(row)
            total_processed += 1

            if row[3]:  # article_resolved
                total_successful += 1
                publisher_success += 1
                status_code = row[5]
                if status_code == 200:
                    print(f"    {pmid}: ✅ (HTTP {status_code})")
                else:
                    print(f"    {pmid}: ✅ (HTTP {status_code})")
            else:
                status_code = row[5]
                print(f"    {pmid}: ❌ (HTTP {status_code})")

        print(f"  Publisher success: {publisher_success}/{len(pmids)}")

        # Small delay to be considerate
        time.sleep(0.3)

    # Write results
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['pmid', 'doi', 'article_url', 'article_resolved', 'HTML_file', 'status_code'])
        writer.writerows(results)

    # Final summary
    success_rate = (total_successful / total_processed * 100) if total_processed > 0 else 0

    print(f"\n{'='*50}")
    print(f"COMPLETE COVERAGE COLLECTION SUMMARY")
    print(f"{'='*50}")
    print(f"Publishers targeted: {len(target_publishers)}")
    print(f"PMIDs processed: {total_processed}")
    print(f"HTML files retrieved: {total_successful}")
    print(f"Overall success rate: {success_rate:.1f}%")
    print(f"Results saved to: {output_file}")
    print(f"HTML files saved to: output/article_html/[publisher]/")


if __name__ == "__main__":
    main()
