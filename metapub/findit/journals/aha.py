"""
American Heart Association (AHA) journal patterns and mappings.

AHA publishes cardiovascular research journals using Volume-Issue-Page (VIP) 
format URLs with journal-specific subdomains.

URL Pattern: http://{host}.ahajournals.org/content/{volume}/{issue}/{first_page}.full.pdf
Dance Function: the_aha_waltz
"""

# AHA journals using VIP format (extracted from misc_vip.py)
aha_journals = [
    'Arterioscler Thromb Vasc Biol',
    'Circulation',
    'Circ Arrhythm Electrophysiol',
    'Circ Cardiovasc Genet',
    'Circ Res',
    'Hypertension',
    'Stroke',
]

# Host mappings for VIP format journals
aha_journal_params = {
    'Arterioscler Thromb Vasc Biol': {'host': 'atvb'},
    'Circulation': {'host': 'circ'},
    'Circ Arrhythm Electrophysiol': {'host': 'circep'},
    'Circ Cardiovasc Genet': {'host': 'circgenetics'},
    'Circ Res': {'host': 'circres'},
    'Hypertension': {'host': 'hyper'},
    'Stroke': {'host': 'stroke'},
}

# VIP URL template for AHA journals
aha_vip_template = 'http://{host}.ahajournals.org/content/{volume}/{issue}/{first_page}.full.pdf'