#!/usr/bin/env python3
"""
Comprehensive FindIt Success Rate Test

Tests FindIt's ability to retrieve PDF URLs across all supported publishers
using verified PMIDs. This provides an overall success rate metric for the
FindIt system and validates the CrossRef workarounds for blocked publishers.

Usage:
    python comprehensive_findit_test.py [--sample-size N] [--publisher NAME]
"""

import sys
sys.path.append('/home/nthmost/projects/git/metapub')

import csv
import tempfile
import argparse
import random
from collections import defaultdict, Counter
from urllib.parse import urlparse
from metapub import PubMedFetcher, FindIt
from metapub.findit.registry import JournalRegistry

# Backfilled PMIDs for missing publishers
BACKFILLED_PMIDS = {
    'Microbiology Spectrum': [
        {'pmid': '38934607', 'doi': '10.1128/spectrum.04266-23', 'article_url': 'https://journals.asm.org/doi/10.1128/spectrum.04266-23', 'domain': 'journals.asm.org'},
        {'pmid': '39320069', 'doi': '10.1128/spectrum.01161-24', 'article_url': 'https://journals.asm.org/doi/10.1128/spectrum.01161-24', 'domain': 'journals.asm.org'},
        {'pmid': '39109857', 'doi': '10.1128/spectrum.00714-24', 'article_url': 'https://journals.asm.org/doi/10.1128/spectrum.00714-24', 'domain': 'journals.asm.org'},
    ],
    'Science Magazine': [
        {'pmid': '40536974', 'doi': '10.1126/science.ads8473', 'article_url': 'https://science.org/doi/10.1126/science.ads8473', 'domain': 'science.org'},
        {'pmid': '40536983', 'doi': '10.1126/science.adx0043', 'article_url': 'https://science.org/doi/10.1126/science.adx0043', 'domain': 'science.org'},
        {'pmid': '39480913', 'doi': '10.1126/science.adn5421', 'article_url': 'https://science.org/doi/10.1126/science.adn5421', 'domain': 'science.org'},
    ],
    'Wolters Kluwer': [
        {'pmid': '39252302', 'doi': '10.1097/MD.0000000000039572', 'article_url': 'https://journals.lww.com/md-journal/fulltext/2024/08160/associations_between_daily_dietary_intake_and.43.aspx', 'domain': 'journals.lww.com'},
        {'pmid': '39432664', 'doi': '10.1097/MD.0000000000040131', 'article_url': 'https://journals.lww.com/md-journal/fulltext/2024/11290/enhanced_recovery_after_surgery_protocol.13.aspx', 'domain': 'journals.lww.com'},
    ],
    'Informa Healthcare': [
        {'pmid': '33840342', 'doi': '10.1080/17538157.2021.1879810', 'article_url': 'https://www.tandfonline.com/doi/full/10.1080/17538157.2021.1879810', 'domain': 'www.tandfonline.com'},
        {'pmid': '29239662', 'doi': '10.1080/17538157.2017.1398753', 'article_url': 'https://www.tandfonline.com/doi/full/10.1080/17538157.2017.1398753', 'domain': 'www.tandfonline.com'},
    ],
    'Oxford Academic (Endocrine Society)': [
        {'pmid': '37580314', 'doi': '10.1210/clinem/dgad463', 'article_url': 'https://academic.oup.com/jcem/article/108/10/2612/7226063', 'domain': 'academic.oup.com'},
        {'pmid': '36974474', 'doi': '10.1210/clinem/dgad174', 'article_url': 'https://academic.oup.com/jcem/article/108/8/1974/7084087', 'domain': 'academic.oup.com'},
    ],
}

# Publisher mapping from domain to registry name
DOMAIN_TO_PUBLISHER = {
    'www.science.org': 'aaas',
    'pubs.acs.org': 'American Chemical Society', 
    'aacrjournals.org': 'American Association for Cancer Research',
    'www.ahajournals.org': 'American Heart Association',
    'journals.physiology.org': 'American Physiological Society',
    'journals.asm.org': 'American Society of Microbiology',
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
    'journals.lww.com': 'Wolters Kluwer LWW',
    'www.mdpi.com': 'MDPI',
    'muse.jhu.edu': 'projectmuse',
    'www.nature.com': 'nature',
    'www.nejm.org': 'New England Journal of Medicine',
    'www.oatext.com': 'oatext',
    'academic.oup.com': 'Oxford University Press',
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
    'www.tandfonline.com': 'Taylor & Francis',
    'www.thieme-connect.de': 'Thieme Medical Publishers',
    'www.journals.uchicago.edu': 'uchicago',
    'medicaljournalssweden.se': 'walshmedia',
    'onlinelibrary.wiley.com': 'wiley',
    'acrjournals.onlinelibrary.wiley.com': 'wiley',
    'www.wjgnet.com': 'wjgnet',
    'www.worldscientific.com': 'worldscientific',
}

def load_verified_pmids():
    """Load and organize verified PMIDs by publisher, including backfilled data."""
    print("Loading verified PMIDs dataset...")
    
    verified_pmids = []
    with open('/home/nthmost/projects/git/metapub/output/findit_verified_pmids_results.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            domain = urlparse(row['article_url']).netloc
            row['domain'] = domain
            verified_pmids.append(row)
    
    # Group by publisher
    pmids_by_publisher = defaultdict(list)
    unmapped_count = 0
    
    for row in verified_pmids:
        domain = row['domain']
        if domain in DOMAIN_TO_PUBLISHER:
            publisher = DOMAIN_TO_PUBLISHER[domain]
            pmids_by_publisher[publisher].append(row)
        else:
            unmapped_count += 1
    
    # Add backfilled PMIDs for missing publishers
    backfilled_count = 0
    for publisher, backfilled_pmids in BACKFILLED_PMIDS.items():
        for pmid_data in backfilled_pmids:
            pmids_by_publisher[publisher].append(pmid_data)
            backfilled_count += 1
    
    print(f"Loaded {len(verified_pmids)} verified PMIDs")
    print(f"Added {backfilled_count} backfilled PMIDs for missing publishers")
    print(f"Total mapped to {len(pmids_by_publisher)} publishers")
    print(f"Unmapped: {unmapped_count} PMIDs")
    
    return pmids_by_publisher

def create_test_sample(pmids_by_publisher, sample_size=None, target_publisher=None):
    """Create a representative test sample."""
    
    if target_publisher:
        # Test specific publisher
        if target_publisher not in pmids_by_publisher:
            print(f"Error: Publisher '{target_publisher}' not found in verified PMIDs")
            return []
        
        pmids = pmids_by_publisher[target_publisher]
        if sample_size and sample_size < len(pmids):
            pmids = random.sample(pmids, sample_size)
        
        print(f"Testing {len(pmids)} PMIDs for publisher: {target_publisher}")
        return [(target_publisher, pmid) for pmid in pmids]
    
    # Create balanced sample across all publishers
    test_sample = []
    
    if sample_size:
        # Calculate per-publisher sample size
        publishers = list(pmids_by_publisher.keys())
        per_publisher = max(1, sample_size // len(publishers))
        
        for publisher, pmids in pmids_by_publisher.items():
            sample_pmids = random.sample(pmids, min(per_publisher, len(pmids)))
            for pmid_data in sample_pmids:
                test_sample.append((publisher, pmid_data))
    else:
        # Use all verified PMIDs
        for publisher, pmids in pmids_by_publisher.items():
            for pmid_data in pmids:
                test_sample.append((publisher, pmid_data))
    
    print(f"Created test sample of {len(test_sample)} PMIDs across {len(pmids_by_publisher)} publishers")
    return test_sample

def test_findit_success_rate(test_sample, verbose=False):
    """Test FindIt success rate on the sample."""
    
    print(f"\nTesting FindIt with {len(test_sample)} PMIDs...")
    print("=" * 60)
    
    fetch = PubMedFetcher()
    
    results = {
        'total': len(test_sample),
        'success': 0,
        'failed': 0,
        'errors': 0,
        'by_publisher': defaultdict(lambda: {'success': 0, 'failed': 0, 'errors': 0})
    }
    
    for i, (publisher, pmid_data) in enumerate(test_sample, 1):
        pmid = pmid_data['pmid']
        expected_doi = pmid_data['doi']
        
        if verbose or i % 10 == 0:
            print(f"[{i:3d}/{len(test_sample)}] Testing PMID {pmid} ({publisher})")
        
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                findit = FindIt(pmid=pmid, cachedir=tmpdir)
                pdf_url = findit.url
                
                if pdf_url:
                    results['success'] += 1
                    results['by_publisher'][publisher]['success'] += 1
                    
                    if verbose:
                        print(f"  ✓ SUCCESS: {pdf_url}")
                else:
                    results['failed'] += 1
                    results['by_publisher'][publisher]['failed'] += 1
                    
                    if verbose:
                        reason = findit.reason if findit.reason else "No reason provided"
                        print(f"  ✗ FAILED: {reason}")
                        
        except Exception as e:
            results['errors'] += 1
            results['by_publisher'][publisher]['errors'] += 1
            
            if verbose:
                print(f"  ✗ ERROR: {e}")
    
    # Calculate success rates
    success_rate = (results['success'] / results['total']) * 100
    
    print(f"\n" + "=" * 60)
    print("COMPREHENSIVE FINDIT TEST RESULTS")
    print("=" * 60)
    print(f"Total PMIDs tested: {results['total']}")
    print(f"Successes: {results['success']}")
    print(f"Failures: {results['failed']}")
    print(f"Errors: {results['errors']}")
    print(f"Overall Success Rate: {success_rate:.1f}%")
    
    # Publisher-level results
    print(f"\nPUBLISHER-LEVEL SUCCESS RATES:")
    print(f"{'Publisher':<30} {'Success':<8} {'Failed':<8} {'Errors':<8} {'Rate':<8}")
    print("-" * 70)
    
    for publisher in sorted(results['by_publisher'].keys()):
        pub_results = results['by_publisher'][publisher]
        total_pub = pub_results['success'] + pub_results['failed'] + pub_results['errors']
        pub_rate = (pub_results['success'] / total_pub) * 100 if total_pub > 0 else 0
        
        print(f"{publisher:<30} {pub_results['success']:<8} {pub_results['failed']:<8} "
              f"{pub_results['errors']:<8} {pub_rate:>6.1f}%")
    
    # Identify best and worst performers
    publisher_rates = []
    for publisher, pub_results in results['by_publisher'].items():
        total_pub = pub_results['success'] + pub_results['failed'] + pub_results['errors']
        if total_pub > 0:
            rate = (pub_results['success'] / total_pub) * 100
            publisher_rates.append((publisher, rate, total_pub))
    
    publisher_rates.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\nTOP 10 PERFORMING PUBLISHERS:")
    for publisher, rate, total in publisher_rates[:10]:
        print(f"  {publisher:<30} : {rate:>5.1f}% ({total} PMIDs)")
    
    print(f"\nBOTTOM 10 PERFORMING PUBLISHERS:")
    for publisher, rate, total in publisher_rates[-10:]:
        print(f"  {publisher:<30} : {rate:>5.1f}% ({total} PMIDs)")
    
    return results

def main():
    parser = argparse.ArgumentParser(description='Comprehensive FindIt success rate test')
    parser.add_argument('--sample-size', type=int, help='Limit test to N PMIDs')
    parser.add_argument('--publisher', help='Test only specific publisher')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--seed', type=int, default=42, help='Random seed for reproducible sampling')
    
    args = parser.parse_args()
    
    # Set random seed for reproducible results
    random.seed(args.seed)
    
    print("COMPREHENSIVE FINDIT SUCCESS RATE TEST")
    print("=" * 50)
    
    # Load verified PMIDs
    pmids_by_publisher = load_verified_pmids()
    
    # Create test sample
    test_sample = create_test_sample(
        pmids_by_publisher, 
        sample_size=args.sample_size, 
        target_publisher=args.publisher
    )
    
    if not test_sample:
        print("No PMIDs to test!")
        return 1
    
    # Run the test
    results = test_findit_success_rate(test_sample, verbose=args.verbose)
    
    # Summary
    success_rate = (results['success'] / results['total']) * 100
    print(f"\n🎯 FINAL RESULT: {success_rate:.1f}% success rate across {len(results['by_publisher'])} publishers")
    
    if success_rate >= 80:
        print("✅ Excellent performance! FindIt is working well across publishers.")
    elif success_rate >= 60:
        print("⚠️  Good performance, but some publishers need attention.")
    else:
        print("❌ Poor performance - significant issues need to be addressed.")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())