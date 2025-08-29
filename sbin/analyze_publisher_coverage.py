#!/usr/bin/env python3
"""
Analyze publisher coverage in verified PMIDs and identify gaps for comprehensive testing.

This script compares the domains found in our verified PMIDs dataset against 
the complete list of publishers supported by FindIt to identify coverage gaps
and build a comprehensive test sampling strategy.
"""

import sys
sys.path.append('/home/nthmost/projects/git/metapub')

import csv
from urllib.parse import urlparse
from metapub.findit.registry import JournalRegistry
from collections import defaultdict, Counter

def load_all_verified_pmids():
    """Load PMIDs from original dataset, deposited additions, AND individual publisher files."""
    import glob
    import os
    from urllib.parse import urlparse
    
    all_pmids = []
    
    # Load original verified PMIDs
    original_count = 0
    with open('/home/nthmost/projects/git/metapub/output/findit_verified_pmids_results.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            all_pmids.append(row)
            original_count += 1
    
    # Load deposited PMIDs for missing publishers
    deposited_count = 0
    try:
        with open('/home/nthmost/projects/git/metapub/missing_publishers_pmid_deposit.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['validation_status'] == 'validated':
                    # Convert to same format as original dataset
                    all_pmids.append({
                        'pmid': row['pmid'],
                        'doi': row['doi'], 
                        'article_url': row['article_url'],
                        'article_resolved': row['article_resolved']
                    })
                    deposited_count += 1
    except FileNotFoundError:
        pass
    
    # Load PMIDs from individual publisher files
    individual_count = 0
    pmids_dir = '/home/nthmost/projects/git/metapub/output/verified_pmids'
    if os.path.exists(pmids_dir):
        for pmid_file in glob.glob(f"{pmids_dir}/*_pmids.txt"):
            publisher_name = os.path.basename(pmid_file).replace('_pmids.txt', '').replace('_', ' ').title()
            
            with open(pmid_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue
                    
                    # Extract PMID (handle comments on same line)
                    pmid = line.split()[0]
                    if pmid.isdigit():
                        # Create placeholder entry (we don't have DOI/URL from these files)
                        all_pmids.append({
                            'pmid': pmid,
                            'doi': f'INDIVIDUAL_FILE_{publisher_name}',  # Placeholder
                            'article_url': f'https://pubmed.ncbi.nlm.nih.gov/{pmid}/',
                            'article_resolved': 'True'
                        })
                        individual_count += 1
    
    print(f"  Original dataset: {original_count}")
    print(f"  Deposited additions: {deposited_count}")
    print(f"  Individual publisher files: {individual_count}")
    
    return all_pmids

def analyze_publisher_coverage():
    """Analyze publisher coverage between verified PMIDs and registry."""
    
    print("FINDIT PUBLISHER COVERAGE ANALYSIS (UPDATED)")
    print("=" * 55)
    
    # Load all verified PMIDs data (original + deposited)
    print("Loading verified PMIDs dataset...")
    original_count = 0
    deposited_count = 0
    
    with open('/home/nthmost/projects/git/metapub/output/findit_verified_pmids_results.csv', 'r') as f:
        original_count = sum(1 for line in f) - 1  # subtract header
    
    verified_pmids = load_all_verified_pmids()
    deposited_count = len(verified_pmids) - original_count
    
    print(f"Found {len(verified_pmids)} total verified PMIDs")
    print(f"  Original dataset: {original_count}")
    print(f"  Deposited additions: {deposited_count}")
    
    # Extract domains from URLs (or infer from individual files)
    print("\nExtracting domains from verified PMIDs...")
    domains = []
    for row in verified_pmids:
        if row['doi'].startswith('INDIVIDUAL_FILE_'):
            # Handle PMIDs from individual publisher files
            publisher_name = row['doi'].replace('INDIVIDUAL_FILE_', '')
            # Map publisher name to domain for consistent analysis
            domain = f"INDIVIDUAL_FILE:{publisher_name}"
            row['domain'] = domain
        else:
            # Handle PMIDs with real URLs
            domain = urlparse(row['article_url']).netloc
            row['domain'] = domain
        domains.append(domain)
    
    domain_counts = Counter(domains)
    
    print(f"Found articles from {len(domain_counts)} unique domains:")
    for domain, count in domain_counts.most_common(20):
        print(f"  {domain:<30} : {count:>3} articles")
    
    # Load registry publishers
    print(f"\nLoading FindIt registry...")
    registry = JournalRegistry()
    conn = registry._get_connection()
    cursor = conn.execute('SELECT DISTINCT name, dance_function FROM publishers ORDER BY name')
    registry_publishers = cursor.fetchall()
    registry.close()
    
    print(f"Found {len(registry_publishers)} publishers in FindIt registry")
    
    # Create domain-to-publisher mapping
    print("\nMapping domains to publishers...")
    
    # Updated mapping including deposited publishers (matched to exact registry names)
    domain_to_publisher = {
        'www.science.org': 'aaas',
        'science.org': 'Science Magazine',  # Exact registry match for deposited PMIDs
        'pubs.acs.org': 'American Chemical Society', 
        'aacrjournals.org': 'American Association for Cancer Research',
        'www.ahajournals.org': 'American Heart Association',
        'journals.physiology.org': 'American Physiological Society',
        'journals.asm.org': 'Microbiology Spectrum',  # Exact registry match for deposited PMIDs
        'www.atsjournals.org': 'American Thoracic Society',
        'pubs.aip.org': 'aip',
        'ajph.aphapublications.org': 'American Journal of Public Health',
        'meridian.allenpress.com': 'allenpress',
        'www.annualreviews.org': 'annualreviews',
        'psycnet.apa.org:443': 'apa',
        'asmedigitalcollection.asme.org': 'asme',
        'portlandpress.com': 'biochemsoc',
        'bioone.org': 'bioone',
        'threedmedprint.biomedcentral.com': 'bmc',
        'aidsrestherapy.biomedcentral.com': 'bmc',
        'actaneurocomms.biomedcentral.com': 'bmc',
        'reproductive-health-journal.biomedcentral.com': 'bmc',
        'spcare.bmj.com': 'BMJ Publishing Group',
        'bmjopengastro.bmj.com': 'BMJ Publishing Group', 
        'heart.bmj.com': 'BMJ Publishing Group',
        'brill.com': 'brill',
        'www.cambridge.org': 'Cambridge University Press',
        'www.cancerbiomed.org': 'cancerbiomed',
        'www.degruyter.com': 'De Gruyter',
        'www.degruyterbrill.com:443': 'De Gruyter',
        'www.dovepress.com': 'dovepress',
        'www.dustri.com': 'dustri',
        'www.emerald.com': 'emerald',
        'www.eurekaselect.com': 'eurekaselect',
        'www.frontiersin.org': 'frontiers',
        'www.hilarispublisher.com': 'hilaris',
        'content.iospress.com:443': 'iospress',
        'www.ingentaconnect.com': 'ingentaconnect',
        'iopscience.iop.org': 'iop',
        'validate.perfdrive.com': 'iop',
        'jamanetwork.com': 'jama',
        'www.jci.org': 'jci',
        'www.jstage.jst.go.jp': 'jstage',
        'karger.com': 'karger',
        'www.liebertpub.com': 'Mary Ann Liebert Publishers',
        'journals.lww.com': 'wolterskluwer',  # Exact registry match for deposited PMIDs
        'www.mdpi.com': 'MDPI',
        'muse.jhu.edu': 'projectmuse',
        'www.nature.com': 'nature',
        'www.nejm.org': 'New England Journal of Medicine',
        'www.oatext.com': 'oatext',
        'academic.oup.com': 'Oxford Academic (Endocrine Society)',  # Exact registry match for deposited PMIDs
        'journals.plos.org': 'Public Library of Science',
        'pnas.org': 'Proceedings of the National Academy of Sciences',
        'pubs.rsc.org': 'rsc',
        'journals.sagepub.com': 'SAGE Publications',
        'www.scielo.br': 'scielo',
        'linkinghub.elsevier.com': 'sciencedirect',
        'sciendo.com': 'sciendo',
        'www.scirp.org': 'scirp',
        'www.spandidos-publications.com': 'spandidos',
        'link.springer.com': 'springer',
        'www.tandfonline.com': 'Informa Healthcare',  # Exact registry match for deposited PMIDs
        'www.thieme-connect.de': 'Thieme Medical Publishers',
        'www.journals.uchicago.edu': 'uchicago',
        'medicaljournalssweden.se': 'walshmedia',
        'onlinelibrary.wiley.com': 'wiley',
        'acrjournals.onlinelibrary.wiley.com': 'wiley',
        'www.wjgnet.com': 'wjgnet',
        'www.worldscientific.com': 'worldscientific',
        
        # Individual publisher files (map filename patterns to registry names)
        'INDIVIDUAL_FILE:Taylor And Francis': 'Taylor & Francis',
        'INDIVIDUAL_FILE:American Society Of Microbiology': 'American Society of Microbiology',
        'INDIVIDUAL_FILE:Oxford University Press': 'Oxford University Press',
        'INDIVIDUAL_FILE:Wolters Kluwer Lww': 'Wolters Kluwer LWW',
        'INDIVIDUAL_FILE:Acm': 'acm',
        'INDIVIDUAL_FILE:Inderscience': 'inderscience',
        'INDIVIDUAL_FILE:Longdom': 'longdom',
        'INDIVIDUAL_FILE:Najms': 'najms',
        'INDIVIDUAL_FILE:Science Magazine': 'Science Magazine',
        'INDIVIDUAL_FILE:Microbiology Spectrum': 'Microbiology Spectrum',
        'INDIVIDUAL_FILE:Oxford Academic Endocrine Society': 'Oxford Academic (Endocrine Society)',
        'INDIVIDUAL_FILE:Informa Healthcare': 'Informa Healthcare',
        'INDIVIDUAL_FILE:Wolterskluwer': 'wolterskluwer',
    }
    
    # Map verified PMIDs to publishers
    pmids_by_publisher = defaultdict(list)
    unmapped_domains = set()
    
    for row in verified_pmids:
        domain = row['domain']
        if domain in domain_to_publisher:
            publisher = domain_to_publisher[domain]
            pmids_by_publisher[publisher].append({
                'pmid': row['pmid'],
                'doi': row['doi'],
                'url': row['article_url']
            })
        else:
            unmapped_domains.add(domain)
    
    # Analyze coverage
    print(f"\nPUBLISHER COVERAGE ANALYSIS:")
    print(f"Mapped {len(pmids_by_publisher)} publishers from verified PMIDs")
    print(f"Unmapped domains: {len(unmapped_domains)}")
    
    if unmapped_domains:
        print("\nUnmapped domains:")
        for domain in sorted(unmapped_domains):
            count = domain_counts.get(domain, 0)
            print(f"  {domain:<30} : {count:>3} articles")
    
    # Get registry publisher names 
    registry_publisher_names = {pub[0] for pub in registry_publishers}
    
    # Find coverage gaps
    covered_publishers = set(pmids_by_publisher.keys())
    missing_publishers = registry_publisher_names - covered_publishers
    
    print(f"\nCOVERAGE SUMMARY:")
    print(f"Registry publishers: {len(registry_publisher_names)}")
    print(f"Covered publishers: {len(covered_publishers)}")
    print(f"Missing publishers: {len(missing_publishers)}")
    print(f"Coverage rate: {len(covered_publishers)/len(registry_publisher_names)*100:.1f}%")
    
    print(f"\nPUBLISHERS WITH VERIFIED PMIDs:")
    for publisher in sorted(covered_publishers):
        count = len(pmids_by_publisher[publisher])
        sample_pmid = pmids_by_publisher[publisher][0]['pmid']
        print(f"  {publisher:<30} : {count:>3} PMIDs (e.g., {sample_pmid})")
    
    print(f"\nMISSING PUBLISHERS (need PMIDs for testing):")
    for publisher in sorted(missing_publishers):
        # Find the dance function for context
        dance_func = None
        for pub_name, pub_dance in registry_publishers:
            if pub_name == publisher:
                dance_func = pub_dance
                break
        print(f"  {publisher:<30} -> {dance_func}")
    
    return {
        'covered_publishers': covered_publishers,
        'missing_publishers': missing_publishers,
        'pmids_by_publisher': dict(pmids_by_publisher),
        'coverage_rate': len(covered_publishers)/len(registry_publisher_names)*100
    }

if __name__ == '__main__':
    results = analyze_publisher_coverage()
    print(f"\n" + "="*55)
    print(f"UPDATED ANALYSIS COMPLETE")
    print(f"Coverage: {results['coverage_rate']:.1f}% of FindIt publishers have verified PMIDs")
    print(f"Ready for comprehensive testing of {len(results['covered_publishers'])} publishers")
    print(f"\nNOTE: Analysis includes deposited PMIDs for missing publishers")
    print(f"Files processed: findit_verified_pmids_results.csv + missing_publishers_pmid_deposit.csv")