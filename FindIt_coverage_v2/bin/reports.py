#!/usr/bin/env python3
"""
Reporting and Analytics Script for FindIt Coverage Testing

This script generates various reports and statistics from the PostgreSQL database
to help analyze FindIt coverage performance across different dimensions.

Available reports:
- Overall summary statistics
- Publisher-specific performance
- Journal-specific performance
- Processing run history
- Failed URL analysis
- Export data for external analysis

Usage:
    python reports.py summary
    python reports.py publisher-stats
    python reports.py journal-stats --top 20
    python reports.py export --list-id 1 --format csv
"""

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Import our database utilities
from database import (
    DatabaseManager, PMIDListManager, PMIDResultsManager,
    ProcessingRunManager, MeshTermManager, setup_logger
)


def print_summary_report(db_manager: DatabaseManager) -> None:
    """Print overall summary statistics."""
    results_manager = PMIDResultsManager(db_manager)
    
    print("=" * 60)
    print("FindIt Coverage Testing - Summary Report")
    print("=" * 60)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Get overall statistics
        stats = results_manager.get_processing_statistics()
        
        print("Overall Statistics:")
        print("-" * 40)
        print(f"Total PMIDs in database: {stats.get('total_pmids', 0):,}")
        print(f"Pass 1 successful: {stats.get('pass1_success', 0):,}")
        print(f"PDF URLs found: {stats.get('pdf_urls_found', 0):,}")
        print(f"PDFs verified: {stats.get('verified_pdfs', 0):,}")
        print()
        
        print("Success Rates:")
        print("-" * 40)
        print(f"PDF availability rate: {stats.get('pdf_availability_rate', 0):.1f}%")
        print(f"Verification success rate: {stats.get('verification_success_rate', 0):.1f}%")
        print()
        
        # Get detailed breakdown
        with db_manager.get_cursor() as cursor:
            # Pass 1 breakdown
            cursor.execute("""
                SELECT pass1_status, COUNT(*) as count 
                FROM pmid_results 
                WHERE pass1_status IS NOT NULL 
                GROUP BY pass1_status 
                ORDER BY count DESC
            """)
            pass1_results = cursor.fetchall()
            
            if pass1_results:
                print("Pass 1 (Article Fetching) Breakdown:")
                print("-" * 40)
                for row in pass1_results:
                    print(f"  {row['pass1_status']}: {row['count']:,}")
                print()
            
            # Pass 2 breakdown
            cursor.execute("""
                SELECT pass2_status, COUNT(*) as count 
                FROM pmid_results 
                WHERE pass2_status IS NOT NULL 
                GROUP BY pass2_status 
                ORDER BY count DESC
            """)
            pass2_results = cursor.fetchall()
            
            if pass2_results:
                print("Pass 2 (PDF Finding) Breakdown:")
                print("-" * 40)
                for row in pass2_results:
                    print(f"  {row['pass2_status']}: {row['count']:,}")
                print()
            
            # Pass 3 breakdown
            cursor.execute("""
                SELECT pass3_status, COUNT(*) as count 
                FROM pmid_results 
                WHERE pass3_status IS NOT NULL 
                GROUP BY pass3_status 
                ORDER BY count DESC
            """)
            pass3_results = cursor.fetchall()
            
            if pass3_results:
                print("Pass 3 (PDF Verification) Breakdown:")
                print("-" * 40)
                for row in pass3_results:
                    print(f"  {row['pass3_status']}: {row['count']:,}")
                print()
            
            # Performance metrics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_verified,
                    ROUND(AVG(time_to_pdf)::numeric, 3) as avg_download_time,
                    ROUND(MIN(time_to_pdf)::numeric, 3) as min_download_time,
                    ROUND(MAX(time_to_pdf)::numeric, 3) as max_download_time,
                    ROUND(AVG(file_size::numeric / 1024 / 1024), 2) as avg_file_size_mb
                FROM pmid_results 
                WHERE verified = true AND time_to_pdf IS NOT NULL
            """)
            perf_stats = cursor.fetchone()
            
            if perf_stats and perf_stats['total_verified'] > 0:
                print("Performance Metrics (Verified PDFs):")
                print("-" * 40)
                print(f"Average download time: {perf_stats['avg_download_time']}s")
                print(f"Min download time: {perf_stats['min_download_time']}s")
                print(f"Max download time: {perf_stats['max_download_time']}s")
                if perf_stats['avg_file_size_mb']:
                    print(f"Average file size: {perf_stats['avg_file_size_mb']:.2f} MB")
                print()
        
    except Exception as e:
        print(f"Error generating summary: {e}")


def print_publisher_stats(db_manager: DatabaseManager, top_n: int = 10) -> None:
    """Print publisher-specific statistics."""
    results_manager = PMIDResultsManager(db_manager)
    
    print("=" * 80)
    print(f"Publisher Performance Report (Top {top_n})")
    print("=" * 80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        publisher_stats = results_manager.get_publisher_statistics()
        
        if not publisher_stats:
            print("No publisher statistics available.")
            return
        
        # Limit to top N
        top_publishers = publisher_stats[:top_n]
        
        print(f"{'Publisher':<30} {'Articles':<8} {'PDF Rate':<9} {'Verify Rate':<11} {'Avg Time':<9}")
        print("-" * 80)
        
        for pub in top_publishers:
            publisher = pub['publisher'] or 'Unknown'
            if len(publisher) > 28:
                publisher = publisher[:25] + "..."
            
            pdf_rate = f"{pub['pdf_availability_rate'] or 0:.1f}%"
            verify_rate = f"{pub['verification_success_rate'] or 0:.1f}%"
            avg_time = f"{pub['avg_download_time'] or 0:.2f}s" if pub['avg_download_time'] else "N/A"
            
            print(f"{publisher:<30} {pub['total_articles']:<8} {pdf_rate:<9} {verify_rate:<11} {avg_time:<9}")
        
        print()
        
    except Exception as e:
        print(f"Error generating publisher stats: {e}")


def print_journal_stats(db_manager: DatabaseManager, top_n: int = 20) -> None:
    """Print journal-specific statistics."""
    print("=" * 90)
    print(f"Journal Performance Report (Top {top_n})")
    print("=" * 90)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        with db_manager.get_cursor() as cursor:
            cursor.execute("""
                SELECT 
                    journal_name,
                    COUNT(*) as total_articles,
                    COUNT(CASE WHEN pass2_status = 'pdf_url_found' THEN 1 END) as pdf_urls_found,
                    COUNT(CASE WHEN verified = TRUE THEN 1 END) as verified_pdfs,
                    ROUND(
                        COUNT(CASE WHEN pass2_status = 'pdf_url_found' THEN 1 END) * 100.0 / COUNT(*), 2
                    ) as pdf_availability_rate,
                    ROUND(
                        COUNT(CASE WHEN verified = TRUE THEN 1 END) * 100.0 / 
                        NULLIF(COUNT(CASE WHEN pass2_status = 'pdf_url_found' THEN 1 END), 0), 2
                    ) as verification_success_rate,
                    ROUND(AVG(time_to_pdf), 3) as avg_download_time
                FROM pmid_results 
                WHERE journal_name IS NOT NULL 
                GROUP BY journal_name 
                HAVING COUNT(*) >= 5  -- Only journals with at least 5 articles
                ORDER BY total_articles DESC
                LIMIT %s
            """, (top_n,))
            
            results = cursor.fetchall()
            
            if not results:
                print("No journal statistics available.")
                return
            
            print(f"{'Journal':<40} {'Articles':<8} {'PDF Rate':<9} {'Verify Rate':<11} {'Avg Time':<9}")
            print("-" * 90)
            
            for row in results:
                journal = row['journal_name'] or 'Unknown'
                if len(journal) > 38:
                    journal = journal[:35] + "..."
                
                pdf_rate = f"{row['pdf_availability_rate'] or 0:.1f}%"
                verify_rate = f"{row['verification_success_rate'] or 0:.1f}%"
                avg_time = f"{row['avg_download_time'] or 0:.2f}s" if row['avg_download_time'] else "N/A"
                
                print(f"{journal:<40} {row['total_articles']:<8} {pdf_rate:<9} {verify_rate:<11} {avg_time:<9}")
            
            print()
        
    except Exception as e:
        print(f"Error generating journal stats: {e}")


def print_processing_runs(db_manager: DatabaseManager) -> None:
    """Print processing run history."""
    print("=" * 100)
    print("Processing Run History")
    print("=" * 100)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        with db_manager.get_cursor() as cursor:
            cursor.execute("""
                SELECT 
                    pr.id,
                    pl.name as list_name,
                    pr.pass_type,
                    pr.status,
                    pr.total_processed,
                    pr.successful,
                    pr.failed,
                    pr.started_at,
                    pr.completed_at,
                    EXTRACT(EPOCH FROM (pr.completed_at - pr.started_at)) as duration_seconds
                FROM processing_runs pr
                JOIN pmid_lists pl ON pr.list_id = pl.id
                ORDER BY pr.started_at DESC
                LIMIT 20
            """)
            
            results = cursor.fetchall()
            
            if not results:
                print("No processing runs found.")
                return
            
            print(f"{'ID':<4} {'List':<20} {'Pass':<6} {'Status':<10} {'Processed':<9} {'Success':<7} {'Failed':<6} {'Duration':<8} {'Started':<16}")
            print("-" * 100)
            
            for row in results:
                list_name = row['list_name'] or 'Unknown'
                if len(list_name) > 18:
                    list_name = list_name[:15] + "..."
                
                duration = ""
                if row['duration_seconds']:
                    minutes = int(row['duration_seconds'] // 60)
                    seconds = int(row['duration_seconds'] % 60)
                    duration = f"{minutes}m{seconds}s"
                
                started = row['started_at'].strftime('%m-%d %H:%M') if row['started_at'] else ""
                
                print(f"{row['id']:<4} {list_name:<20} {row['pass_type']:<6} {row['status']:<10} "
                      f"{row['total_processed'] or 0:<9} {row['successful'] or 0:<7} {row['failed'] or 0:<6} "
                      f"{duration:<8} {started:<16}")
            
            print()
        
    except Exception as e:
        print(f"Error generating processing run history: {e}")


def export_data(db_manager: DatabaseManager, list_id: Optional[int] = None, 
               format_type: str = 'csv', output_file: Optional[str] = None) -> None:
    """Export data to CSV or JSON format."""
    
    try:
        # Build query
        where_clause = ""
        params = []
        
        if list_id:
            # Get PMIDs for the specific list
            list_manager = PMIDListManager(db_manager)
            pmids = list_manager.get_pmid_list(list_id)
            if not pmids:
                print(f"No PMIDs found for list ID {list_id}")
                return
            
            where_clause = "WHERE pmid = ANY(%s)"
            params = [pmids]
        
        with db_manager.get_cursor() as cursor:
            cursor.execute(f"""
                SELECT 
                    pmid,
                    title,
                    journal_name,
                    publisher,
                    doi,
                    pii,
                    pmc,
                    pdf_url,
                    findit_reason,
                    verified,
                    time_to_pdf,
                    http_status_code,
                    content_type,
                    file_size,
                    is_good_pmid,
                    pass1_status,
                    pass2_status,
                    pass3_status,
                    pass1_error,
                    pass2_error,
                    pass3_error,
                    created_at,
                    updated_at,
                    pass1_completed_at,
                    pass2_completed_at,
                    pass3_completed_at
                FROM pmid_results
                {where_clause}
                ORDER BY pmid
            """, params)
            
            results = cursor.fetchall()
            
            if not results:
                print("No data to export")
                return
            
            # Generate filename if not provided
            if not output_file:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                list_suffix = f"_list{list_id}" if list_id else "_all"
                output_file = f"findit_results{list_suffix}_{timestamp}.{format_type}"
            
            output_path = Path(__file__).parent.parent / "data" / "exports" / output_file
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if format_type.lower() == 'csv':
                with open(output_path, 'w', newline='', encoding='utf-8') as f:
                    if results:
                        writer = csv.DictWriter(f, fieldnames=results[0].keys())
                        writer.writeheader()
                        for row in results:
                            writer.writerow(dict(row))
            
            elif format_type.lower() == 'json':
                # Convert datetime objects to strings for JSON serialization
                json_data = []
                for row in results:
                    row_dict = dict(row)
                    for key, value in row_dict.items():
                        if hasattr(value, 'isoformat'):
                            row_dict[key] = value.isoformat()
                    json_data.append(row_dict)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            else:
                print(f"Unsupported format: {format_type}")
                return
            
            print(f"✓ Exported {len(results)} records to {output_path}")
        
    except Exception as e:
        print(f"Error exporting data: {e}")


def print_oa_analysis(db_manager: DatabaseManager) -> None:
    """Print Open Access analysis report."""
    print("=" * 80)
    print("Open Access Analysis Report")
    print("=" * 80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        with db_manager.get_cursor() as cursor:
            cursor.execute("SELECT * FROM oa_access_analysis ORDER BY total_articles DESC")
            results = cursor.fetchall()
            
            if not results:
                print("No Open Access data available.")
                return
            
            print(f"{'OA Type':<12} {'Repository':<20} {'Articles':<8} {'Verified':<8} {'Avg Time':<9}")
            print("-" * 80)
            
            total_oa_articles = 0
            total_verified = 0
            
            for row in results:
                oa_type = row['oa_type'] or 'unknown'
                repo_type = row['repository_type'] or 'unknown'
                if len(repo_type) > 18:
                    repo_type = repo_type[:15] + "..."
                
                avg_time = f"{row['avg_download_time'] or 0:.2f}s" if row['avg_download_time'] else "N/A"
                
                print(f"{oa_type:<12} {repo_type:<20} {row['total_articles']:<8} {row['verified_articles']:<8} {avg_time:<9}")
                
                total_oa_articles += row['total_articles']
                total_verified += row['verified_articles']
            
            print()
            print(f"Total Open Access articles: {total_oa_articles:,}")
            print(f"Total verified OA articles: {total_verified:,}")
            print()
    
    except Exception as e:
        print(f"Error generating OA analysis: {e}")


def print_doi_coverage_analysis(db_manager: DatabaseManager) -> None:
    """Print DOI coverage analysis."""
    print("=" * 70)
    print("DOI Coverage Analysis")
    print("=" * 70)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        with db_manager.get_cursor() as cursor:
            cursor.execute("SELECT * FROM doi_coverage_analysis ORDER BY total_pmids DESC")
            results = cursor.fetchall()
            
            if not results:
                print("No DOI coverage data available.")
                return
            
            print(f"{'DOI Status':<12} {'Total':<8} {'Pass1 OK':<9} {'PDF Found':<10} {'Verified':<9} {'PDF Rate':<9} {'Verify Rate':<11}")
            print("-" * 70)
            
            for row in results:
                doi_status = row['doi_status']
                pdf_rate = f"{row['pdf_success_rate'] or 0:.1f}%" if row['pdf_success_rate'] else "N/A"
                verify_rate = f"{row['verification_rate'] or 0:.1f}%" if row['verification_rate'] else "N/A"
                
                print(f"{doi_status:<12} {row['total_pmids']:<8} {row['pass1_success']:<9} "
                      f"{row['pdf_found']:<10} {row['verified']:<9} {pdf_rate:<9} {verify_rate:<11}")
            
            print()
    
    except Exception as e:
        print(f"Error generating DOI coverage analysis: {e}")


def print_failure_analysis(db_manager: DatabaseManager) -> None:
    """Print detailed failure analysis."""
    print("=" * 80)
    print("Failure Analysis Report")
    print("=" * 80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        with db_manager.get_cursor() as cursor:
            cursor.execute("SELECT * FROM failure_analysis ORDER BY failure_count DESC")
            results = cursor.fetchall()
            
            if not results:
                print("No failure data available.")
                return
            
            print(f"{'Failure Reason':<35} {'Count':<8} {'%Total':<7} {'No DOI':<7} {'%No DOI':<8}")
            print("-" * 80)
            
            for row in results:
                reason = row['failure_reason_detailed'] or 'unknown'
                if len(reason) > 33:
                    reason = reason[:30] + "..."
                
                pct_total = f"{row['failure_percentage'] or 0:.1f}%"
                pct_no_doi = f"{row['pct_failures_without_doi'] or 0:.1f}%"
                
                print(f"{reason:<35} {row['failure_count']:<8} {pct_total:<7} "
                      f"{row['failures_without_doi']:<7} {pct_no_doi:<8}")
            
            print()
    
    except Exception as e:
        print(f"Error generating failure analysis: {e}")


def print_yearly_trends(db_manager: DatabaseManager) -> None:
    """Print publication year trends."""
    print("=" * 90)
    print("Publication Year Trends")
    print("=" * 90)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        with db_manager.get_cursor() as cursor:
            cursor.execute("SELECT * FROM yearly_trends_analysis ORDER BY publication_year DESC LIMIT 15")
            results = cursor.fetchall()
            
            if not results:
                print("No yearly trends data available.")
                return
            
            print(f"{'Year':<6} {'Articles':<8} {'PDF Found':<10} {'Verified':<9} {'Green OA':<9} {'Gold OA':<8} {'PDF Rate':<9} {'OA %':<7}")
            print("-" * 90)
            
            for row in results:
                year = row['publication_year'] or 'Unknown'
                pdf_rate = f"{row['pdf_success_rate'] or 0:.1f}%"
                oa_pct = f"{row['oa_percentage'] or 0:.1f}%" if row['oa_percentage'] else "N/A"
                
                print(f"{year:<6} {row['total_articles']:<8} {row['pdf_found']:<10} "
                      f"{row['verified']:<9} {row['green_oa']:<9} {row['gold_oa']:<8} {pdf_rate:<9} {oa_pct:<7}")
            
            print()
    
    except Exception as e:
        print(f"Error generating yearly trends: {e}")


def print_mesh_analysis(db_manager: DatabaseManager, top_n: int = 20) -> None:
    """Print MeSH term analysis report."""
    print("=" * 90)
    print(f"MeSH Term Analysis (Top {top_n})")
    print("=" * 90)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        mesh_manager = MeshTermManager(db_manager)
        
        # Overall MeSH statistics
        mesh_stats = mesh_manager.get_mesh_statistics()
        print("Overall MeSH Statistics:")
        print("-" * 40)
        print(f"Articles with MeSH terms: {mesh_stats.get('articles_with_mesh', 0):,}")
        print(f"Total MeSH assignments: {mesh_stats.get('total_mesh_assignments', 0):,}")
        print(f"Unique MeSH terms: {mesh_stats.get('unique_mesh_terms', 0):,}")
        print(f"Major topic assignments: {mesh_stats.get('major_topic_assignments', 0):,}")
        print(f"Qualified assignments: {mesh_stats.get('qualified_assignments', 0):,}")
        print()
        
        # Major MeSH topics analysis
        with db_manager.get_cursor() as cursor:
            cursor.execute(f"SELECT * FROM major_mesh_topics ORDER BY article_count DESC LIMIT {top_n}")
            major_topics = cursor.fetchall()
            
            if major_topics:
                print("Major MeSH Topics (Primary Research Focus):")
                print("-" * 90)
                print(f"{'MeSH Term':<35} {'Articles':<8} {'Green OA':<9} {'Gold OA':<8} {'Verified':<9} {'OA %':<7} {'Avg Year':<8}")
                print("-" * 90)
                
                for row in major_topics:
                    mesh_term = row['mesh_term'] or 'Unknown'
                    if len(mesh_term) > 33:
                        mesh_term = mesh_term[:30] + "..."
                    
                    oa_pct = f"{row['oa_percentage'] or 0:.1f}%"
                    avg_year = str(int(row['avg_publication_year'])) if row['avg_publication_year'] else "N/A"
                    
                    print(f"{mesh_term:<35} {row['article_count']:<8} {row['green_oa_count']:<9} "
                          f"{row['gold_oa_count']:<8} {row['verified_count']:<9} {oa_pct:<7} {avg_year:<8}")
                print()
        
        # MeSH qualifiers analysis
        with db_manager.get_cursor() as cursor:
            cursor.execute("SELECT * FROM mesh_qualifier_analysis ORDER BY article_count DESC LIMIT 15")
            qualifiers = cursor.fetchall()
            
            if qualifiers:
                print("Most Common MeSH Qualifiers (Research Approaches):")
                print("-" * 60)
                print(f"{'Qualifier':<25} {'Articles':<8} {'OA Count':<9} {'OA %':<7}")
                print("-" * 60)
                
                for row in qualifiers:
                    qualifier = row['qualifier'] or 'Unknown'
                    if len(qualifier) > 23:
                        qualifier = qualifier[:20] + "..."
                    
                    oa_pct = f"{row['oa_percentage'] or 0:.1f}%"
                    
                    print(f"{qualifier:<25} {row['article_count']:<8} {row['oa_count']:<9} {oa_pct:<7}")
                print()
    
    except Exception as e:
        print(f"Error generating MeSH analysis: {e}")


def print_mesh_oa_comparison(db_manager: DatabaseManager) -> None:
    """Compare OA rates across different MeSH topics."""
    print("=" * 80)
    print("MeSH Topics: Open Access Comparison")
    print("=" * 80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        with db_manager.get_cursor() as cursor:
            # Find topics with significant OA differences
            cursor.execute("""
                SELECT 
                    mt.mesh_term,
                    COUNT(DISTINCT mt.pmid) as total_articles,
                    COUNT(CASE WHEN pr.oa_type IN ('green', 'gold') THEN 1 END) as oa_articles,
                    COUNT(CASE WHEN pr.oa_type NOT IN ('green', 'gold', 'unknown') OR pr.oa_type IS NULL THEN 1 END) as closed_articles,
                    ROUND(
                        COUNT(CASE WHEN pr.oa_type IN ('green', 'gold') THEN 1 END) * 100.0 / COUNT(*), 1
                    ) as oa_percentage
                FROM mesh_terms mt
                JOIN pmid_results pr ON mt.pmid = pr.pmid
                WHERE mt.is_major_topic = TRUE
                AND pr.pass1_status = 'success'
                GROUP BY mt.mesh_term
                HAVING COUNT(DISTINCT mt.pmid) >= 5
                ORDER BY oa_percentage DESC
                LIMIT 15
            """)
            
            results = cursor.fetchall()
            
            if not results:
                print("No MeSH topic data available for OA comparison.")
                return
            
            print("Topics with Highest Open Access Rates:")
            print("-" * 80)
            print(f"{'MeSH Term':<40} {'Total':<7} {'OA':<5} {'Closed':<7} {'OA %':<7}")
            print("-" * 80)
            
            for row in results:
                mesh_term = row['mesh_term'] or 'Unknown'
                if len(mesh_term) > 38:
                    mesh_term = mesh_term[:35] + "..."
                
                oa_pct = f"{row['oa_percentage']:.1f}%"
                
                print(f"{mesh_term:<40} {row['total_articles']:<7} {row['oa_articles']:<5} "
                      f"{row['closed_articles']:<7} {oa_pct:<7}")
            
            print()
    
    except Exception as e:
        print(f"Error generating MeSH OA comparison: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Reporting and Analytics for FindIt Coverage Testing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Overall summary
  python reports.py summary
  
  # Publisher performance (top 15)
  python reports.py publisher-stats --top 15
  
  # Journal performance (top 30)
  python reports.py journal-stats --top 30
  
  # Processing run history
  python reports.py runs
  
  # Open Access analysis
  python reports.py oa-analysis
  
  # DOI coverage analysis
  python reports.py doi-analysis
  
  # Failure analysis
  python reports.py failure-analysis
  
  # Publication year trends
  python reports.py yearly-trends
  
  # MeSH term analysis (top 30)
  python reports.py mesh-analysis --top 30
  
  # MeSH topic Open Access comparison
  python reports.py mesh-oa-comparison
  
  # Export all data to CSV
  python reports.py export --format csv
  
  # Export specific list to JSON
  python reports.py export --list-id 1 --format json --output my_results.json
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Summary command
    subparsers.add_parser('summary', help='Show overall summary statistics')
    
    # Publisher stats command
    pub_parser = subparsers.add_parser('publisher-stats', help='Show publisher performance')
    pub_parser.add_argument('--top', type=int, default=10, help='Number of top publishers to show')
    
    # Journal stats command
    journal_parser = subparsers.add_parser('journal-stats', help='Show journal performance')
    journal_parser.add_argument('--top', type=int, default=20, help='Number of top journals to show')
    
    # Processing runs command
    subparsers.add_parser('runs', help='Show processing run history')
    
    # Enhanced analysis commands
    subparsers.add_parser('oa-analysis', help='Show Open Access analysis')
    subparsers.add_parser('doi-analysis', help='Show DOI coverage analysis')
    subparsers.add_parser('failure-analysis', help='Show detailed failure analysis')
    subparsers.add_parser('yearly-trends', help='Show publication year trends')
    
    # MeSH analysis commands
    mesh_parser = subparsers.add_parser('mesh-analysis', help='Show MeSH term analysis')
    mesh_parser.add_argument('--top', type=int, default=20, help='Number of top MeSH terms to show')
    subparsers.add_parser('mesh-oa-comparison', help='Compare OA rates across MeSH topics')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export data to file')
    export_parser.add_argument('--list-id', type=int, help='Export specific PMID list (default: all)')
    export_parser.add_argument('--format', choices=['csv', 'json'], default='csv', help='Export format')
    export_parser.add_argument('--output', help='Output filename (auto-generated if not specified)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize database
    db_manager = DatabaseManager()
    
    try:
        if args.command == 'summary':
            print_summary_report(db_manager)
        elif args.command == 'publisher-stats':
            print_publisher_stats(db_manager, args.top)
        elif args.command == 'journal-stats':
            print_journal_stats(db_manager, args.top)
        elif args.command == 'runs':
            print_processing_runs(db_manager)
        elif args.command == 'oa-analysis':
            print_oa_analysis(db_manager)
        elif args.command == 'doi-analysis':
            print_doi_coverage_analysis(db_manager)
        elif args.command == 'failure-analysis':
            print_failure_analysis(db_manager)
        elif args.command == 'yearly-trends':
            print_yearly_trends(db_manager)
        elif args.command == 'mesh-analysis':
            print_mesh_analysis(db_manager, args.top)
        elif args.command == 'mesh-oa-comparison':
            print_mesh_oa_comparison(db_manager)
        elif args.command == 'export':
            export_data(db_manager, args.list_id, args.format, args.output)
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()