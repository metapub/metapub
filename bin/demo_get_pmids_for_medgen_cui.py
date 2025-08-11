import sys

from metapub import MedGenFetcher
from metapub import PubMedFetcher

try:
    cui = sys.argv[1]
except IndexError:
    print("Supply CUI (Concept ID) as argument to this script.")
    sys.exit()

pmfetch = PubMedFetcher()
fetch = MedGenFetcher()

concept = fetch.concept_by_cui(cui)
print("#### CUI: %s" % cui)
print("# %s" % concept.title)
print("#")
print("#")


pmids = fetch.pubmeds_for_cui(cui)

for pmid in pmids:
    print("#### %s" % pmid)
    pma = pmfetch.article_by_pmid(pmid)
    print(pma.year, pma.title, pma.journal)
    print("")

