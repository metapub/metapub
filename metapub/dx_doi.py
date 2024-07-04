import logging
import requests
import certifi

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

    _log = logging.getLogger('metapub.DxDOI')

    def __init__(self, **kwargs):
        if kwargs.get('debug', False):
            self._log.setLevel(logging.DEBUG)
        else:
            self._log.setLevel(logging.INFO)

        cachedir = kwargs.get('cachedir', DEFAULT_CACHE_DIR)
        self._cache = _get_dx_doi_cache(cachedir)

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
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'http://dx.doi.org'
        }

        session = requests.Session()
        session.headers.update(headers)

        try:
            response = session.get(DX_DOI_URL % doi, allow_redirects=True, verify=certifi.where())
            # Ship the result from 404 and 403 "Forbidden" since this is a positive result.
            # We just can't continue reading from this URL due to bot detection or publisher dumbness.
            if response.status_code in [200, 301, 302, 307, 308, 403, 404]:
                return response.url
            response.raise_for_status()
        except requests.RequestException as e:
            raise DxDOIError(f'dx.doi.org lookup failed for doi "{doi}" (Exception: {str(e)})')

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
