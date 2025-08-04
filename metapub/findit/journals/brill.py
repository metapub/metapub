"""Brill Academic Publishers (brill.com) journals.

Brill is a Dutch international academic publisher founded in 1683, specializing in
the humanities, international law, social sciences, and biology.
They publish over 600 journals and around 2000 new books and reference works annually.

Based on investigation, Brill uses DOI prefix 10.1163 for their publications.
Articles are hosted on brill.com with DOI-based access patterns.

URL pattern investigation shows DOI resolution to brill.com article pages.
Some content may be behind institutional paywalls but many articles have
open access or trial access available.
"""

# DOI-based template for Brill Academic Publishers
# Based on investigation showing DOI prefix 10.1163 redirects to brill.com
brill_template = 'https://doi.org/{doi}'

# Brill Academic Publishers journals from categorized analysis
# These journals were identified from brill.com domain in categorized_unknown_journals.txt
# Focused on humanities, social sciences, and biology journals published by Brill
brill_journals = [
    'Behaviour',
    'Asian Med',
    'Early Sci Med',
    'Phronesis',
    'Toung Pao',
    'Bijdr Dierkd',
    'Contributions Zool',
    'Amphora',
    'Archives Histoire Doctrinale Litteraire Moyen Age',
    'Aries',
    'Art Islam',
    'Asian Biotechnol Dev Rev',
    'Asian J Int Law',
    'Biblica',
    'Biblical Interpretation',
    'Bijdragen',
    'Brill Research Perspectives Islam Law',
    'Bull Sch Orient Afr Stud',
    'China Information',
    'Chinese J Int Law',
    'Church Hist Relig Cult',
    'Contagion',
    'Critical Survey',
    'Dead Sea Discoveries',
    'Dutch Rev Lang Lit',
    'Early Modern Low Countries',
    'Ecohealth Sustainability',
    'European Constitutional Law Review',
    'European J Int Law',
    'Fascism',
    'Greek Roman Musical Stud',
    'Hague J Diplomacy',
    'History Religions',
    'Isr Law Rev',
    'J Arabic Lit',
    'J Econ Soc Hist Orient',
    'J Empirical Theol',
    'J Int Arbitration',
    'J Int Crim Justice',
    'J Law Religion',
    'J Persianate Stud',
    'J Reform Judaism',
    'J World Intellect Prop',
    'Jew Stud Q',
    'Leiden J Int Law',
    'Mnemosyne',
    'Nordic J Int Law',
    'Nuncius',
    'Research Ethics',
    'Rev Bib',
    'Vigiliae Christianae',
    'Yearb Int Humanitarian Law'
]