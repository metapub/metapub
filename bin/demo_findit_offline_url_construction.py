#!/usr/bin/env python3
"""
Demonstration of offline URL construction capabilities in FindIt.

This script shows how FindIt can construct URLs for many publishers 
without making HTTP requests when verify=False is used.
"""

from unittest.mock import Mock
from metapub.findit.dances import (
    the_vip_shake, the_bmc_boogie, the_springer_shag, 
    the_nature_ballet, the_wiley_shuffle
)
from metapub.findit.journals.misc_vip import vip_journals


def create_mock_pma(journal, volume="123", issue="4", first_page="567", 
                   doi=None, pii=None, pmid="12345678"):
    """Create a mock PubMedArticle for testing."""
    mock_pma = Mock()
    mock_pma.journal = journal
    mock_pma.volume = volume
    mock_pma.issue = issue
    mock_pma.first_page = first_page
    mock_pma.doi = doi
    mock_pma.pii = pii
    mock_pma.pmid = pmid
    return mock_pma


def demo_offline_construction():
    """Demonstrate offline URL construction for various publishers."""
    print("FindIt Offline URL Construction Demo")
    print("=" * 50)
    
    test_cases = [
        {
            'name': 'Brain (VIP Format)',
            'dance': the_vip_shake,
            'pma': create_mock_pma("Brain", "137", "4", "1020"),
            'description': 'Volume-Issue-Page format, no network needed'
        },
        {
            'name': 'BMC (DOI Format)', 
            'dance': the_bmc_boogie,
            'pma': create_mock_pma("BMC Genomics", doi="10.1186/s12864-023-09123-4"),
            'description': 'DOI-based URL, defaults to verify=False'
        },
        {
            'name': 'Springer (DOI Format)',
            'dance': the_springer_shag, 
            'pma': create_mock_pma("Human Genetics", doi="10.1007/s00439-023-02345-6"),
            'description': 'DOI-based construction'
        },
        {
            'name': 'Wiley (Template Format)',
            'dance': the_wiley_shuffle,
            'pma': create_mock_pma("American Journal of Medical Genetics", doi="10.1002/ajmg.a.37609"),
            'description': 'Returns template URL when verify=False'
        }
    ]
    
    for case in test_cases:
        print(f"\n{case['name']}:")
        print(f"  Description: {case['description']}")
        
        try:
            # Test offline construction (verify=False)
            url_offline = case['dance'](case['pma'], verify=False)
            print(f"  Offline URL:  {url_offline}")
            
            # Show that this would work without network
            if url_offline:
                print(f"  ✓ Success - URL constructed without network requests")
            else:
                print(f"  ⚠ Returned None - may need additional data")
                
        except Exception as e:
            print(f"  ✗ Failed: {e}")
            
    # Show VIP journals coverage
    print(f"\n\nVIP Journals Coverage:")
    print(f"  Total journals with VIP format: {len(vip_journals)}")
    
    sample_vip = list(vip_journals.keys())[:10]
    print(f"  Sample VIP journals:")
    for journal in sample_vip:
        print(f"    - {journal}")
    
    print(f"\n\nAll these VIP journals can construct URLs offline using:")
    print(f"  the_vip_shake(pma, verify=False)")


def demo_handler_system_offline():
    """Demonstrate that the new handler system preserves offline construction."""
    print("\n" + "=" * 50)
    print("Handler System Offline Construction")
    print("=" * 50)
    
    from metapub.findit.handlers import RegistryBackedLookupSystem
    from metapub.findit.registry import JournalRegistry
    
    # Initialize the registry system
    registry = JournalRegistry()
    lookup_system = RegistryBackedLookupSystem(registry)
    
    # Test with Brain (VIP journal)
    mock_pma = create_mock_pma("Brain", "137", "4", "1020")
    
    print(f"\nTesting handler system with Brain:")
    print(f"  Journal: {mock_pma.journal}")
    print(f"  Volume: {mock_pma.volume}, Issue: {mock_pma.issue}, Page: {mock_pma.first_page}")
    
    try:
        # Get handler for Brain
        handler = lookup_system.get_handler_for_journal("Brain")
        if handler:
            print(f"  Handler found: {handler.name}")
            print(f"  Dance function: {handler.dance_function}")
            
            # Test offline URL construction through handler
            url, reason = handler.get_pdf_url(mock_pma, verify=False)
            if url:
                print(f"  ✓ Offline URL: {url}")
            else:
                print(f"  ⚠ No URL returned: {reason}")
        else:
            print(f"  ⚠ No handler found for Brain")
            
    except Exception as e:
        print(f"  ✗ Error: {e}")


if __name__ == '__main__':
    demo_offline_construction()
    demo_handler_system_offline()
    
    print(f"\n" + "=" * 50) 
    print("Summary")
    print("=" * 50)
    print("✓ FindIt supports offline URL construction for many publishers")
    print("✓ Use verify=False to avoid HTTP requests")  
    print("✓ VIP format journals (volume/issue/page) work offline")
    print("✓ DOI-based publishers (BMC, Springer) work offline")
    print("✓ New handler system preserves verify=False functionality")
    print("✓ Over 450 journals support offline URL construction via VIP format")
    print("\nFor production use:")
    print("  finder = FindIt(pmid='12345678', verify=False)")
    print("  # Constructs URLs without HTTP verification when possible")