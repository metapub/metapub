from __future__ import absolute_import, print_function, unicode_literals

import logging
from metapub import PubMedFetcher

logging.getLogger('eutils').setLevel(logging.DEBUG)
logging.getLogger('metapub').setLevel(logging.DEBUG)

fetch = PubMedFetcher()
pmbook = fetch.article_by_pmid('20301577')


print(pmbook.title)
print(pmbook.abstract)
print(pmbook.year)

print()
print(pmbook.citation)

