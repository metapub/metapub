"""
IOP Publishing (Institute of Physics Publishing) journal list.

IOP Publishing (formerly Institute of Physics Publishing) is a British publisher
focused on physics and related fields. They publish journals through both
iopscience.iop.org and validate.perfdrive.com domains.

URL format: https://iopscience.iop.org/article/{doi}/pdf
Alternative formats: https://validate.perfdrive.com/article/{doi}/pdf

DOI patterns: various (10.1088/* is most common for IOP)
"""

# Combined IOP journals from both validate.perfdrive.com and iopscience.iop.org clusters
iop_journals = (
    # From validate.perfdrive.com cluster (43 journals)
    'Phys Med Biol',                                    # Physics in Medicine & Biology
    'Biomed Phys Eng Express',                          # Biomedical Physics & Engineering Express
    'J Electrochem Soc',                                # Journal of The Electrochemical Society
    'J Micromech Microeng',                             # Journal of Micromechanics and Microengineering
    'Europhys Lett',                                    # Europhysics Letters
    'Supercond Sci Technol',                            # Superconductor Science and Technology
    'Astrophys J',                                      # The Astrophysical Journal
    'Publ Astron Soc Pac',                              # Publications of the Astronomical Society of the Pacific
    'Fluid Dyn Res',                                    # Fluid Dynamics Research
    'Biofabrication',                                   # Biofabrication
    'Methods Appl Fluoresc',                            # Methods and Applications in Fluorescence
    'J Phys A Math Theor',                              # Journal of Physics A: Mathematical and Theoretical
    'Biomed Mater',                                     # Biomedical Materials
    'Planet Sci J',                                     # The Planetary Science Journal
    'J Phys Commun',                                    # Journal of Physics Communications
    'Nanotechnology',                                   # Nanotechnology
    'J Phys A Math Gen',                                # Journal of Physics A: Mathematical and General
    'Inverse Probl',                                    # Inverse Problems
    'ECS J Solid State Sci Technol',                   # ECS Journal of Solid State Science and Technology
    'Metrologia',                                       # Metrologia
    'IOP Conf Ser Mater Sci Eng',                      # IOP Conference Series: Materials Science and Engineering
    'Prog Biomed Eng (Bristol)',                       # Progress in Biomedical Engineering
    'Environ Res Commun',                               # Environmental Research Communications
    'J Phys Condens Matter',                            # Journal of Physics: Condensed Matter
    'J Phys G Nucl Part Phys',                         # Journal of Physics G: Nuclear and Particle Physics
    'J Phys D Appl Phys',                              # Journal of Physics D: Applied Physics
    'Meas Sci Technol',                                # Measurement Science and Technology
    'Bioinspir Biomim',                                 # Bioinspiration & Biomimetics
    '2d Mater',                                         # 2D Materials
    'Mater Res Express',                                # Materials Research Express
    'Quantum Sci Technol',                             # Quantum Science and Technology
    'Class Quantum Gravity',                            # Classical and Quantum Gravity
    'J Opt',                                            # Journal of Optics
    'Comput Sci Discov',                                # Computational Science & Discovery
    'Nonlinearity',                                     # Nonlinearity
    'Quantum Elec (Woodbury)',                          # Quantum Electronics
    'JPhys Photonics',                                  # Journal of Physics: Photonics
    'J Opt B Quantum Semiclassical Opt',               # Journal of Optics B: Quantum and Semiclassical Optics
    'J Convex Anal',                                    # Journal of Convex Analysis
    'Jpn J Appl Phys (2008)',                          # Japanese Journal of Applied Physics
    'Surf Topogr',                                      # Surface Topography: Metrology and Properties
    'Phys Scr',                                         # Physica Scripta
    'IOP Conf Ser Earth Environ Sci',                  # IOP Conference Series: Earth and Environmental Science
    
    # From iopscience.iop.org cluster (32 journals)
    'Astrophys J Lett',                                 # The Astrophysical Journal Letters
    'Converg Sci Phys Oncol',                          # Convergent Science Physical Oncology
    'Environ Res Lett',                                 # Environmental Research Letters
    'Rep Prog Phys',                                    # Reports on Progress in Physics
    'Clin Phys Physiol Meas',                          # Clinical Physics and Physiological Measurement
    'Smart Mater Struct',                               # Smart Materials and Structures
    'Laser Phys',                                       # Laser Physics
    'Physiol Meas',                                     # Physiological Measurement
    'J Sci Instrum',                                    # Journal of Scientific Instruments
    'Plasma Sources Sci Technol',                       # Plasma Sources Science and Technology
    'J Radiol Prot',                                    # Journal of Radiological Protection
    'Astron J',                                         # The Astronomical Journal
    'J Breath Res',                                     # Journal of Breath Research
    'J Phys Conf Ser',                                  # Journal of Physics: Conference Series
    'ECS Trans',                                        # ECS Transactions
    'New J Phys',                                       # New Journal of Physics
    'J Stat Mech',                                      # Journal of Statistical Mechanics: Theory and Experiment
    'Plasma Phys Control Fusion',                       # Plasma Physics and Controlled Fusion
    'Phys Biol',                                        # Physical Biology
    'J Instrum',                                        # Journal of Instrumentation
    'Laser Phys Lett',                                  # Laser Physics Letters
    'Chin Phys B',                                      # Chinese Physics B
    'Res Notes AAS',                                    # Research Notes of the AAS
    'J Neural Eng',                                     # Journal of Neural Engineering
    'Phys Educ',                                        # Physics Education
    'Apex',                                             # Apex (Journal title)
    'Nano Futures',                                     # Nano Futures
    'J Phys E',                                         # Journal of Physics E: Scientific Instruments
    'Semicond Sci Technol',                             # Semiconductor Science and Technology
    'Electrochem Soc Interface',                        # The Electrochemical Society Interface
    'Res Astron Astrophys',                            # Research in Astronomy and Astrophysics
    'Commun Theor Phys',                               # Communications in Theoretical Physics
)

# IOP uses multiple URL formats
iop_format = 'https://iopscience.iop.org/article/{doi}/pdf'
iop_alt_format = 'https://validate.perfdrive.com/article/{doi}/pdf'