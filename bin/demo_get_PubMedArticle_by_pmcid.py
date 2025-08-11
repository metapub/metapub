import sys, logging
from metapub import PubMedFetcher

logging.loglevel =  logging.INFO 

try:
    someid = sys.argv[1]
except IndexError:
    print('Supply a PMCID or DOI (example: ./blah.py PMC3479421)')
    sys.exit()


fetch = PubMedFetcher()
article = fetch.article_by_pmcid(someid)

print(article.title)
print(', '.join(article.authors))
print()

print(article.journal, article.volume_issue)
print()
print('Pubmed ID: ' + article.pmid)


"""
<pmcids status="ok">
<request idtype="pmcid" pmcids="" versions="yes" showaiid="no">
<echo>tool=medgen-python;email=naomi.most%40invitae.com;ids=PMC3479421</echo>
</request>
<record requested-id="PMC3479421" pmcid="PMC3479421" pmid="22676651" doi="10.1186/1750-1172-7-35"><versions><version pmcid="PMC3479421.1" current="true"/></versions></record>
</pmcids>
"""

