from metapub import ClinVarFetcher

cv = ClinVarFetcher()
v = cv.variant(12007)
print(v.variation_name)
print(v.content)