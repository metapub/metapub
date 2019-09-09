from metapub import ClinVarFetcher

cvfetch = ClinVarFetcher()
for varid in range(1, 1000):
    print(varid)
    try:
        var = cvfetch.variant(varid)
        print(var.variation_name)
        print(var.hgvs_c)
    except Exception as error:
        print(error)

    print()
