#!/usr/bin/env python3
"""
Pass 2: PDF URL Finding Script for FindIt Coverage Testing

This script uses FindIt to find PDF URLs for articles that were successfully 
processed in Pass 1. It stores the results in the PostgreSQL database without
verifying that the URLs actually work (that's done in Pass 3).

The script:
1. Processes PMIDs that have pass1_status = 'success'
2. Uses FindIt to find PDF URLs (unverified)
3. Stores PDF URLs and metadata in the pmid_results table
4. Handles errors gracefully and tracks processing status
5. Supports resuming from interruptions
6. Provides detailed progress reporting

Usage:
    python pass2_pdf_finding.py --list-id 1
    python pass2_pdf_finding.py --list-id 1 --start-index 1000
    python pass2_pdf_finding.py --list-id 1 --start-index 1000 --end-index 2000
"""

import argparse
import sys
import time
from pathlib import Path
from typing import List, Optional, Tuple

# Import our database utilities
from database import (
    DatabaseManager, PMIDListManager, PMIDResultsManager, 
    ProcessingRunManager, setup_logger
)
from enhanced_analysis import (
    OADetector, FailureAnalyzer
)

# Add parent directory to sys.path for metapub imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from metapub import PubMedFetcher, FindIt
from metapub.exceptions import MetaPubError, NoPDFLink


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


def get_processable_pmids(results_manager: PMIDResultsManager, pmids: List[str]) -> Tuple[List[str], int]:
    """
    Get PMIDs that can be processed in pass2 and find resume index.
    
    Returns:
        Tuple of (processable_pmids, resume_index)
    """
    processable_pmids = []
    processed_pmids = set()
    
    # Get PMIDs that have pass2 status (any final status)
    for status in ['pdf_url_found', 'no_pdf_url', 'no_pdf_link', 'findit_error', 'no_article']:
        status_pmids = results_manager.get_pmids_by_status('pass2_status', status)
        processed_pmids.update(status_pmids)
    
    # Find PMIDs that are successful in pass1 but not yet processed in pass2
    resume_index = 0
    for i, pmid in enumerate(pmids):
        result = results_manager.get_pmid_result(pmid)
        if result and result.get('pass1_status') == 'success':
            if pmid not in processed_pmids:
                if resume_index == 0:
                    resume_index = i  # First unprocessed PMID
                processable_pmids.append(pmid)
    
    return processable_pmids, resume_index


def prompt_for_resume(pmids: List[str], resume_index: int, auto_resume: bool = False) -> int:
    """Prompt user to resume or start fresh."""
    if resume_index == 0:
        return 0  # Nothing to resume from
    
    total = len(pmids)
    
    print(f"\n=== Previous Run Detected ===")
    print(f"Would resume from index {resume_index} (PMID: {pmids[resume_index] if resume_index < len(pmids) else 'END'})")
    print(f"Total PMIDs in list: {total}")
    
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


def find_pdf_urls(list_id: int, start_index: int = 0, end_index: Optional[int] = None,
                  report_every: int = 50, auto_resume: bool = False) -> None:
    """
    Find PDF URLs for PMIDs in the specified list.
    
    Args:
        list_id: Database ID of the PMID list to process
        start_index: Starting index in PMID list
        end_index: Ending index in PMID list (None for all)
        report_every: Report progress every N articles
        auto_resume: Automatically resume without prompting
    """
    
    # Set up logging
    logger = setup_logger("pass2_pdf_finding", "pass2_pdf_finding.log")
    logger.info("=== Starting PDF URL Finding (Pass 2) ===")
    
    try:
        # Initialize database managers
        db_manager = DatabaseManager()
        list_manager = PMIDListManager(db_manager)
        results_manager = PMIDResultsManager(db_manager)
        run_manager = ProcessingRunManager(db_manager)
        
        # Get list info and PMIDs
        list_info = list_manager.get_pmid_list_info(list_id)
        if not list_info:
            raise ValueError(f"PMID list with ID {list_id} not found")
        
        logger.info(f"Processing PMID list: {list_info['name']} (ID: {list_id})")
        
        all_pmids = list_manager.get_pmid_list(list_id)
        if not all_pmids:
            raise ValueError(f"No PMIDs found in list {list_id}")
        
        logger.info(f"Loaded {len(all_pmids)} PMIDs from list")
        
        # Get PMIDs that can be processed (optimized single query)
        processable_pmids = results_manager.get_processable_pmids_for_pass2(list_id)
        
        logger.info(f"Found {len(processable_pmids)} PMIDs ready for PDF finding")
        
        if not processable_pmids:
            print("No PMIDs ready for PDF finding. Run Pass 1 first.")
            return
        
        # For resume functionality, find the first unprocessed PMID in the original list order
        auto_resume_index = 0
        if processable_pmids:
            first_processable_pmid = processable_pmids[0]
            try:
                auto_resume_index = all_pmids.index(first_processable_pmid)
            except ValueError:
                auto_resume_index = 0
        
        # Check for resume opportunity if start_index not manually specified
        actual_start_index = start_index
        if start_index == 0:  # Only auto-resume if start_index wasn't manually set
            actual_start_index = prompt_for_resume(all_pmids, auto_resume_index, auto_resume)
        
        # Apply start/end index filtering to processable PMIDs
        # Since processable_pmids are already in list order, we can slice them directly
        processable_set = set(processable_pmids)
        
        # Filter all_pmids by start/end index, then keep only processable ones
        if end_index is not None:
            filtered_all_pmids = all_pmids[actual_start_index:end_index]
        else:
            filtered_all_pmids = all_pmids[actual_start_index:]
        
        # Keep the order from all_pmids but only include processable PMIDs
        pmids_to_process = [pmid for pmid in filtered_all_pmids if pmid in processable_set]
        
        if not pmids_to_process:
            logger.warning("No processable PMIDs in the specified range")
            print("No processable PMIDs in the specified range")
            return
        
        logger.info(f"Processing {len(pmids_to_process)} PMIDs ready for PDF finding")
        print(f"Processing {len(pmids_to_process)} PMIDs from list '{list_info['name']}'")
        print(f"(These are PMIDs with successful Pass 1 results)")
        
        # Start processing run tracking
        run_id = run_manager.start_processing_run(
            list_id=list_id,
            pass_type='pass2',
            start_index=actual_start_index,
            end_index=actual_start_index + len(pmids_to_process) if end_index else None
        )
        
        # Initialize PubMed fetcher (for article retrieval)
        fetch = PubMedFetcher()
        logger.info("Initialized PubMedFetcher")
        
        # Set up progress reporting
        progress = ProgressReporter(len(pmids_to_process), report_every)
        
        # Process counters
        pdf_found = 0
        no_pdf = 0
        errors = 0
        
        # Process each PMID
        for i, pmid in enumerate(pmids_to_process):
            try:
                logger.debug(f"Processing PMID {pmid}")
                
                # Get existing article data from database
                result = results_manager.get_pmid_result(pmid)
                if not result or result.get('pass1_status') != 'success':
                    logger.warning(f"PMID {pmid} not ready for pass2 processing")
                    continue
                
                # Get the article (should be cached from Pass 1)
                article = fetch.article_by_pmid(pmid)
                
                if not article:
                    logger.warning(f"No article found for PMID {pmid}")
                    results_manager.upsert_pmid_result(
                        pmid=pmid,
                        pass2_status='no_article',
                        pass2_completed_at='CURRENT_TIMESTAMP',
                        pass2_error='Article not found during pass2'
                    )
                    errors += 1
                    continue
                
                # Try to find PDF URL using FindIt (unverified)
                try:
                    findit = FindIt(pmid=pmid, verify=False)
                    pdf_url = findit.url
                    
                    if pdf_url:
                        # Enhanced OA and repository detection
                        repository_type, oa_type = OADetector.detect_repository_type(pdf_url)
                        
                        results_manager.upsert_pmid_result(
                            pmid=pmid,
                            pdf_url=pdf_url,
                            findit_reason='pdf_url_found',
                            repository_detected=repository_type,
                            repository_type=repository_type,
                            oa_type=oa_type,
                            pass2_status='pdf_url_found',
                            pass2_completed_at='CURRENT_TIMESTAMP'
                        )
                        
                        pdf_found += 1
                        logger.debug(f"Found PDF URL for PMID {pmid}: {pdf_url}")
                        
                    else:
                        # Analyze failure reason
                        failure_reason = FailureAnalyzer.categorize_failure(
                            article, 'no_pdf_url', None
                        )
                        
                        results_manager.upsert_pmid_result(
                            pmid=pmid,
                            findit_reason='no_pdf_url',
                            failure_reason_detailed=failure_reason,
                            pass2_status='no_pdf_url',
                            pass2_completed_at='CURRENT_TIMESTAMP'
                        )
                        
                        no_pdf += 1
                        logger.debug(f"No PDF URL found for PMID {pmid}")
                
                except NoPDFLink as e:
                    # Analyze NoPDFLink failure
                    failure_reason = FailureAnalyzer.categorize_failure(
                        article, str(e), f"NoPDFLink: {str(e)}"
                    )
                    
                    results_manager.upsert_pmid_result(
                        pmid=pmid,
                        findit_reason=str(e),
                        failure_reason_detailed=failure_reason,
                        pass2_status='no_pdf_link',
                        pass2_completed_at='CURRENT_TIMESTAMP',
                        pass2_error=f"NoPDFLink: {str(e)}"
                    )
                    
                    no_pdf += 1
                    logger.debug(f"NoPDFLink for PMID {pmid}: {e}")
                
                except Exception as e:
                    # Analyze general FindIt error
                    failure_reason = FailureAnalyzer.categorize_failure(
                        article, 'findit_error', f"FindIt error: {str(e)}"
                    )
                    
                    results_manager.upsert_pmid_result(
                        pmid=pmid,
                        findit_reason='findit_error',
                        failure_reason_detailed=failure_reason,
                        pass2_status='findit_error',
                        pass2_completed_at='CURRENT_TIMESTAMP',
                        pass2_error=f"FindIt error: {str(e)}"
                    )
                    
                    errors += 1
                    logger.error(f"FindIt error for PMID {pmid}: {e}")
                
            except Exception as e:
                results_manager.upsert_pmid_result(
                    pmid=pmid,
                    findit_reason='unexpected_error',
                    pass2_status='findit_error',
                    pass2_completed_at='CURRENT_TIMESTAMP',
                    pass2_error=f"Unexpected error: {str(e)}"
                )
                
                errors += 1
                logger.error(f"Unexpected error for PMID {pmid}: {e}")
            
            # Update processing run
            current = i + 1
            run_manager.update_processing_run(
                run_id=run_id,
                total_processed=current,
                successful=pdf_found,
                failed=errors
            )
            
            # Report progress
            progress.report(
                current, 
                logger, 
                f"PDF URLs: {pdf_found}, No PDF: {no_pdf}, Errors: {errors}"
            )
        
        # Complete processing run
        run_manager.complete_processing_run(run_id, 'completed')
        
        # Final summary
        total_processed = pdf_found + no_pdf + errors
        pdf_rate = (pdf_found / total_processed * 100) if total_processed > 0 else 0
        
        logger.info("=== PDF URL Finding Complete ===")
        logger.info(f"Total processed: {total_processed}")
        logger.info(f"PDF URLs found: {pdf_found}")
        logger.info(f"No PDF available: {no_pdf}")
        logger.info(f"Errors: {errors}")
        logger.info(f"PDF availability rate: {pdf_rate:.1f}%")
        
        print(f"\n=== Pass 2 Complete ===")
        print(f"Processed: {total_processed} PMIDs")
        print(f"✓ PDF URLs found: {pdf_found} ({pdf_rate:.1f}%)")
        print(f"✗ No PDF available: {no_pdf}")
        print(f"⚠ Errors: {errors}")
        print(f"Results stored in database")
        
    except Exception as e:
        logger.error(f"Fatal error in PDF finding process: {e}")
        print(f"Fatal error: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Pass 2: PDF URL Finding for FindIt Coverage Testing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process by file (auto-creates/finds list)
  python pass2_pdf_finding.py --file clinvar_citations.txt
  
  # Process by list name (without extension)
  python pass2_pdf_finding.py --name clinvar_citations
  
  # Process all ready PMIDs in list by ID
  python pass2_pdf_finding.py --list-id 1
  
  # Resume from specific index
  python pass2_pdf_finding.py --name clinvar_citations --start-index 1000
  
  # Process subset
  python pass2_pdf_finding.py --list-id 1 --start-index 1000 --end-index 2000
  
  # Auto-resume without prompting
  python pass2_pdf_finding.py --name clinvar_citations --auto-resume

Note: Only PMIDs with successful Pass 1 results will be processed.
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
        else:
            # Use provided list_id
            list_id = args.list_id
        
        find_pdf_urls(
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