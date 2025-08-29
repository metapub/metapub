#!/usr/bin/env python3
"""
Categorize unknown journals by likelihood of PDF retrieval success.

Reads from output/FINDIT_TODO/unknown_publishers_clean.txt and categorizes journals
into HIGH, MEDIUM, and LOW likelihood based on:
- HIGH: Journals with domains that host multiple journals (patterns likely)
- MEDIUM: Journals with domains but appear to be one-off journals
- LOW: Journals with no domain from DOI resolution

Output: organized file with journals grouped by likelihood, HIGH at top.
Uses ALL PMIDs, not samples.
"""

import os
import sys
import csv
import tempfile
from collections import defaultdict, Counter
from urllib.parse import urlparse
from pathlib import Path

# Add metapub to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from metapub.findit.journals import get_supported_journals


def load_unknown_journals_csv(file_path):
    """Load journal data from unknown_publishers_clean.txt CSV file."""
    journals_data = []
    
    try:
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                journals_data.append({
                    'pmid': row['PMID'],
                    'journal': row['Journal'],
                    'doi': row['doi'] if row['doi'] else None,
                    'doi_url': row['doi_url'] if row['doi_url'] else None,
                    'domain': row['domain'] if row['domain'] else None,
                    'year': row['year'] if row['year'] else None
                })
    except FileNotFoundError:
        print(f"Error: {file_path} not found")
        return []
    
    print(f"Loaded {len(journals_data)} journal entries from {file_path}")
    return journals_data


def group_by_journal(journals_data):
    """Group entries by journal name."""
    journal_groups = defaultdict(list)
    
    for entry in journals_data:
        journal = entry['journal']
        journal_groups[journal].append(entry)
    
    return dict(journal_groups)


def analyze_journal_group(journal, entries):
    """Analyze a group of entries for the same journal to determine likelihood."""
    
    # Collect all domains from DOI resolution for this journal
    domains = []
    pmids = []
    entries_with_domains = []
    
    for entry in entries:
        pmids.append(entry['pmid'])
        if entry['domain']:
            domains.append(entry['domain'])
            entries_with_domains.append(entry)
    
    # Determine likelihood based on domain analysis
    if not domains:
        # No domains from DOI resolution
        return 'LOW', {
            'reason': 'No domain from DOI resolution',
            'pmids': pmids,
            'total_entries': len(entries),
            'domains': []
        }
    
    # Count domain occurrences
    domain_counter = Counter(domains)
    most_common_domain = domain_counter.most_common(1)[0][0] if domains else None
    
    # Known multi-journal publisher patterns
    multi_journal_indicators = [
        'springer', 'wiley', 'elsevier', 'tandfonline', 'sagepub', 
        'journals.', 'academic', 'publishing', 'press', 'science',
        'nature', 'cell', 'karger', 'thieme', 'cambridge', 'oxford',
        'biomedcentral', 'hindawi', 'frontiersin', 'mdpi', 'plos'
    ]
    
    is_likely_multi_journal = any(indicator in most_common_domain for indicator in multi_journal_indicators) if most_common_domain else False
    
    if is_likely_multi_journal:
        return 'HIGH', {
            'reason': f'Domain suggests multi-journal publisher: {most_common_domain}',
            'pmids': pmids,
            'total_entries': len(entries),
            'domains': list(set(domains)),
            'primary_domain': most_common_domain
        }
    else:
        return 'MEDIUM', {
            'reason': f'Has domain but appears to be single journal or small publisher: {most_common_domain}',
            'pmids': pmids,
            'total_entries': len(entries),
            'domains': list(set(domains)),
            'primary_domain': most_common_domain
        }


def find_domain_groups(categories):
    """Group journals by domain to identify potential publisher patterns."""
    domain_groups = defaultdict(list)
    
    # Collect all journals with their primary domains
    for category in ['HIGH', 'MEDIUM']:
        for item in categories[category]:
            analysis = item['analysis']
            if 'primary_domain' in analysis:
                domain = analysis['primary_domain']
                domain_groups[domain].append({
                    'journal': item['journal'],
                    'category': category,
                    'pmid_count': len(analysis['pmids'])
                })
    
    # Find domains with multiple journals (potential for grouping)
    multi_journal_domains = {domain: journals for domain, journals in domain_groups.items() if len(journals) > 1}
    
    return multi_journal_domains


def categorize_journals(journal_groups, supported_journals):
    """Categorize all journals by likelihood."""
    categories = {
        'HIGH': [],
        'MEDIUM': [],
        'LOW': []
    }
    
    processed = 0
    total = len(journal_groups)
    
    print(f"Analyzing {total} unique journals...")
    
    for journal, entries in journal_groups.items():
        processed += 1
        if processed % 50 == 0:
            print(f"  Processed {processed}/{total} journals...")
        
        # Skip if journal is already supported
        if journal in supported_journals:
            continue
        
        # Analyze this journal group
        likelihood, analysis = analyze_journal_group(journal, entries)
        
        categories[likelihood].append({
            'journal': journal,
            'analysis': analysis
        })
    
    return categories


def write_categorized_results(categories, multi_journal_domains, output_path):
    """Write categorized results to output file."""
    
    total_journals = sum(len(cat) for cat in categories.values())
    
    content = f"""# Categorized Unknown Journals for FindIt Implementation
# Generated by categorize_unknown_journals.py
# 
# Total journals analyzed: {total_journals}
# HIGH likelihood: {len(categories['HIGH'])} journals
# MEDIUM likelihood: {len(categories['MEDIUM'])} journals  
# LOW likelihood: {len(categories['LOW'])} journals
#
# Likelihood categories:
# HIGH: Domain suggests multi-journal publisher (patterns likely discoverable)
# MEDIUM: Has domain but appears to be single journal or small publisher
# LOW: No domain from DOI resolution
#
# Multi-journal domains found: {len(multi_journal_domains)}
# ========================================================================

"""

    # First, show domain groupings for HIGH likelihood
    if multi_journal_domains:
        content += f"\n{'='*80}\n"
        content += f"DOMAINS WITH MULTIPLE JOURNALS (Potential for Grouping)\n"
        content += f"{'='*80}\n\n"
        
        for domain, journals in sorted(multi_journal_domains.items(), key=lambda x: len(x[1]), reverse=True):
            content += f"Domain: {domain}\n"
            content += f"Journals: {len(journals)}\n"
            total_pmids = sum(j['pmid_count'] for j in journals)
            content += f"Total PMIDs: {total_pmids}\n"
            for journal_info in journals:
                # Find the actual PMIDs for this journal
                journal_name = journal_info['journal']
                journal_pmids = []
                
                # Look through categories to find this journal's PMIDs
                for category in ['HIGH', 'MEDIUM']:
                    for item in categories[category]:
                        if item['journal'] == journal_name:
                            journal_pmids = item['analysis']['pmids']
                            break
                
                pmid_str = ', '.join(journal_pmids) if journal_pmids else 'No PMIDs found'
                content += f"  - {journal_info['journal']} ({journal_info['pmid_count']} PMIDs): {pmid_str} [{journal_info['category']}]\n"
            content += f"{'-'*60}\n\n"

    # Write categories
    for likelihood in ['HIGH', 'MEDIUM', 'LOW']:
        content += f"\n{'='*80}\n"
        content += f"LIKELIHOOD: {likelihood}\n"
        content += f"{'='*80}\n\n"
        
        # Sort by total entries (frequency) descending
        sorted_journals = sorted(categories[likelihood], 
                               key=lambda x: x['analysis']['total_entries'], 
                               reverse=True)
        
        content += f"# {len(sorted_journals)} journals in {likelihood} likelihood category\n\n"
        
        for item in sorted_journals:
            journal = item['journal']
            analysis = item['analysis']
            
            content += f"Journal: {journal}\n"
            content += f"Total PMIDs: {analysis['total_entries']}\n"
            # Print all PMIDs, wrapping long lines
            pmid_list = analysis['pmids']
            if len(pmid_list) <= 10:
                content += f"PMIDs: {', '.join(pmid_list)}\n"
            else:
                # Break into multiple lines for readability
                content += f"PMIDs: "
                for i, pmid in enumerate(pmid_list):
                    if i > 0 and i % 10 == 0:
                        content += f"\n       "
                    content += f"{pmid}"
                    if i < len(pmid_list) - 1:
                        content += ", "
                content += "\n"
            content += f"Reason: {analysis['reason']}\n"
            
            if analysis['domains']:
                content += f"Domains: {', '.join(analysis['domains'])}\n"
                if 'primary_domain' in analysis:
                    content += f"Primary Domain: {analysis['primary_domain']}\n"
            
            content += f"{'-'*60}\n\n"
    
    # Write to file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(content)
    
    print(f"Results written to {output_path}")


def main():
    """Main execution function."""
    print("Categorizing unknown journals by PDF retrieval likelihood...")
    
    # File paths
    base_dir = os.path.dirname(os.path.dirname(__file__))
    input_file = os.path.join(base_dir, 'output', 'FINDIT_TODO', 'unknown_publishers_clean.txt')
    output_file = os.path.join(base_dir, 'output', 'categorized_unknown_journals.txt')
    
    # Load data
    journals_data = load_unknown_journals_csv(input_file)
    if not journals_data:
        print("No journal data loaded. Exiting.")
        return
    
    # Get supported journals to filter out
    print("Getting list of supported journals...")
    with tempfile.TemporaryDirectory() as tmpdir:
        supported_journals = set()
        try:
            supported_journals = set(get_supported_journals())
        except Exception as e:
            print(f"Warning: Could not get supported journals list: {e}")
    
    print(f"Found {len(supported_journals)} already supported journals")
    
    # Group by journal name
    journal_groups = group_by_journal(journals_data)
    print(f"Found {len(journal_groups)} unique journal names")
    
    # Categorize journals
    categories = categorize_journals(journal_groups, supported_journals)
    
    # Find domain groupings
    multi_journal_domains = find_domain_groups(categories)
    
    # Write results
    write_categorized_results(categories, multi_journal_domains, output_file)
    
    print(f"\nSummary:")
    print(f"- Total unique journals: {len(journal_groups)}")
    print(f"- HIGH likelihood: {len(categories['HIGH'])} journals")
    print(f"- MEDIUM likelihood: {len(categories['MEDIUM'])} journals")
    print(f"- LOW likelihood: {len(categories['LOW'])} journals")
    print(f"- Multi-journal domains: {len(multi_journal_domains)}")
    print(f"- Results saved to: {output_file}")


if __name__ == '__main__':
    main()