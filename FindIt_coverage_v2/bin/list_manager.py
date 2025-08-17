#!/usr/bin/env python3
"""
List Management Utility for FindIt Coverage Testing

This utility allows you to list, delete, and manage PMID lists in the database.

Usage:
    python list_manager.py list                    # List all lists
    python list_manager.py delete --id 1           # Delete list by ID
    python list_manager.py delete --name clinvar   # Delete list by name
    python list_manager.py info --id 1             # Show list details
    python list_manager.py info --name clinvar     # Show list details by name
"""

import argparse
import sys
from pathlib import Path

# Import our database utilities
from database import DatabaseManager, PMIDListManager, PMIDResultsManager, setup_logger


def list_all_lists(list_manager: PMIDListManager) -> None:
    """List all PMID lists with basic statistics."""
    lists = list_manager.list_pmid_lists()
    
    if not lists:
        print("No PMID lists found in database")
        return
    
    print(f"Found {len(lists)} PMID lists:")
    print()
    
    # Header
    print(f"{'ID':<4} {'Name':<20} {'Total PMIDs':<12} {'Created':<20} {'File Path'}")
    print("-" * 80)
    
    for pmid_list in lists:
        list_id = pmid_list['id']
        name = pmid_list['name'][:19] if len(pmid_list['name']) > 19 else pmid_list['name']
        total = pmid_list['total_pmids'] or 0
        created = pmid_list['created_at'].strftime('%Y-%m-%d %H:%M') if pmid_list['created_at'] else 'Unknown'
        file_path = pmid_list['file_path'] or 'N/A'
        
        # Truncate long file paths
        if len(file_path) > 40:
            file_path = '...' + file_path[-37:]
        
        print(f"{list_id:<4} {name:<20} {total:<12} {created:<20} {file_path}")


def show_list_info(list_manager: PMIDListManager, results_manager: PMIDResultsManager, 
                  list_id: int = None, name: str = None) -> None:
    """Show detailed information about a specific list."""
    if name:
        # Find by name first
        all_lists = list_manager.list_pmid_lists()
        found_list = None
        for pmid_list in all_lists:
            if pmid_list['name'] == name:
                found_list = pmid_list
                list_id = pmid_list['id']
                break
        
        if not found_list:
            print(f"No list found with name: {name}")
            return
    else:
        found_list = list_manager.get_pmid_list_info(list_id)
        if not found_list:
            print(f"No list found with ID: {list_id}")
            return
    
    print(f"=== List Information ===")
    print(f"ID: {found_list['id']}")
    print(f"Name: {found_list['name']}")
    print(f"Description: {found_list['description'] or 'N/A'}")
    print(f"Total PMIDs: {found_list['total_pmids'] or 0}")
    print(f"Created: {found_list['created_at']}")
    print(f"File Path: {found_list['file_path'] or 'N/A'}")
    print()
    
    # Get processing statistics
    pmids = list_manager.get_pmid_list(list_id)
    if pmids:
        print(f"=== Processing Statistics ===")
        print(f"PMIDs in list: {len(pmids)}")
        
        # Count by pass1 status
        pass1_stats = {'success': 0, 'not_found': 0, 'error': 0, 'pending': 0}
        pass2_stats = {'pdf_url_found': 0, 'no_pdf_url': 0, 'no_pdf_link': 0, 'findit_error': 0, 'pending': 0}
        pass3_stats = {'verified': 0, 'failed': 0, 'error': 0, 'pending': 0}
        
        for pmid in pmids:
            result = results_manager.get_pmid_result(pmid)
            if result:
                # Pass 1 status
                status1 = result.get('pass1_status')
                if status1 in pass1_stats:
                    pass1_stats[status1] += 1
                else:
                    pass1_stats['pending'] += 1
                
                # Pass 2 status
                status2 = result.get('pass2_status')
                if status2 in pass2_stats:
                    pass2_stats[status2] += 1
                else:
                    pass2_stats['pending'] += 1
                
                # Pass 3 status
                status3 = result.get('pass3_status')
                if status3 in pass3_stats:
                    pass3_stats[status3] += 1
                else:
                    pass3_stats['pending'] += 1
            else:
                pass1_stats['pending'] += 1
                pass2_stats['pending'] += 1
                pass3_stats['pending'] += 1
        
        print(f"Pass 1 (Article Fetching):")
        print(f"  ✓ Success: {pass1_stats['success']}")
        print(f"  ✗ Not found: {pass1_stats['not_found']}")
        print(f"  ⚠ Error: {pass1_stats['error']}")
        print(f"  ⏳ Pending: {pass1_stats['pending']}")
        
        print(f"Pass 2 (PDF Finding):")
        print(f"  ✓ PDF URL found: {pass2_stats['pdf_url_found']}")
        print(f"  ✗ No PDF: {pass2_stats['no_pdf_url'] + pass2_stats['no_pdf_link']}")
        print(f"  ⚠ Error: {pass2_stats['findit_error']}")
        print(f"  ⏳ Pending: {pass2_stats['pending']}")
        
        print(f"Pass 3 (PDF Verification):")
        print(f"  ✓ Verified: {pass3_stats['verified']}")
        print(f"  ✗ Failed: {pass3_stats['failed']}")
        print(f"  ⚠ Error: {pass3_stats['error']}")
        print(f"  ⏳ Pending: {pass3_stats['pending']}")


def delete_list(list_manager: PMIDListManager, list_id: int = None, 
               name: str = None, force: bool = False) -> None:
    """Delete a PMID list."""
    if name:
        # Show what we're about to delete
        all_lists = list_manager.list_pmid_lists()
        found_list = None
        for pmid_list in all_lists:
            if pmid_list['name'] == name:
                found_list = pmid_list
                list_id = pmid_list['id']
                break
        
        if not found_list:
            print(f"No list found with name: {name}")
            return
    else:
        found_list = list_manager.get_pmid_list_info(list_id)
        if not found_list:
            print(f"No list found with ID: {list_id}")
            return
    
    print(f"About to delete list:")
    print(f"  ID: {found_list['id']}")
    print(f"  Name: {found_list['name']}")
    print(f"  Total PMIDs: {found_list['total_pmids'] or 0}")
    print(f"  Created: {found_list['created_at']}")
    print()
    print("WARNING: This will delete the list and ALL associated processing data!")
    print("This action cannot be undone.")
    
    if not force:
        response = input("Are you sure you want to delete this list? [y/N]: ").strip().lower()
        if response not in ['y', 'yes']:
            print("Deletion cancelled")
            return
    
    # Perform deletion
    if name:
        success = list_manager.delete_pmid_list_by_name(name)
    else:
        success = list_manager.delete_pmid_list(list_id)
    
    if success:
        print(f"✓ Successfully deleted list '{found_list['name']}' (ID: {found_list['id']})")
    else:
        print(f"✗ Failed to delete list")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="PMID List Management Utility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all lists
  python list_manager.py list
  
  # Show detailed info about a list
  python list_manager.py info --name clinvar_citations
  python list_manager.py info --id 1
  
  # Delete a list (with confirmation)
  python list_manager.py delete --name clinvar_citations
  python list_manager.py delete --id 1
  
  # Force delete without confirmation
  python list_manager.py delete --name old_list --force
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all PMID lists')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Show detailed list information')
    info_group = info_parser.add_mutually_exclusive_group(required=True)
    info_group.add_argument('--id', type=int, help='List ID')
    info_group.add_argument('--name', type=str, help='List name')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a PMID list')
    delete_group = delete_parser.add_mutually_exclusive_group(required=True)
    delete_group.add_argument('--id', type=int, help='List ID to delete')
    delete_group.add_argument('--name', type=str, help='List name to delete')
    delete_parser.add_argument('--force', action='store_true', 
                              help='Delete without confirmation')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        # Initialize database managers
        db_manager = DatabaseManager()
        list_manager = PMIDListManager(db_manager)
        results_manager = PMIDResultsManager(db_manager)
        
        if args.command == 'list':
            list_all_lists(list_manager)
        elif args.command == 'info':
            show_list_info(list_manager, results_manager, 
                          list_id=getattr(args, 'id', None), 
                          name=getattr(args, 'name', None))
        elif args.command == 'delete':
            delete_list(list_manager, 
                       list_id=getattr(args, 'id', None),
                       name=getattr(args, 'name', None),
                       force=args.force)
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()