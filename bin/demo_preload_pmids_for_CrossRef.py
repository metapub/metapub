from __future__ import absolute_import, print_function, unicode_literals

import os, sys, shutil
import logging

from metapub import PubMedFetcher
from metapub.exceptions import *
from metapub.convert import pmid2doi

DEBUG = True

####
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("eutils").setLevel(logging.INFO)
####

fetch = PubMedFetcher()

if __name__=='__main__':
    try:
        filename = sys.argv[1]
    except IndexError:
        print('Supply a filename containing a list of PMIDs as argument to this script.')
        sys.exit()

    pmids = open(filename, 'r').readlines()
    for pmid in [item.strip() for item in pmids if item.strip() != '']:
        try:
            pma = fetch.article_by_pmid(pmid)
            doi = pmid2doi(pmid) or ''
            print(','.join([pmid, doi, pma.title]))
            print('')

        except InvalidPMID:
            print(pmid, ',,INVALID')

        
        
