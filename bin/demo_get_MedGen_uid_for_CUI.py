from __future__ import absolute_import, print_function, unicode_literals

import sys

from metapub import MedGenFetcher

# example of CUID: C0000039

try:
    cui = sys.argv[1]
except IndexError:
    print('Supply a ConceptID (CUI) to this script as its argument.')
    sys.exit()

####
import logging
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("eutils").setLevel(logging.WARNING)
####

fetch = MedGenFetcher()
uid = fetch.uid_for_cui(cui)
print(uid)

