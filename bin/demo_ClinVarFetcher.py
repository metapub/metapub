from __future__ import absolute_import, print_function

import sys
from metapub import ClinVarFetcher
from metapub.exceptions import MetaPubError

def demo_clinvar_fetcher(variant_ids=None):
    """
    Demonstrate ClinVarFetcher functionality.
    
    Args:
        variant_ids: List of variant IDs to test, or None for default examples
    """
    cvfetch = ClinVarFetcher()
    
    # Use provided variant IDs or default examples
    if variant_ids is None:
        # Known valid ClinVar variant IDs
        variant_ids = [12001, 12000, 12003]  # Confirmed working variant IDs
    
    print(f"ClinVarFetcher Demo - Testing {len(variant_ids)} variant(s)")
    print("=" * 60)
    print("Note: This demo shows ClinVarFetcher API usage and error handling.")
    print("WARNING: ClinVarFetcher may be affected by NCBI API changes (April 2019).")
    print("The 'rettype=variation' parameter was deprecated in favor of 'rettype=vcv'.")
    print("=" * 60)
    
    for varid in variant_ids:
        print(f"Fetching variant ID: {varid}")
        try:
            var = cvfetch.variant(varid)
            print(f'  ✓ Successfully fetched variant {varid}')
            print(f'  Name: {var.variation_name}')
            print(f'  HGVS_c: {var.hgvs_c or "N/A"}')
            print(f'  HGVS_g: {var.hgvs_g or "N/A"}')
            print(f'  HGVS_p: {var.hgvs_p or "N/A"}')
            print(f'  Molecular consequences: {var.molecular_consequences or "N/A"}')
        except MetaPubError as error:
            print(f"  ✗ Variant {varid} not found: {error}")
        except Exception as error:
            print(f"  ✗ Unexpected error for variant {varid}: {error}")
        print("-" * 30)

if __name__ == "__main__":
    # Allow command line variant IDs
    if len(sys.argv) > 1:
        try:
            variant_ids = [int(arg) for arg in sys.argv[1:]]
            demo_clinvar_fetcher(variant_ids)
        except ValueError:
            print("Error: All arguments must be valid variant ID numbers")
            print("Usage: python demo_ClinVarFetcher.py [variant_id1] [variant_id2] ...")
            sys.exit(1)
    else:
        demo_clinvar_fetcher()
