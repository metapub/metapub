import requests
from metapub import FindIt
from metapub import PubMedFetcher
from datetime import datetime
import csv


def fetch_pmids(year_from, year_to, count):
    fetcher = PubMedFetcher()
    pmids = []

    for year in range(year_from, year_to + 1):
        query = f'{year}[dp]'
        result = fetcher.pmids_for_query(query, retmax=count)
        pmids.extend(result)
        if len(pmids) >= count:
            break
    return pmids


# Example usage:
pmids = fetch_pmids(2022, 2024, count=150)


with open('embargo_check_results.csv', 'w', newline='') as csvfile:
    fieldnames = ['PMID', 'is_embargoed', 'Findit_reason']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for pmid in pmids:
        print(f"{pmid}")

        src = FindIt(pmid, use_nih=True)
        print("Journal:", src.pma.journal)
        print("Title:", src.pma.title)
        print("Keywords:", src.pma.keywords)
        print()
        print(f"Embargo date:", src.pma.history.get('pmc-release', None))

        is_embargoed = False

        if src.url:
            findit_reason = src.url
            is_embargoed = False
        else:
            findit_reason = src.reason
            if findit_reason.startswith("PAYWALL") and "embargo" in src.reason:
                is_embargoed = True

        print(f"FindIt result for PMID {pmid}: {findit_reason}")

        # Write to CSV
        writer.writerow({'PMID': pmid, 'is_embargoed': is_embargoed, 'Findit_reason': findit_reason})
        print("---------")

