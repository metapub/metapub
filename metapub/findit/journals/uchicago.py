# University of Chicago Press
# 
# journals.uchicago.edu
#
# The University of Chicago Press is one of the largest and oldest university presses
# in the United States. It publishes academic journals, books, and scholarly content
# across various disciplines including humanities, social sciences, education, 
# biological sciences, and physical sciences.
#
# URL Patterns:
#   - Article view: https://www.journals.uchicago.edu/doi/[DOI]
#   - PDF download: https://www.journals.uchicago.edu/doi/pdf/[DOI]
#
# DOI Pattern:
#   - 10.1086/[ID] (University of Chicago Press DOI pattern)
#
# Notes:
#   - Many articles require subscription or institutional access
#   - Some articles are freely accessible (open access)
#   - Articles are indexed in PubMed with PMIDs across multiple disciplines
#   - DOI resolution typically redirects to article pages

# URL format template - will be used in the dance function
uchicago_format = 'https://www.journals.uchicago.edu/doi/pdf/{doi}'

# Complete list of University of Chicago Press journals (59 total)
# NOTE: Using PubMed abbreviated journal names to match PMA data
uchicago_journals = (
    'AJS',
    'Am J Educ (Chic Ill)',
    'Am J Health Econ',
    'Am J Sociol',
    'Am Nat',
    'Biol Bull',
    'Bot Gaz',
    'Br J Philos Sci',
    'China J',
    'Class Philol',
    'Comp Educ Rev',
    'Crime Justice',
    'Crit Inq',
    'Curr Anthropol',
    'Econ Dev Cult Change',
    'Elem Sch J',
    'Engl Lit Renaiss',
    'Environ Hist Durh N C',
    'Ethics',
    'HAU',
    'Hist Relig',
    'Int J Plant Sci',
    'Isis',
    'J Anthropol Res',
    'J Assoc Consum Res',
    'J Assoc Environ Resour Econ',
    'J Clin Ethics',
    'J Geol',
    'J Hum Cap',
    'J Labor Econ',
    'J Law Econ',
    'J Legal Stud',
    'J Mod Hist',
    'J Near East Stud',
    'J Polit',
    'J Polit Econ',
    'J Relig',
    'J Soc Social Work Res',
    'Libr Q',
    'Mod Philol',
    'NBER Macroecon Annu',
    'Natl Tax J',
    'Osiris',
    'Pap Bibliogr Soc Am',
    'Physiol Biochem Zool',
    'Physiol Zool',
    'Q Rev Biol',
    'Renaiss Drama',
    'Rev Environ Econ Policy',
    'Signs (Chic)',
    'Signs Soc (Chic)',
    'Soc Hist Alcohol Drugs',
    'Soc Serv Rev',
    'Source Notes Hist Art',
    'Southwest J Anthropol',
    'Speculum',
    'Stud Decor Arts',
    'Supreme Court Rev',
    'Winterthur Portf',
)