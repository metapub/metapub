from __future__ import absolute_import, print_function, unicode_literals

from metapub.findit import FindIt

#TODO: update these PMIDS (they're out of date now)...
SAMPLE_PMIDS = { 'embargoed': [ '25575644', '25700512', '25554792', '25146281', '25766237', '25370453' ],
                 'nonembargoed': ['26098888' ],
                 'non_pmc': ['26111251', '17373727']
               }

def print_url_and_reasons_from_pmid_list(pmids, listname='LIST'):
    print('@@@', listname)
    for pmid in pmids:
        source = FindIt(pmid=pmid, use_nih=True)
        embdate = source.pma.history.get('pmc-release', None)
        print('\t', source.pmid, source.pma.journal, 'PMC id = ', source.pma.pmc, ' pmc-release = %r' % embdate) 

        if source.url:
            print('\t', pmid, source.pma.journal, source.url)
        else:
            print('\t', pmid, source.pma.journal, source.reason)
            print('\t', pmid, source.pma.journal, 'Backup URL: ', source.backup_url)
    print()

for listname in sorted(SAMPLE_PMIDS.keys()):
    print_url_and_reasons_from_pmid_list(SAMPLE_PMIDS[listname], listname.upper())

