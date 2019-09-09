from __future__ import absolute_import, print_function

from metapub import ClinVarFetcher
from metapub.exceptions import MetaPubError

cvfetch = ClinVarFetcher()
for varid in range(12000, 20000):
    print(varid)
    try:
        var = cvfetch.variant(varid)
        print('Name:', var.variation_name)
        print('Hgvs_c:', var.hgvs_c)
        print('Hgvs_g:', var.hgvs_g)
        print('Hgvs_p:', var.hgvs_p)
        print(var.molecular_consequences)
    except MetaPubError as error:
        print(error)
    print()
