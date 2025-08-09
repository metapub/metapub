# IOS Press
# 
# content.iospress.com
#
# IOS Press is an international publisher of scientific and technical books and journals
# based in Amsterdam, Netherlands. It specializes in computer science, artificial intelligence,
# biomedical sciences, health technologies, and other technical disciplines.
#
# URL Patterns:
#   - Article view: https://content.iospress.com/articles/[journal]/[DOI]
#   - PDF download: https://content.iospress.com/download/[journal]/[DOI]
#
# DOI Pattern:
#   - 10.3233/[JOURNAL]-[ID] (IOS Press DOI pattern)
#
# Notes:
#   - Many articles require subscription or institutional access
#   - Some articles are freely accessible (open access)
#   - Articles are indexed in PubMed with PMIDs across medical and technical fields
#   - Journal abbreviations are used in URLs

# URL format template - evidence-based pattern for the_doi_slide generic function
iospress_format = 'https://content.iospress.com/doi/pdf/{doi}?download=true'

# Complete list of IOS Press journals (54 total)
# NOTE: Using PubMed abbreviated journal names to match PMA data
iospress_journals = (
    'Adv Neuroimmune Biol',
    'Appl Ontol',
    'Biomed Mater Eng',
    'Biomed Spectrosc Imaging',
    'Biorheology',
    'Biorheology Suppl',
    'Bladder Cancer',
    'Brain Plast',
    'Breast Dis',
    'Cancer Biomark',
    'Clin Hemorheol',
    'Clin Hemorheol Microcirc',
    'Fundam Inform',
    'Hum Antibodies',
    'In Silico Biol',
    'Inf Knowl Syst Manage',
    'Inf Serv Use',
    'Integr Comput Aided Eng',
    'Int J Dev Sci',
    'Int J Hybrid Intell Syst',
    'Int J Risk Saf Med',
    'Isokinet Exerc Sci',
    'J Alzheimers Dis',
    'J Alzheimers Dis Rep',
    'J Ambient Intell Smart Environ',
    'J Back Musculoskelet Rehabil',
    'J Berry Res',
    'J Comput Secur',
    'J Econ Soc Meas',
    'J Huntingtons Dis',
    'J Neonatal Perinatal Med',
    'J Neuromuscul Dis',
    'J Parkinsons Dis',
    'J Pediatr Neuroradiol',
    'J Pediatr Rehabil Med',
    'J Vestib Res',
    'J Vocat Rehabil',
    'J Xray Sci Technol',
    'Kidney Cancer',
    'Med J Nutrition Metab',
    'Model Assist Stat Appl',
    'NeuroRehabilitation',
    'Nutr Aging (Amst)',
    'Nutr Healthy Aging',
    'Occup Ergon',
    'Physiother Pract Res',
    'Restor Neurol Neurosci',
    'Semant Web',
    'Stat J IAOS',
    'Strength Fract Complex',
    'Technol Disabil',
    'Technol Health Care',
    'Transl Sci Rare Dis',
    'Work',
)