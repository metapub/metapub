#!/usr/bin/env python3
"""
Pass 1: Article Fetching Script for FindIt Coverage Testing

This script fetches article metadata from PubMed for all PMIDs in a specified list
and stores the results in the PostgreSQL database. This is the first pass in the
FindIt coverage testing pipeline.

The script:
1. Fetches article metadata (title, journal, DOI, PII, PMC, etc.)
2. Stores results in the pmid_results table
3. Handles errors gracefully and tracks processing status
4. Supports resuming from interruptions
5. Provides detailed progress reporting

Usage:
    python pass1_article_fetching.py --list-id 1
    python pass1_article_fetching.py --list-id 1 --start-index 1000
    python pass1_article_fetching.py --list-id 1 --start-index 1000 --end-index 2000
"""

import argparse
import sys
import time
from pathlib import Path
from typing import List, Optional

# Import our database utilities
from database import (
    DatabaseManager, PMIDListManager, PMIDResultsManager, 
    ProcessingRunManager, MeshTermManager, setup_logger
)
from enhanced_analysis import (
    AlternativeIdDetector, MetadataEnhancer, MeshExtractor, get_findit_registry_status
)

# Add parent directory to sys.path for metapub imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from metapub import PubMedFetcher
from metapub.exceptions import MetaPubError


class ProgressReporter:
    """Progress reporting utility."""
    
    def __init__(self, total: int, report_every: int = 50):
        self.total = total
        self.report_every = report_every
        self.last_report = 0
        self.start_time = time.time()
    
    def should_report(self, current: int) -> bool:
        """Check if we should report progress now."""
        return (current - self.last_report) >= self.report_every or current == self.total
    
    def report(self, current: int, logger, extra_info: str = ""):
        """Report current progress."""
        if self.should_report(current):
            elapsed = time.time() - self.start_time
            rate = current / elapsed if elapsed > 0 else 0
            eta = (self.total - current) / rate if rate > 0 else 0
            
            percent = (current / self.total) * 100 if self.total > 0 else 0
            
            msg = f"Progress: {current}/{self.total} ({percent:.1f}%) - {rate:.1f}/sec - ETA: {eta:.0f}s"
            if extra_info:
                msg += f" - {extra_info}"
            
            logger.info(msg)
            print(f"[{time.strftime('%H:%M:%S')}] {msg}")
            
            self.last_report = current


def get_resume_index(results_manager: PMIDResultsManager, pmids: List[str]) -> int:
    """Get the index where processing should resume."""
    processed_pmids = set()
    
    # Get PMIDs that have pass1 status (any final status)
    for status in ['success', 'not_found', 'error']:
        status_pmids = results_manager.get_pmids_by_status('pass1_status', status)
        processed_pmids.update(status_pmids)
    
    # Find first unprocessed PMID
    for i, pmid in enumerate(pmids):
        if pmid not in processed_pmids:
            return i
    
    # All processed
    return len(pmids)


def prompt_for_resume(pmids: List[str], resume_index: int, auto_resume: bool = False) -> int:
    """Prompt user to resume or start fresh."""
    if resume_index == 0:
        return 0  # Nothing to resume from
    
    total = len(pmids)
    completed = resume_index
    
    print(f"\n=== Previous Run Detected ===")
    print(f"Found {completed} PMIDs already processed")
    print(f"Total PMIDs in list: {total}")
    print(f"Would resume from index {resume_index} (PMID: {pmids[resume_index] if resume_index < len(pmids) else 'END'})")
    
    if auto_resume:
        print("Auto-resuming from previous position...")
        return resume_index
    
    while True:
        response = input("\nResume from previous position? [y/n/manual]: ").strip().lower()
        if response in ['y', 'yes']:
            print(f"Resuming from index {resume_index}")
            return resume_index
        elif response in ['n', 'no']:
            print("Starting fresh (previous progress will remain but duplicates may occur)")
            return 0
        elif response in ['m', 'manual']:
            try:
                manual_index = int(input(f"Enter start index (0-{len(pmids)}): "))
                if 0 <= manual_index <= len(pmids):
                    print(f"Starting from manual index {manual_index}")
                    return manual_index
                else:
                    print(f"Index must be between 0 and {len(pmids)}")
            except ValueError:
                print("Please enter a valid integer")
        else:
            print("Please enter 'y', 'n', or 'manual'")


def create_list_from_pmid_range(start_pmid: int, end_pmid: int, list_manager: PMIDListManager) -> int:
    """
    Create a new list from a range of PMID numbers.
    
    Args:
        start_pmid: Starting PMID number (inclusive)
        end_pmid: Ending PMID number (inclusive)
        list_manager: PMIDListManager instance
        
    Returns:
        List ID (int)
    """
    if start_pmid > end_pmid:
        raise ValueError(f"Start PMID ({start_pmid}) must be <= end PMID ({end_pmid})")
    
    pmid_count = end_pmid - start_pmid + 1
    if pmid_count > 100000:
        raise ValueError(f"Range too large ({pmid_count:,} PMIDs). Maximum allowed: 100,000")
    
    # Generate list name
    list_name = f"pmid_range_{start_pmid}_{end_pmid}"
    
    # Check if list already exists with this range
    existing_lists = list_manager.list_pmid_lists()
    for existing_list in existing_lists:
        if existing_list['name'] == list_name:
            print(f"Found existing range list: '{existing_list['name']}' (ID: {existing_list['id']})")
            return existing_list['id']
    
    # Create new list
    print(f"Creating PMID range list: {start_pmid} to {end_pmid} ({pmid_count:,} PMIDs)")
    list_id = list_manager.create_pmid_list(
        name=list_name,
        description=f"Auto-generated PMID range: {start_pmid}-{end_pmid}",
        file_path=None
    )
    
    # Generate PMIDs and insert them
    print(f"Generating {pmid_count:,} PMIDs...")
    pmids = [(list_id, str(pmid), pmid - start_pmid + 1) for pmid in range(start_pmid, end_pmid + 1)]
    
    # Insert PMIDs in batches to avoid memory issues
    batch_size = 1000
    db_manager = list_manager.db
    
    with db_manager.get_cursor() as cursor:
        # First, insert all PMIDs into pmid_results table (ignore conflicts)
        pmid_values = [(str(pmid),) for _, pmid, _ in pmids]
        
        print("Inserting PMIDs into results table...")
        for i in range(0, len(pmid_values), batch_size):
            batch = pmid_values[i:i + batch_size]
            cursor.executemany(
                "INSERT INTO pmid_results (pmid) VALUES (%s) ON CONFLICT (pmid) DO NOTHING",
                batch
            )
            if i % (batch_size * 10) == 0:  # Progress every 10k
                print(f"  Progress: {i + len(batch):,}/{len(pmid_values):,}")
        
        # Insert into pmid_list_members
        print("Creating list membership...")
        for i in range(0, len(pmids), batch_size):
            batch = pmids[i:i + batch_size]
            cursor.executemany(
                "INSERT INTO pmid_list_members (list_id, pmid, position) VALUES (%s, %s, %s)",
                batch
            )
        
        # Update total count
        cursor.execute(
            "UPDATE pmid_lists SET total_pmids = %s WHERE id = %s",
            (pmid_count, list_id)
        )
    
    print(f"✓ Created range list ID {list_id} with {pmid_count:,} PMIDs")
    return list_id


def get_or_create_list_by_file(file_path: str, list_manager: PMIDListManager) -> int:
    """
    Get existing list ID by filename or create new list if not found.
    Uses filename without extension and folder as the list name.
    
    Args:
        file_path: Path to the PMID file
        list_manager: PMIDListManager instance
        
    Returns:
        List ID (int)
    """
    file_path_obj = Path(file_path)
    
    if not file_path_obj.exists():
        raise FileNotFoundError(f"PMID file not found: {file_path}")
    
    # Use filename without extension and without folder as list name
    list_name = file_path_obj.stem
    
    # Check if list already exists with this name
    existing_lists = list_manager.list_pmid_lists()
    for existing_list in existing_lists:
        if existing_list['name'] == list_name:
            print(f"Found existing list: '{existing_list['name']}' (ID: {existing_list['id']})")
            return existing_list['id']
    
    # Create new list
    print(f"Creating new list: '{list_name}' from file: {file_path}")
    list_id = list_manager.create_pmid_list(
        name=list_name,
        description=f"Auto-created from file: {file_path_obj.name}",
        file_path=str(file_path_obj.absolute())
    )
    
    # Load PMIDs from file
    pmid_count = list_manager.load_pmid_list_from_file(list_id, file_path)
    print(f"✓ Created list ID {list_id} with {pmid_count} PMIDs")
    
    return list_id


def get_or_create_list_by_name(list_name: str, list_manager: PMIDListManager) -> int:
    """
    Get existing list ID by list name.
    
    Args:
        list_name: Name of the list to find
        list_manager: PMIDListManager instance
        
    Returns:
        List ID (int)
    """
    # Check if list already exists with this name
    existing_lists = list_manager.list_pmid_lists()
    for existing_list in existing_lists:
        if existing_list['name'] == list_name:
            print(f"Found existing list: '{existing_list['name']}' (ID: {existing_list['id']})")
            return existing_list['id']
    
    raise ValueError(f"No list found with name: {list_name}")


def fetch_articles(list_id: int, start_index: int = 0, end_index: Optional[int] = None,
                  report_every: int = 50, auto_resume: bool = False) -> None:
    """
    Fetch articles for PMIDs in the specified list.
    
    Args:
        list_id: Database ID of the PMID list to process
        start_index: Starting index in PMID list
        end_index: Ending index in PMID list (None for all)
        report_every: Report progress every N articles
        auto_resume: Automatically resume without prompting
    """
    
    # Set up logging
    logger = setup_logger("pass1_article_fetching", "pass1_article_fetching.log")
    logger.info("=== Starting Article Fetching (Pass 1) ===")
    
    try:
        # Initialize database managers
        db_manager = DatabaseManager()
        list_manager = PMIDListManager(db_manager)
        results_manager = PMIDResultsManager(db_manager)
        run_manager = ProcessingRunManager(db_manager)
        mesh_manager = MeshTermManager(db_manager)
        
        # Get list info and PMIDs
        list_info = list_manager.get_pmid_list_info(list_id)
        if not list_info:
            raise ValueError(f"PMID list with ID {list_id} not found")
        
        logger.info(f"Processing PMID list: {list_info['name']} (ID: {list_id})")
        
        all_pmids = list_manager.get_pmid_list(list_id)
        if not all_pmids:
            raise ValueError(f"No PMIDs found in list {list_id}")
        
        logger.info(f"Loaded {len(all_pmids)} PMIDs from list")
        
        # Check for resume opportunity if start_index not manually specified
        actual_start_index = start_index
        if start_index == 0:  # Only auto-resume if start_index wasn't manually set
            resume_index = get_resume_index(results_manager, all_pmids)
            actual_start_index = prompt_for_resume(all_pmids, resume_index, auto_resume)
        
        # Apply start/end index filtering
        if end_index is not None:
            pmids = all_pmids[actual_start_index:end_index]
        else:
            pmids = all_pmids[actual_start_index:]
        
        if not pmids:
            logger.warning("No PMIDs to process after filtering")
            print("No PMIDs to process after filtering")
            return
        
        logger.info(f"Processing {len(pmids)} PMIDs (indices {actual_start_index} to {actual_start_index + len(pmids) - 1})")
        print(f"Processing {len(pmids)} PMIDs from list '{list_info['name']}'")
        
        # Start processing run tracking
        run_id = run_manager.start_processing_run(
            list_id=list_id,
            pass_type='pass1',
            start_index=actual_start_index,
            end_index=actual_start_index + len(pmids) if end_index else None
        )
        
        # Initialize PubMed fetcher
        fetch = PubMedFetcher()
        logger.info("Initialized PubMedFetcher")
        
        # Set up progress reporting
        progress = ProgressReporter(len(pmids), report_every)
        
        # Process counters
        successful = 0
        not_found = 0
        errors = 0
        
        # Process each PMID
        for i, pmid in enumerate(pmids):
            try:
                logger.debug(f"Processing PMID {pmid}")
                
                # Fetch article from PubMed
                article = fetch.article_by_pmid(pmid)
                
                if article:
                    # Extract basic article metadata
                    title = getattr(article, 'title', None)
                    journal = getattr(article, 'journal', None)
                    doi = getattr(article, 'doi', None)
                    pii = getattr(article, 'pii', None)
                    pmc = getattr(article, 'pmc', None)
                    
                    # Enhanced metadata extraction
                    publication_year = MetadataEnhancer.extract_publication_year(article)
                    article_type = MetadataEnhancer.detect_article_type(article)
                    is_retracted = MetadataEnhancer.check_retraction(article)
                    
                    # Alternative identifiers analysis
                    alt_ids = AlternativeIdDetector.detect_alternative_ids(article)
                    
                    # MeSH terms extraction
                    mesh_terms = MeshExtractor.extract_mesh_terms(article)
                    mesh_summary = MeshExtractor.get_mesh_summary(mesh_terms)
                    
                    # Journal/publisher registry status
                    publisher = getattr(article, 'publisher', None)
                    journal_in_registry, publisher_supported = get_findit_registry_status(journal, publisher)
                    
                    # Store in database with enhanced metadata
                    results_manager.upsert_pmid_result(
                        pmid=pmid,
                        title=title,
                        journal_name=journal,
                        publisher=publisher,
                        doi=doi,
                        pii=pii,
                        pmc=pmc,
                        publication_year=publication_year,
                        article_type=article_type,
                        is_retracted=is_retracted,
                        has_pmc=alt_ids['has_pmc'],
                        has_arxiv_id=alt_ids['has_arxiv_id'],
                        has_alternative_ids=alt_ids['has_alternative_ids'],
                        other_identifiers=alt_ids['other_identifiers'],
                        journal_in_findit_registry=journal_in_registry,
                        publisher_supported=publisher_supported,
                        has_mesh_terms=mesh_summary['has_mesh_terms'],
                        mesh_term_count=mesh_summary['mesh_term_count'],
                        major_mesh_count=mesh_summary['major_mesh_count'],
                        is_good_pmid=True,
                        pass1_status='success',
                        pass1_completed_at='CURRENT_TIMESTAMP'
                    )
                    
                    # Store MeSH terms separately
                    if mesh_terms:
                        mesh_manager.store_mesh_terms(pmid, mesh_terms)
                    
                    successful += 1
                    logger.debug(f"Successfully processed PMID {pmid}: {title}")
                    
                else:
                    # Article not found
                    results_manager.upsert_pmid_result(
                        pmid=pmid,
                        is_good_pmid=False,
                        pass1_status='not_found',
                        pass1_completed_at='CURRENT_TIMESTAMP',
                        pass1_error='Article not found in PubMed'
                    )
                    
                    not_found += 1
                    logger.warning(f"Article not found for PMID {pmid}")
                
            except MetaPubError as e:
                # MetaPub specific error
                results_manager.upsert_pmid_result(
                    pmid=pmid,
                    is_good_pmid=False,
                    pass1_status='error',
                    pass1_completed_at='CURRENT_TIMESTAMP',
                    pass1_error=f"MetaPubError: {str(e)}"
                )
                
                errors += 1
                logger.error(f"MetaPubError for PMID {pmid}: {e}")
                
            except Exception as e:
                # Unexpected error
                results_manager.upsert_pmid_result(
                    pmid=pmid,
                    is_good_pmid=False,
                    pass1_status='error',
                    pass1_completed_at='CURRENT_TIMESTAMP',
                    pass1_error=f"Unexpected error: {str(e)}"
                )
                
                errors += 1
                logger.error(f"Unexpected error for PMID {pmid}: {e}")
            
            # Update processing run
            current = i + 1
            run_manager.update_processing_run(
                run_id=run_id,
                total_processed=current,
                successful=successful,
                failed=not_found + errors
            )
            
            # Report progress
            progress.report(
                current, 
                logger, 
                f"Success: {successful}, Not found: {not_found}, Errors: {errors}"
            )
        
        # Complete processing run
        run_manager.complete_processing_run(run_id, 'completed')
        
        # Final summary
        total_processed = successful + not_found + errors
        success_rate = (successful / total_processed * 100) if total_processed > 0 else 0
        
        logger.info("=== Article Fetching Complete ===")
        logger.info(f"Total processed: {total_processed}")
        logger.info(f"Successful: {successful}")
        logger.info(f"Not found: {not_found}")
        logger.info(f"Errors: {errors}")
        logger.info(f"Success rate: {success_rate:.1f}%")
        
        print(f"\n=== Pass 1 Complete ===")
        print(f"Processed: {total_processed} PMIDs")
        print(f"✓ Successful: {successful} ({success_rate:.1f}%)")
        print(f"✗ Not found: {not_found}")
        print(f"⚠ Errors: {errors}")
        print(f"Results stored in database")
        
    except Exception as e:
        logger.error(f"Fatal error in article fetching process: {e}")
        print(f"Fatal error: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Pass 1: Article Fetching for FindIt Coverage Testing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process PMID file (auto-creates list)
  python pass1_article_fetching.py --file clinvar_citations.txt
  
  # Process existing list by name (without extension)
  python pass1_article_fetching.py --name clinvar_citations
  
  # Process PMID range (auto-creates list)
  python pass1_article_fetching.py --pmid-range "30000000:30001000"
  
  # Process existing list by ID
  python pass1_article_fetching.py --list-id 1
  
  # Resume from specific index
  python pass1_article_fetching.py --file clinvar_citations.txt --start-index 1000
  
  # Process subset of range
  python pass1_article_fetching.py --pmid-range "30000000:30010000" --end-index 5000
  
  # Auto-resume without prompting
  python pass1_article_fetching.py --name clinvar_citations --auto-resume
        """
    )
    
    # Mutually exclusive group for list specification
    list_group = parser.add_mutually_exclusive_group(required=True)
    list_group.add_argument(
        '--file',
        type=str,
        help='Path to PMID file (will auto-create list from filename without extension)'
    )
    list_group.add_argument(
        '--name',
        type=str,
        help='Name of existing list to process (filename without extension)'
    )
    list_group.add_argument(
        '--list-id',
        type=int,
        help='Database ID of existing PMID list to process'
    )
    list_group.add_argument(
        '--pmid-range',
        type=str,
        help='PMID range as "start:end" (e.g., "30000000:30001000"). Max 100k PMIDs.'
    )
    parser.add_argument(
        '--start-index',
        type=int,
        default=0,
        help='Starting index in PMID list (for resuming)'
    )
    parser.add_argument(
        '--end-index',
        type=int,
        help='Ending index in PMID list (for partial runs)'
    )
    parser.add_argument(
        '--report-every',
        type=int,
        default=50,
        help='Report progress every N articles'
    )
    parser.add_argument(
        '--auto-resume',
        action='store_true',
        help='Automatically resume from previous position without prompting'
    )
    
    args = parser.parse_args()
    
    try:
        # Determine list_id
        if args.file:
            # Auto-create list from file
            db_manager = DatabaseManager()
            list_manager = PMIDListManager(db_manager)
            list_id = get_or_create_list_by_file(args.file, list_manager)
        elif args.name:
            # Find existing list by name
            db_manager = DatabaseManager()
            list_manager = PMIDListManager(db_manager)
            list_id = get_or_create_list_by_name(args.name, list_manager)
        elif args.pmid_range:
            # Auto-create list from PMID range
            try:
                start_str, end_str = args.pmid_range.split(':')
                start_pmid = int(start_str.strip())
                end_pmid = int(end_str.strip())
            except ValueError:
                raise ValueError("PMID range must be in format 'start:end' (e.g., '30000000:30001000')")
            
            db_manager = DatabaseManager()
            list_manager = PMIDListManager(db_manager)
            list_id = create_list_from_pmid_range(start_pmid, end_pmid, list_manager)
        else:
            # Use provided list_id
            list_id = args.list_id
        
        fetch_articles(
            list_id=list_id,
            start_index=args.start_index,
            end_index=args.end_index,
            report_every=args.report_every,
            auto_resume=args.auto_resume
        )
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()