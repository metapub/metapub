"""
American Chemical Society (ACS) journal patterns and mappings.

ACS publishes chemistry and chemical engineering journals using DOI-based URLs.
All ACS journals follow a consistent DOI-based PDF access pattern.

URL Pattern: http://pubs.acs.org/doi/pdf/{DOI}
Dance Function: the_doi_slide
"""

# Publisher metadata
PUBLISHER_INFO = {
    'name': 'American Chemical Society',
    'dance_function': 'the_doi_slide',
    'base_url': 'http://pubs.acs.org',
    'url_pattern': 'http://pubs.acs.org/doi/pdf/{doi}',
    'identifier_type': 'doi'
}

# Template for ACS DOI-based URLs
acs_template = 'http://pubs.acs.org/doi/pdf/{doi}'

# American Chemical Society journals (extracted from misc_doi.py)
acs_journals = [
    'ACS Appl Bio Mater',
    'ACS Appl Electron Mater',
    'ACS Appl Energy Mater',
    'ACS Appl Mater',
    'ACS Appl Mater Interfaces',
    'ACS Appl Nano Mater',
    'ACS Appl Polym Mater',
    'ACS Biomater Sci Eng',
    'ACS Catal',
    'ACS Cent Sci',
    'ACS Chem Biol',
    'ACS Chem Neurosci',
    'ACS Comb Sci',
    'ACS Earth Space Chem',
    'ACS Energy Lett',
    'ACS Infect Dis',
    'ACS Macro Lett',
    'ACS Mater Lett',
    'ACS Med Chem Lett',
    'ACS Nano',
    'ACS Omega',
    'ACS Pharmacol Transl Sci',
    'ACS Photonics',
    'ACS Sens',
    'ACS Sustain Chem Eng',
    'ACS Symp Ser Am Chem Soc',
    'ACS Synth Biol',
    'Acc Chem Res',
    'Acc Mater Res',
    'Anal Chem',
    'Biochemistry',
    'Bioconjug Chem',
    'Biomacromolecules',
    'Chem Health Saf',
    'Chem Mater',
    'Chem Res Toxicol',
    'Chem Rev',
    'Cryst Growth Des',
    'Energy Fuels',
    'Environ Sci Technol',
    'Environ Sci Technol Lett',
    'Ind Eng Chem',
    'Ind Eng Chem Res',
    'Inorg Chem',
    'J Agric Food Chem',
    'J Am Chem Soc',
    'J Chem Doc',
    'J Chem Educ',
    'J Chem Eng Data',
    'J Chem Health Saf',
    'J Chem Inf Comput Sci',
    'J Chem Inf Model',
    'J Chem Theory Comput',
    'J Comb Chem',
    'J Med Chem',
    'J Med Pharm Chem',
    'J Nat Prod',
    'J Phys Chem',
    'J Phys Chem A',
    'J Phys Chem B',
    'J Phys Chem Biophys',
    'J Phys Chem C Nanomater Interfaces',
    'J Phys Chem Lett',
    'J Phys Colloid Chem',
    'J Proteome Res',
    'Langmuir',
    'Macromolecules',
    'Mol Pharm',
    'Nano Lett',
    'Org Lett',
    'Org Process Res Dev',
    'Organometallics',
    'Photonics',
]