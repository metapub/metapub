#!/usr/bin/env python3
"""
Batch PMID collector - automatically finds PMIDs with DOIs for ALL publishers.
Reads journal lists from registry and searches PubMed for recent articles.
"""

import sys
import time
import json
from pathlib import Path
from typing import List, Dict, Optional
from metapub import PubMedFetcher
from metapub.exceptions import MetaPubError
from metapub.findit.migrate_journals import PUBLISHER_CONFIGS

def find_pmids_for_publisher(config: Dict, max_per_journal: int = 2, years: str = "2020:2024") -> List[Dict]:
    """
    Find PMIDs with DOIs for a specific publisher.
    
    Args:
        config: Publisher configuration dict
        max_per_journal: Maximum PMIDs per journal (default: 2)
        years: Year range to search (default: 2020-2024)
    
    Returns:
        List of dicts with pmid, doi, journal, title info
    """
    fetcher = PubMedFetcher()
    results = []
    publisher_name = config['name']
    journals = config.get('journals', [])
    
    if not journals:
        print(f"  No journal list for {publisher_name}")
        return results
    
    # Sample journals - try to get a good mix
    if isinstance(journals, dict):
        # For dict-based journal configs (like AAAS), use the keys
        all_journals = list(journals.keys())
    elif isinstance(journals, (list, tuple)):
        all_journals = list(journals)
    else:
        print(f"  Unknown journal format for {publisher_name}: {type(journals)}")
        return results
    
    # For publishers with many journals, sample from different parts of the list
    # This helps avoid all old/discontinued journals at the beginning
    if len(all_journals) > 10:
        # Take some from beginning, middle, and end
        indices = [
            0,  # First
            len(all_journals)//4,  # 1/4 through
            len(all_journals)//2,  # Middle
            3*len(all_journals)//4,  # 3/4 through
            len(all_journals)-2,  # Second to last
            len(all_journals)-1   # Last
        ]
        sample_journals = []
        for i in indices:
            if 0 <= i < len(all_journals) and all_journals[i] not in sample_journals:
                sample_journals.append(all_journals[i])
        sample_journals = sample_journals[:6]
    else:
        sample_journals = all_journals[:5]
    
    
    for journal in sample_journals:
        # Build search query
        query = f'"{journal}"[Journal] AND {years}[pdat]'
        
        try:
            # Search PubMed
            pmids = fetcher.pmids_for_query(query, retmax=max_per_journal)
            
            if not pmids:
                continue
            
            # Check each PMID for DOI
            for pmid in pmids:
                try:
                    article = fetcher.article_by_pmid(pmid)
                    
                    if article.doi:
                        result = {
                            'pmid': pmid,
                            'doi': article.doi,
                            'journal': article.journal,
                            'title': article.title[:60] + '...' if len(article.title) > 60 else article.title,
                            'year': article.year
                        }
                        results.append(result)
                        
                except Exception as e:
                    continue
                
                # Be nice to NCBI
                time.sleep(0.3)
                
                # Stop if we have enough for this publisher
                if len(results) >= 10:
                    break
                    
        except Exception as e:
            continue
        
        # Stop if we have enough
        if len(results) >= 10:
            break
    
    return results

def main():
    """Main function to collect PMIDs for all publishers"""
    
    output_dir = Path("output/verified_pmids")
    
    # Track progress
    total_publishers = len(PUBLISHER_CONFIGS)
    collected = 0
    failed = 0
    
    print(f"Collecting PMIDs for {total_publishers} publishers...")
    print("This will take some time due to NCBI rate limits...")
    print("=" * 60)
    
    # Process each publisher
    for i, config in enumerate(PUBLISHER_CONFIGS, 1):
        publisher_name = config['name']
        
        # Clean name for filename
        clean_name = publisher_name.lower().replace(' ', '_').replace('&', 'and')
        clean_name = ''.join(c for c in clean_name if c.isalnum() or c == '_')
        pmid_file = output_dir / f"{clean_name}_pmids.txt"
        
        print(f"\n[{i}/{total_publishers}] {publisher_name}")
        
        # Check if already has PMIDs (skip if file has actual PMIDs)
        existing_pmids = []
        if pmid_file.exists():
            with open(pmid_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        existing_pmids.append(line)
        
        if existing_pmids:
            print(f"  Already has {len(existing_pmids)} PMIDs - skipping")
            collected += 1
            continue
        
        # Find PMIDs
        try:
            results = find_pmids_for_publisher(config)
            
            if results:
                # Read existing template
                with open(pmid_file, 'r') as f:
                    template_lines = []
                    for line in f:
                        if line.strip() and not line.strip().startswith('# Example PMIDs'):
                            template_lines.append(line)
                        else:
                            break
                
                # Write back with actual PMIDs
                with open(pmid_file, 'w') as f:
                    # Write template header
                    f.writelines(template_lines)
                    f.write("\n# COLLECTED PMIDs with verified DOIs:\n")
                    
                    # Write PMIDs
                    for result in results:
                        f.write(f"{result['pmid']}  # {result['journal']} - {result['doi']}\n")
                
                print(f"  ✓ Collected {len(results)} PMIDs with DOIs")
                collected += 1
            else:
                print(f"  ✗ No PMIDs found with DOIs")
                failed += 1
                
        except Exception as e:
            print(f"  ! Error: {e}")
            failed += 1
        
        # Progress indicator
        if i % 10 == 0:
            print(f"\n--- Progress: {i}/{total_publishers} processed ---")
            time.sleep(1)  # Extra pause every 10 publishers
    
    # Summary
    print("\n" + "=" * 60)
    print("COLLECTION SUMMARY:")
    print(f"  Total publishers: {total_publishers}")
    print(f"  Successfully collected: {collected}")
    print(f"  Failed/No results: {failed}")
    print(f"  Already had PMIDs: {total_publishers - collected - failed}")
    
    # Create summary report
    summary_file = output_dir / "collection_summary.json"
    summary = {
        "total_publishers": total_publishers,
        "collected": collected,
        "failed": failed,
        "already_had_pmids": total_publishers - collected - failed,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nSummary saved to: {summary_file}")
    print("\nNext steps:")
    print("1. Review collected PMIDs in output/verified_pmids/")
    print("2. Run verify_publisher_pmids.py to verify correctness")
    print("3. Run findit_complete_collector.py to gather HTML samples")

if __name__ == "__main__":
    main()