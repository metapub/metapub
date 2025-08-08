"""
American Physiological Society (APS) journal patterns and mappings.

APS publishes physiology journals using Volume-Issue-Page (VIP) 
format URLs with journal-specific subdomains.

URL Pattern: http://{host}.physiology.org/content/{volume}/{issue}/{first_page}.full.pdf
Dance Function: the_aps_quickstep
"""

# APS journals using VIP format (extracted from misc_vip.py)
aps_journals = [
    'Am J Physiol Cell Physiol',
    'Am J Physiol Endocrinol Metab',
    'Am J Physiol Gastrointest Liver Physiol',
    'Am J Physiol Heart Circ Physiol',
    'Am J Physiol Lung Cell Mol Physiol',
    'Am J Physiol Regul Integr Comp Physiol',
    'Am J Physiol Renal Physiol',
    'J Appl Physiol',
    'J Neurophysiol',
    'Physiology (Bethesda)',
    'Physiol Genomics',
    'Physiol Rep',
    'Physiol Rev',
]

# Host mappings for VIP format journals
aps_journal_params = {
    'Am J Physiol Cell Physiol': {'host': 'ajpcell'},
    'Am J Physiol Endocrinol Metab': {'host': 'ajpendo'},
    'Am J Physiol Gastrointest Liver Physiol': {'host': 'ajpgi'},
    'Am J Physiol Heart Circ Physiol': {'host': 'ajpheart'},
    'Am J Physiol Lung Cell Mol Physiol': {'host': 'ajplung'},
    'Am J Physiol Regul Integr Comp Physiol': {'host': 'ajpregu'},
    'Am J Physiol Renal Physiol': {'host': 'ajprenal'},
    'J Appl Physiol': {'host': 'jap'},
    'J Neurophysiol': {'host': 'jn'},  # Note: original had 'jb' which seems wrong
    'Physiology (Bethesda)': {'host': 'physiologyonline'},
    'Physiol Genomics': {'host': 'physiolgenomics'},
    'Physiol Rep': {'host': 'physreports'},
    'Physiol Rev': {'host': 'physrev'},
}

# VIP URL template for APS journals  
aps_vip_template = 'http://{host}.physiology.org/content/{volume}/{issue}/{first_page}.full.pdf'