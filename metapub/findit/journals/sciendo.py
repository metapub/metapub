"""Sciendo (De Gruyter) journal configuration for FindIt.

Sciendo is De Gruyter's open access publishing platform, launched in 2018.
It hosts a diverse collection of academic journals across multiple disciplines,
primarily from Eastern European and international publishers.

URL pattern: https://sciendo.com/article/{doi}
DOI patterns: Various (10.2478/*, 10.1515/*, etc.) due to publisher diversity
"""

# All Sciendo journals from cluster analysis
sciendo_journals = (
    'Pril (Makedon Akad Nauk Umet Odd Med Nauki)',
    'J Soc Struct',
    'Gravit Space Res',
    'J Nematol',
    'Endocr Regul',
    'Rom J Intern Med',
    'Dev Period Med',
    'Balkan J Med Genet',
    'Scand J Child Adolesc Psychiatr Psychol',
    'Interdiscip Toxicol',
    'J Electr Bioimpedance',
    'Zdr Varst',
    'Radiol Oncol',
    'Asian Biomed (Res Rev News)',
    'Beitr Tab Int',
    'Biomed Hum Kinet',
    'J Mother Child',
    'Arh Hig Rada',
    'Acta Pharm',
    'Immunohematology',
    'Pol J Microbiol',
    'Helminthologia',
    'J Crit Care Med (Targu Mures)',
    'J Vet Res',
    'Forum Clin Oncol',
    'Rev Rom Med Lab',
    'Acta Med Marisiensis',
    'Prilozi',
    'J Data Inf Sci',
)

# URL format template for Sciendo articles
sciendo_format = "https://sciendo.com/article/{doi}"