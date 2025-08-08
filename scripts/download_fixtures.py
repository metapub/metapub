#!/usr/bin/env python3
"""
Download XML fixtures for Taylor & Francis and PNAS PMIDs.

This script downloads real PubMed XML data for verified PMIDs
and saves them as fixtures for testing without network dependencies.
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from metapub import PubMedFetcher

# Taylor & Francis verified PMIDs
TAYLOR_FRANCIS_PMIDS = [
    '35067114',  # AIDS Care - 10.1080/09540121.2022.2029813
    '38962805',  # AIDS Care - 10.1080/09540121.2024.2374185
    '37065682',  # Drugs (Abingdon Engl) - 10.1080/09687637.2022.2055446
    '35095222',  # Drugs (Abingdon Engl) - 10.1080/09687637.2020.1856786
    '37008990',  # J Appl Econ - 10.1080/15140326.2022.2041158
    '32306807',  # Xenobiotica - 10.1080/00498254.2020.1755909
    '38738473',  # Xenobiotica - 10.1080/00498254.2024.2351044
]

# PNAS verified PMIDs  
PNAS_PMIDS = [
    '38011560',  # Proc Natl Acad Sci U S A - 10.1073/pnas.2305772120
    '38147649',  # Proc Natl Acad Sci U S A - 10.1073/pnas.2308706120
    '37903272',  # Proc Natl Acad Sci U S A - 10.1073/pnas.2308214120
]

def download_xml_fixture(pmid, output_dir):
    """Download XML for a PMID and save as fixture."""
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Check if fixture already exists
    xml_file = os.path.join(output_dir, f'{pmid}.xml')
    if os.path.exists(xml_file):
        print(f"✓ {pmid}.xml already exists")
        return True
    
    try:
        # Download XML using PubMedFetcher
        fetcher = PubMedFetcher()
        xml_data = fetcher.qs.efetch({'db': 'pubmed', 'id': pmid})
        
        # Save XML to fixture file  
        with open(xml_file, 'w', encoding='utf-8') as f:
            if isinstance(xml_data, bytes):
                f.write(xml_data.decode('utf-8'))
            else:
                f.write(xml_data)
        
        print(f"✓ Downloaded {pmid}.xml")
        return True
        
    except Exception as e:
        print(f"✗ Failed to download {pmid}: {e}")
        return False

def main():
    """Download all XML fixtures."""
    
    # Set up paths
    project_root = os.path.dirname(os.path.dirname(__file__))
    fixtures_dir = os.path.join(project_root, 'tests', 'fixtures', 'pmid_xml')
    
    print(f"Downloading XML fixtures to: {fixtures_dir}")
    print()
    
    # Download Taylor & Francis PMIDs
    print("Downloading Taylor & Francis PMIDs...")
    tf_success = 0
    for pmid in TAYLOR_FRANCIS_PMIDS:
        if download_xml_fixture(pmid, fixtures_dir):
            tf_success += 1
    
    print(f"Taylor & Francis: {tf_success}/{len(TAYLOR_FRANCIS_PMIDS)} downloaded")
    print()
    
    # Download PNAS PMIDs
    print("Downloading PNAS PMIDs...")
    pnas_success = 0
    for pmid in PNAS_PMIDS:
        if download_xml_fixture(pmid, fixtures_dir):
            pnas_success += 1
    
    print(f"PNAS: {pnas_success}/{len(PNAS_PMIDS)} downloaded")
    print()
    
    total_success = tf_success + pnas_success
    total_pmids = len(TAYLOR_FRANCIS_PMIDS) + len(PNAS_PMIDS)
    
    print(f"Total: {total_success}/{total_pmids} XML fixtures downloaded")
    
    if total_success == total_pmids:
        print("✅ All fixtures downloaded successfully!")
        return 0
    else:
        print("❌ Some fixtures failed to download")
        return 1

if __name__ == '__main__':
    sys.exit(main())