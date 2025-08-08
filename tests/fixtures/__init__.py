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
}