import os, sys, shutil
import logging

from metapub import PubMedFetcher, CrossRefFetcher
from metapub.exceptions import MetaPubError
from metapub.text_mining import find_doi_in_string
from metapub.config import get_process_log

logging.getLogger('metapub').setLevel(logging.DEBUG)

# Print a log to a file.
log = get_process_log('demo.log', logging.DEBUG, 'metapub')
log.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
log.addHandler(ch)

fetch = PubMedFetcher()
CR = CrossRefFetcher()

def get_doi(pmid):
    pma = fetch.article_by_pmid(pmid)
    log.debug("looking up %s (title: %s, journal: %s)" % (pmid, pma.title, pma.journal))
    if pma.doi:
        log.debug('Found it in Medline XML')
        return pma.doi

    work = CR.article_by_pma(pma)
    if work is None:
        log.info("CrossRef couldn't find it.")
    else:
        log.info("CrossRef found it with score=%i" % work.score)
        log.info("Your DOI sir: %s" % work.doi)
        log.info("Title: %s" % work.title[0])

        #if find_doi_in_string(work.doi):
        #    print('...which looks like a real DOI, but will it blend??!\n') 
        #    print(work)
            
        if not find_doi_in_string(work.doi):
            log.info('...not very DOI-like. :(')
            log.info('Title: %s' % work.title[0])

if __name__=='__main__':
    try:
        pmid = sys.argv[1]
    except IndexError:
        print('Supply a PubMed ID as the argument to this script.')
        sys.exit()
    
    get_doi(pmid)
    print('\nDONEZ0RS.\n')

