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