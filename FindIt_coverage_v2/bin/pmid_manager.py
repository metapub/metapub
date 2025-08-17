#!/usr/bin/env python3
"""
PMID List Manager for FindIt Coverage Testing

This script manages PMID lists in the PostgreSQL database, allowing users to:
- Load PMID lists from files
- List existing PMID lists
- Create new PMID lists
- Export PMID lists
- Get statistics on PMID lists

Usage:
    pmid_manager.py load --name "My List" --file path/to/pmids.txt
    pmid_manager.py list
    pmid_manager.py export --list-id 1 --output exported_pmids.txt
    pmid_manager.py stats --list-id 1
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

# Import our database utilities
from database import DatabaseManager, PMIDListManager, PMIDResultsManager, setup_logger


def load_pmid_list(name: str, file_path: str, description: str = None) -> None:
    """Load a PMID list from a file into the database."""
    logger = setup_logger("pmid_manager", "pmid_manager.log")
    
    try:
        # Validate file exists
        if not Path(file_path).exists():
            raise FileNotFoundError(f"PMID file not found: {file_path}")
        
        # Initialize database managers
        db_manager = DatabaseManager()
        list_manager = PMIDListManager(db_manager)
        
        # Create the PMID list entry
        logger.info(f"Creating PMID list: {name}")
        list_id = list_manager.create_pmid_list(
            name=name,
            description=description,
            file_path=str(Path(file_path).absolute())
        )
        
        # Load PMIDs from file
        logger.info(f"Loading PMIDs from file: {file_path}")
        pmid_count = list_manager.load_pmid_list_from_file(list_id, file_path)
        
        print(f"✓ Successfully loaded PMID list '{name}' (ID: {list_id})")
        print(f"  File: {file_path}")
        print(f"  PMIDs loaded: {pmid_count}")
        
        logger.info(f"Successfully loaded {pmid_count} PMIDs into list {list_id}")
        
    except Exception as e:
        logger.error(f"Failed to load PMID list: {e}")
        print(f"Error: {e}")
        sys.exit(1)


def list_pmid_lists() -> None:
    """List all PMID lists in the database."""
    logger = setup_logger("pmid_manager", "pmid_manager.log")
    
    try:
        db_manager = DatabaseManager()
        list_manager = PMIDListManager(db_manager)
        
        lists = list_manager.list_pmid_lists()
        
        if not lists:
            print("No PMID lists found in database.")
            return
        
        print(f"Found {len(lists)} PMID list(s):")
        print()
        
        for pmid_list in lists:
            print(f"ID: {pmid_list['id']}")
            print(f"  Name: {pmid_list['name']}")
            print(f"  PMIDs: {pmid_list['total_pmids']}")
            print(f"  Created: {pmid_list['created_at']}")
            if pmid_list['description']:
                print(f"  Description: {pmid_list['description']}")
            if pmid_list['file_path']:
                print(f"  Source file: {pmid_list['file_path']}")
            print()
        
    except Exception as e:
        logger.error(f"Failed to list PMID lists: {e}")
        print(f"Error: {e}")
        sys.exit(1)


def export_pmid_list(list_id: int, output_file: str) -> None:
    """Export a PMID list to a file."""
    logger = setup_logger("pmid_manager", "pmid_manager.log")
    
    try:
        db_manager = DatabaseManager()
        list_manager = PMIDListManager(db_manager)
        
        # Get list info
        list_info = list_manager.get_pmid_list_info(list_id)
        if not list_info:
            raise ValueError(f"PMID list with ID {list_id} not found")
        
        # Get PMIDs
        pmids = list_manager.get_pmid_list(list_id)
        
        # Write to file
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write(f"# PMID List: {list_info['name']}\n")
            f.write(f"# Exported from FindIt Coverage Database\n")
            f.write(f"# Total PMIDs: {len(pmids)}\n")
            if list_info['description']:
                f.write(f"# Description: {list_info['description']}\n")
            f.write("#\n")
            
            for pmid in pmids:
                f.write(f"{pmid}\n")
        
        print(f"✓ Exported {len(pmids)} PMIDs to {output_file}")
        print(f"  List: {list_info['name']} (ID: {list_id})")
        
        logger.info(f"Exported {len(pmids)} PMIDs from list {list_id} to {output_file}")
        
    except Exception as e:
        logger.error(f"Failed to export PMID list: {e}")
        print(f"Error: {e}")
        sys.exit(1)


def show_pmid_list_stats(list_id: int) -> None:
    """Show statistics for a PMID list."""
    logger = setup_logger("pmid_manager", "pmid_manager.log")
    
    try:
        db_manager = DatabaseManager()
        list_manager = PMIDListManager(db_manager)
        results_manager = PMIDResultsManager(db_manager)
        
        # Get list info
        list_info = list_manager.get_pmid_list_info(list_id)
        if not list_info:
            raise ValueError(f"PMID list with ID {list_id} not found")
        
        # Get PMIDs
        pmids = list_manager.get_pmid_list(list_id)
        
        print(f"PMID List Statistics: {list_info['name']} (ID: {list_id})")
        print("=" * 60)
        print(f"Total PMIDs: {len(pmids)}")
        print(f"Created: {list_info['created_at']}")
        if list_info['description']:
            print(f"Description: {list_info['description']}")
        if list_info['file_path']:
            print(f"Source file: {list_info['file_path']}")
        print()
        
        # Count processing status for PMIDs in this list
        status_counts = {
            'pass1_success': 0,
            'pass1_not_found': 0,
            'pass1_error': 0,
            'pass1_unprocessed': 0,
            'pass2_pdf_found': 0,
            'pass2_no_pdf': 0,
            'pass2_error': 0,
            'pass2_unprocessed': 0,
            'pass3_verified': 0,
            'pass3_failed': 0,
            'pass3_error': 0,
            'pass3_unprocessed': 0
        }
        
        with db_manager.get_cursor() as cursor:
            for pmid in pmids:
                cursor.execute("SELECT * FROM pmid_results WHERE pmid = %s", (pmid,))
                result = cursor.fetchone()
                
                if not result:
                    status_counts['pass1_unprocessed'] += 1
                    status_counts['pass2_unprocessed'] += 1
                    status_counts['pass3_unprocessed'] += 1
                    continue
                
                # Pass 1 status
                pass1_status = result.get('pass1_status')
                if pass1_status == 'success':
                    status_counts['pass1_success'] += 1
                elif pass1_status == 'not_found':
                    status_counts['pass1_not_found'] += 1
                elif pass1_status in ['error', 'metapub_error', 'unexpected_error']:
                    status_counts['pass1_error'] += 1
                else:
                    status_counts['pass1_unprocessed'] += 1
                
                # Pass 2 status
                pass2_status = result.get('pass2_status')
                if pass2_status == 'pdf_url_found':
                    status_counts['pass2_pdf_found'] += 1
                elif pass2_status in ['no_pdf_url', 'no_pdf_link']:
                    status_counts['pass2_no_pdf'] += 1
                elif pass2_status in ['error', 'findit_error', 'no_article']:
                    status_counts['pass2_error'] += 1
                else:
                    status_counts['pass2_unprocessed'] += 1
                
                # Pass 3 status
                pass3_status = result.get('pass3_status')
                if pass3_status == 'verified':
                    status_counts['pass3_verified'] += 1
                elif pass3_status == 'failed':
                    status_counts['pass3_failed'] += 1
                elif pass3_status == 'error':
                    status_counts['pass3_error'] += 1
                else:
                    status_counts['pass3_unprocessed'] += 1
        
        # Display statistics
        print("Processing Status:")
        print("-" * 40)
        
        print("Pass 1 (Article Fetching):")
        print(f"  ✓ Success: {status_counts['pass1_success']}")
        print(f"  ✗ Not found: {status_counts['pass1_not_found']}")
        print(f"  ⚠ Error: {status_counts['pass1_error']}")
        print(f"  ○ Unprocessed: {status_counts['pass1_unprocessed']}")
        
        print("\nPass 2 (PDF URL Finding):")
        print(f"  ✓ PDF URLs found: {status_counts['pass2_pdf_found']}")
        print(f"  ✗ No PDF available: {status_counts['pass2_no_pdf']}")
        print(f"  ⚠ Error: {status_counts['pass2_error']}")
        print(f"  ○ Unprocessed: {status_counts['pass2_unprocessed']}")
        
        print("\nPass 3 (PDF Verification):")
        print(f"  ✓ Verified: {status_counts['pass3_verified']}")
        print(f"  ✗ Failed: {status_counts['pass3_failed']}")
        print(f"  ⚠ Error: {status_counts['pass3_error']}")
        print(f"  ○ Unprocessed: {status_counts['pass3_unprocessed']}")
        
        # Calculate percentages
        total_processed_pass1 = len(pmids) - status_counts['pass1_unprocessed']
        total_processed_pass2 = len(pmids) - status_counts['pass2_unprocessed']
        total_processed_pass3 = len(pmids) - status_counts['pass3_unprocessed']
        
        print("\nSuccess Rates:")
        print("-" * 40)
        if total_processed_pass1 > 0:
            success_rate_1 = (status_counts['pass1_success'] / total_processed_pass1) * 100
            print(f"Pass 1 success rate: {success_rate_1:.1f}%")
        
        if status_counts['pass1_success'] > 0:
            pdf_rate = (status_counts['pass2_pdf_found'] / status_counts['pass1_success']) * 100
            print(f"PDF availability rate: {pdf_rate:.1f}%")
        
        if status_counts['pass2_pdf_found'] > 0:
            verify_rate = (status_counts['pass3_verified'] / status_counts['pass2_pdf_found']) * 100
            print(f"PDF verification rate: {verify_rate:.1f}%")
        
    except Exception as e:
        logger.error(f"Failed to show PMID list stats: {e}")
        print(f"Error: {e}")
        sys.exit(1)


def create_empty_pmid_list(name: str, description: str = None) -> None:
    """Create an empty PMID list."""
    logger = setup_logger("pmid_manager", "pmid_manager.log")
    
    try:
        db_manager = DatabaseManager()
        list_manager = PMIDListManager(db_manager)
        
        list_id = list_manager.create_pmid_list(name=name, description=description)
        
        print(f"✓ Created empty PMID list '{name}' (ID: {list_id})")
        logger.info(f"Created empty PMID list {list_id}: {name}")
        
    except Exception as e:
        logger.error(f"Failed to create PMID list: {e}")
        print(f"Error: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="PMID List Manager for FindIt Coverage Testing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Load PMIDs from file
  python pmid_manager.py load --name "Test Set 1" --file test_pmids.txt
  
  # Load with description
  python pmid_manager.py load --name "Large Sample" --file large_set.txt --description "10k random PMIDs"
  
  # List all PMID lists
  python pmid_manager.py list
  
  # Export PMID list to file
  python pmid_manager.py export --list-id 1 --output exported_pmids.txt
  
  # Show statistics for a list
  python pmid_manager.py stats --list-id 1
  
  # Create empty list
  python pmid_manager.py create --name "Empty List" --description "For manual addition"
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Load command
    load_parser = subparsers.add_parser('load', help='Load PMID list from file')
    load_parser.add_argument('--name', required=True, help='Name for the PMID list')
    load_parser.add_argument('--file', required=True, help='Path to PMID file (one PMID per line)')
    load_parser.add_argument('--description', help='Description of the PMID list')
    
    # List command
    subparsers.add_parser('list', help='List all PMID lists')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export PMID list to file')
    export_parser.add_argument('--list-id', type=int, required=True, help='PMID list ID to export')
    export_parser.add_argument('--output', required=True, help='Output file path')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show statistics for a PMID list')
    stats_parser.add_argument('--list-id', type=int, required=True, help='PMID list ID')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create empty PMID list')
    create_parser.add_argument('--name', required=True, help='Name for the PMID list')
    create_parser.add_argument('--description', help='Description of the PMID list')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'load':
        load_pmid_list(args.name, args.file, args.description)
    elif args.command == 'list':
        list_pmid_lists()
    elif args.command == 'export':
        export_pmid_list(args.list_id, args.output)
    elif args.command == 'stats':
        show_pmid_list_stats(args.list_id)
    elif args.command == 'create':
        create_empty_pmid_list(args.name, args.description)


if __name__ == "__main__":
    main()