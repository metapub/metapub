import os, logging

from .config import PKGNAME, API_KEY
from .exceptions import MetaPubError

# == suppress the chatter of requests == #
logging.getLogger('requests').setLevel(logging.ERROR)
# ==

import functools


@functools.lru_cache(maxsize=1)
def get_eutils_client(cache_path, cache=None):
    """
    :param cache_path: valid filesystem path to SQLite cache file
    :param api_key: (optional) NCBI API Key obtainable from https://www.ncbi.nlm.nih.gov
    :return: lightweight NCBI client object (drop-in replacement for eutils)
    """
    from .eutils_compat import QueryService
    return QueryService(cache=cache_path, api_key=API_KEY)


