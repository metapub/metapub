import csv
import logging
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from metapub import PubMedFetcher, FindIt
from metapub.exceptions import MetaPubError
from eutils.exceptions import EutilsRequestError

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', handlers=[
    logging.FileHandler("journal_inventory.log"),
    logging.StreamHandler()
])

MEDLINE_JOURNAL_FILE = "/tmp/journals.csv"


fetch = PubMedFetcher()



# Predefined list of journal abbreviations
journal_abbrs = [
    "Cell", "Cancer Cell", "Cell Chem. Biol.", "Cell Host Microbe",
    "Cell Metab.", "Cell Rep.", "Cell Stem Cell", "Curr. Biol.",
    "Dev. Cell", "Immunity", "Mol. Cell", "Neuron", "Structure",
    "Trends Biochem. Sci.", "Trends Biotechnol.", "Trends Cancer",
    "Trends Cell Biol.", "Trends Cogn. Sci.", "Trends Ecol. Evol.",
    "Trends Endocrinol. Metab.", "Trends Genet.", "Trends Immunol.",
    "Trends Microbiol.", "Trends Mol. Med.", "Trends Neurosci.",
    "Trends Parasitol.", "Trends Pharmacol. Sci.", "Trends Plant Sci.",
    "Heliyon", "iScience", "Med", "One Earth", "Patterns", "Star Protoc."
]

def get_num_pmids(journal_abbr):
    query = f'{journal_abbr}[ta]'
    pmids = fetch.pmids_for_query(query)
    return pmids

def get_article_by_pmid_with_retry(pmid, retries=5, delay=1):
    for attempt in range(retries):
        try:
            return fetch.article_by_pmid(pmid)
        except (MetaPubError, EutilsRequestError) as e:
            if attempt < retries - 1:
                time.sleep(delay * (2 ** attempt))
            else:
                raise e

def get_sample_pmids(pmids):
    sample_pmids = {}
    current_year = datetime.now().year
    ten_years_ago = current_year - 10
    last_year = current_year - 1

    oldest_pmid = None
    oldest_year = current_year

    for pmid in pmids:
        article = get_article_by_pmid_with_retry(pmid)
        article_year = int(article.year)

        if article_year < oldest_year:
            oldest_year = article_year
            oldest_pmid = pmid

        if article_year == ten_years_ago:
            sample_pmids['ten_years_ago'] = pmid
        if article_year == last_year:
            sample_pmids['last_year'] = pmid

        if 'ten_years_ago' in sample_pmids and 'last_year' in sample_pmids and oldest_pmid:
            break

    sample_pmids['oldest'] = oldest_pmid

    return sample_pmids

def check_findit_support(pmid):
    src = FindIt(pmid)
    if src.reason.startswith("NOFORMAT"):
        return False
    return True

def process_journal(journal):
    pmids = get_num_pmids(journal)
    num_pmids = len(pmids)
    
    if num_pmids == 0:
        sample_pmids = {}
        findit_support = None
    else:
        sample_pmids = get_sample_pmids(pmids)
        if sample_pmids:
            pmid_to_check = sample_pmids.get('last_year') or sample_pmids.get('ten_years_ago') or sample_pmids.get('oldest')
            findit_support = check_findit_support(pmid_to_check) if pmid_to_check else None
        else:
            findit_support = None
    
    logging.info(f"Processed {journal}: num_pmids={num_pmids}, sample_pmids={sample_pmids}, findit_support={findit_support}")
    return {
        'jrnl_abbrev': journal,
        'num_pmids': num_pmids,
        'sample_pmids': ', '.join(sample_pmids.values()) if sample_pmids else '',
        'findit_support': findit_support
    }

def main():
    output_file = 'journal_support.csv'
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(process_journal, journal): journal for journal in journal_abbrs}
        results = []
        for future in as_completed(futures):
            results.append(future.result())
    
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['jrnl_abbrev', 'num_pmids', 'sample_pmids', 'findit_support']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

if __name__ == '__main__':
    main()

