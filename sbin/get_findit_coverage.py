from __future__ import absolute_import, print_function, unicode_literals

import sys

from metapub import FindIt, PubMedFetcher

from metapub.findit.dances import the_doi_2step

from config import PMID_OUTPUT_FILENAME, FINDIT_COVERAGE_CSV

fetch = PubMedFetcher()

outfile = open(FINDIT_COVERAGE_CSV, 'w')

# template for CSV output
CSV_OUTPUT_TEMPLATE = '{source.pma.journal},{source.pma.year},{source.pma.pmid},{url},{source.reason}\n'

# For each pubmed ID in pregenerated list, create a FindIt source object.
# 
# For each source object, write results to the CSV with heuristics:
#
#   If source.reason.startswith('NOFORMAT'), assign url=source.backup_url
#

def write_findit_result_to_csv(source):
    url = source.url
    if source.reason and source.reason.startswith(('NOFORMAT', 'TODO')):
        if source.doi:
            try:
                url = the_doi_2step(source.doi)
            except Exception as err:
                url = 'http://dx.doi.org/%s' % source.doi
        else:
            url = '(no doi)'
    outfile.write(CSV_OUTPUT_TEMPLATE.format(source=source, url=url))
    outfile.flush()

def main(start_pmid=0):
    pmids = open(PMID_OUTPUT_FILENAME).read()

    if start_pmid:
        idx = pmids.find(str(start_pmid))
    else:
        idx = 0

    for pmid in pmids[idx:].split('\n'):
        source = FindIt(pmid, verify=False)
        print('[{source.pma.journal}]\t{source.pmid}: {source.url} ({source.reason})'.format(source=source))
        write_findit_result_to_csv(source)

if __name__ == '__main__':
    try:
        start_pmid = int(sys.argv[1])
    except TypeError:
        print('Argument must be an integer! (Pubmed ID)')
        sys.exit()
    except IndexError:
        print('Supply pmid as argument to this script. (use 0 if starting over.)')
        sys.exit()

    main(start_pmid)


