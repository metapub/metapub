from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

from .aaas import aaas_format, aaas_journals
from .biochemsoc import biochemsoc_format, biochemsoc_journals
from .bmc import BMC_journals, BMC_format
from .cell import cell_format, cell_journals
from .degruyter import degruyter_journals
from .dustri import dustri_journals
from .endo import endo_journals
from .jama import jama_journals
from .jstage import jstage_journals
from .karger import karger_journals, karger_format
from .lancet import lancet_journals
from .nature import nature_journals, nature_format
from .misc_doi import doi_templates, simple_formats_doi
from .misc_pii import simple_formats_pii
from .misc_vip import vip_format, vip_journals, vip_journals_nonstandard
from .scielo import scielo_journals, scielo_format
from .sciencedirect import sciencedirect_journals, sciencedirect_url
from .springer import springer_journals
from .spandidos import spandidos_format, spandidos_journals
from .wiley import wiley_journals
from .wolterskluwer import wolterskluwer_journals

from .cantdo_list import JOURNAL_CANTDO_LIST

from .paywalled import (schattauer_journals, RSC_journals,
                       thieme_journals, weird_paywall_publishers)

# At the bottom of this script, collect all journal abbrevs into a set.
SUPPORTED_JOURNALS = set()

#### Formats too small to have their own submodules (yet):

# JCI == Journal of Clinical Investigation
jci_journals = ('J Clin Invest')

# NAJMS == North Am J Med Sci
najms_journals = ('N Am J Med Sci')

paywall_journals = schattauer_journals + thieme_journals + \
                   weird_paywall_publishers + RSC_journals

# simple_formats_pmid: links to PDFs that can be constructed using the
# pubmed ID
simple_formats_pmid = {
    'Medicina (B Aires)': 'http://www.medicinabuenosaires.com/PMID/{pmid}.pdf',
}

# journals whose articles can best be accessed by loading up via dx.doi.org
#       and then doing some text replacement on the URL.
doi2step_journals = (
    # ex.
    # http://www.palgrave-journals.com/jphp/journal/v36/n2/pdf/jphp201453a.pdf
    'J Public Health Policy'
)

##########

# SUPPORTED_JOURNALS AUTOMATED COLLECTION

# Helper function to add journal abbreviations to the set
def _add_journals(journals):
    if isinstance(journals, dict):
        SUPPORTED_JOURNALS.update(journals.keys())
    elif isinstance(journals, (list, tuple)):
        SUPPORTED_JOURNALS.update(journals)

# Adding journal abbreviations from various sources
_add_journals(aaas_journals)
_add_journals(biochemsoc_journals)
_add_journals(BMC_journals)
_add_journals(cell_journals)
_add_journals(degruyter_journals)
_add_journals(dustri_journals)
_add_journals(endo_journals)
_add_journals(jama_journals)
_add_journals(jstage_journals)
_add_journals(karger_journals)
_add_journals(lancet_journals)
_add_journals(nature_journals)
_add_journals(vip_journals)
_add_journals(vip_journals_nonstandard)
_add_journals(scielo_journals)
_add_journals(sciencedirect_journals)
_add_journals(springer_journals)
_add_journals(spandidos_journals)
_add_journals(wiley_journals)
_add_journals(wolterskluwer_journals)
_add_journals(jci_journals)
_add_journals(najms_journals)
_add_journals(paywall_journals)
_add_journals(doi2step_journals)

# Convert the set to a sorted list
SUPPORTED_JOURNALS = sorted(SUPPORTED_JOURNALS)

#__all__ = [
#    "SUPPORTED_JOURNALS",
    # Other variables and imports
#]


