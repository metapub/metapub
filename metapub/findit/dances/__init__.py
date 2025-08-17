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
    the_pii_polka, the_pii_prance, the_pii_shuffle, the_pmc_twist, the_bmc_boogie, OK_STATUS_CODES,
    detect_paywall_from_html, PAYWALL_TERMS, unified_uri_get
)

# Publisher-specific dance functions (alphabetical order)
from .aacr import the_aacr_jitterbug
from .acm import the_acm_reel
from .aha import the_aha_waltz
# AIP now uses the_doi_slide generic function
from .allenpress import the_allenpress_advance
from .annualreviews import the_annualreviews_round
# APA now uses the_doi_slide generic function
# APS now uses the_doi_slide generic function
from .asm import the_asm_shimmy
from .asme import the_asme_animal
from .biochemsoc import the_biochemsoc_saunter
# BioOne now uses the_vip_shake generic function
from .bmj import the_bmj_bump
from .brill import the_brill_bridge
from .cambridge import the_cambridge_foxtrot
# CancerBiomed now uses the_vip_shake generic function
# De Gruyter now uses the_doi_slide generic function
from .dovepress import the_dovepress_peacock
from .dustri import the_dustri_polka
# Emerald now uses the_doi_slide generic function
from .oxford_academic import the_oxford_academic_foxtrot
from .eureka import the_eureka_frug
# Frontiers now uses the_doi_slide generic function
from .hilaris import the_hilaris_hop
from .inderscience import the_inderscience_ula
from .ingenta import the_ingenta_flux
from .iop import the_iop_fusion
# IOS Press now uses the_doi_slide generic function
from .jama import the_jama_dance
from .jci import the_jci_jig
from .jstage import the_jstage_dive
from .karger import the_karger_conga
from .longdom import the_longdom_hustle
from .mdpi import the_mdpi_moonwalk
from .najms import the_najms_mazurka
from .nature import the_nature_ballet
from .oatext import the_oatext_orbit
from .plos import the_plos_pogo
from .projectmuse import the_projectmuse_syrtos
from .rsc import the_rsc_reaction
# SAGE now uses the_doi_slide generic function
# Sciendo now uses the_doi_slide generic function
from .scielo import the_scielo_chula
from .sciencedirect import the_sciencedirect_disco
from .scirp import the_scirp_timewarp
# Spandidos now uses the_doi_slide generic function
# Springer now uses the_doi_slide generic function
# Thieme now uses the_doi_slide generic function
# UChicago now uses the_doi_slide generic function
from .walshmedia import the_walshmedia_bora
# Wiley now uses the_doi_slide generic function
from .wjgnet import the_wjgnet_wave
from .wolterskluwer import the_wolterskluwer_volta
# World Scientific now uses the_doi_slide generic function

