__doc__ = "Utilities for cache file creation and management."
__author__ = "nthmost"

import os, logging
from datetime import datetime

from .ncbi_client import SimpleCache as SQLiteCache

from .config import PKGNAME, DEFAULT_CACHE_DIR
from .exceptions import MetaPubError


def datetime_to_timestamp(dt, epoch=datetime(1970,1,1)):
    """takes a python datetime object and converts it to a Unix timestamp.

    This is a non-timezone-aware function.

    :param dt: datetime to convert to timestamp
    :param epoch: datetime, option specification of start of epoch [default: 1/1/1970]
    :return: timestamp
    """
    td = dt - epoch
    return (td.microseconds + (td.seconds + td.days * 86400))


def get_cache_path(cachedir=DEFAULT_CACHE_DIR, filename='metapub-cache.db'):
    """ checks if cachedir exists; if not, tries to create it;
    raises MetaPubError if it can't be created.

        if cachedir is None, returns None.

        Default: DEFAULT_CACHE_DIR set in config.py (~/.cache)

        Supports expansion of user directory shortcut '~' to full path.

    :param cachedir: directory to store
    :param filename: name of cache file
    :return: path to SQLite DB file
    :raises MetaPubError
    """
    if cachedir is None:
        return None

    elif cachedir.find('~') > -1:
        cachedir = os.path.expanduser(cachedir)

    if _require_dir(cachedir):
        return os.path.join(cachedir, filename)
    else:
        raise MetaPubError('Could not create cache directory location %s' % cachedir)


def _require_dir(targetdir):
    """Ensure a directory exists, creating it if necessary.
    
    Internal utility function used by get_cache_path to ensure
    cache directories exist before use.
    
    :param targetdir: path to directory that must exist
    :type targetdir: str
    :return: True if directory exists or was created successfully, False otherwise
    :rtype: bool
    """
    if os.path.exists(targetdir):
        return True

    try:
        os.makedirs(targetdir)
        return True
    except OSError:
        return False

def cleanup_dir(cachedir):
    """Remove all files from a cache directory and delete the directory itself.
    
    This function is used for cache maintenance and cleanup operations.
    Silently handles errors if files cannot be removed.
    
    :param cachedir: path to directory to clean up
    :type cachedir: str
    :return: None
    """
    try:
        for item in os.listdir(cachedir):
            os.unlink(os.path.join(cachedir, item))
    except OSError:
        pass

    try:
        os.rmdir(cachedir)
    except OSError:
        pass
