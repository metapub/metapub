from metapub import ClinVarFetcher

print("ClinVar Demo - Testing a few example variant IDs")
print("=" * 50)
print("Note: This demo shows ClinVarFetcher basic usage and error handling.")
print("WARNING: ClinVarFetcher may be affected by NCBI API changes (April 2019).")
print("The library may need updates to work with the new ClinVar API format.")
print("=" * 50)

cvfetch = ClinVarFetcher()

# Test with known valid ClinVar variant IDs
test_variants = [12222, 12111, 12100]

for varid in test_variants:
    print(f"Testing variant ID: {varid}")
    try:
        var = cvfetch.variant(varid)
        print(f"  ✓ Found: {var.variation_name}")
        print(f"  HGVS_c: {var.hgvs_c}")
    except Exception as error:
        print(f"  ✗ Error: {error}")
    print("-" * 30)

print("\nDemo completed. Use demo_ClinVarFetcher.py for more features.")
