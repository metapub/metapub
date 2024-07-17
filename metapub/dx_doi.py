import logging
import requests
import certifi
from requests.adapters import HTTPAdapter
import urllib3
from urllib3.util import Retry

from .cache_utils import SQLiteCache, get_cache_path
from .base import Borg
from .config import DEFAULT_CACHE_DIR
from .exceptions import BadDOI, DxDOIError
from .text_mining import find_doi_in_string

DX_DOI_URL = 'http://dx.doi.org/%s'
CACHE_FILENAME = 'dx_doi-cache.db'

DX_DOI_CACHE = None

def _get_dx_doi_cache(cachedir=DEFAULT_CACHE_DIR):
    global DX_DOI_CACHE
    if not DX_DOI_CACHE:
        _cache_path = get_cache_path(cachedir, CACHE_FILENAME)
        DX_DOI_CACHE = SQLiteCache(_cache_path)
    return DX_DOI_CACHE


class DxDOI(Borg):
    """ Looks up DOIs in dx.doi.org and caches results in an SQLite
    cache. This is a Borg singleton object.

    Methods:

        resolve (doi, *args): uses supplied doi to get link to publisher.

        check_doi (doi, *args): returns doi if supplied DOI is good,
                                raises BadDOI if not good.
    """

    def __init__(self, retries=1, **kwargs):
        self._log = logging.getLogger('metapub.DxDOI')
        self._log.setLevel(logging.INFO)
        self.retries = retries
        cachedir = kwargs.get('cachedir', DEFAULT_CACHE_DIR)
        self._cache = _get_dx_doi_cache(cachedir)

    def _create_session(self):
        session = requests.Session()
        retry_strategy = Retry(
            total=self.retries,  # Total number of retries
            backoff_factor=0.1,  # Don't wait long for retries
            status_forcelist=[429, 500, 502, 503, 504],  # Retry on these status codes
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'http://dx.doi.org'
        })
        return session

    def check_doi(self, doi, whitespace=False):
        """ Checks validity of supplied doi.

        If whitespace is True (default False), allows supplied doi to
        contain whitespace.

        :param doi: (str)
        :param whitespace: (bool)
        :return: doi (str) -- verified DOI)
        :raise BadDOI if supplied DOI fails regular expression check.
        """

        result_doi = find_doi_in_string(doi, whitespace=False)
        if result_doi is None:
            raise BadDOI('Supplied DOI "%s" fails doi check' % doi)
        return doi

    def _query_api(self, doi):
        session = self._create_session()
        response = None
        try:
            response = session.get(DX_DOI_URL % doi, allow_redirects=True, verify=certifi.where(), timeout=5)
            response.raise_for_status()
            if response.status_code in [200, 301, 302, 307, 308, 402, 403]:
                self._log.info(f'URL is accessible: {response.url} (Status code: {response.status_code})')
                self._cache[doi] = response.url
                return response.url
        except requests.exceptions.RequestException as e:
            if response is not None and response.status_code in [402, 403, 408, 429]:
                self._log.info(f'URL returned status code {response.status_code}: {response.url}')
                self._cache[doi] = response.url
                return response.url
            elif isinstance(e, requests.exceptions.ConnectionError):
                self._log.error(f'Connection error for URL: {DX_DOI_URL % doi}')
            raise DxDOIError(f'Error processing DOI {doi}: {str(e)}')
        finally:
            session.close()

    def resolve(self, doi, check_doi=True, whitespace=False, skip_cache=False):
        """ Takes a doi (string), returns a url to article page on journal website.

        if check_doi is True (default True), checks DOI before
        submitting query to dx.doi.org.

        if whitespace is True (default False), allows prospective
        dois to contain whitespace when checked.

        if skip_cache is True (default False), doesn't check cache for
        pre-existing results (loads from remote dx.doi.org).

        :param doi: (str)
        :param check_doi: (bool)
        :param whitespace: (bool)
        :param skip_cache: (bool)
        :return: url (str)
        :raises BadDOI: if supplied DOI failed regular expression check
        :raises DxDOIError: if not-ok HTTP status code while loading url
        :raises ConnectionError: if problem making dx.doi.org connection
        """
        if doi is None or doi.strip()=='':
            raise BadDOI('DOI cannot be None or empty string')

        if check_doi:
            doi = self.check_doi(doi, whitespace=whitespace)
            
        url = None
        if not skip_cache:
            url = self._query_cache(doi)

        if url == None:
            url = self._query_api(doi)

            if self._cache:
                cache_key = self._make_cache_key(doi)
                self._cache[cache_key] = url
                self._log.info('cached results for key {cache_key} ({doi}) '.format(
                        cache_key=cache_key, doi=doi))
        return url

    def _make_cache_key(self, inp):
        return inp.strip()

    def _query_cache(self, key):
        """ Return results for a cache lookup, if found.

        :param key: (str)
        :return: val (str) or None
        """
        if self._cache:
            cache_key = self._make_cache_key(key)
            try:
                val = self._cache[cache_key]
                self._log.debug('cache hit for key {cache_key} ({key}) '.format(
                    cache_key=cache_key, key=key))
                return val
            except KeyError:
                self._log.debug('cache miss for key {cache_key} ({key}) '.format(
                        cache_key=cache_key, key=key))
                return None
        else:
            self._log.debug('cache disabled (self._cache is None)')
            return None



