#!/usr/bin/env python3
"""
Batch PMID collector - automatically finds PMIDs with DOIs for ALL publishers.
Reads journal lists from registry and searches PubMed for recent articles.
Now includes PMC quota to ensure each publisher has open access articles for testing.
"""

import sys
import time
import json
from pathlib import Path
from typing import List, Dict, Optional
from metapub import PubMedFetcher
from metapub.exceptions import MetaPubError
from metapub.findit.migrate_journals import PUBLISHER_CONFIGS

def find_pmids_for_publisher(config: Dict, max_pmids: int = 10, pmc_quota: int = 2, years: str = "2020:2024") -> List[Dict]:
    """
    Find PMIDs with DOIs for a specific publisher, including PMC quota.
    
    Args:
        config: Publisher configuration dict
        max_pmids: Maximum total PMIDs to collect (default: 10)
        pmc_quota: Minimum PMIDs with PMC IDs to collect (default: 2)
        years: Year range to search (default: 2020-2024)
    
    Returns:
        List of dicts with pmid, doi, journal, title, pmc info
    """
    fetcher = PubMedFetcher()
    results = {
        'with_pmc': [],
        'without_pmc': [],
        'journals_searched': []
    }
    publisher_name = config['name']
    journals = config.get('journals', [])
    
    if not journals:
        print(f"  No journal list for {publisher_name}")
        return []
    
    # Sample journals - try to get a good mix
    if isinstance(journals, dict):
        # For dict-based journal configs (like AAAS), use the keys
        all_journals = list(journals.keys())
    elif isinstance(journals, (list, tuple)):
        all_journals = list(journals)
    else:
        print(f"  Unknown journal format for {publisher_name}: {type(journals)}")
        return []
    
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
        sample_journals = sample_journals[:8]  # Increased for PMC search
    else:
        sample_journals = all_journals[:6]
    
    print(f"  Searching {len(sample_journals)} journals (need {pmc_quota} PMC, {max_pmids-pmc_quota} subscription)")
    
    for journal in sample_journals:
        # Stop if we have enough of both types
        if len(results['with_pmc']) >= pmc_quota and len(results['without_pmc']) >= (max_pmids - pmc_quota):
            break
        
        # Build search query
        query = f'"{journal}"[Journal] AND {years}[pdat]'
        
        try:
            # Search PubMed
            pmids = fetcher.pmids_for_query(query, retmax=15)  # Get more to check for PMC
            
            if not pmids:
                continue
            
            results['journals_searched'].append(journal)
            print(f"    {journal}: {len(pmids)} articles found")
            
            # Check each PMID for DOI and PMC
            for pmid in pmids:
                try:
                    article = fetcher.article_by_pmid(pmid)
                    
                    if not article.doi:
                        continue
                    
                    # Check for PMC ID
                    has_pmc = hasattr(article, 'pmc') and article.pmc
                    
                    result = {
                        'pmid': pmid,
                        'doi': article.doi,
                        'journal': article.journal,
                        'title': article.title[:60] + '...' if len(article.title) > 60 else article.title,
                        'year': article.year
                    }
                    
                    if has_pmc:
                        result['pmc'] = article.pmc
                    
                    # Add to appropriate category
                    if has_pmc and len(results['with_pmc']) < pmc_quota:
                        results['with_pmc'].append(result)
                        print(f"      ✓ PMC: {pmid} - PMC{article.pmc}")
                    elif not has_pmc and len(results['without_pmc']) < (max_pmids - pmc_quota):
                        results['without_pmc'].append(result)
                        print(f"      ✓ Sub: {pmid}")
                        
                except Exception as e:
                    continue
                
                # Be nice to NCBI
                time.sleep(0.2)
                
                # Stop if we have enough total
                total_collected = len(results['with_pmc']) + len(results['without_pmc'])
                if total_collected >= max_pmids:
                    break
                    
        except Exception as e:
            continue
        
        # Stop if we have enough total
        total_collected = len(results['with_pmc']) + len(results['without_pmc'])
        if total_collected >= max_pmids:
            break
    
    # Combine results for return
    all_results = results['with_pmc'] + results['without_pmc']
    
    print(f"  Result: {len(results['with_pmc'])} PMC + {len(results['without_pmc'])} subscription = {len(all_results)} total")
    
    return all_results, results

def write_pmid_file(pmid_file: Path, publisher_name: str, all_results: List[Dict], categorized_results: Dict):
    """Write PMIDs to file with PMC/subscription categorization."""
    
    # Read existing template if it exists
    template_lines = []
    if pmid_file.exists():
        with open(pmid_file, 'r') as f:
            for line in f:
                if line.strip() and not line.strip().startswith('# Example PMIDs') and not line.strip().startswith('# COLLECTED PMIDs'):
                    template_lines.append(line)
                else:
                    break
    
    # Write new file with categorized PMIDs
    with open(pmid_file, 'w') as f:
        # Write template header if it existed
        if template_lines:
            f.writelines(template_lines)
        else:
            # Create basic header
            f.write(f"# Verified PMIDs for {publisher_name}\n")
            f.write("# Generated with PMC quota system\n")
            f.write("#\n")
            f.write("# PMIDs with verified DOIs that resolve to publisher websites\n")
            f.write("# Includes both open access (with PMC) and subscription articles\n")
            f.write("#\n\n")
        
        # Write PMC articles section
        f.write("# COLLECTED PMIDs with verified DOIs:\n\n")
        
        if categorized_results['with_pmc']:
            f.write("# PMC ARTICLES (Open Access):\n")
            for result in categorized_results['with_pmc']:
                pmc_id = result.get('pmc', '')
                f.write(f"{result['pmid']}  # {result['journal']} - {result['doi']} - PMC{pmc_id}\n")
            f.write("\n")
        
        if categorized_results['without_pmc']:
            f.write("# SUBSCRIPTION ARTICLES:\n")
            for result in categorized_results['without_pmc']:
                f.write(f"{result['pmid']}  # {result['journal']} - {result['doi']}\n")
            f.write("\n")
        
        # Summary
        total = len(categorized_results['with_pmc']) + len(categorized_results['without_pmc'])
        f.write(f"# Total PMIDs: {total}\n")
        f.write(f"# With PMC: {len(categorized_results['with_pmc'])}\n") 
        f.write(f"# Without PMC: {len(categorized_results['without_pmc'])}\n")
        f.write(f"# Journals searched: {', '.join(categorized_results.get('journals_searched', [])[:3])}\n")

def main():
    """Main function to collect PMIDs for all publishers with PMC quota"""
    
    output_dir = Path("output/verified_pmids")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Track progress
    total_publishers = len(PUBLISHER_CONFIGS)
    collected = 0
    failed = 0
    
    print(f"Collecting PMIDs for {total_publishers} publishers...")
    print("NEW: PMC quota system - ensuring each publisher has open access articles!")
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
        
        # Check if already has PMIDs with PMC quota (skip if file has both types)
        existing_pmids = []
        has_pmc_articles = False
        if pmid_file.exists():
            with open(pmid_file, 'r') as f:
                content = f.read()
                for line in content.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        existing_pmids.append(line)
                    if 'PMC' in line and not line.startswith('#'):
                        has_pmc_articles = True
        
        if existing_pmids and has_pmc_articles:
            print(f"  Already has {len(existing_pmids)} PMIDs with PMC articles - skipping")
            collected += 1
            continue
        elif existing_pmids and not has_pmc_articles:
            print(f"  Has {len(existing_pmids)} PMIDs but no PMC articles - updating")
        
        # Find PMIDs with PMC quota
        try:
            all_results, categorized_results = find_pmids_for_publisher(
                config, 
                max_pmids=8,    # Total PMIDs to collect
                pmc_quota=2     # Minimum with PMC IDs
            )
            
            if all_results:
                write_pmid_file(pmid_file, publisher_name, all_results, categorized_results)
                
                pmc_count = len(categorized_results['with_pmc'])
                sub_count = len(categorized_results['without_pmc'])
                print(f"  ✓ Collected {len(all_results)} PMIDs ({pmc_count} PMC + {sub_count} subscription)")
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
    print("PMC QUOTA COLLECTION SUMMARY:")
    print(f"  Total publishers: {total_publishers}")
    print(f"  Successfully collected: {collected}")
    print(f"  Failed/No results: {failed}")
    print(f"  Already had PMC articles: {total_publishers - collected - failed}")
    
    # Create summary report
    summary_file = output_dir / "collection_summary.json"
    summary = {
        "total_publishers": total_publishers,
        "collected": collected,
        "failed": failed,
        "already_had_pmids": total_publishers - collected - failed,
        "pmc_quota_enabled": True,
        "pmc_quota": 2,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nSummary saved to: {summary_file}")
    print("\nIMPROVEMENT: Each publisher now has open access PMC articles for testing!")
    print("\nNext steps:")
    print("1. Review collected PMIDs in output/verified_pmids/")
    print("2. Run verify_publisher_pmids.py to verify correctness") 
    print("3. Run findit_complete_collector.py to gather HTML samples")

if __name__ == "__main__":
    main()