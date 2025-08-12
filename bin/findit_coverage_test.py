#!/usr/bin/env python3
"""
Comprehensive FindIt Coverage Test Script

Tests a large PMID list against FindIt to evaluate coverage, collect statistics,
and identify problematic cases for later analysis.

Usage:
    python bin/findit_coverage_test.py PMID_lists/findit_coverage [--output-dir results]

Features:
- Verbose logging to file with rotation
- Comprehensive statistics tracking
- Error categorization and analysis
- Progress reporting
- Resume capability (skip already processed PMIDs)
- Publisher success rate analysis
- Journal coverage reporting
"""

import os
import sys
import re
import logging
import argparse
import json
import time
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime
import signal

from metapub import FindIt

# Global stats tracking
class CoverageStats:
    def __init__(self):
        self.total_processed = 0
        self.successful_urls = 0
        self.failed_lookups = 0
        self.start_time = time.time()
        
        # Detailed tracking
        self.error_categories = defaultdict(int)
        self.publisher_stats = defaultdict(lambda: {'success': 0, 'total': 0})
        self.journal_stats = defaultdict(lambda: {'success': 0, 'total': 0})
        self.doi_score_distribution = defaultdict(int)
        self.processing_times = []
        
        # Problem cases for analysis
        self.problem_cases = {
            'missing_doi': [],
            'low_doi_score': [],
            'format_errors': [],
            'access_denied': [],
            'unknown_errors': []
        }
    
    def add_success(self, pmid, url, journal, doi_score, processing_time):
        self.total_processed += 1
        self.successful_urls += 1
        self.processing_times.append(processing_time)
        self.doi_score_distribution[doi_score] += 1
        
        # Extract publisher from URL for stats
        publisher = self._extract_publisher_from_url(url)
        if publisher:
            self.publisher_stats[publisher]['success'] += 1
            self.publisher_stats[publisher]['total'] += 1
        
        if journal:
            self.journal_stats[journal]['success'] += 1
            self.journal_stats[journal]['total'] += 1
    
    def add_failure(self, pmid, reason, journal, doi_score, processing_time):
        self.total_processed += 1
        self.failed_lookups += 1
        self.processing_times.append(processing_time)
        
        if doi_score is not None:
            self.doi_score_distribution[doi_score] += 1
        
        # Categorize error
        category = self._categorize_error(reason)
        self.error_categories[category] += 1
        
        # Track publisher failure
        publisher = self._extract_publisher_from_reason(reason)
        if publisher:
            self.publisher_stats[publisher]['total'] += 1
        
        if journal:
            self.journal_stats[journal]['total'] += 1
        
        # Store problem cases for analysis (limit to avoid memory issues)
        if category in self.problem_cases and len(self.problem_cases[category]) < 100:
            self.problem_cases[category].append({
                'pmid': pmid,
                'reason': reason,
                'journal': journal,
                'doi_score': doi_score
            })
    
    def _extract_publisher_from_url(self, url):
        """Extract publisher name from URL domain."""
        if not url:
            return None
        
        domain_mapping = {
            'sciencedirect.com': 'ScienceDirect',
            'springer.com': 'Springer', 
            'nature.com': 'Nature',
            'wiley.com': 'Wiley',
            'eurekaselect.com': 'EurekaSelect',
            'cambridge.org': 'Cambridge',
            'oxford.org': 'Oxford',
            'bmj.com': 'BMJ',
            'plos.org': 'PLOS',
            'frontiersin.org': 'Frontiers',
            'mdpi.com': 'MDPI',
            'taylorandfrancis.com': 'Taylor & Francis',
            'karger.com': 'Karger',
            'thieme.de': 'Thieme'
        }
        
        for domain, publisher in domain_mapping.items():
            if domain in url.lower():
                return publisher
        
        # Extract domain as fallback
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            return domain.replace('www.', '')
        except:
            return 'unknown'
    
    def _extract_publisher_from_reason(self, reason):
        """Extract publisher name from error reason."""
        if 'ScienceDirect' in reason:
            return 'ScienceDirect'
        elif 'EurekaSelect' in reason:
            return 'EurekaSelect'
        elif 'Nature' in reason:
            return 'Nature'
        # Add more as needed
        return None
    
    def _categorize_error(self, reason):
        """Categorize error reasons for analysis."""
        if not reason:
            return 'unknown'
        
        reason_lower = reason.lower()
        
        if 'missing' in reason_lower and 'doi' in reason_lower:
            return 'missing_doi'
        elif 'doi' in reason_lower and ('failed' in reason_lower or 'score' in reason_lower):
            return 'low_doi_score'
        elif any(x in reason_lower for x in ['paywall', 'denied', 'subscription']):
            return 'access_denied'
        elif any(x in reason_lower for x in ['format', 'template', 'piit', 'pii']):
            return 'format_errors'
        elif 'cantdo' in reason_lower:
            return 'unsupported_journal'
        elif 'noformat' in reason_lower:
            return 'no_handler'
        else:
            return 'unknown_errors'
    
    def get_success_rate(self):
        """Calculate overall success rate."""
        if self.total_processed == 0:
            return 0.0
        return (self.successful_urls / self.total_processed) * 100
    
    def get_avg_processing_time(self):
        """Calculate average processing time per PMID."""
        if not self.processing_times:
            return 0.0
        return sum(self.processing_times) / len(self.processing_times)
    
    def get_elapsed_time(self):
        """Get total elapsed time."""
        return time.time() - self.start_time
    
    def print_summary(self, logger):
        """Print comprehensive statistics summary."""
        elapsed = self.get_elapsed_time()
        
        logger.info("=" * 80)
        logger.info("FINDIT COVERAGE TEST SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total PMIDs processed: {self.total_processed:,}")
        logger.info(f"Successful URLs: {self.successful_urls:,}")
        logger.info(f"Failed lookups: {self.failed_lookups:,}")
        logger.info(f"Success rate: {self.get_success_rate():.2f}%")
        logger.info(f"Average processing time: {self.get_avg_processing_time():.3f}s per PMID")
        logger.info(f"Total elapsed time: {elapsed/3600:.2f} hours")
        logger.info(f"Processing rate: {self.total_processed/elapsed:.2f} PMIDs/second")
        
        # Error category breakdown
        logger.info("\nError Category Breakdown:")
        for category, count in sorted(self.error_categories.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / self.failed_lookups) * 100 if self.failed_lookups > 0 else 0
            logger.info(f"  {category}: {count:,} ({percentage:.1f}%)")
        
        # Top publishers by success rate
        logger.info("\nTop Publishers by Success Rate:")
        publisher_success_rates = []
        for pub, stats in self.publisher_stats.items():
            if stats['total'] >= 10:  # Minimum threshold
                rate = (stats['success'] / stats['total']) * 100
                publisher_success_rates.append((pub, rate, stats['success'], stats['total']))
        
        for pub, rate, success, total in sorted(publisher_success_rates, key=lambda x: x[1], reverse=True)[:10]:
            logger.info(f"  {pub}: {rate:.1f}% ({success:,}/{total:,})")
        
        # DOI score distribution
        logger.info("\nDOI Score Distribution:")
        scores = list(self.doi_score_distribution.keys())
        # Handle None values in sorting
        none_scores = [s for s in scores if s is None]
        numeric_scores = [s for s in scores if s is not None]
        sorted_scores = sorted(numeric_scores, reverse=True) + none_scores
        
        for score in sorted_scores:
            count = self.doi_score_distribution[score]
            percentage = (count / self.total_processed) * 100
            score_label = "None" if score is None else str(score)
            logger.info(f"  Score {score_label}: {count:,} ({percentage:.1f}%)")


def setup_logging(output_dir):
    """Setup comprehensive logging with file rotation."""
    log_dir = Path(output_dir) / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"findit_coverage_{timestamp}.log"
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific log levels
    logging.getLogger('eutils').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    
    return logging.getLogger('findit_coverage')


def validate_pmid(pmid_str):
    """Validate PMID format."""
    pmid_str = pmid_str.strip()
    return re.match(r'^\d+$', pmid_str) is not None


def load_pmids(pmid_file):
    """Load and validate PMIDs from file."""
    pmids = []
    with open(pmid_file, 'r') as f:
        for line_num, line in enumerate(f, 1):
            pmid = line.strip()
            if not pmid:
                continue
            if validate_pmid(pmid):
                pmids.append(pmid)
            else:
                logging.warning(f"Invalid PMID format at line {line_num}: {pmid}")
    
    return list(set(pmids))  # Remove duplicates


def load_processed_pmids(output_dir):
    """Load already processed PMIDs for resume capability."""
    processed_file = Path(output_dir) / "processed_pmids.txt"
    if processed_file.exists():
        with open(processed_file, 'r') as f:
            return set(line.strip() for line in f)
    return set()


def save_processed_pmid(output_dir, pmid):
    """Save processed PMID for resume capability."""
    processed_file = Path(output_dir) / "processed_pmids.txt"
    with open(processed_file, 'a') as f:
        f.write(f"{pmid}\n")


def save_stats_snapshot(output_dir, stats):
    """Save current statistics snapshot."""
    stats_file = Path(output_dir) / "stats_snapshot.json"
    
    # Convert stats to JSON-serializable format
    stats_data = {
        'total_processed': stats.total_processed,
        'successful_urls': stats.successful_urls,
        'failed_lookups': stats.failed_lookups,
        'success_rate': stats.get_success_rate(),
        'elapsed_time': stats.get_elapsed_time(),
        'error_categories': dict(stats.error_categories),
        'publisher_stats': dict(stats.publisher_stats),
        'doi_score_distribution': dict(stats.doi_score_distribution),
        'problem_cases': stats.problem_cases,
        'avg_processing_time': stats.get_avg_processing_time()
    }
    
    with open(stats_file, 'w') as f:
        json.dump(stats_data, f, indent=2)


def signal_handler(signum, frame, stats, output_dir, logger):
    """Handle interrupt signals gracefully."""
    logger.info(f"Received signal {signum}, saving progress...")
    save_stats_snapshot(output_dir, stats)
    stats.print_summary(logger)
    logger.info("Progress saved. Exiting...")
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description='Test FindIt coverage on a large PMID list')
    parser.add_argument('pmid_file', help='File containing PMIDs (one per line)')
    parser.add_argument('--output-dir', default='findit_coverage_results', 
                       help='Output directory for results and logs')
    parser.add_argument('--batch-size', type=int, default=1000,
                       help='Batch size for progress reporting and stats saving')
    parser.add_argument('--resume', action='store_true',
                       help='Resume from where we left off')
    
    args = parser.parse_args()
    
    # Setup output directory and logging
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger = setup_logging(output_dir)
    
    # Load PMIDs
    logger.info(f"Loading PMIDs from {args.pmid_file}")
    pmids = load_pmids(args.pmid_file)
    logger.info(f"Loaded {len(pmids):,} unique PMIDs")
    
    # Handle resume
    processed_pmids = set()
    if args.resume:
        processed_pmids = load_processed_pmids(output_dir)
        logger.info(f"Resuming: skipping {len(processed_pmids):,} already processed PMIDs")
        pmids = [pmid for pmid in pmids if pmid not in processed_pmids]
        logger.info(f"Remaining PMIDs to process: {len(pmids):,}")
    
    # Initialize stats
    stats = CoverageStats()
    
    # Setup signal handlers for graceful exit
    def signal_wrapper(signum, frame):
        signal_handler(signum, frame, stats, output_dir, logger)
    
    signal.signal(signal.SIGINT, signal_wrapper)
    signal.signal(signal.SIGTERM, signal_wrapper)
    
    # Main processing loop
    logger.info("Starting FindIt coverage test...")
    
    for i, pmid in enumerate(pmids, 1):
        start_time = time.time()
        
        try:
            # Initialize FindIt with unverified URLs for speed
            src = FindIt(pmid=pmid, verify=False)
            
            processing_time = time.time() - start_time
            
            # Log detailed info
            logger.debug(f"PMID {pmid}: Journal='{src.pma.journal}', DOI={src.doi}, Score={src.doi_score}")
            
            if src.url:
                stats.add_success(pmid, src.url, src.pma.journal, src.doi_score, processing_time)
                logger.info(f"SUCCESS {pmid}: {src.url}")
            else:
                stats.add_failure(pmid, src.reason, src.pma.journal, src.doi_score, processing_time)
                logger.info(f"FAILED {pmid}: {src.reason}")
            
            # Save progress
            save_processed_pmid(output_dir, pmid)
            
        except Exception as error:
            processing_time = time.time() - start_time
            error_msg = str(error)
            stats.add_failure(pmid, f"EXCEPTION: {error_msg}", None, None, processing_time)
            logger.error(f"ERROR {pmid}: {error_msg}")
            save_processed_pmid(output_dir, pmid)
        
        # Progress reporting and stats saving
        if i % args.batch_size == 0:
            elapsed = time.time() - stats.start_time
            rate = stats.total_processed / elapsed
            remaining = len(pmids) - i
            eta = remaining / rate if rate > 0 else 0
            
            logger.info(f"Progress: {i:,}/{len(pmids):,} ({i/len(pmids)*100:.1f}%) | "
                       f"Success rate: {stats.get_success_rate():.1f}% | "
                       f"Rate: {rate:.2f} PMIDs/s | "
                       f"ETA: {eta/3600:.1f}h")
            
            save_stats_snapshot(output_dir, stats)
    
    # Final summary
    logger.info("Processing complete!")
    save_stats_snapshot(output_dir, stats)
    stats.print_summary(logger)
    
    logger.info(f"Results saved to: {output_dir}")


if __name__ == "__main__":
    main()