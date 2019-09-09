import os
import coloredlogs
import logging

coloredlogs.install()

log = logging.getLogger('metapub.config')

PKGNAME = 'metapub'

# email address of this package's maintainer, included with certain NCBI calls.
# you can change this to another email address if you would prefer to be contacted.
DEFAULT_EMAIL = 'naomi@nthmost.com'

# where to place XML (temporarily) when downloaded.
TMPDIR = '/tmp'

# default cache directory for SQLite cache engines
DEFAULT_CACHE_DIR = os.path.join(os.path.expanduser('~'), '.cache')
if not os.access(DEFAULT_CACHE_DIR, os.W_OK):
    # default cache dir is not writeable
    # therefore ask the os for a temp directory
    import tempfile
    DEFAULT_CACHE_DIR = tempfile.gettempdir()

API_KEY = os.getenv('NCBI_API_KEY', None)
if API_KEY:
    log.debug('NCBI_API_KEY found.')
else:
    log.warning('NCBI_API_KEY was not set.')

def get_process_log(filepath, loglevel=logging.INFO, name=PKGNAME+'.process'):
    "Sets up a file-based logger for process logging and returns its log object."
    log = logging.getLogger(name)
    log.setLevel(loglevel)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh = logging.FileHandler(filepath)
    fh.setFormatter(formatter)
    fh.setLevel(loglevel)
    log.addHandler(fh)
    return log

def get_data_log(filepath, name=PKGNAME+'.data'):
    "Sets up a file-based logger for data logging and returns its log object."
    datalog = logging.getLogger(name)
    datalog.setLevel(logging.DEBUG)
    datalog.propagate = False
    formatter = logging.Formatter('')
    fh = logging.FileHandler(filepath)
    fh.setFormatter(formatter)
    datalog.addHandler(fh)
    return datalog

