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
    the_pii_polka, the_pmc_twist, the_bmc_boogie, OK_STATUS_CODES,
    detect_paywall_from_html, PAYWALL_TERMS
)

# Publisher-specific dance functions (alphabetical order)
from .aacr import the_aacr_jitterbug
from .acm import the_acm_reel
from .aha import the_aha_waltz
from .aip import the_aip_allegro
from .allenpress import the_allenpress_advance
from .annualreviews import the_annualreviews_round
from .apa import the_apa_dab
from .aps import the_aps_quickstep
from .asm import the_asm_shimmy
from .asme import the_asme_animal
from .biochemsoc import the_biochemsoc_saunter
from .bioone import the_bioone_bounce
from .brill import the_brill_bridge
from .cambridge import the_cambridge_foxtrot
from .cell import the_cell_pogo
from .degruyter import the_degruyter_danza
from .dovepress import the_dovepress_peacock
from .emerald import the_emerald_ceili
from .endo import the_endo_mambo
from .eureka import the_eureka_frug
from .frontiers import the_frontiers_square
from .hilaris import the_hilaris_hop
from .inderscience import the_inderscience_ula
from .ingenta import the_ingenta_flux
from .iop import the_iop_fusion
from .iospress import the_iospress_freestyle
from .jama import the_jama_dance
from .jci import the_jci_jig
from .jstage import the_jstage_dive
from .karger import the_karger_conga
from .lancet import the_lancet_tango
from .longdom import the_longdom_hustle
from .mdpi import the_mdpi_moonwalk
from .najms import the_najms_mazurka
from .nature import the_nature_ballet
from .oatext import the_oatext_orbit
from .projectmuse import the_projectmuse_syrtos
from .rsc import the_rsc_reaction
from .sage import the_sage_hula
from .sciendo import the_sciendo_spiral
from .scielo import the_scielo_chula
from .sciencedirect import the_sciencedirect_disco
from .scirp import the_scirp_timewarp
from .spandidos import the_spandidos_lambada
from .springer import the_springer_shag
from .thieme import the_thieme_tap
from .uchicago import the_uchicago_walk
from .walshmedia import the_walshmedia_bora
from .wiley import the_wiley_shuffle
from .wjgnet import the_wjgnet_wave
from .wolterskluwer import the_wolterskluwer_volta
from .worldscientific import the_worldscientific_robot

