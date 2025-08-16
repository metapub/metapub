from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

from .misc_pii import simple_formats_pii
from .misc_vip import vip_format, vip_journals, vip_journals_nonstandard
from .cantdo_list import JOURNAL_CANTDO_LIST

try:
    from ..registry import JournalRegistry
except ImportError:
    JournalRegistry = None

# simple_formats_pmid: links to PDFs that can be constructed using the
# pubmed ID
simple_formats_pmid = {
    'Medicina (B Aires)': 'http://www.medicinabuenosaires.com/PMID/{pmid}.pdf',
}

# Registry-based SUPPORTED_JOURNALS
def get_supported_journals():
    """Get list of supported journals from the registry database.

    This replaces the static SUPPORTED_JOURNALS list with a dynamic
    version that reads from the journal registry database.
    """
    if JournalRegistry is None:
        # Fallback to empty list if registry not available
        return []
        
    try:
        registry = JournalRegistry()
        journals = registry.get_all_journals()
        registry.close()
        return sorted(journals)
    except Exception:
        # Fallback to empty list if registry not available
        return []

# Lazy loading of SUPPORTED_JOURNALS
_supported_journals_cache = None

def _get_supported_journals():
    """Get supported journals with caching."""
    global _supported_journals_cache
    if _supported_journals_cache is None:
        _supported_journals_cache = get_supported_journals()
    return _supported_journals_cache

# Property-like access to SUPPORTED_JOURNALS
class SupportedJournalsProperty:
    def __bool__(self):
        return len(_get_supported_journals()) > 0

    def __len__(self):
        return len(_get_supported_journals())

    def __iter__(self):
        return iter(_get_supported_journals())

    def __contains__(self, item):
        return item in _get_supported_journals()

    def __getitem__(self, key):
        return _get_supported_journals()[key]

# Create property-like object for backward compatibility
SUPPORTED_JOURNALS = SupportedJournalsProperty()

# HELP NEEDED ESPECIALLY WITH CHINESE JOURNALS...!
# https://zhyxycx.periodicals.net.cn/default.html

