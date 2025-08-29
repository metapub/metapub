from metapub import PubMedFetcher
fetch = PubMedFetcher()


#print('Brugada Syndrome: diagnosis')
results = fetch.pmids_for_medical_genetics_query('Brugada Syndrome', 'diagnosis', debug=True, year=2013)

print('First three results:')
print(results[:3])

print('')

#print('Hereditary Hemorrhagic Telangiectasia: Genetic Counseling')

results = fetch.pmids_for_medical_genetics_query('Hereditary Hemorrhagic Telangiectasia', 'genetic_counseling', debug=True)
print('First three results:')
print(results[:3])
print('')

