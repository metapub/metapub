from __future__ import absolute_import, unicode_literals, print_function

import sys, logging

from metapub.convert import pmid2doi
from metapub import DxDOI
from metapub.exceptions import *

logging.getLogger('metapub').setLevel(logging.DEBUG)

def generate_pmid_list(start_pmid):
    start_pmid = int(start_pmid)
    return list(range(start_pmid, start_pmid+20))

def run_pmid_list(pmids):
    dx_doi = DxDOI()

    for pmid in pmids:
        try:
            doi = pmid2doi(pmid)
        except InvalidPMID:
            continue

        if doi:
            print(pmid, ':', doi)
            try:
                url = dx_doi.resolve(doi)
                print(pmid, ':', url)
            except Exception as error:
                print('no url:', error)
        else:
            print(pmid, ': no doi')

def main(start_pmid):
    pmids = generate_pmid_list(start_pmid)
    run_pmid_list(pmids)


if __name__=='__main__':
    try:
        start_pmid = sys.argv[1]
    except IndexError:
        print('Supply starting pubmed ID as argument to this script.')
        sys.exit()

    main(start_pmid)

