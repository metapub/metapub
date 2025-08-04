"""
ASME (American Society of Mechanical Engineers) journal list.

ASME is a professional engineering society that publishes technical journals
covering mechanical engineering, biomechanical engineering, manufacturing,
energy, and related fields. Their journals are hosted on the ASME Digital
Collection platform.

URL format: https://asmedigitalcollection.asme.org/[journal]/article-pdf/{doi}
Alternative: https://asmedigitalcollection.asme.org/[journal]/article/{doi}

DOI patterns: Typically 10.1115/* for ASME journals
"""

# ASME journals from asmedigitalcollection.asme.org cluster (39 journals)
asme_journals = (
    'Appl Mech Rev',                                    # Applied Mechanics Reviews
    'J Appl Mech',                                      # Journal of Applied Mechanics
    'J Comput Nonlinear Dyn',                           # Journal of Computational and Nonlinear Dynamics
    'J Comput Inf Sci Eng',                             # Journal of Computing and Information Science in Engineering
    'J Eng Gas Turbine Power',                          # Journal of Engineering for Gas Turbines and Power
    'J Press Vessel Technol',                           # Journal of Pressure Vessel Technology
    'J Sol Energy Eng',                                 # Journal of Solar Energy Engineering
    'J Turbomach',                                      # Journal of Turbomachinery
    'J Med Device',                                     # Journal of Medical Devices
    'J Vib Acoust',                                     # Journal of Vibration and Acoustics
    'J Biomech Eng',                                    # Journal of Biomechanical Engineering
    'Proc ASME Dyn Syst Control Conf',                 # Proceedings of the ASME Dynamic Systems and Control Conference
    'Proc ASME Des Eng Tech Conf',                     # Proceedings of the ASME Design Engineering Technical Conferences
    'J Heat Transfer',                                  # Journal of Heat Transfer
    'J Tribol',                                         # Journal of Tribology
    'J Energy Resour Technol',                         # Journal of Energy Resources Technology
    'J Eng Sci Med Diagn Ther',                        # Journal of Engineering and Science in Medical Diagnostics and Therapy
    'Mater Perform Charact',                            # Journal of Materials Performance and Characterization
    'J Dyn Syst Meas Control',                         # Journal of Dynamic Systems, Measurement, and Control
    'J Mech Des N Y',                                   # Journal of Mechanical Design
    'J Manuf Sci Eng',                                 # Journal of Manufacturing Science and Engineering
    'J Micro Nanomanuf',                               # Journal of Micro- and Nano-Manufacturing
    'Smart Sustain Manuf Syst',                        # Journal of Smart and Sustainable Manufacturing Systems
    'J Verif Valid Uncertain Quantif',                 # Journal of Verification, Validation and Uncertainty Quantification
    'J Fluids Eng',                                    # Journal of Fluids Engineering
    'J Test Eval',                                     # Journal of Testing and Evaluation
    'J Mech Robot',                                     # Journal of Mechanisms and Robotics
    'J ASTM Int',                                       # Journal of ASTM International
    'J Electron Packag',                               # Journal of Electronic Packaging
    'J Fuel Cell Sci Technol',                         # Journal of Fuel Cell Science and Technology
    'Proc ASME Micro Nanoscale Heat Mass Transf Int Conf (2012)',  # Proceedings of ASME Micro/Nanoscale Heat & Mass Transfer International Conference
    'Int Mech Eng Congress Expo',                      # ASME International Mechanical Engineering Congress and Exposition
    'J Nanotechnol Eng Med',                           # Journal of Nanotechnology in Engineering and Medicine
    'J Therm Sci Eng Appl',                            # Journal of Thermal Science and Engineering Applications
    'Proc ASME Conf Smart Mater Adapt Struct Intell Syst',  # Proceedings of the ASME Conference on Smart Materials, Adaptive Structures and Intelligent Systems
    'Adv Civ Eng Mater',                               # ASCE-ASME Journal of Advanced Civil Engineering Materials
    'Proc Int Conf Nanochannels Microchannels Minichannels',  # Proceedings of International Conference on Nanochannels, Microchannels, and Minichannels
    'Proc ASME Int Conf Manuf Sci Eng',                # Proceedings of the ASME International Conference on Manufacturing Science and Engineering
    'J Eng Mater Technol',                             # Journal of Engineering Materials and Technology
)

# ASME URL format - will need to determine journal codes
asme_format = 'https://asmedigitalcollection.asme.org/{journal_code}/article-pdf/{doi}'