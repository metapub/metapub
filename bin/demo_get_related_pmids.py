from __future__ import absolute_import, print_function, unicode_literals

import sys

from metapub import PubMedFetcher

fetch = PubMedFetcher()

try:
    pmid = sys.argv[1]
except IndexError:
    print("Supply a pubmed ID as the argument to this script.")
    sys.exit()

result = fetch.related_pmids(pmid)

for key in list(result.keys()):
    print(key)
    for pmid in result[key]:
        outp = pmid
        article = fetch.article_by_pmid(pmid)
        #outp += ' %s' % article.title
        outp += ' %s' % article.citation
        if article.pmc:
            outp += ' (PMC)'
        outp += '\n'
        print(outp)

    print("")
    

