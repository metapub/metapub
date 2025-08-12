"""
SAGE Publications journal patterns and mappings.

SAGE Publications is a major academic publisher with journals using DOI-based URLs
and Volume-Issue-Page (VIP) format URLs depending on the journal.

URL Pattern: https://journals.sagepub.com/doi/pdf/{DOI}
Alternative: http://{host}/content/{volume}/{issue}/{first_page}.full.pdf
Dance Function: the_sage_hula
"""

# SAGE journals using VIP format (extracted from misc_vip.py)
sage_journals = []  # Journal list moved to YAML configuration

# Host mappings for VIP format journals
sage_journal_params = {
    'Ann Clin Biochem': {'host': 'acb.sagepub.com'},
    'Angiology': {'host': 'ang.sagepub.com'},
    'Assessment': {'host': 'asm.sagepub.com'},
    'Clin Appl Thromb Hemost': {'host': 'cat.sagepub.com'},
    'Clin Pediatr': {'host': 'cpj.sagepub.com'},
    'Clin Pediatr (Phila)': {'host': 'cpj.sagepub.com'},
    'J Aging Health': {'host': 'jah.sagepub.com'},
    'J Child Neurol': {'host': 'jcn.sagepub.com'},
    'J Dent Res': {'host': 'jdr.sagepub.com'},
    'J Hum Lact': {'host': 'jhl.sagepub.com'},
    'J Renin Angiotensin Aldosterone Syst': {'host': 'jra.sagepub.com'},
    'Lupus': {'host': 'lup.sagepub.com'},
}

# VIP URL template for SAGE journals
sage_vip_template = 'http://{host}/content/{volume}/{issue}/{first_page}.full.pdf'

# DOI-based template for SAGE reader interface (for the_doi_slide)
sage_format = 'https://journals.sagepub.com/doi/reader/{doi}'

# TODO: pull these into sage_journal_params by finding their host subdomain
# Additional SAGE journals that may use the main DOI-based system
# These would be added as more SAGE journals are identified
sage_additional_journals = []  # Journal list moved to YAML configuration
