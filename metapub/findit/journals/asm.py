"""
American Society of Microbiology (ASM) journal patterns and mappings.

ASM publishes microbiology, infectious disease, and related journals using
Volume-Issue-Page (VIP) format URLs with journal-specific subdomains.

URL Pattern: http://{host}.asm.org/content/{volume}/{issue}/{first_page}.full.pdf
Dance Function: the_asm_shimmy
"""

# ASM journals using VIP format (extracted from misc_vip.py)
asm_journals = [
    'Antimicrob Agents Chemother',
    'Appl Environ Microbiol', 
    'Clin Microbiol Rev',
    'Clin Vaccine Immunol',
    'Eukaryot Cell',
    'Genome Announc',
    'Infect Immun',
    'J Bacteriol',
    'J Clin Microbiol',
    'J Virol',
    'MBio',
    'mSystems',
    'mSphere', 
    'Microbiol Mol Biol Rev',
    'Mol Cell Biol',
]

# Host mappings for VIP format journals
asm_journal_params = {
    'Antimicrob Agents Chemother': {'host': 'aac'},
    'Appl Environ Microbiol': {'host': 'aem'},
    'Clin Microbiol Rev': {'host': 'cmr'},
    'Clin Vaccine Immunol': {'host': 'cvi'},
    'Eukaryot Cell': {'host': 'ec'},
    'Genome Announc': {'host': 'genomea'},
    'Infect Immun': {'host': 'iai'},
    'J Bacteriol': {'host': 'jb'},
    'J Clin Microbiol': {'host': 'jcm'},
    'J Virol': {'host': 'jvi'},
    'MBio': {'host': 'mbio'},
    'mSystems': {'host': 'msystems'},
    'mSphere': {'host': 'msphere'},
    'Microbiol Mol Biol Rev': {'host': 'mmbr'},
    'Mol Cell Biol': {'host': 'mcb'},
}

# VIP URL template for ASM journals
asm_vip_template = 'http://{host}.asm.org/content/{volume}/{issue}/{first_page}.full.pdf'