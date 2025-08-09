"""Test fixtures and utilities."""

from metapub.pubmedarticle import PubMedArticle
import os

def load_pmid_xml(pmid):
    """Load PubMedArticle from saved XML fixture.
    
    :param pmid: PMID string
    :return: PubMedArticle object
    """
    xml_file = os.path.join(os.path.dirname(__file__), 'pmid_xml', f'{pmid}.xml')
    if not os.path.exists(xml_file):
        raise FileNotFoundError(f'XML fixture not found for PMID {pmid}: {xml_file}')
    
    with open(xml_file, 'r', encoding='utf-8') as f:
        xml_data = f.read()
    
    return PubMedArticle(xml_data)


# Evidence PMIDs with metadata for reference
EVIDENCE_PMIDS = {
    # AAAS (Science journals)
    '35108047': {'doi': '10.1126/sciadv.abl6449', 'journal': 'Sci Adv'},
    '37552767': {'doi': '10.1126/scisignal.ade0385', 'journal': 'Sci Signal'}, 
    '37729413': {'doi': '10.1126/sciadv.adi3902', 'journal': 'Sci Adv'},
    '37883555': {'doi': '10.1126/science.adh8285', 'journal': 'Science'},
    '39236155': {'doi': '10.1126/science.adn0327', 'journal': 'Science'},
}

# WorldScientific PMIDs with metadata
WORLDSCIENTIFIC_EVIDENCE_PMIDS = {
    '32292800': {'doi': '10.1142/S2339547819500067', 'journal': 'Technology (Singap World Sci)'},
    '24808625': {'doi': '10.1142/S0218213013600063', 'journal': 'Int J Artif Intell Tools'},
    '37868702': {'doi': '10.1142/s1088424623500700', 'journal': 'J Porphyr Phthalocyanines'},
}

# Taylor & Francis PMIDs with metadata
TAYLOR_FRANCIS_EVIDENCE_PMIDS = {
    '35067114': {'doi': '10.1080/09540121.2022.2029813', 'journal': 'AIDS Care'},
    '38962805': {'doi': '10.1080/09540121.2024.2374185', 'journal': 'AIDS Care'},
    '37065682': {'doi': '10.1080/09687637.2022.2055446', 'journal': 'Drugs (Abingdon Engl)'},
    '35095222': {'doi': '10.1080/09687637.2020.1856786', 'journal': 'Drugs (Abingdon Engl)'},
    '37008990': {'doi': '10.1080/15140326.2022.2041158', 'journal': 'J Appl Econ'},
    '32306807': {'doi': '10.1080/00498254.2020.1755909', 'journal': 'Xenobiotica'},
    '38738473': {'doi': '10.1080/00498254.2024.2351044', 'journal': 'Xenobiotica'},
}

# PNAS PMIDs with metadata
PNAS_EVIDENCE_PMIDS = {
    '38011560': {'doi': '10.1073/pnas.2305772120', 'journal': 'Proc Natl Acad Sci U S A'},
    '38147649': {'doi': '10.1073/pnas.2308706120', 'journal': 'Proc Natl Acad Sci U S A'},
    '37903272': {'doi': '10.1073/pnas.2308214120', 'journal': 'Proc Natl Acad Sci U S A'},
}

# APA PMIDs with metadata
APA_EVIDENCE_PMIDS = {
    '34843274': {'doi': '10.1037/amp0000904', 'journal': 'Am Psychol'},
    '32437181': {'doi': '10.1037/amp0000660', 'journal': 'Am Psychol'},
    '38546579': {'doi': '10.1037/com0000370', 'journal': 'J Comp Psychol'},
    '32496081': {'doi': '10.1037/com0000239', 'journal': 'J Comp Psychol'},
    '38573673': {'doi': '10.1037/prj0000611', 'journal': 'Psychiatr Rehabil J'},
    '33856845': {'doi': '10.1037/prj0000481', 'journal': 'Psychiatr Rehabil J'},
    '38271020': {'doi': '10.1037/rep0000539', 'journal': 'Rehabil Psychol'},
    '33119379': {'doi': '10.1037/rep0000367', 'journal': 'Rehabil Psychol'},
    '24349601': {'doi': '10.1037/a0030292', 'journal': 'J Neurosci Psychol Econ', 'pmc': 'PMC3858957'},
}

# AJPH PMIDs with metadata
AJPH_EVIDENCE_PMIDS = {
    '34709863': {'doi': '10.2105/AJPH.2021.306505', 'journal': 'Am J Public Health'},
    '35679569': {'doi': '10.2105/AJPH.2022.306873', 'journal': 'Am J Public Health'},
    '34529508': {'doi': '10.2105/AJPH.2021.306453', 'journal': 'Am J Public Health'},
}

# APS (American Physiological Society) PMIDs with metadata
APS_EVIDENCE_PMIDS = {
    '34995163': {'doi': '10.1152/ajpheart.00590.2021', 'journal': 'Am J Physiol Heart Circ Physiol'},
    '36367692': {'doi': '10.1152/ajpheart.00477.2022', 'journal': 'Am J Physiol Heart Circ Physiol'},
    '36717101': {'doi': '10.1152/ajpcell.00544.2022', 'journal': 'Am J Physiol Cell Physiol'},
}

# De Gruyter PMIDs with metadata (true De Gruyter with 10.1515 DOI prefix)
DEGRUYTER_EVIDENCE_PMIDS = {
    '38534005': {'doi': '10.1515/cclm-2024-0070', 'journal': 'Clin Chem Lab Med'},
    '36318760': {'doi': '10.1515/jpem-2022-0309', 'journal': 'J Pediatr Endocrinol Metab'},
    '38716869': {'doi': '10.1515/hmbci-2022-0093', 'journal': 'Horm Mol Biol Clin Investig'},
}

# RSC (Royal Society of Chemistry) PMIDs with metadata
RSC_EVIDENCE_PMIDS = {
    '32935693': {'doi': '10.1039/d0np00027b', 'journal': 'Nat Prod Rep', 'pmc': 'PMC7864896'},
    '38170905': {'doi': '10.1039/d3np00037k', 'journal': 'Nat Prod Rep', 'pmc': 'PMC11043010'},
    '31712796': {'doi': '10.1039/c9em00386j', 'journal': 'Environ Sci Process Impacts'},
    '34817495': {'doi': '10.1039/d1em00296a', 'journal': 'Environ Sci Process Impacts'},
    '35699396': {'doi': '10.1039/d1em00553g', 'journal': 'Environ Sci Process Impacts'},
    '37787043': {'doi': '10.1039/d3em00224a', 'journal': 'Environ Sci Process Impacts'},
    '37655634': {'doi': '10.1039/d3em00235g', 'journal': 'Environ Sci Process Impacts'},
    '35485580': {'doi': '10.1039/d2em00039c', 'journal': 'Environ Sci Process Impacts'},
}

# J-STAGE (Japan Science and Technology Information Aggregator, Electronic) PMIDs with metadata
JSTAGE_EVIDENCE_PMIDS = {
    '31588070': {'doi': '10.5761/atcs.ra.19-00158', 'journal': 'Ann Thorac Cardiovasc Surg', 'pmc': 'PMC7184035'},
    '34334504': {'doi': '10.5761/atcs.ra.21-00040', 'journal': 'Ann Thorac Cardiovasc Surg', 'pmc': 'PMC8915931'},
    '38028269': {'doi': '10.33160/yam.2023.11.001', 'journal': 'Yonago Acta Med', 'pmc': 'PMC10674056'},
}

# ASM (American Society for Microbiology) PMIDs with metadata
ASM_EVIDENCE_PMIDS = {
    '35856662': {'doi': '10.1128/aac.00216-22', 'journal': 'Antimicrob Agents Chemother', 'pmc': 'PMC9380527'},
    '39382274': {'doi': '10.1128/aac.00924-24', 'journal': 'Antimicrob Agents Chemother', 'pmc': 'PMC11539232'},
    '36598232': {'doi': '10.1128/jb.00337-22', 'journal': 'J Bacteriol'},
    '38591913': {'doi': '10.1128/jb.00024-24', 'journal': 'J Bacteriol', 'pmc': 'PMC11112993'},
    '38329942': {'doi': '10.1128/msystems.01299-23', 'journal': 'mSystems', 'pmc': 'PMC10949424'},
}

# Wiley PMIDs with metadata
WILEY_EVIDENCE_PMIDS = {
    '39077977': {'doi': '10.1002/acr2.11726', 'journal': 'ACR Open Rheumatol'},
    '35726897': {'doi': '10.1002/acr2.11476', 'journal': 'ACR Open Rheumatol'},
    '33474827': {'doi': '10.1111/1759-7714.13823', 'journal': 'Thorac Cancer'},
    '36247735': {'doi': '10.1111/jofi.13173', 'journal': 'J Finance'},
    '35573891': {'doi': '10.1155/2021/5792975', 'journal': 'Wirel Commun Mob Comput'},
}

# Thieme Medical Publishers PMIDs with metadata
THIEME_EVIDENCE_PMIDS = {
    '38048813': {'doi': '10.1055/a-2189-0166', 'journal': 'Psychother Psychosom Med Psychol'},
    '25364329': {'doi': '10.1055/s-0034-1387804', 'journal': 'Evid Based Spine Care J', 'pmc': 'PMC4212699'},
    '219391': {'doi': '10.1055/s-0028-1085314', 'journal': 'Neuropadiatrie'},
    '36644330': {'doi': '10.1055/s-0040-1721489', 'journal': 'ACI open', 'pmc': 'PMC9838214'},
    '32894878': {'doi': '10.1055/s-0040-1715580', 'journal': 'Methods Inf Med'},
}

# IOP Publishing (Institute of Physics) PMIDs with metadata
IOP_EVIDENCE_PMIDS = {
    '38914107': {'doi': '10.1088/1361-6560/ad5b48', 'journal': 'Phys Med Biol'},
    '38914053': {'doi': '10.1088/1361-6528/ad5afd', 'journal': 'Nanotechnology'},
    '38799617': {'doi': '10.3847/1538-4357/ad380b', 'journal': 'Astrophys J', 'pmc': 'PMC11120190'},
}

# ASME (American Society of Mechanical Engineers) PMIDs with metadata
ASME_EVIDENCE_PMIDS = {
    '38449742': {'doi': '10.1115/1.4063271', 'journal': 'J Appl Mech', 'pmc': 'PMC10913807'},
    '38913074': {'doi': '10.1115/1.4065813', 'journal': 'J Biomech Eng', 'pmc': 'PMC11500806'},
    '35833154': {'doi': '10.1115/1.4053197', 'journal': 'J Heat Transfer', 'pmc': 'PMC8823200'},
}

# OAText PMIDs with metadata (minimal set due to limited PubMed indexing)
OATEXT_EVIDENCE_PMIDS = {
    # Note: OAText articles may have limited PubMed representation
    # Using representative DOI patterns from test suite for structural validation
    '99999901': {'doi': '10.15761/JSIN.1000229', 'journal': 'J Syst Integr Neurosci'},
    '99999902': {'doi': '10.15761/CCRR.1000123', 'journal': 'Clin Case Rep Rev'},
    '99999903': {'doi': '10.15761/HMO.1000456', 'journal': 'HMO'},
}