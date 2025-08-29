#!/usr/bin/env python3
"""
Demo script for HTML citation formatting in metapub

This script demonstrates the restored citation_html functionality by:
1. Fetching several interesting PubMed articles
2. Showing both plain and HTML citations  
3. Pretty-printing HTML citations with ANSI colors on the CLI

Usage:
    python demo_citation_html.py
    python demo_citation_html.py --pmids 12345,67890  # custom PMIDs
    python demo_citation_html.py --no-color          # disable colors
"""

import sys
import argparse
import re

from metapub import PubMedFetcher

# ANSI color codes for pretty printing
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    
    # Foreground colors
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'

def colorize_html_citation(html_citation, use_colors=True):
    """Convert HTML citation to colored CLI output"""
    if not use_colors:
        # Just strip HTML tags for plain output
        citation = re.sub(r'<[^>]+>', '', html_citation)
        return citation
    
    # Replace HTML tags with ANSI color codes
    citation = html_citation
    
    # Make italic text cyan
    citation = re.sub(r'<i>(.*?)</i>', f'{Colors.CYAN}\\1{Colors.RESET}', citation)
    
    # Make bold text yellow and bold
    citation = re.sub(r'<b>(.*?)</b>', f'{Colors.YELLOW}{Colors.BOLD}\\1{Colors.RESET}', citation)
    
    return citation

def print_separator(char="=", length=80, color=None):
    """Print a separator line"""
    if color:
        print(f"{color}{char * length}{Colors.RESET}")
    else:
        print(char * length)

def print_article_info(article, use_colors=True):
    """Print detailed article information with formatting"""
    title_color = Colors.GREEN + Colors.BOLD if use_colors else ""
    reset = Colors.RESET if use_colors else ""
    
    print(f"\n{title_color}📄 {article.title}{reset}")
    print(f"   PMID: {article.pmid}")
    print(f"   Journal: {article.journal}")
    print(f"   Year: {article.year}")
    print(f"   Authors: {', '.join(article.authors[:3])}{'...' if len(article.authors) > 3 else ''}")

def demo_citation_formatting():
    """Main demo function"""
    parser = argparse.ArgumentParser(description='Demo HTML citation formatting')
    parser.add_argument('--pmids', help='Comma-separated list of PMIDs to demo (default: curated examples)')
    parser.add_argument('--no-color', action='store_true', help='Disable ANSI colors')
    args = parser.parse_args()
    
    use_colors = not args.no_color
    
    # Curated list of interesting articles for demo
    if args.pmids:
        demo_pmids = args.pmids.split(',')
    else:
        demo_pmids = [
            '23435529',   # Ruvolo et al - reproductive medicine
            '25633503',   # CRISPR gene editing breakthrough
            '30971826',   # Machine learning in medicine
            '20301546',   # GeneReviews book article 
            '18612690',   # Article with multiple abstract sections
        ]
    
    fetcher = PubMedFetcher()
    
    # Print header
    header_color = Colors.BLUE + Colors.BOLD if use_colors else ""
    reset = Colors.RESET if use_colors else ""
    
    print(f"\n{header_color}🧬 metapub Citation HTML Formatting Demo{reset}")
    print_separator("=", color=Colors.BLUE if use_colors else None)
    
    print(f"\nThis demo shows the restored HTML citation formatting functionality.")
    print(f"Articles will display both plain text and styled citations.\n")
    
    successful_demos = 0
    total_demos = len(demo_pmids)
    
    for i, pmid in enumerate(demo_pmids, 1):
        try:
            print_separator("-", color=Colors.MAGENTA if use_colors else None)
            section_color = Colors.MAGENTA + Colors.BOLD if use_colors else ""
            print(f"\n{section_color}📋 Article {i}/{total_demos} (PMID: {pmid}){reset}")
            
            # Fetch article
            article = fetcher.article_by_pmid(pmid.strip())
            
            # Show article details
            print_article_info(article, use_colors)
            
            # Show plain citation
            plain_label = Colors.WHITE + Colors.BOLD if use_colors else ""
            print(f"\n{plain_label}📝 Plain Citation:{reset}")
            print(f"   {article.citation}")
            
            # Show HTML citation with colors
            html_label = Colors.CYAN + Colors.BOLD if use_colors else ""
            print(f"\n{html_label}🎨 HTML Citation (styled):{reset}")
            styled_citation = colorize_html_citation(article.citation_html, use_colors)
            print(f"   {styled_citation}")
            
            # Show raw HTML for reference
            if use_colors:
                raw_label = Colors.YELLOW
                print(f"\n{raw_label}🔧 Raw HTML:{reset}")
                print(f"   {article.citation_html}")
            
            successful_demos += 1
            
        except Exception as e:
            error_color = Colors.RED + Colors.BOLD if use_colors else ""
            print(f"\n{error_color}❌ Error fetching PMID {pmid}: {e}{reset}")
            print(f"   This might be due to network issues or an invalid PMID.")
    
    # Summary
    print_separator("=", color=Colors.GREEN if use_colors else None)
    summary_color = Colors.GREEN + Colors.BOLD if use_colors else ""
    
    if successful_demos == total_demos:
        print(f"\n{summary_color}✅ Demo completed successfully! ({successful_demos}/{total_demos} articles){reset}")
        print(f"\nKey HTML formatting features demonstrated:")
        if use_colors:
            print(f"   • {Colors.CYAN}Journal names in italic{reset} (HTML: <i>)")
            print(f"   • {Colors.YELLOW}{Colors.BOLD}Volume numbers in bold{reset} (HTML: <b>)")
            print(f"   • {Colors.CYAN}\"et al\" in italic{reset} (HTML: <i>)")
        else:
            print(f"   • Journal names in italic (HTML: <i>)")
            print(f"   • Volume numbers in bold (HTML: <b>)")
            print(f"   • \"et al\" in italic (HTML: <i>)")
    else:
        print(f"\n{summary_color}⚠️  Demo completed with some issues ({successful_demos}/{total_demos} articles successful){reset}")
    
    print(f"\n{Colors.BLUE if use_colors else ''}The citation_html functionality has been restored and is ready for use!{reset}")
    print(f"Perfect for integration with web applications like MaveDB.\n")

if __name__ == '__main__':
    try:
        demo_citation_formatting()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Demo interrupted by user.{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {e}{Colors.RESET}")
        sys.exit(1)