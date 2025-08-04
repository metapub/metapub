"""Royal Society of Chemistry (RSC) Publishers (pubs.rsc.org) journals.

The Royal Society of Chemistry (RSC) is a learned society and professional body
for chemical scientists, founded in 1841. They publish over 50 journals covering
all areas of chemistry and related fields.

Based on investigation, RSC uses DOI prefix 10.1039 for their publications
hosted on pubs.rsc.org. Many RSC journals have open access articles or trial access.

URL pattern investigation shows DOI resolution to pubs.rsc.org article pages.
Some content may be behind institutional paywalls but many articles have
open access or are available through various access models.
"""

# DOI-based template for Royal Society of Chemistry
# Based on investigation showing DOI prefix 10.1039 redirects to pubs.rsc.org
rsc_template = 'https://doi.org/{doi}'

# Royal Society of Chemistry journals from categorized analysis
# These journals were identified from pubs.rsc.org domain in categorized_unknown_journals.txt
# Includes historical and current RSC publications across all chemistry fields
rsc_journals = [
    'Discuss Faraday Soc',
    'Faraday Discuss Chem Soc', 
    'React Chem Eng',
    'Environ Sci (Camb)',
    'Environ Sci Nano',
    'Mater Horiz',
    'Inorg Chem Front',
    'Org Chem Front',
    'CrystEngComm',
    'Chem Commun (Camb)',
    'Chem Soc Rev',
    'J Chem Soc Chem Commun',
    'J Anal At Spectrom',
    'J Mater Chem',
    'New J Chem',
    'Faraday Discuss',
    'Catal Sci Technol',
    'Nanoscale',
    'J Mater Chem C Mater',
    'Anal Methods',
    'Chem Sci',
    'Energy Environ Sci',
    'Biomater Sci',
    'Polym Chem',
    'J Mater Chem A Mater',
    'J Mater Chem B',
    'Environ Sci Process Impacts',
    'J Chem Soc Perkin 1',
    'Soft Matter',
    'RSC Med Chem',
    'RSC Chem Biol',
    'Mater Adv',
    'Mol Biosyst',
    'Green Chem',
    'RSC Adv',
    'Sustain Energy Fuels',
    'Nanoscale Adv',
    'Org Biomol Chem',
    'J Chem Soc',
    'J Environ Monit',
    'Nouv J Chim',
    'Lab Chip',
    'Dalton Trans',
    'Phys Chem Chem Phys',
    'Analyst',
    'Mater Chem Front',
    'Mol Syst Des Eng',
    'Nanoscale Horiz',
    'Mol Omics',
    'Medchemcomm', 
    'Food Funct',
    
    # Include the existing journal from paywalled.py
    'Nat Prod Rep'
]