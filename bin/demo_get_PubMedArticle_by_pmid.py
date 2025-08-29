import sys

from metapub import PubMedFetcher
from metapub import FindIt

# examples of different formats:
# 18612690: PubMedArticle with multiple AbstractText sections
# 1234567:  PubMedArticle with no abstract whatsoever
# 20301546: PubMedBookArticle from GeneReviews

####
import logging
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("eutils").setLevel(logging.WARNING)

ch = logging.StreamHandler()
logging.getLogger("metapub").setLevel(logging.INFO)
logging.getLogger("metapub").addHandler(ch)
####

try:
    pmid = sys.argv[1]
except IndexError:
    print('Supply a pubmed ID as the argument to this script.')
    print('')
    print('Example: python demo_pubmed.py 123456')
    sys.exit()

article = PubMedFetcher().article_by_pmid(pmid)

print('')
print(article.pmid, article.title)
print('')
print('authors: %s' % ','.join(article.authors))
print('journal: %s' % article.journal)
print('')
excerpt = '(empty)' if article.abstract is None else article.abstract[:100] + '[...]'
print('abstract: %s' % excerpt)
print('')
print('pii:',str(article.pii))
print('doi:',str(article.doi))
print('pmc:',str(article.pmc))
print('volume:',str(article.volume))
print('issue:',str(article.issue))
print('pages:',str(article.pages))
print('year:',str(article.year))
print('')
print('MeSH headings: ')
for DUI in list(article.mesh.keys()):
    print('\t', DUI, article.mesh[DUI]['descriptor_name'], article.mesh.get('qualifier_name', ''))

if article.publication_types:
    print('\nPublication Type Information')
    for pt in list(article.publication_types.keys()):
        print('\t', pt, article.publication_types[pt])

if article.chemicals:
    print('\nChemical List')
    for DUI in list(article.chemicals.keys()):
        print('\t', DUI, article.chemicals[DUI]['substance_name'])

if article.grants:
    print('\nGrant Information')
    for gr in grants:
        print('\t', gr)

if article.history:
    print('\nArticle History')
    for hist in article.history:
        print('\t', hist, article.history[hist])

print('')

print('FindIt results:')
source = FindIt(pmid=pmid)
print('\tdoi:', source.doi)
print('\turl:', source.url)
print('\tbackup:', source.backup_url)
print('\treason:', source.reason)

print(article.citation_html)
