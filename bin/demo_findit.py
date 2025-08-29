import logging

from metapub.findit import FindIt

older_pmids = ['2655732', '320292', '7686069', '7689822', '1287655', '7683021', '1309291', '1255861']

najms_pmids = ['26199928', '24083224', '24083223', '24083222']

vip_pmids = ['1255861',     # J Virol
             '15252189',    # Physiol Genomics
             '12066726',    # Br J Anaesth (oxford)
             '22796417',    # Bone
             '16958849',    # FEMS Microbiol Lett (oxford)
             '17351018',    # Protein Eng Des Sel (oxford)
             '9854186',     # J Endocrinol
            ]

vip_nonstandard_pmids = [ '1586703',
                        ]  #Blood

doi_pmids = ['15727972',         # Am J Public Health
             '12170759', 
             '12444763',         # Inorg Chem (acs)
             '23136976',         # J Phys Chem A (acs)
             '25410894',         # Pharmacogenomics
            ]

pii_pmids = ['26061871',    # Clin Trans Med
            ]

#TODO when Dustri dance is complete
dustri_pmids = ['26042486']

karger_pmids = ['23970213',  #Ann Nutr Metab
                '11509830',  #Cell Physiol Biochem w/ bad doi in PMA
                '20805699',  #Nephron Clin Pract
               ]

nature_pmids = ['16419642',  #Hypertens Res
                '18830250',  #J Hum Hypertens
                '12187393',  #Int J Obes Relat Metab Disord
               ]

springer_pmids = [
            '25543539',     #Hum Genet
            '25666562', 
            ]

jstage_pmids = ['11446670', 
                '10458483',
                '21297370',  #Yakugaku Zasshi
               ] 

wiley_pmids = ['14981756', 
               '10474162', 
               '10470409',
               '10782214',  #Anim Genet
               '11695191',  #Pest Manag Sci
               '15059157',  #Acta Obstet Gynecol Scand
               '22533155',  #Wiad Lek
              ]

jama_pmids = ['8765374',    # Schweiz Med Wochenschr
              '13217497',   #AMA Arch Intern Med
             ]

biochemsoc_pmids = ['11776', '25896238', '11980567']

JAMA_pmids = ['25742465', '23754022', '25739104']

JCI_pmids = ['26011642', '25985270', '26030226']

BMC_pmids = ['25943194',     # BMC Genet
             '20170543',     # BMC Cancer
             '25927199',     # BMC Bioinformatics
             '25935646',     # BMC Genet
             '25929254',     # BMC Med Genet
             '25954321',     # Genome Med
             '25958000',     # Hum Genomics
             '25937888',     # J Clin Bioinfoma
             '25968637',     # J Transl Med
            ]

PMC_pmids = ['25717385',     # Lancet Psychiatry
             '17534376',     # Eur J Hum Genet
            ]  

Lancet_pmids = ['25529582',     # marked Free Article
                '25483163',     # not marked Free
                '25456370',     #Lancet Oncol, not marked Free
               ]

SD_pmids = ['20000000',    # J Environ Sci (China)
            '25735572', 
            '24565554', 
            '10545037',
            '16644204',
            '15878741',     #Biochim Biophys Acta / http://www.sciencedirect.com/science/article/pii/S0925443905000177
            '23246278',     #Molecular Genetics and Metabolism
            '206004',       #Virology
            '19168055',     #Eur J Pharmacol
            ]

def print_urls_and_reasons_from_pmid_list(pmids):
    for pmid in pmids:
        source = FindIt(pmid=pmid, retry_errors=True)
        if source.url:
            print("Got: ", pmid, source.url, source.pma.journal)
        else:
            print("Nope: ", pmid, source.reason, source.pma.journal)
            #if source.reason.startswith('NOFORMAT'):
            #    from IPython import embed; embed()
            #print("Backup URL: ", pmid, source.backup_url

print("")
print("doi journals:")
print_urls_and_reasons_from_pmid_list(doi_pmids)

print("")
print("vip journals:")
print_urls_and_reasons_from_pmid_list(vip_pmids)

print("")
print("vip nonstandard journals:")
print_urls_and_reasons_from_pmid_list(vip_nonstandard_pmids)

print("")
print("pii based journals:")
print_urls_and_reasons_from_pmid_list(pii_pmids)

print("")
print("PMC (or should be):")
print_urls_and_reasons_from_pmid_list(PMC_pmids)

print("")
print("Biochemical Society:")
print_urls_and_reasons_from_pmid_list(biochemsoc_pmids)

print("")
print("JAMA jama jama jama jama chameleon:")
print_urls_and_reasons_from_pmid_list(jama_pmids)

print("")
print("Wiley E. Publisher:")
print_urls_and_reasons_from_pmid_list(wiley_pmids)

print("")
print("karger:")
print_urls_and_reasons_from_pmid_list(karger_pmids)

print("")
print("Springer:")
print_urls_and_reasons_from_pmid_list(springer_pmids)

print("")
print("Nature:")
print_urls_and_reasons_from_pmid_list(nature_pmids)

print("")
print("jstage:")
print_urls_and_reasons_from_pmid_list(jstage_pmids)

print("")
print("J Clin Invest (JCI):")
print_urls_and_reasons_from_pmid_list(JCI_pmids)

print("")
print("BMC journals:")
print_urls_and_reasons_from_pmid_list(BMC_pmids)

print("")
print("ScienceDirect:")
print_urls_and_reasons_from_pmid_list(SD_pmids)

print("")
print("JAMA:")
print_urls_and_reasons_from_pmid_list(JAMA_pmids)

print("")
print("Lancet:")
print_urls_and_reasons_from_pmid_list(Lancet_pmids)

print("")
print("NAJMS:")
print_urls_and_reasons_from_pmid_list(najms_pmids)


print("")
print("older articles:")
print_urls_and_reasons_from_pmid_list(older_pmids)

