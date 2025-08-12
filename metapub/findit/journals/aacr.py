"""
American Association for Cancer Research (AACR) journal patterns and mappings.

AACR publishes cancer research journals using Volume-Issue-Page (VIP)
format URLs with journal-specific subdomains.

URL Pattern: http://{host}.aacrjournals.org/content/{volume}/{issue}/{first_page}.full.pdf
Dance Function: the_aacr_jitterbug
"""

# AACR journals using VIP format (extracted from misc_vip.py)
aacr_journals = []  # Journal list moved to YAML configuration

# Host mappings for VIP format journals
aacr_journal_params = {
    'Blood Cancer Discov': {'host': 'bloodcancerdiscov'},
    'Cancer Discov': {'host': 'cancerdiscovery'},
    'Cancer Epidemiol Biomarkers Prev': {'host': 'cebp'},
    'Cancer Immunol Res': {'host': 'cancerimmunolres'},
    'Cancer Prev Res (Phila)': {'host': 'cancerpreventionresearch'},
    'Cancer Res': {'host': 'cancerres'},
    'Clin Cancer Res': {'host': 'clincancerres'},
    'Mol Canc Therapeut': {'host': 'mct'},
    'Mol Cancer Ther': {'host': 'mct'},
    'Mol Cancer Res': {'host': 'mcr'},
}

# VIP URL template for AACR journals
aacr_vip_template = 'http://{host}.aacrjournals.org/content/{volume}/{issue}/{first_page}.full.pdf'
