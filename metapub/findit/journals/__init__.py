from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

# All journal configurations are now handled through the YAML-based registry system

try:
    from ..registry import JournalRegistry
except ImportError:
    JournalRegistry = None

# simple_formats_pmid: links to PDFs that can be constructed using the
# pubmed ID
simple_formats_pmid = {
    'Medicina (B Aires)': 'http://www.medicinabuenosaires.com/PMID/{pmid}.pdf',
}


# HELP NEEDED ESPECIALLY WITH CHINESE JOURNALS...!
# https://zhyxycx.periodicals.net.cn/default.html

