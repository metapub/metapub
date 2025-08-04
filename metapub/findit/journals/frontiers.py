"""Frontiers Media S.A. journal configuration for FindIt.

Frontiers is a major open-access academic publisher founded in 2007,
specializing in digital publishing across multiple disciplines.
Known for their innovative article-level metrics and transparent peer review.

URL pattern: https://www.frontiersin.org/articles/{doi}/full
DOI patterns: 10.3389/* (primary pattern for Frontiers)
"""

# All Frontiers journals from cluster analysis
frontiers_journals = (
    'Front Vet Sci',
    'Front Cardiovasc Med', 
    'Front Chem',
    'Front Cell Dev Biol',
    'Front Bioeng Biotechnol',
    'Front Ecol Evol',
    'Front Evol Neurosci',
    'Frontiers (Boulder)',
    'Front Mol Neurosci',
    'Front Neural Circuits',
    'Front Cell Neurosci',
    'Front Syst Neurosci',
    'Front Neuroanat',
    'Front Comput Neurosci',
    'Front Hum Neurosci',
    'Front Neurorobot',
    'Front Neuroinform',
    'Front Mar Sci',
    'Front Phys',
    'Front Nutr',
    'Front Surg',
    'Front Med (Lausanne)',
    'Front Aging Neurosci',
    'Front Pediatr',
    'Front Public Health',
    'Front Neurol',
    'Front Pharmacol',
    'Front Synaptic Neurosci',
    'Front Physiol',
    'Front Microbiol',
    'Front Psychol',
    'Front Psychiatry',
    'Front Cell Infect Microbiol',
    'Front Sports Act Living',
    'Front Big Data',
    'Front Artif Intell',
    'Front Mol Biosci',
    'Front Earth Sci (Lausanne)',
    'Front Robot AI',
    'Front Sustain Food Syst',
    'Front Mech Eng',
    'Front Built Environ',
    'Front Appl Math Stat',
    'Front Digit Health',
    'Front Med Technol',
    'Front Mater',
    'Front Environ Sci',
    'Front Commun (Lausanne)',
    'Front Res Metr Anal',
    'Oncol Rev',
    'Front Endocrinol (Lausanne)',
    'Front Genet',
    'Front Immunol',
    'Front Plant Sci',
    'Front Oncol',
    'Front Neuroenergetics',
    'Front Neurosci',
    'Front Energy Res',
    'Front Educ (Lausanne)',
    'Front ICT',
)

# URL format template for Frontiers articles
frontiers_format = "https://www.frontiersin.org/articles/{doi}/full"