import time
import logging

from ..pubmedcentral import get_pmid_for_otherid
from ..pubmedfetcher import PubMedFetcher
from ..crossref import CrossRefFetcher
from ..cache_utils import SQLiteCache, get_cache_path, datetime_to_timestamp
from ..dx_doi import DxDOI
from ..convert import doi2pmid, pmid2doi, interpret_pmids_for_citation_results
from ..exceptions import MetaPubError, DxDOIError, BadDOI
from ..utils import hostname_of, remove_chars, asciify
from ..text_mining import find_doi_in_string
from ..config import DEFAULT_CACHE_DIR

from .methods import re_pmcid, try_pmid_methods, try_doi_methods, try_vip_methods


# UrlReverse cacheing engine globals
URLREVERSE_CACHE = None
CACHE_FILENAME = 'urlreverse.db'

pm_fetch = None
dxdoi = None
cr_fetch = None

def _start_engines():
    global pm_fetch
    if not pm_fetch:
        pm_fetch = PubMedFetcher()
    global dxdoi
    if not dxdoi:
        dxdoi = DxDOI()
    global cr_fetch
    if not cr_fetch:
        cr_fetch = CrossRefFetcher()


def get_article_info_from_url(url):
    """ Using regular expressions, attempt to determine the "format" of the submitted URL, and if 
    possible, extract useful information from the URL for article lookup by ID or citation.

    Possible results:
        'vip': volume-issue-page --> {'format': 'vip', 'volume': <V>, 'issue': <I>, 'first_page': <P>, 'jtitle': <jrnl>}
        'doi': has doi in the url --> {'format': 'doi', 'doi': <DOI>, 'method': <get_doi_function>}
        'pmid': has pmid in the url --> {'format': 'pmid', 'pmid': <PMID>}
        'pmcid': has PMC id in the url --> {'format': 'pmcid': 'pmcid': <PMCID>}

    If none of the available methods work to parse the URL, the result dictionary will be:
        {'format': 'unknown'}

    :param url:
    :return: result dictionary (see above)
    """
    # maybe the DOI is deducible from the URL:
    doidict = try_doi_methods(url)
    if doidict:
        doidict['format'] = 'doi'
        return doidict

    # maybe the pubmed ID is in the URL:
    pmid = try_pmid_methods(url)
    if pmid:
        outd = {'pmid': pmid, 'format': 'pmid'}
        return outd

    # maybe the PubmedCentral ID is in the URL:
    #if 'nih.gov' in url or 'europepmc.org' in url:
    match = re_pmcid.match(url)
    if match:
        outd = match.groupdict()
        outd['format'] = 'pmcid'
        return outd

    # maybe this is a volume-issue-page formatted link and we can look it up by citation or CrossRef:
    vipdict = try_vip_methods(url)
    if vipdict:
        vipdict['format'] = 'vip'
        return vipdict

    return {'format': 'unknown'}


def _get_urlreverse_cache(cachedir=DEFAULT_CACHE_DIR):
    global URLREVERSE_CACHE
    if not URLREVERSE_CACHE:
        _cache_path = get_cache_path(cachedir, CACHE_FILENAME)
        URLREVERSE_CACHE = SQLiteCache(_cache_path)
    return URLREVERSE_CACHE


class UrlReverse(object):

    """ UrlReverse takes a url and performs the switchboard operations that hopefully lead
    to the successful "reversal" of an article url into its origination DOI and/or PMID.

    Whether the object is able to discover either or both of these identifiers depends 
    highly on the information available in the URL and inferable from what is known about
    the publisher or website that the article was found upon.

    Example:

        urlrev = UrlReverse('http://jmg.bmj.com/content/43/2/97.full.pdf')
        print(urlrev.doi)       # 10.1136/jmg.2005.030833
        print(urlrev.pmid)      # 15879500

    Human inspection can quickly verify that the above PDF definitely maps to this 
    PubMed entry:

        https://www.ncbi.nlm.nih.gov/pubmed/15879500

    (Adding a machine-verification step might be a further development of UrlReverse;
    however, it would add significant page-loading and processing time. Might be better
    off as an external "wrapper" around the UrlReverse operations.)

    The "steps" attribute will be of most interest if you want to know how UrlReverse
    arrived at its ID conclusions. 

    In the case of the above BMJ article URL, while the URL might have typically been
    "reversible" to a DOI from its constituent information, using DxDOI to verify whether
    the resultant DOI -- "10.1136/bmj.43.2.97" -- was a real one resulted in a DxDOIError,
    indicating that we did not have the Real McCoy.

    Using print(urlrev.steps), we get the following:
            
        [u'FOUND PMID via PubmedFetcher.pmids_for_citation',
         u'FOUND DOI via pmid2doi',
         u'VERIFY dx.doi.org: http://jmg.bmj.com/content/43/2/97']

    So, UrlReverse had to use a fallback method -- the pmids_for_citation approach, a 
    relatively slower method, but which in this case got the job done. This approach
    relies on the use of knowing a volume, first_page, and journal name, and 
    (hopefully) receiving a single unambiguous result from the query.

    When ambiguous results are received, UrlReverse considers this a failure (see `steps`).

    Args:

        skip_cache: (default: False) whether to load results afresh, regardless of cache contents.

    Keyword args:

        expiry_date: (default: None) forces cache to reload results older than given date.
        cachedir: (default: ~/.cache) allows change of cachedir; set to None to disable cache.
        debug: (default: False) raises log level of 'metapub.UrlReverse' logger to logging.DEBUG
    """

    def __init__(self, url, skip_cache=False, **kwargs):
        if not url.lower().startswith('http'):
            url = 'http://' + url

        _start_engines()

        self.url = url
        self.steps = []

        self.pmid = None
        self.doi = None
        self.info = None

        self.expiry_date = kwargs.get('expiry_date', None)

        cachedir = kwargs.get('cachedir', DEFAULT_CACHE_DIR)
        self._cache = None if cachedir is None else _get_urlreverse_cache(cachedir)

        self._log = logging.getLogger('metapub.UrlReverse')
        if kwargs.get('debug', False):
            self._log.setLevel(logging.DEBUG)
        else:
            self._log.setLevel(logging.INFO)

        if self._cache:
            self._load_from_cache()
        else:
            self._urlreverse()

    def _urlreverse(self):
        """ the switchboard operator of the urlreverse methods.

        mutates:
            self.info
            self.format
            self.pmid
            self.doi
            self.steps
        """
        self.info = get_article_info_from_url(self.url)
        self.format = self.info['format']

        if self.format == 'pmid':
            self.pmid = self.info['pmid']
            #self.doi = pmid2doi(self.pmid)
            if self.pmid:
                self.steps.append('FOUND PMID from inferred PMID in URL')

        elif self.format == 'doi':
            self.doi = self.info['doi']
            self.steps.append('FOUND DOI via inferred doi')
            self.pmid = doi2pmid(self.doi)
            if self.pmid:
                try:
                    int(self.pmid)
                    self.steps.append('FOUND PMID via doi2pmid')
                except:
                    # we'll log this further down (avoiding repeated code).
                    pass
            else:
                self.steps.append('NO PMID from doi2pmid')

        elif self.format == 'vip':
            try:
                self._try_citation_methods()
            except MetaPubError as error:
                self.pmid = None
                self.steps.append('NO PMID from VIP info + citation methods')

        elif self.format == 'pmcid':
            self.pmid = get_pmid_for_otherid(self.info['pmcid'])
            self.doi = doi2pmid(self.pmid)
            if self.pmid:
                self.steps.append('FOUND PMID from PMCID -> PMID lookup')

        if self.pmid and self.pmid.startswith('NOT_FOUND'):
            self.steps.append('NO PMID: PMID citation lookup resulted in "%s"' % self.pmid)
            self.pmid = None

        if self.doi and not self.pmid:
            self._try_backup_doi2pmid_methods()

        if self.doi:
            try:
                urlres = dxdoi.resolve(self.doi)
                self.steps.append('VERIFY dx.doi.org: %s' % urlres)
            except (DxDOIError, BadDOI) as error:
                self.doi = None
                self.steps.append('VERIFY dx.doi.org: PROBLEM with DOI: %r' % error)

        # Finally: ADMIT DEFEAT
        if not self.doi and not self.pmid:
            self.steps.append('NO DOI. NO PMID. All methods failed. END OF LINE.')

    def _store_cache(self):
        """ Store this object in cache by explicitly choosing variables to store as
        values, using self.url as the cache key.

        A time.time() timestamp will be added to the value dictionary when stored.

        There is no return from this function. Exceptions from the SQLiteCache 
        object may be raised.
        """
        cache_value = self.to_dict()
        cache_value['timestamp'] = time.time()
        self._cache[self._make_cache_key(self.url)] = cache_value

    def _load_from_cache(self, retry=False, expiry_date=None):
        cache_result = self._query_cache(self.url, expiry_date)

        if cache_result:
            self.pmid = cache_result['pmid']
            self.doi = cache_result['doi']
            self.steps = cache_result['steps']
            self.info = cache_result['info']

            if retry:
                if 'END OF LINE' in ';'.join(self.steps):
                    self._urlreverse()
                    self._store_cache()

        else:
            self._urlreverse()
            self._store_cache()

    def _make_cache_key(self, url):
        """ Returns url normalized via str() function for hash lookup / store. """
        return str(url)

    def _query_cache(self, cache_key, expiry_date=None):
        """ Return results of a lookup from the cache, if available.
        Return None if not available.

        Cache results are stored with a time.time() timestamp.

        When expiry_date is supplied, results from the cache past their
        sell-by date will be expunged from the cache and return will be None.

        expiry_date can be either a python datetime or a timestamp. 

        :param: cache_key: (required)
        :param: expiry_date (optional, default None)
        :return: (dict) result of cache lookup
        :rtype: dict or None
        """

        if hasattr(expiry_date, 'strftime'):
            # convert to timestamp
            sellby = datetime_to_timestamp(expiry_date)
        else:
            # make sure sellby is a number, not None
            sellby = expiry_date if expiry_date else 0

        if self._cache:
            cache_key = self._make_cache_key(cache_key)
            try:
                res = self._cache[cache_key]
                timestamp = res['timestamp']
                if timestamp < sellby:
                    self._log.debug('Cache: expunging result for %s (%i)', cache_key, timestamp)
                else:
                    self._log.debug('Cache: returning result for %s (%i)', cache_key, timestamp)
                return res

            except KeyError:
                self._log.debug('Cache: no result for key %s', cache_key)
                return None
        else:
            self._log.debug('Cache disabled (self._cache is None)')
            return None

    def _try_citation_methods(self):
        # 1) try pubmed citation match to get a PMID.
        pmids = pm_fetch.pmids_for_citation(**self.info)
        pmid = interpret_pmids_for_citation_results(pmids)
        if pmid and pmid != 'AMBIGUOUS':
            self.pmid = pmid
            self.doi = pmid2doi(pmid)
            self.steps.append('FOUND PMID via PubmedFetcher.pmids_for_citation')
            if self.doi:
                self.steps.append('FOUND DOI via pmid2doi')
            return

        # 2) try CrossRef -- most effective when title available, but may work without it.
        #       Get a DOI and then backref to PMID.

    def _try_backup_doi2pmid_methods(self):
        """ Uses CrossRef and Pubmed Advanced Query combinations to try to get an 
        unambiguous PMID result. Mutates self.pmid (if found unambigously) and self.steps
        (appending strings documenting the process by which PMID was(n't) acquired).
        """

        # All hinges on whether CrossRef can give us a good result. If not, fail out early.
        work = cr_fetch.article_by_doi(self.doi)

        if not work:
            self.steps.append('No results in CrossRef searching by DOI. Quitting here.')
            return None
    
        # bowlderize the title (remove urlencoded chars, unicode-only chars, and punctuation).
        # ps. some entries have no title (really!)

        title = remove_chars(work.title[0].strip())
        if title.strip() == '':
            self.steps.append('CrossRef result has no title. This bodes not well. Continuing anyway.')

        pmids = []

        if title:
            # try just searching Pubmed by title first. If we get one single result, that should be it.
            pmids = pm_fetch.pmids_for_query(title)

            if len(pmids) == 1:
                self.pmid = pmids[0]
                self.steps.append('FOUND PMID via Pubmed Advanced Query')
                return

            elif len(pmids) == 0:
                self.pmid = None
                self.steps.append('Zero results for title "%s" in Pubmed, attempting coordinate match' % title)
                title = ''

            elif len(pmids) > 1 and len(title.split(' ')) < 3:
                # title could be something like "Abstract" or "Pituitary" or "Endocrinology Yearbook" -- too vague.
                self.steps.append('Title "%s" too VAGUE, attempting coordinate match' % title)
                title = ''

        # we have ambiguous results (or no title at all) -- let's try to narrow the field based on
        # whether we have a viable title or not.

        # Two paths diverged in a wood, and I...

        if title=='':
            # strict coordinates
            params = {'VI': work.volume,
                      'IP': work.issue,
                      'AU': work.author1_last_fm,
                      'PG': work.first_page,
                      'DP': work.pubyear,
                     }
            try:
                pmids = pm_fetch.pmids_for_query(work.to_citation()['journal'], **params)
            except KeyError:
                # hrm, no title and no jtitle, eh... let's bail.
                self.steps.append('NO PMID. CrossRef data unworkable (no jtitle). END OF LINE.')
                return 

        else:
            if work.volume and work.issue:
                self.steps.append('AMBIGUOUS results for title "%s", trying with volume/issue')
                pmids = pm_fetch.pmids_for_query(title, VI=work.volume, IP=work.issue)
            elif work.volume and work.author1_last_fm:
                self.steps.append('AMBIGUOUS results for title "%s", trying with first author')
                pmids = pm_fetch.pmids_for_query(title, AU=author1_last_fm)
            elif work.first_page and work.author1_last_fm:
                self.steps.append('AMBIGUOUS results for title "%s", trying with first_page')
                pmids = pm_fetch.pmids_for_query(title, PG=work.first_page)
            elif work.volume:
                self.steps.append('AMBIGUOUS results for title "%s", trying with volume')
                pmids = pm_fetch.pmids_for_query(title, VI=work.volume)

        # that should have narrowed the field substantially. we should give up if it's still ambiguous.
        if len(pmids) == 1:
            self.pmid = pmids[0]
            self.steps.append('FOUND PMID via Pubmed Advanced Query')
        elif len(pmids) == 0:
            self.pmid = None
            self.steps.append('NO PMID, zero results from pubmed advanced query. (Data from CrossRef was: %r)' % (work))
        else:
            self.pmid = None
            self.steps.append('NO PMID, AMBIGUOUS results from pubmed advanced query (%i possibilities). %s' % (len(pmids), work))

    def to_dict(self):
        """ Returns a dictionary containing all public object attributes (i.e. not starting with an underscore). """
        outd = {}
        for key in self.__dict__:
            if not key.startswith('_'):
                outd[key] = self.__dict__[key]
        return outd

