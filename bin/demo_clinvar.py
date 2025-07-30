import tempfile
from metapub import ClinVarFetcher

# Demo with known valid ClinVar variant IDs
# Note: Most low-numbered IDs are invalid, so we use a curated list
VALID_IDS = [4, 8, 1013, 10000, 12000, 12003, 12004, 12005, 12006, 12007]

# Use a temporary cache directory to avoid conflicts
with tempfile.TemporaryDirectory() as tmpdir:
    cvfetch = ClinVarFetcher(cachedir=tmpdir)
    print("ClinVar Fetcher Demo - showing valid variants")
    print("=" * 50)

    for varid in VALID_IDS:
        print(f"Variant ID: {varid}")
        try:
            var = cvfetch.variant(varid)
            print(f"  Name: {var.variation_name}")
            print(f"  Type: {var.variation_type}")
            print(f"  Gene(s): {[gene['Symbol'] for gene in var.genes]}")
            print(f"  HGVS_c: {var.hgvs_c}")
            print(f"  HGVS_g: {var.hgvs_g[:2]}...")  # Show first 2 genomic HGVS
            print(f"  HGVS_p: {var.hgvs_p}")
            print(f"  Location: {var.cytogenic_location}")
            print(f"  Species: {var.species}")
        except Exception as error:
            print(f"  ERROR: {error}")

        print()

    print("ClinVar demo completed.")

