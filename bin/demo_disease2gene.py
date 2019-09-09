from __future__ import absolute_import, print_function, unicode_literals

import sys

from tabulate import tabulate
from metapub import MedGenFetcher

try:
    term = sys.argv[1]
except IndexError:
    print('Supply a disease/syndrome/condition name in quotation marks as the argument to this script.')
    sys.exit()

####
import logging
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("eutils").setLevel(logging.INFO)
####

fetch = MedGenFetcher()
uids = fetch.uids_by_term(term)
print(uids)

headers = ['CUI', 'Title', 'Semantic Type', 'MedGenUID', 
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

    if concept.associated_genes:
        line = [concept.CUI, concept.title, concept.semantic_type, concept.medgen_uid]
        line.append(_join_or_NA(concept.OMIM))
        line.append(_join_or_NA(concept.modes_of_inheritance, 'name'))
        line.append(_join_or_NA(concept.associated_genes, 'hgnc')) 
        table.append(line)
    else:
        continue


print(tabulate(table, headers, tablefmt="simple"))

