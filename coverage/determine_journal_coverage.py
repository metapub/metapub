import csv
from metapub import PubMedFetcher
from metapub import FindIt
from metapub.findit import SUPPORTED_JOURNALS

MEDLINE_JOURNAL_LIST = "/tmp/journals.csv"

OUTPUT_CSV = "/tmp/findit_journal_coverage.csv"

def fetch_pmids_for_years(journal_abbrev, years):
    fetcher = PubMedFetcher()
    pmids = []
    
    for year in years:
        try:
            pmids_for_year = fetcher.pmids_for_query(f'{journal_abbrev}[TA] AND {year}[DP]', retmax=1)
            if pmids_for_year:
                pmids.append(pmids_for_year[0])
            else:
                pmids.append(None)
        except Exception as e:
            pmids.append(None)
            print(f"Error fetching PMIDs for {journal_abbrev} in {year}: {e}")

    return pmids

def create_output_csv(input_file_path, output_file_path):
    years = [2024, 2018, 2008]
    
    with open(input_file_path, newline='') as infile, open(output_file_path, 'w', newline='') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = ['journal_abbrev', 'PMIDs', 'FindIt_coverage']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in reader:
            journal_abbrev = row['MedAbbr']
            if journal_abbrev in SUPPORTED_JOURNALS:
                 writer.writerow({
                    'journal_abbrev': journal_abbrev,
                    'PMIDs': None,
                    'FindIt_coverage': True,
                  })

            else:
                pmids = fetch_pmids_for_years(journal_abbrev, years)

                writer.writerow({
                    'journal_abbrev': journal_abbrev,
                    'PMIDs': ','.join([str(pmid) if pmid else 'None' for pmid in pmids]),
                    'FindIt_coverage': False
                })

create_output_csv(MEDLINE_JOURNAL_LIST, OUTPUT_CSV)


