# Longdom Publishing
# 
# longdom.org
#
# Longdom Publishing is an open access publisher that publishes journals
# across various fields including medical sciences, life sciences, and technology.
# Note: This publisher has been flagged by some as potentially predatory.
#
# URL Patterns:
#   - Article view: https://www.longdom.org/articles/[article-slug]
#   - PDF download: https://www.longdom.org/articles-pdfs/[article-slug].pdf
#
# DOI Pattern:
#   - Various DOI patterns (10.4172, 10.35248, etc.)
#
# Notes:
#   - Many articles are open access
#   - Articles are indexed in PubMed with PMIDs
#   - Publisher has been subject to criticism regarding editorial practices
#   - Included here for completeness as articles appear in PubMed

# URL format template - will be used in the dance function
longdom_format = 'https://www.longdom.org/articles-pdfs/{article_slug}.pdf'

# Complete list of Longdom journals (47 total)
# NOTE: Using PubMed abbreviated journal names to match PMA data
longdom_journals = (
    'Adv Tech Biol Med',
    'Anat Physiol',
    'Angiol Open Access',
    'Autism Open Access',
    'Biochem Pharmacol (Los Angel)',
    'Cell Dev Biol',
    'Endocrinol Metab Syndr',
    'Gynecol Obstet (Sunnyvale)',
    'Immunotherapy (Los Angel)',
    'Intern Med Open Access',
    'J Alcohol Drug Depend',
    'J Anesth Clin Res',
    'J Antivir Antiretrovir',
    'J Bone Marrow Res',
    'J Bone Res',
    'J Chromatogr Sep Tech',
    'J Clin Cell Immunol',
    'J Clin Exp Cardiolog',
    'J Clin Exp Dermatol Res',
    'J Clin Exp Ophthalmol',
    'J Clin Toxicol',
    'J Depress Anxiety',
    'J Dev Drugs',
    'J Down Syndr Chromosom Abnorm',
    'J Drug Metab Toxicol',
    'J Genet Syndr Gene Ther',
    'J Glycobiol',
    'J Glycomics Lipidomics',
    'J Leuk (Los Angel)',
    'J Mol Imaging Dyn',
    'J Nanomedine Biotherapeutic Discov',
    'J Nutr Food Sci',
    'J Osteoporos Phys Act',
    'J Perioper Crit Intensiv Care Nurs',
    'J Probiotics Health',
    'J Psychol Psychother',
    'J Womens Health Care',
    'J Yoga Phys Ther',
    'Mass Spectrom Purif Tech',
    'Matern Pediatr Nutr',
    'Mycobact Dis',
    'Pediatr Ther',
    'Reprod Syst Sex Disord',
    'Rheumatology (Sunnyvale)',
    'Transcr Open Access',
    'Transl Med (Sunnyvale)',
    'Virol Mycol',
)