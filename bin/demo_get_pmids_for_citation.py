from metapub import PubMedFetcher
fetch = PubMedFetcher()
params = { 'jtitle': 'American Journal of Medical Genetics', 
           'year': 1996, 
           'volume': 61, 
           'spage': 10, 
           'authors': 'Katherine M. Hegmann; Aimee S. Spikes; Avi Orr-Urtreger; Lisa G. Shaffer' }

stuff = fetch.pmids_for_citation(**params)
print(params)
print(stuff)

params = { 'jtitle':'Journal of Neural Transmission', 
           'year':2014, 
           'volume':121, 
           'first_page':1077, 
           # author_name='Freitag'
         } 

stuff = fetch.pmids_for_citation(**params)

print(params)
print(stuff)

params = { 'journal':'Genetics in Medicine',
           'year':2017, 
           'volume':19, 
           'first_page':1105, 
           'aulast':'Nykamp',
         }

stuff = fetch.pmids_for_citation(**params)

print(params)
print(stuff)
