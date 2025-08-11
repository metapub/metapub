from metapub import FindIt, PubMedFetcher

from metapub.findit.dances import the_doi_2step

from config import JOURNAL_ISOABBR_LIST_FILENAME, PMID_OUTPUT_FILENAME

fetch = PubMedFetcher()

outfile = open(PMID_OUTPUT_FILENAME, 'w')

def write_pmid_to_list(pmid):
    outfile.write(pmid + '\n')
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
    jrnls = sorted(open(JOURNAL_ISOABBR_LIST_FILENAME).read().split('\n'))

    for jrnl in jrnls:
        jrnl = jrnl.strip()
        if jrnl == '':
            continue

        years = ['1975', '1980', '1990', '2002', '2013']
        num_desired = len(years)
        pmids = get_sample_pmids_for_journal(jrnl, years=years)
        if len(pmids) < num_desired:
            pmids = pmids + get_sample_pmids_for_journal(jrnl, max_pmids=num_desired-len(pmids))

        print('[%s] Sample pmids: %r' % (jrnl, pmids))
        for pmid in pmids:
            write_pmid_to_list(pmid)

if __name__ == '__main__':
    main()

