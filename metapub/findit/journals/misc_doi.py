# simple formats are used for URLs that can be deduced from PubMedArticle XML
#
#       !ACHTUNG!  informa has been known to block IPs for the capital offense of
#                  having "More than 25 sessions created in 5 minutes"
#

doi_templates = {
    'acs': 'http://pubs.acs.org/doi/pdf/{a.doi}',
    'akademii': 'http://www.akademiai.com/content/{a.pii}/fulltext.pdf',
    'ats': 'http://www.atsjournals.org/doi/pdf/{a.doi}',
    'futuremed': 'http://www.futuremedicine.com/doi/pdf/{a.doi}',
    'informa': 'http://informahealthcare.com/doi/pdf/{a.doi}',
    'lancet': 'http://www.thelancet.com/pdfs/journals/{ja}/PII{a.pii}.pdf',
    'liebert': 'http://online.liebertpub.com/doi/pdf/{a.doi}',
    'plos': 'http://www.plosone.org/article/fetchObject.action?uri=info:doi/{a.doi}&representation=PDF',
    'taylor_francis': 'http://www.tandfonline.com/doi/pdf/{a.doi}',
    'wiley': 'http://onlinelibrary.wiley.com/doi/{a.doi}/pdf',
    'jci': 'http://www.jci.org/articles/view/{a.pii}/pdf',
}

simple_formats_doi = {
    'Acta Oncol': doi_templates['informa'],
    'Ann Hum Biol': doi_templates['informa'],
    'Hemoglobin': doi_templates['informa'],
    'J Matern Fetal Neonatal Med': doi_templates['informa'],
    'Ophthalmic Genet': doi_templates['informa'],
    'Platelets': doi_templates['informa'],
    'Ren Fail': doi_templates['informa'],
    'Scand J Rheumatol': doi_templates['informa'],
    'Scand J Urol Nephrol': doi_templates['informa'],
    'Xenobiotica': doi_templates['informa'],

    'Am J Public Health': 'http://ajph.aphapublications.org/doi/pdf/{a.doi}',
    'Am J Respir Cell Mol Biol': doi_templates['ats'],
    'Am J Respir Crit Care Med': doi_templates['ats'],

    'Anal Chem': doi_templates['acs'],
    'ACS Appl Mater': doi_templates['acs'],
    'ACS Chem Biol': doi_templates['acs'],
    'ACS Nano': doi_templates['acs'],
    'Biochemistry': doi_templates['acs'],
    'Chem Res Toxicol': doi_templates['acs'],
    'Inorg Chem': doi_templates['acs'],
    'J Agric Food Chem': doi_templates['acs'],
    'J Am Chem Soc': doi_templates['acs'],
    'J Comb Chem': doi_templates['acs'],
    'J Med Chem': doi_templates['acs'],
    'J Phys Chem A': doi_templates['acs'],
    'Langmuir': doi_templates['acs'],
    'Nano Lett': doi_templates['acs'],

    'BMJ Open Gastroenterol': 'http://bmjopengastro.bmj.com/doi/pdf/{a.doi}',
    'Microbiol Spectr': 'http://www.asmscience.org/content/journal/microbiolspec/{a.doi}', #10.1128/microbiolspec.VMBF-0028-2015

    # http://www.bioone.org/action/showPublications?type=byAlphabet
    # TODO: 'http://www.bioone.org/doi/pdf/{a.doi}',

    'AIDS Res Hum Retroviruses': doi_templates['liebert'],
    'Antioxid Redox Signal': doi_templates['liebert'],
    'Child Obes': doi_templates['liebert'],
    'DNA Cell Biol': doi_templates['liebert'],
    'Genet Test': doi_templates['liebert'],
    'Genet Test Mol Biomarkers': doi_templates['liebert'],
    'Thyroid': doi_templates['liebert'],
    'Vector Borne Zoonotic Dis': doi_templates['liebert'],

    # TODO: the rest of futuremed journals. see http://www.futuremedicine.com/
    'Pharmacogenomics': doi_templates['futuremed'],

    'Acta Orthop Scand': doi_templates['taylor_francis'],
    'Acta Orthop Scand Suppl': doi_templates['taylor_francis'],
    'Acta Otolaryngol': doi_templates['taylor_francis'],
    'Acta Otolaryngol Suppl': doi_templates['taylor_francis'],
    'Acta Otorhinolaryngol Belg': doi_templates['taylor_francis'],
    'Autophagy': doi_templates['taylor_francis'],
    'Biosci Biotechnol Biochem': doi_templates['taylor_francis'],
    'Cancer Biol Ther': doi_templates['taylor_francis'],
    'Cell Cycle': doi_templates['taylor_francis'],
    'Drug Metab Rev': doi_templates['taylor_francis'],
    'Environ Technol': doi_templates['taylor_francis'],
    'Health Commun': doi_templates['taylor_francis'],
    'J Biomol Struct Dyn': doi_templates['taylor_francis'],
    'J Pers Assess': doi_templates['taylor_francis'],
    'Pediatr Hematol Oncol': doi_templates['taylor_francis'],
    'Worm': doi_templates['taylor_francis'],

    'PLoS Biol': doi_templates['plos'],
    'PLoS Comput Biol': doi_templates['plos'],
    'PLoS Genet': doi_templates['plos'],
    'PLoS Med': doi_templates['plos'],
    'PLoS ONE': doi_templates['plos'],
    'PLoS Pathog': doi_templates['plos'],
    'N Engl J Med':  'http://www.nejm.org/doi/pdf/{a.doi}',
}
