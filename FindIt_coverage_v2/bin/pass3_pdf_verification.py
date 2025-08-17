#!/usr/bin/env python3
"""
Pass 3: PDF Verification Script for FindIt Coverage Testing

This script verifies that PDF URLs found in Pass 2 are actually accessible and
working by attempting to download them. It measures download time, file size,
and other metrics to assess the quality of the PDF URLs.

The script:
1. Processes PMIDs that have pass2_status = 'pdf_url_found'
2. Attempts to download PDF URLs with timeout and retry logic
3. Measures download time, file size, HTTP status, content type
4. Stores verification results in the pmid_results table
5. Handles errors gracefully and tracks processing status
6. Supports resuming from interruptions
7. Provides detailed progress reporting

Usage:
    python pass3_pdf_verification.py --list-id 1
    python pass3_pdf_verification.py --list-id 1 --start-index 1000
    python pass3_pdf_verification.py --list-id 1 --start-index 1000 --end-index 2000
"""

import argparse
import sys
import time
import requests
from pathlib import Path
from typing import List, Optional, Tuple
from urllib.parse import urlparse

# Import our database utilities
from database import (
    DatabaseManager, PMIDListManager, PMIDResultsManager, 
    ProcessingRunManager, setup_logger
)
from enhanced_analysis import OADetector


class ProgressReporter:
    """Progress reporting utility."""
    
    def __init__(self, total: int, report_every: int = 25):
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


def get_verifiable_pmids(results_manager: PMIDResultsManager, pmids: List[str]) -> Tuple[List[str], int]:
    """
    Get PMIDs that can be verified in pass3 and find resume index.
    
    Returns:
        Tuple of (verifiable_pmids, resume_index)
    """
    verifiable_pmids = []
    processed_pmids = set()
    
    # Get PMIDs that have pass3 status (any final status)
    for status in ['verified', 'failed', 'error']:
        status_pmids = results_manager.get_pmids_by_status('pass3_status', status)
        processed_pmids.update(status_pmids)
    
    # Find PMIDs that have PDF URLs but aren't yet verified
    resume_index = 0
    for i, pmid in enumerate(pmids):
        result = results_manager.get_pmid_result(pmid)
        if result and result.get('pass2_status') == 'pdf_url_found' and result.get('pdf_url'):
            if pmid not in processed_pmids:
                if resume_index == 0:
                    resume_index = i  # First unprocessed PMID
                verifiable_pmids.append(pmid)
    
    return verifiable_pmids, resume_index


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


def verify_pdf_url(url: str, timeout: int = 30, max_retries: int = 2) -> Tuple[bool, dict]:
    """
    Verify a PDF URL by attempting to download it.
    
    Args:
        url: PDF URL to verify
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts
        
    Returns:
        Tuple of (success, metrics_dict)
    """
    metrics = {
        'http_status_code': None,
        'content_type': None,
        'file_size': None,
        'time_to_pdf': None,
        'error_message': None
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for attempt in range(max_retries + 1):
        try:
            start_time = time.time()
            
            response = requests.get(
                url, 
                headers=headers, 
                timeout=timeout,
                stream=True,
                allow_redirects=True
            )
            
            end_time = time.time()
            download_time = end_time - start_time
            
            metrics['http_status_code'] = response.status_code
            metrics['content_type'] = response.headers.get('content-type', '').lower()
            metrics['time_to_pdf'] = round(download_time, 3)
            
            if response.status_code == 200:
                # Try to get content length
                content_length = response.headers.get('content-length')
                if content_length:
                    metrics['file_size'] = int(content_length)
                else:
                    # Download first chunk to estimate size
                    chunk = next(response.iter_content(chunk_size=8192), b'')
                    if chunk:
                        metrics['file_size'] = len(chunk)
                
                # Check if content type suggests it's a PDF
                content_type = metrics['content_type']
                is_pdf_content = (
                    'pdf' in content_type or 
                    'application/pdf' in content_type or
                    content_type.startswith('application/') and 'pdf' in content_type
                )
                
                # If we got data and it looks like a PDF, consider it successful
                if is_pdf_content or metrics['file_size'] and metrics['file_size'] > 1000:
                    return True, metrics
                else:
                    metrics['error_message'] = f"Content type '{content_type}' doesn't appear to be PDF"
                    return False, metrics
            else:
                metrics['error_message'] = f"HTTP {response.status_code}: {response.reason}"
                return False, metrics
                
        except requests.exceptions.Timeout:
            metrics['error_message'] = f"Timeout after {timeout}s (attempt {attempt + 1})"
            if attempt == max_retries:
                return False, metrics
            time.sleep(1)  # Brief delay before retry
            
        except requests.exceptions.RequestException as e:
            metrics['error_message'] = f"Request error: {str(e)} (attempt {attempt + 1})"
            if attempt == max_retries:
                return False, metrics
            time.sleep(1)  # Brief delay before retry
            
        except Exception as e:
            metrics['error_message'] = f"Unexpected error: {str(e)}"
            return False, metrics
    
    return False, metrics


def verify_pdf_urls(list_id: int, start_index: int = 0, end_index: Optional[int] = None,
                   report_every: int = 25, timeout: int = 30, auto_resume: bool = False) -> None:
    """
    Verify PDF URLs for PMIDs in the specified list.
    
    Args:
        list_id: Database ID of the PMID list to process
        start_index: Starting index in PMID list
        end_index: Ending index in PMID list (None for all)
        report_every: Report progress every N articles
        timeout: HTTP request timeout in seconds
        auto_resume: Automatically resume without prompting
    """
    
    # Set up logging
    logger = setup_logger("pass3_pdf_verification", "pass3_pdf_verification.log")
    logger.info("=== Starting PDF Verification (Pass 3) ===")
    
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
        
        # Get PMIDs that can be verified (optimized single query)
        verifiable_pmids = results_manager.get_processable_pmids_for_pass3(list_id)
        
        logger.info(f"Found {len(verifiable_pmids)} PMIDs ready for PDF verification")
        
        if not verifiable_pmids:
            print("No PMIDs ready for PDF verification. Run Pass 2 first.")
            return
        
        # For resume functionality, find the first unprocessed PMID in the original list order
        auto_resume_index = 0
        if verifiable_pmids:
            first_verifiable_pmid = verifiable_pmids[0]
            try:
                auto_resume_index = all_pmids.index(first_verifiable_pmid)
            except ValueError:
                auto_resume_index = 0
        
        # Check for resume opportunity if start_index not manually specified
        actual_start_index = start_index
        if start_index == 0:  # Only auto-resume if start_index wasn't manually set
            actual_start_index = prompt_for_resume(all_pmids, auto_resume_index, auto_resume)
        
        # Apply start/end index filtering to verifiable PMIDs
        # Since verifiable_pmids are already in list order, we can slice them directly
        verifiable_set = set(verifiable_pmids)
        
        # Filter all_pmids by start/end index, then keep only verifiable ones
        if end_index is not None:
            filtered_all_pmids = all_pmids[actual_start_index:end_index]
        else:
            filtered_all_pmids = all_pmids[actual_start_index:]
        
        # Keep the order from all_pmids but only include verifiable PMIDs
        pmids_to_process = [pmid for pmid in filtered_all_pmids if pmid in verifiable_set]
        
        if not pmids_to_process:
            logger.warning("No verifiable PMIDs in the specified range")
            print("No verifiable PMIDs in the specified range")
            return
        
        logger.info(f"Processing {len(pmids_to_process)} PMIDs ready for PDF verification")
        print(f"Processing {len(pmids_to_process)} PMIDs from list '{list_info['name']}'")
        print(f"(These are PMIDs with PDF URLs found in Pass 2)")
        
        # Start processing run tracking
        run_id = run_manager.start_processing_run(
            list_id=list_id,
            pass_type='pass3',
            start_index=actual_start_index,
            end_index=actual_start_index + len(pmids_to_process) if end_index else None
        )
        
        # Set up progress reporting
        progress = ProgressReporter(len(pmids_to_process), report_every)
        
        # Process counters
        verified = 0
        failed = 0
        errors = 0
        
        # Process each PMID
        for i, pmid in enumerate(pmids_to_process):
            try:
                logger.debug(f"Processing PMID {pmid}")
                
                # Get existing result with PDF URL
                result = results_manager.get_pmid_result(pmid)
                if not result or result.get('pass2_status') != 'pdf_url_found' or not result.get('pdf_url'):
                    logger.warning(f"PMID {pmid} not ready for pass3 processing")
                    continue
                
                pdf_url = result['pdf_url']
                logger.debug(f"Verifying PDF URL for PMID {pmid}: {pdf_url}")
                
                # Verify the PDF URL
                success, metrics = verify_pdf_url(pdf_url, timeout=timeout)
                
                if success:
                    # Enhanced OA analysis with content type
                    content_analysis = OADetector.analyze_content_type(
                        metrics['content_type'], pdf_url
                    )
                    
                    # Get existing OA type from database or detect it
                    existing_result = results_manager.get_pmid_result(pmid)
                    current_oa_type = existing_result.get('oa_type') if existing_result else None
                    
                    # If OA type is still unknown, try to refine it based on verification
                    if current_oa_type == 'unknown' and content_analysis.get('repository_hint'):
                        if content_analysis['repository_hint'] == 'PMC':
                            current_oa_type = 'green'
                    
                    results_manager.upsert_pmid_result(
                        pmid=pmid,
                        verified=True,
                        time_to_pdf=metrics['time_to_pdf'],
                        http_status_code=metrics['http_status_code'],
                        content_type=metrics['content_type'],
                        file_size=metrics['file_size'],
                        oa_type=current_oa_type,
                        pass3_status='verified',
                        pass3_completed_at='CURRENT_TIMESTAMP'
                    )
                    
                    verified += 1
                    logger.debug(f"Successfully verified PDF for PMID {pmid} in {metrics['time_to_pdf']}s")
                    
                else:
                    results_manager.upsert_pmid_result(
                        pmid=pmid,
                        verified=False,
                        time_to_pdf=metrics['time_to_pdf'],
                        http_status_code=metrics['http_status_code'],
                        content_type=metrics['content_type'],
                        file_size=metrics['file_size'],
                        pass3_status='failed',
                        pass3_completed_at='CURRENT_TIMESTAMP',
                        pass3_error=metrics['error_message']
                    )
                    
                    failed += 1
                    logger.debug(f"Failed to verify PDF for PMID {pmid}: {metrics['error_message']}")
                
            except Exception as e:
                results_manager.upsert_pmid_result(
                    pmid=pmid,
                    verified=False,
                    pass3_status='error',
                    pass3_completed_at='CURRENT_TIMESTAMP',
                    pass3_error=f"Unexpected error: {str(e)}"
                )
                
                errors += 1
                logger.error(f"Unexpected error for PMID {pmid}: {e}")
            
            # Update processing run
            current = i + 1
            run_manager.update_processing_run(
                run_id=run_id,
                total_processed=current,
                successful=verified,
                failed=failed + errors
            )
            
            # Report progress
            progress.report(
                current, 
                logger, 
                f"Verified: {verified}, Failed: {failed}, Errors: {errors}"
            )
        
        # Complete processing run
        run_manager.complete_processing_run(run_id, 'completed')
        
        # Final summary
        total_processed = verified + failed + errors
        verification_rate = (verified / total_processed * 100) if total_processed > 0 else 0
        
        logger.info("=== PDF Verification Complete ===")
        logger.info(f"Total processed: {total_processed}")
        logger.info(f"Verified: {verified}")
        logger.info(f"Failed: {failed}")
        logger.info(f"Errors: {errors}")
        logger.info(f"Verification rate: {verification_rate:.1f}%")
        
        print(f"\n=== Pass 3 Complete ===")
        print(f"Processed: {total_processed} PMIDs")
        print(f"✓ Verified: {verified} ({verification_rate:.1f}%)")
        print(f"✗ Failed: {failed}")
        print(f"⚠ Errors: {errors}")
        print(f"Results stored in database")
        
    except Exception as e:
        logger.error(f"Fatal error in PDF verification process: {e}")
        print(f"Fatal error: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Pass 3: PDF Verification for FindIt Coverage Testing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Verify by file (auto-creates/finds list)
  python pass3_pdf_verification.py --file clinvar_citations.txt
  
  # Verify by list name (without extension)
  python pass3_pdf_verification.py --name clinvar_citations
  
  # Verify all PDF URLs in list by ID
  python pass3_pdf_verification.py --list-id 1
  
  # Resume from specific index
  python pass3_pdf_verification.py --name clinvar_citations --start-index 1000
  
  # Process subset
  python pass3_pdf_verification.py --list-id 1 --start-index 1000 --end-index 2000
  
  # Auto-resume with custom timeout
  python pass3_pdf_verification.py --name clinvar_citations --auto-resume --timeout 60

Note: Only PMIDs with PDF URLs found in Pass 2 will be processed.
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
        default=25,
        help='Report progress every N articles'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=30,
        help='HTTP request timeout in seconds'
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
        
        verify_pdf_urls(
            list_id=list_id,
            start_index=args.start_index,
            end_index=args.end_index,
            report_every=args.report_every,
            timeout=args.timeout,
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