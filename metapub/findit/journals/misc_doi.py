# simple formats are used for URLs that can be deduced from PubMedArticle XML
#
#       !ACHTUNG!  informa has been known to block IPs for the capital offense of
#                  having "More than 25 sessions created in 5 minutes"
#

# Templates for remaining miscellaneous journals

doi_templates = {
    'akademii': 'http://www.akademiai.com/content/{a.pii}/fulltext.pdf',
    'ats': 'http://www.atsjournals.org/doi/pdf/{a.doi}',
    'lancet': 'http://www.thelancet.com/pdfs/journals/{ja}/PII{a.pii}.pdf',
    'liebert': 'http://online.liebertpub.com/doi/pdf/{a.doi}',
    'plos': 'http://www.plosone.org/article/fetchObject.action?uri=info:doi/{a.doi}&representation=PDF',
    'jci': 'http://www.jci.org/articles/view/{a.pii}/pdf',
}

simple_formats_doi = {
    # Informa Healthcare journals moved to journals/informa.py

    'Am J Public Health': 'http://ajph.aphapublications.org/doi/pdf/{a.doi}',
    'Am J Respir Cell Mol Biol': doi_templates['ats'],
    'Am J Respir Crit Care Med': doi_templates['ats'],

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

    # PLOS (Public Library of Science) journals
    'J Data Mining Genomics Proteomics': doi_templates['plos'],
    'J Pet Environ Biotechnol': doi_templates['plos'],
    'PLoS Biol': doi_templates['plos'],
    'PLoS Clin Trials': doi_templates['plos'],
    'PLoS Comput Biol': doi_templates['plos'],
    'PLoS Genet': doi_templates['plos'],
    'PLoS Med': doi_templates['plos'],
    'PLoS Negl Trop Dis': doi_templates['plos'],
    'PLoS One': doi_templates['plos'],
    'PLoS Pathog': doi_templates['plos'],

    'N Engl J Med':  'http://www.nejm.org/doi/pdf/{a.doi}',
}
