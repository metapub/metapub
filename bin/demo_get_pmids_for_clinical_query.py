from __future__ import absolute_import, print_function, unicode_literals

from metapub import PubMedFetcher
fetch = PubMedFetcher()

term = 'Global developmental delay'

print('%s: etiology broad' % term)
results = fetch.pmids_for_clinical_query(term, 'etiology', debug=True, year=2013)

print('First three results:')
print(results[:3])

print('')

print('%s: etiology narrow' % term)

results = fetch.pmids_for_clinical_query(term, 'etiology', 'narrow', debug=True, year=2013)
print('First three results:')
print(results[:3])
print('')

print('tyrosine kinase inhibitor: diagnosis')
results = fetch.pmids_for_clinical_query('tyrosine kinase inhibitor', 'diagnosis', 'broad', debug=True, year=2013)
print(len(results))
print('First three results:')
print(results[:3])
print('')

