__author__ = 'nthmost'

import time
import logging
import coloredlogs

import requests

from urllib.parse import urlparse

from ..crossref import CrossRefFetcher
from ..exceptions import MetaPubError
from ..utils import asciify
from ..config import DEFAULT_CACHE_DIR
from ..pubmedfetcher import PubMedFetcher
from ..convert import doi2pmid
from ..cache_utils import get_cache_path, SQLiteCache, datetime_to_timestamp

from .logic import find_article_from_pma
from .dances import the_sciencedirect_disco, the_doi_2step, the_wolterskluwer_volta
from .journals import SUPPORTED_JOURNALS

log = logging.getLogger('metapub.findit')

coloredlogs.install()

""" findit/findit.py

    Provides FindIt object, providing a tidy object layer
        into the logic.get_pdf_from_pma function. (see logic.py)

    The FindIt class allows lookups of the PDF starting from only a
    DOI or a PMID, using the following instantiation approaches:

    source = FindIt('1234567')   # assumes argument is a pubmed ID

    source = FindIt(pmid=1234567)  # pmid can be an int or a string

    source = FindIt(doi="10.xxxx/xxx.xxx")   # doi instead of pmid.

    See the FindIt docstring for more information.

    *** IMPORTANT NOTE ***

    In many cases, this code performs intermediary HTTP requests in order to
    scrape a PDF url out of a page, and sometimes tests the url to make sure
    that what's being sent back is in fact a PDF.

    If you would like these requests to go through a proxy (e.g. if you would
    like to prevent making multiple requests of the same servers, which may have
    effects like getting your IP shut off from PubMedCentral), set the
    HTTP_PROXY environment variable in your code or on the command line before
    using any FindIt functionality.
"""

CACHE_FILENAME = 'findit.db'

FINDIT_CACHE = None


pm_fetch = None

def _start_engines():
    global pm_fetch
    if not pm_fetch:
        log.debug('Started FindIt engine.')
        pm_fetch = PubMedFetcher()

def _get_findit_cache(cachedir):
    global FINDIT_CACHE
    # allow swap of cache directory without restarting process.
    # this is mostly for testing but also a few limited use cases.
    if not FINDIT_CACHE:
        _cache_path = get_cache_path(cachedir, CACHE_FILENAME)
        FINDIT_CACHE = SQLiteCache(_cache_path)
        log.info('FindIt Cache initialized at %s', _cache_path)
    return FINDIT_CACHE


class FindIt(object):
    """ FindIt

        FindIt helps locate an article's fulltext PDF based on its pubmed ID
        or doi, using the following instantiation approaches:

        source = FindIt('1234567')   # assumes argument is a pubmed ID

        source = FindIt(pmid=1234567)  # pmid can be an int or a string

        source = FindIt(doi="10.xxxx/xxx.xxx")   # doi instead of pmid.

        The machinery in the FindIt object performs all necessary data lookups
        (e.g. looking up a missing DOI, or using a DOI to get a PubMedArticle)
        to end up with a url and reason, which attaches to the FindIt object
        in the following attributes:

        source = FindIt(pmid=PMID)
        source.url
        source.reason
        source.pmid
        source.doi
        source.doi_score

        The "doi_score" is an indication of where the DOI for this PMID ended up
        coming from. If it was supplied by the user or by PubMed, doi_score will be 100.

        If CrossRef came into play during the process to find a DOI that was missing
        for the PubMedArticle object, the doi_score will come from CrossRef (0 to 100).

        Network Timeout Configuration (v0.11+):
        =======================================
        
        FindIt now includes timeout controls to prevent infinite stalling:
        - request_timeout: HTTP request timeout in seconds (default: 10)
        - max_redirects: Maximum redirects to follow (default: 3)
        
        These parameters are applied consistently across all publisher-specific
        strategies to ensure reliable operation.
    """

    def __init__(self, pmid=None, cachedir=DEFAULT_CACHE_DIR, **kwargs):
        """Initialize FindIt to locate full-text PDFs for academic papers.

        Args:
            pmid (str or int, optional): PubMed ID of the article to find.
            cachedir (str, optional): Directory for caching results. Defaults to
                system cache directory. Set to None to disable caching.
            **kwargs: Additional keyword arguments:
                doi (str): DOI of the article (alternative to pmid).
                url (str): Pre-existing URL (for testing/validation).
                use_nih (bool): Use NIH access when available. Defaults to False.
                use_crossref (bool): Enable CrossRef fallback for missing DOIs.
                    Defaults to False.
                doi_min_score (int): Minimum CrossRef confidence score for DOI
                    matches. Defaults to 60.
                verify (bool): Verify URLs by testing HTTP response. Defaults to True.
                retry_errors (bool): Retry if cached result has error reasons like
                    "PAYWALL", "TODO", "CANTDO", or "TXERROR". Note: "NOFORMAT"
                    results are always retried. Defaults to False.
                debug (bool): Enable debug logging. Defaults to False.
                tmpdir (str): Temporary directory for downloads. Defaults to '/tmp'.
                request_timeout (int): Timeout in seconds for HTTP requests. Defaults to 10.
                max_redirects (int): Maximum number of redirects to follow. Defaults to 3.

        Raises:
            MetaPubError: If neither pmid nor doi is provided.

        Note:
            After initialization, access results via the `url` and `reason` attributes.
            If url is None, check `reason` for explanation of why PDF wasn't found.
        """

        _start_engines()

        self.pmid = pmid if pmid else kwargs.get('pmid', None)
        self.doi = kwargs.get('doi', None)
        self.url = kwargs.get('url', None)
        self.reason = None
        self.use_nih = kwargs.get('use_nih', False)
        self.use_crossref = kwargs.get('use_crossref', False)

        if self.use_crossref:
            self.crfetch = CrossRefFetcher()
            log.debug('CrossRefFetcher initialized for FindIt.')

        #TODO: revisit this whole score thing (check our CrossRef work, it's been a minute.)
        self.doi_min_score = kwargs.get('doi_min_score', 60)   #60, maybe?
        self.tmpdir = kwargs.get('tmpdir', '/tmp')
        self.doi_score = None
        self.pma = None

        self.verify = kwargs.get('verify', True)
        retry_errors = kwargs.get('retry_errors', False)
        
        # Network timeout and redirect settings
        self.request_timeout = kwargs.get('request_timeout', 10)
        self.max_redirects = kwargs.get('max_redirects', 3)

        # Store cachedir for registry system
        self._cachedir = cachedir

        if cachedir is None:
            self._cache = None
        else:
            self._cache = _get_findit_cache(cachedir)

        self._log = logging.getLogger('metapub.findit')
        if kwargs.get('debug', False):
            self._log.setLevel(logging.DEBUG)
        else:
            self._log.setLevel(logging.INFO)

        if self.pmid:
            self._load_pma_from_pmid()
        elif self.doi:
            self._load_pma_from_doi()
        else:
            raise MetaPubError(
                'Supply either a pmid or a doi to instantiate. e.g. FindIt(pmid=1234567)')

        try:
            if self._cache:
                self.url, self.reason = self.load_from_cache(verify=self.verify, retry_errors=retry_errors)
            else:
                self.url, self.reason = self.load(verify=self.verify)

        except requests.exceptions.ConnectionError as error:
            self.reason = 'TXERROR: %r' % error

    def load(self, verify=True):
        """Find full-text PDF URL for the loaded article.

        This method performs the core FindIt logic using publisher-specific
        strategies to locate downloadable PDFs.

        Args:
            verify (bool, optional): Test URLs by making HTTP requests to ensure
                files are downloadable. Setting to False speeds up processing
                significantly. Defaults to True.

        Returns:
            Tuple[Optional[str], Optional[str]]: A tuple of (url, reason).
                - url: Direct link to PDF if found, None otherwise.
                - reason: Explanation if PDF not found (e.g., "PAYWALL", "NOFORMAT").
                  May be None if URL was successfully found.

        Note:
            If a ConnectionError occurs during lookup, returns (None, "TXERROR: <details>").
        """
        return find_article_from_pma(self.pma, use_nih=self.use_nih, verify=verify, 
                                   cachedir=self._cachedir, request_timeout=self.request_timeout,
                                   max_redirects=self.max_redirects)

    def load_from_cache(self, verify=True, retry_errors=False):
        """Load article URL from cache, with fallback to fresh lookup.

        Checks cache for previously computed results using article identifiers.
        If not cached or retry_errors is True for error reasons, performs fresh
        lookup and caches the result.

        Args:
            verify (bool, optional): Verify URLs by testing HTTP response.
                Defaults to True.
            retry_errors (bool, optional): Force fresh lookup if cached result
                has error reasons like "TODO", "PAYWALL", "CANTDO", or "TXERROR".
                Note: "NOFORMAT" results are always retried since new publisher
                support is frequently added. Defaults to False.

        Returns:
            Tuple[Optional[str], Optional[str]]: A tuple of (url, reason).
                - url: Direct link to PDF if found, None otherwise.
                - reason: Explanation if PDF not found, None if successful.

        Note:
            Connection errors are not cached to avoid persisting temporary network issues.
        """
        # Always retry NOFORMAT results since new journal support gets added frequently
        retry_reasons = ['NOFORMAT']
        # Optionally retry other error types when requested
        if retry_errors:
            retry_reasons.extend(['PAYWALL', 'TODO', 'CANTDO', 'TXERROR'])

        cache_result = self._query_cache(self.pmid)

        if cache_result:
            url = cache_result['url']
            reason = cache_result.get('reason', '') or ''  # Handle None
            verified = cache_result.get('verify', False)

            # Extract the error code (part before ':' if present)
            reason_code = reason.split(':')[0] if reason else ''

            # Decision logic in ranked order
            # 1. Always retry certain errors.
            # 2. Cache result is unverified && we're still not verifying.
            # 3. Cache result is verified && no error retries called for.

            must_retry = reason_code in retry_reasons

            if not must_retry and (verified or not verify):
                return (url, reason)


        # === RETRY === #
        # we're here for one of the following reasons:
        # 1) no cache result for this query
        # 2) previous result was unverified and now verify=True
        # 3) previous result had a "reason" in retry_reasons
        url, reason = self.load(verify=verify)
        self._store_cache(self.pmid, url=url, reason=reason, verify=verify)
        return (url, reason)

    def _load_pma_from_pmid(self):
        """ Loads self.pma if self.pmid is present.

        Mutates:
            self.doi (using crossref to look this information up if necessary)
            self.doi_score (100 if doi found in self.pma, else crossref score)
        """

        self.pma = pm_fetch.article_by_pmid(self.pmid)

        if self.pma.doi:
            self.doi = self.pma.doi
            self.doi_score = 100
            return

        # if desired, try to learn the DOI using CrossRef
        if self.pma.doi == None:
            if self.use_crossref:
                self._log.debug('Using CrossRef to find DOI for PMID %s', self.pmid)
                work = self.crfetch.article_by_pma(self.pma)
                if work:
                    self.doi = work.doi
                    self.doi_score = work.score
                    self._log.debug('\tFound DOI ', self.doi, ' with score ', self.doi_score)
                else:
                    self._log.debug('\tCrossRef DOI lookup failed for PMID %s.', self.pmid)
                    self.reason = 'MISSING: doi (CrossRef lookup failed)'
            else:
                self.reason = 'MISSING: doi (CrossRef lookups disabled)'

    def _load_pma_from_doi(self):
        """ Loads self.pma if self.doi is present.

        Mutates:
            self.pmid (using metapub.convert.doi2pmid)
            self.pma  (if pmid was found)
            self.doi_score (10.0 if doi found in self.pma, else crossref score)
        """
        self.pmid = doi2pmid(self.doi)
        if self.pmid:
            self.pma = pm_fetch.article_by_pmid(self.pmid)
            self.doi_score = 100
        else:
            raise MetaPubError('Could not get a pmid for doi %s' % self.doi)

    def to_dict(self):
        """ Returns a dictionary containing the public attributes of this object"""
        return {'pmid': self.pmid,
                'doi': self.doi,
                'reason': self.reason,
                'url': self.url,
                'doi_score': self.doi_score,
                }

    def _make_cache_key(self, pmid):
        """ Returns normalized key (pmid as integer) for hash lookup / store. """
        return int(pmid)

    def _store_cache(self, cache_key, **kwargs):
        """ Store supplied cache_key pointing to values supplied in kwargs.

        A time.time() timestamp will be added to the value dictionary when stored.

        There is no return from this function. Exceptions from the SQLiteCache
        object may be raised.
        """
        cache_value = kwargs.copy()
        cache_value['timestamp'] = time.time()
        self._cache[self._make_cache_key(cache_key)] = cache_value

    def _query_cache(self, pmid, expiry_date=None):
        """ Return results of a lookup from the cache, if available.
        Return None if not available.

        Cache results are stored with a time.time() timestamp.

        When expiry_date is supplied, results from the cache past their
        sell-by date will be expunged from the cache and return will be None.

        expiry_date can be either a python datetime or a timestamp.

        :param: cache_key: (required)
        :param: expiry_date (optional, default None)
        :rtype: (url, reason) or None
        """

        if hasattr(expiry_date, 'strftime'):
            # convert to timestamp
            sellby = datetime_to_timestamp(expiry_date)
        else:
            # make sure sellby is a number, not None
            sellby = expiry_date if expiry_date else 0

        if self._cache:
            cache_key = self._make_cache_key(pmid)
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

