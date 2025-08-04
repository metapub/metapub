# World Scientific Publishing
# 
# worldscientific.com
#
# World Scientific Publishing is a major academic publisher for scientific,
# technical, and medical content. It publishes journals, books, and conference
# proceedings in various fields including physics, mathematics, computer science,
# engineering, chemistry, and life sciences.
#
# URL Patterns:
#   - Article view: https://www.worldscientific.com/doi/[DOI]
#   - PDF download: https://www.worldscientific.com/doi/pdf/[DOI]
#
# DOI Pattern:
#   - 10.1142/[ID] (World Scientific DOI pattern)
#
# Notes:
#   - Many articles require subscription or institutional access
#   - Some articles are freely accessible (open access)
#   - Articles are indexed in PubMed with PMIDs for bio-computing and medical related content
#   - DOI resolution typically redirects to article pages

# URL format template - will be used in the dance function
worldscientific_format = 'https://www.worldscientific.com/doi/pdf/{doi}'

# Complete list of World Scientific journals (60 total)
# NOTE: Using PubMed abbreviated journal names to match PMA data
worldscientific_journals = (
    'Adv Adapt Data Anal',
    'Am J Chin Med',
    'Am J Chin Med (Gard City N Y)',
    'Asian Dev Rev',
    'Biomed Eng (Singapore)',
    'Biophys Rev Lett',
    'Clim Chang Econ (Singap)',
    'Comp Med East West',
    'Fractals',
    'Gene Ther Regul',
    'Hand Surg',
    'Hong Kong Physiother J',
    'Int J Algebra Comput',
    'Int J Appl Mech',
    'Int J Artif Intell Tools',
    'Int J Bifurcat Chaos',
    'Int J Comput Geom Appl',
    'Int J Comput Intell Appl',
    'Int J Comput Mater Sci Eng',
    'Int J Comput Methods',
    'Int J Coop Inf Syst',
    'Int J HR',
    'Int J Image Graph',
    'Int J Inf Technol Decis Mak',
    'Int J Mod Phys A',
    'Int J Mod Phys B',
    'Int J Mod Phys C',
    'Int J Mod Phys Conf Ser',
    'Int J Nanosci',
    'Int J Neural Syst',
    'Int J Semant Comput',
    'Int J Wavelets Multiresolut Inf Process',
    'Intern J Pattern Recognit Artif Intell',
    'J Adv Dielectr',
    'J Algebra Appl',
    'J Bioinform Comput Biol',
    'J Biol Syst',
    'J Dev Entrep',
    'J Hand Surg Asian Pac Vol',
    'J Innov Opt Health Sci',
    'J Knot Theory Ramif',
    'J Mech Med Biol',
    'J Med Robot Res',
    'J Micromech Mol Phys',
    'J Mol Eng Mater',
    'J Musculoskelet Res',
    'J Porphyr Phthalocyanines',
    'J Theor Comput Chem',
    'Math Models Methods Appl Sci',
    'Mod Phys Lett A',
    'Mod Phys Lett B',
    'Mol Front J',
    'Nano',
    'Nano Life',
    'Pac Symp Biocomput',
    'Parallel Process Lett',
    'Q J Finance',
    'Quantum Bioinform IV (2010)',
    'Quantum Bioinform V (2011)',
    'Technology',
)