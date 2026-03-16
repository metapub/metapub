"""Demo: convert a DOI to a PubMed ID using metapub.convert.doi2pmid.

Usage:
    python demo_doi2pmid.py
    python demo_doi2pmid.py 10.1038/nature12373
"""

import sys

from metapub.convert import doi2pmid

# Well-known DOIs for testing
SAMPLE_DOIS = [
    '10.1038/nature12373',       # Nature - BRCA1 paper
    '10.1056/NEJMoa1200303',     # NEJM
    '10.1016/j.ajhg.2013.03.015', # AJHG
]

if __name__ == '__main__':
    if len(sys.argv) > 1:
        dois = sys.argv[1:]
    else:
        dois = SAMPLE_DOIS

    for doi in dois:
        print(f'DOI: {doi}')
        pmid = doi2pmid(doi)
        if pmid == 'AMBIGUOUS':
            print(f'  Result: AMBIGUOUS (multiple PubMed matches)')
        elif pmid is None:
            print(f'  Result: not found in PubMed')
        else:
            print(f'  PMID: {pmid}')
        print()
