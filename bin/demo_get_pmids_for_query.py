from metapub import PubMedFetcher
fetch = PubMedFetcher()
params = { 'jtitle': 'American Journal of Medical Genetics', 
                    'year': 1996, 
                    'volume': 61, 
                    'author1_lastfm': 'Hegmann' }

stuff = fetch.pmids_for_query(**params)
print(params)
print(stuff)

# the following article was deleted from pubmed (or changed such that this
# set of parameters no longer returns an article)
params = { 'TA':'Journal of Neural Transmission', 
                    'pdat':2014, 
                    'vol':121, 
                    'aulast': 'Freitag'
         } 
stuff = fetch.pmids_for_query(**params)

print(params)
print(stuff)

#params = { 'mesh': 'breast neoplasm' }
#stuff = fetch.pmids_for_query(since='2014', until='2015/3/1', pmc_only=True, **params)

pmids = fetch.pmids_for_query(since='2015/3/1', retmax=1000)
assert len(pmids)==1000

pmids = fetch.pmids_for_query(journal='N Am J Med Sci', pmc_only=False)
pmc_only = fetch.pmids_for_query(journal='N Am J Med Sci', pmc_only=True, year=2008)

non_pmc = [pmid for pmid in pmids if pmid not in pmc_only]

print(non_pmc)

