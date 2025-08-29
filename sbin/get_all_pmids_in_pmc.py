
from metapub import PubMedFetcher
from datetime import date

#tested py2k/py3k compatible --nm 10/28/2015

OUTPUT_FILE = 'pmids_in_pmc'

fout = open(OUTPUT_FILE, 'w')

fetch = PubMedFetcher()

def write_batch(pmid_list):
    'writes list of pmids to file; flushes write to disk'
    for pmid in pmid_list:
        fout.write('%s\n' % pmid)
    fout.flush()

def fetch_and_write_batch(year):
    startnum = 0
    curnum = 1000
    batchmax = 1000

    batch = []
    current_return = []

    while curnum == batchmax:
        batch = fetch.pmids_for_query(pmc_only=True, year=year, debug=True,
                                      retstart=startnum, retmax=batchmax)
        write_batch(batch)
        curnum = len(batch)
        startnum = startnum + batchmax

    print("Ended batch acquisition for PMC year %i with %i entries" % (year, startnum+curnum))
    print("")


def main():
    thisyear = date.today().year

    for year in range(1800, thisyear + 1):
        fetch_and_write_batch(year)


if __name__=='__main__':
    main()

