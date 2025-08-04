"""
Inderscience Publishers journal list.

Inderscience Publishers is an independent academic publisher of journals
in engineering, technology, science, and management. They publish over 
400 peer-reviewed journals, with many titles starting with "International
Journal of..."

URL format: https://www.inderscienceonline.com/doi/pdf/{doi}
Alternative: https://www.inderscienceonline.com/doi/{doi}

DOI patterns: Various (typically 10.1504/*)
"""

# Inderscience journals from inderscienceonline.com cluster (40 journals)
inderscience_journals = (
    'Int J Biomed Eng Technol',                         # International Journal of Biomedical Engineering and Technology
    'Int J Public Pol',                                 # International Journal of Public Policy
    'Int J Funct Inform Personal Med',                  # International Journal of Functional Informatics and Personalised Medicine
    'Int J Biomed Nanosci Nanotechnol',                 # International Journal of Biomedical Nanoscience and Nanotechnology
    'Int J Bioinform Res Appl',                         # International Journal of Bioinformatics Research and Applications
    'Int J Electron Healthc',                           # International Journal of Electronic Healthcare
    'Int J Data Min Bioinform',                         # International Journal of Data Mining and Bioinformatics
    'Int J Min Miner Eng',                              # International Journal of Mining and Mineral Engineering
    'Botulinum J',                                      # The Botulinum Journal
    'Int J Environ Pollut',                             # International Journal of Environment and Pollution
    'Int J Quant Res Educ',                             # International Journal of Quantitative Research in Education
    'Int J Biotechnol',                                 # International Journal of Biotechnology
    'Int J Metadata Semant Ontol',                      # International Journal of Metadata, Semantics and Ontologies
    'Int J Behav Healthc Res',                          # International Journal of Behavioural and Healthcare Research
    'Int J Risk Assess Manag',                          # International Journal of Risk Assessment and Management
    'Int J Veh Saf',                                    # International Journal of Vehicle Safety
    'Int J Immunol Stud',                               # International Journal of Immunological Studies
    'Int J Comput Biol Drug Des',                       # International Journal of Computational Biology and Drug Design
    'Int J Biom',                                       # International Journal of Biometrics
    'Int J Migr Bord Stud',                             # International Journal of Migration and Border Studies
    'Int J Auton Adapt Commun Syst',                    # International Journal of Autonomous and Adaptive Communications Systems
    'Int J Comput Vis Robot',                           # International Journal of Computer Vision and Robotics
    'Int J Exp Comput Biomech',                         # International Journal for Experimental and Computational Biomechanics
    'Int J Bus Inf Syst',                               # International Journal of Business Information Systems
    'Int J Chin Cult Manag',                            # International Journal of Chinese Culture and Management
    'Int J Nanotechnol',                                # International Journal of Nanotechnology
    'Int J Heavy Veh Syst',                             # International Journal of Heavy Vehicle Systems
    'Int J Inf Syst Change Manag',                      # International Journal of Information Systems and Change Management
    'Int J Environ Waste Manag',                        # International Journal of Environment and Waste Management
    'Int J Comput Healthc',                             # International Journal of Computers in Healthcare
    'Int J Knowl Eng Soft Data Paradig',                # International Journal of Knowledge Engineering and Soft Data Paradigms
    'Int J Med Eng Inform',                             # International Journal of Medical Engineering and Informatics
    'Int J Nanomanuf',                                  # International Journal of Nanomanufacturing
    'Int J Prod Lifecycle Manag',                       # International Journal of Product Lifecycle Management
    'Int J Model Identif Control',                      # International Journal of Modelling, Identification and Control
    'Int J Entrep Innov Manag',                         # International Journal of Entrepreneurship and Innovation Management
    'Int J Contin Eng Educ Life Long Learn',            # International Journal of Continuing Engineering Education and Life-Long Learning
    'Int J Learn Chang',                                # International Journal of Learning and Change
    'Int J Soc Syst Sci',                               # International Journal of Social System Science
    'Int J Low Radiat',                                 # International Journal of Low Radiation
)

# Inderscience URL format
inderscience_format = 'https://www.inderscienceonline.com/doi/pdf/{doi}'