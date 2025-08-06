"""AIP Publishing journal data.

This module contains journal data for AIP Publishing (American Institute of Physics),
which publishes physics and related science journals through pubs.aip.org.
"""

aip_journals = (
    'Struct Dyn',
    'Appl Phys Rev',
    'Biomicrofluidics',
    'Phys Fluids (1994)',
    'Biointerphases',
    'J Vac Sci Technol B Microelectron Nanometer Struct Process Meas Phenom',
    'Proc Meet Acoust',
    'J Vac Sci Technol A',
    'Am J Phys',
    'J Laser Appl',
    'APL Mater',
    'J Phys Chem Ref Data',
    'Rev Sci Instrum',
    'J Math Phys',
    'Phys Plasmas',
    'J Rheol (N Y N Y)',
    'J Acoust Soc Am',
    'J Chem Phys',
    'J Vac Sci Technol B Nanotechnol Microelectron',
    'AIP Conf Proc',
    'Biophys Rev (Melville)',
    'Chaos',
    'J Appl Phys',
    'Appl Phys Lett',
    'APL Photonics',
    'APL Bioeng',
    'AIP Adv',
    'Med Phys Mex Symp Med Phys',
    'Acoust Res Lett Online',
    'Phys Teach',
)

aip_format = 'https://pubs.aip.org/aip/{journal}/{article}/{volume}/{article_id}/pdf'

# DOI-based template for AIP (for the_doi_slide)
aip_doi_format = 'https://pubs.aip.org/aip/article-pdf/doi/{doi}'