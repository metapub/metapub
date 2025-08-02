"""
American Association for Cancer Research (AACR) journal patterns and mappings.

AACR publishes cancer research journals using Volume-Issue-Page (VIP) 
format URLs with journal-specific subdomains.

URL Pattern: http://{host}.aacrjournals.org/content/{volume}/{issue}/{first_page}.full.pdf
Dance Function: the_aacr_jitterbug
"""

# Publisher metadata
PUBLISHER_INFO = {
    'name': 'American Association for Cancer Research',
    'dance_function': 'the_aacr_jitterbug',
    'base_url': 'https://aacrjournals.org',
    'url_pattern': 'http://{host}.aacrjournals.org/content/{volume}/{issue}/{first_page}.full.pdf',
    'identifier_type': 'vip'  # Volume-Issue-Page format
}

# AACR journals using VIP format (extracted from misc_vip.py)
aacr_journals = [
    'Cancer Discov',
    'Cancer Epidemiol Biomarkers Prev',
    'Cancer Res',
    'Clin Cancer Res',
    'Mol Canc Therapeut',
    'Mol Cancer Ther',
]

# Host mappings for VIP format journals
aacr_journal_params = {
    'Cancer Discov': {'host': 'cancerdiscovery'},
    'Cancer Epidemiol Biomarkers Prev': {'host': 'cebp'},
    'Cancer Res': {'host': 'cancerres'},
    'Clin Cancer Res': {'host': 'clincancerres'},
    'Mol Canc Therapeut': {'host': 'mct'},
    'Mol Cancer Ther': {'host': 'mct'},
}

# VIP URL template for AACR journals
aacr_vip_template = 'http://{host}.aacrjournals.org/content/{volume}/{issue}/{first_page}.full.pdf'