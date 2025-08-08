from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

# Legacy imports still needed by some parts of the system
from .misc_pii import simple_formats_pii
from .misc_vip import vip_format, vip_journals, vip_journals_nonstandard
from .bmc import BMC_journals, BMC_format
from .cambridge import cambridge_journals
from .sage import sage_journals, sage_journal_params, sage_vip_template
from .informa import informa_journals, informa_template
from .oxford import oxford_vip_template
from .bmj import bmj_journals, bmj_vip_template
from .nejm import nejm_journals, PUBLISHER_INFO as nejm_publisher_info
from .lww import lww_journals, lww_template
from .acs import acs_journals, acs_template
from .taylor_francis import taylor_francis_journals, taylor_francis_template
from .wiley import wiley_journals, wiley_template
from .cantdo_list import JOURNAL_CANTDO_LIST

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
    try:
        from ..registry import JournalRegistry
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

