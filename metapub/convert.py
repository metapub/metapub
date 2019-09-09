"""convert.py: mildly-experimental mashups of various services to get needed IDs.

Defines command-line tools `convert pmid2doi` and `convert doi2pmid`.
"""

import logging
import coloredlogs
from urllib.error import HTTPError

from .pubmedfetcher import PubMedFetcher
from .crossref import CrossRefFetcher
from .exceptions import *

log = logging.getLogger('metapub.convert')

coloredlogs.install()

cr_fetch = None   #CrossRefFetcher()
pm_fetch = None   #PubMedFetcher()


__version__ = '0.1'
__doc__ = """Convert.pmid2doi / Convert.doi2pmid / Convert.bookid2pmid

Usage:
    convert -h 
    convert pmid2doi <pmid> [options]
    convert doi2pmid <doi>  [options]
    convert bookid2pmid <book_id>  [options]

Options:
    -h, --help      Show this help page
    -v, --version   Show this command's version.
    -q, --quiet     Shut up all that log garbage.
    -d, --debug     No wait, give me ALL the log garbage! Superceded by --quiet.
    -a, --article   Also print out the article information (from PubMedArticle) if possible.
    -w, --work      Also print out info from the CrossRef entry, if possible.
"""


def _start_engines():
    global cr_fetch
    global pm_fetch
    if not cr_fetch:
        cr_fetch = CrossRefFetcher()
    if not pm_fetch:
        pm_fetch = PubMedFetcher()
    

def interpret_pmids_for_citation_results(pmids):
    if len(pmids) == 1:
        if pmids[0] == 'NOT_FOUND':
            return None
        elif pmids[0].startswith('AMBIGUOUS'):
            return 'AMBIGUOUS'
        return str(pmids[0])
    elif len(pmids) == 0:
        return None
    else:
        return 'AMBIGUOUS'


def PubMedArticle2doi(pma):
    '''Starting with a PubMedArticle object, use CrossRef to find a DOI for given article.

    Args:
        pma (PubMedArticle)

    Returns:
        doi (str) or None
    '''
    _start_engines()

    work = cr_fetch.article_by_pma(pma)
    if work:
        log.debug('CrossRefWork found (%s) with Crossref score %i.', work.doi, work.score)
        return work.doi

    return None


def pmid2doi(pmid):
    '''starting with a pubmed ID, lookup article in pubmed. If DOI found in PubMedArticle object,
        return it.  Otherwise, use CrossRef to find the DOI for given article.

    Args:
        pmid (str or int)

    Returns:
        doi (str) or None

    Raises:
        InvalidPMID (if pmid is invalid)
    '''
    # let MetaPubError pass back to the caller if pmid is not for realz..
    _start_engines()
    pma = pm_fetch.article_by_pmid(pmid)
    if pma.doi:
        log.debug('PMID %s: Found DOI in MedLine XML.', pmid)
        return pma.doi
    return PubMedArticle2doi(pma)


def doi2pmid(doi):
    '''uses CrossRef and PubMed eutils to lookup a PMID given a known doi.

    Warning: NO validation of input DOI performed here. Use
             metapub.text_mining.find_doi_in_string beforehand if needed.

    If a PMID can be found, return it. Otherwise return None.

    In very rare cases, use of the CrossRef->pubmed citation method used
    here may result in more than one pubmed ID. In this case, this function
    will return instead the word 'AMBIGUOUS'.

    :param pmid: (str or int)
    :return doi: (str) if found; 'AMBIGUOUS' if citation count > 1; None if no results.
    '''
    # for PMA, skip the validation; some pubmed XML has weird partial strings for DOI.
    # We should allow people to search using these oddball strings.
    _start_engines()
    doi = doi.strip()
    try:
        pma = pm_fetch.article_by_doi(doi)
        log.debug('doi2pmid: Found PubMedArticle for DOI %s via eutils fetch', doi)
        return pma.pmid
    except:
        pass

    # Try doing a DOI lookup right in an advanced query string. Sometimes works and has
    # benefit of being a cached query so it is quick to do again, should we need.
    pmids = pm_fetch.pmids_for_query(doi)
    if len(pmids) == 1:
        # we need to cross-check; pubmed sometimes screws us over by giving us an article
        # with a SIMILAR doi. *facepalm*
        pma = pm_fetch.article_by_pmid(pmids[0])
        if pma.doi == doi:
            log.debug('doi2pmid: Found PMID via PubMed advanced query for DOI %s', doi)
            return pma.pmid

        log.debug('Pubmed advanced query gave us a problematic result...')
        log.debug('\tSearch: %s' % doi)
        log.debug('\tReturn: %s' % pma.doi)

    # Try Looking up DOI in CrossRef, then feeding results to pubmed citation query tool...
    try:
        work = cr_fetch.article_by_doi(doi)
        log.debug('doi2pmid: Found CrossRef article for DOI %s', doi)
    except HTTPError as error:
        if str(error).find('404') > -1:
            log.info('doi2pmid: DOI %s was not found in CrossRef.  Giving up.', doi)
            return None
        log.debug('doi2pmid: Unexpected HTTP error occurred during CrossRef lookup:')
        log.debug(error)
        return None

    pmids = pm_fetch.pmids_for_citation(**work.to_citation())

    if pmids:
        return interpret_pmids_for_citation_results(pmids)
    else:
        return None


def bookid2pmid(book_id):
    """Convenience interface to PubMedFetcher.pmid_for_bookID"""
    _start_engines()
    return pm_fetch.pmid_for_bookID(book_id)


def main():
    from docopt import docopt
    args = docopt(__doc__, version=__version__)

    if args['--quiet']:
        logging.getLogger('metapub.*').setLevel(logging.INFO)

    elif args['--debug']:
        logging.getLogger('metapub.*').setLevel(logging.DEBUG)

    if args['doi2pmid']:
        doi = args['<doi>']
        print('DOI: ', doi)
        pmid = doi2pmid(doi)
        print('PMID: ', pmid)
    elif args['pmid2doi']:
        pmid = args['<pmid>']
        print('PMID: ', pmid)
        doi = pmid2doi(pmid)
        print('DOI: ', doi)
    elif args['bookid2pmid']:
        book_id = args['<book_id>']
        print('BookID: ', book_id)
        pmid = bookid2pmid(book_id)
        print('PMID: ', pmid) 

    print()
    if args['--article']:
        pma = pm_fetch.article_by_pmid(pmid)
        print(pma)

    if args['--work']:
        work = cr_fetch.article_by_doi(doi)
        print(work)

