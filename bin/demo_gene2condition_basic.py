from __future__ import absolute_import, print_function, unicode_literals

import sys

from tabulate import tabulate
from metapub import MedGenFetcher

try:
    input_gene = sys.argv[1]
except IndexError:
    print('Supply a Hugo gene name to this script as its argument.')
    sys.exit()

####
import logging
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("eutils").setLevel(logging.INFO)
####

fetch = MedGenFetcher()
uids = fetch.uids_by_term(input_gene+'[gene]')
print(uids)

# TODO: Term Hierarchy Children (only 1 tier below), Term Hierarchy Parents (only 1 tier above)

headers = ['CUI', 'Hugo', 'Title', 'Semantic Type', 'MedGenUID', 
           'OMIM ID', 'Modes of Inheritance', 'Assoc Genes', ]

table = []

def _join_or_NA(some_list, select=None, joiner=','):
    'returns a joined string or NA if empty'
    if some_list and select:
        return joiner.join(item[select] for item in some_list)
    elif some_list:
        return joiner.join([item for item in some_list])
    else:
        return 'NA'

for this_id in uids:
    concept = fetch.concept_by_uid(this_id)
    #print concept.to_dict()
    assert concept.medgen_uid == this_id
    line = [concept.CUI, input_gene, concept.title, concept.semantic_type, concept.medgen_uid]

    line.append(_join_or_NA(concept.OMIM))
    line.append(_join_or_NA(concept.modes_of_inheritance, 'name'))
    line.append(_join_or_NA(concept.associated_genes, 'hgnc')) 

    table.append(line)

print(tabulate(table, headers, tablefmt="simple"))

