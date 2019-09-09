from __future__ import absolute_import, print_function, unicode_literals

import sys

from metapub import FindIt, PubMedFetcher

from metapub.findit.dances import the_doi_2step

from metapub.findit.journals.jstage import jstage_journals

fetch = PubMedFetcher()

outfile = open('jstage.csv', 'w')

# template for CSV output
CSV_OUTPUT_TEMPLATE = '{source.pma.journal},{source.url}\n'

# For each pubmed ID in pregenerated list, create a FindIt source object.
# 
# For each source object, write results to the CSV with heuristics:
#
#   If source.reason.startswith('NOFORMAT'), assign url=source.backup_url
#

def write_findit_result_to_csv(source):
    outfile.write(CSV_OUTPUT_TEMPLATE.format(source=source))
    outfile.flush()


def get_sample_pmids_for_journal(jrnl, years=None, max_pmids=3):
    samples = []
    if years is None:
        pmids = fetch.pmids_for_query(journal=jrnl)
        idx = 0
        while idx < len(pmids) and idx < max_pmids:
            samples.append(pmids[idx])
            idx += 1
    else:
        for year in years:
            pmids = fetch.pmids_for_query(journal=jrnl, year=year)
            if len(pmids) < 1:
                continue
            samples.append(pmids[0])
    return samples


def main():
    jrnls = jstage_journals

    for jrnl in jrnls:
        pmids = get_sample_pmids_for_journal(jrnl)
        for pmid in pmids:
            source = FindIt(pmid)
            print('[{source.pma.journal}]\t{source.pmid}: {source.url} ({source.reason})'.format(source=source))
            write_findit_result_to_csv(source)
             

if __name__ == '__main__':
    main()
