"""Dance functions organized by publisher.

This module provides organized dance functions in separate files.
All dance functions have been extracted from the main dances.py file
and organized by publisher for better maintainability.
"""

# Import organized dance functions from individual publisher modules

# Generic/framework functions
from .generic import (
    the_doi_2step, standardize_journal_name, verify_pdf_url, rectify_pma_for_vip_links,
    the_doi_slide, the_pmid_pogo, the_vip_shake, the_vip_nonstandard_shake,
    the_pii_polka, the_pmc_twist, the_bmc_boogie, OK_STATUS_CODES
)

from .acm import the_acm_reel
from .annualreviews import the_annualreviews_round
from .frontiers import the_frontiers_square
from .sciendo import the_sciendo_spiral
from .aip import the_aip_allegro
from .jci import the_jci_jig
from .najms import the_najms_mazurka
from .aaas import the_aaas_twist
from .jama import the_jama_dance
from .jstage import the_jstage_dive
from .wiley import the_wiley_shuffle
from .nature import the_nature_ballet
from .sciencedirect import the_sciencedirect_disco
from .dovepress import the_dovepress_peacock
from .springer import the_springer_shag
from .scielo import the_scielo_chula
from .lancet import the_lancet_tango
from .wolterskluwer import the_wolterskluwer_volta

