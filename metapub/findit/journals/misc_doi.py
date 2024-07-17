import pkg_resources
import os


# DOI simple formats are used for URLs that can be deduced from PubMedArticle XML
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

# Start simple_formats_doi dict with the outliers, the non-template-followers,
# and publishers with only a few journals in pubmed. Then we'll fill it in with
# journals en masse from publisher_lists/*.txt where textfile names should match
# the name of the template in doi_templates.

simple_formats_doi = {
    # ATS
    'Am J Public Health': 'http://ajph.aphapublications.org/doi/pdf/{a.doi}',
    'Am J Respir Cell Mol Biol': doi_templates['ats'],
    'Am J Respir Crit Care Med': doi_templates['ats'],

    # BMJ
    'BMJ Open Gastroenterol': 'http://bmjopengastro.bmj.com/doi/pdf/{a.doi}',
    'Microbiol Spectr': 'http://www.asmscience.org/content/journal/microbiolspec/{a.doi}', #10.1128/microbiolspec.VMBF-0028-2015

    # FUTUREMED
    # TODO: the rest of futuremed journals. see http://www.futuremedicine.com/
    'Pharmacogenomics': doi_templates['futuremed'],

    # LIEBERT
    'AIDS Res Hum Retroviruses': doi_templates['liebert'],
    'Antioxid Redox Signal': doi_templates['liebert'],
    'Child Obes': doi_templates['liebert'],
    'DNA Cell Biol': doi_templates['liebert'],
    'Genet Test': doi_templates['liebert'],
    'Genet Test Mol Biomarkers': doi_templates['liebert'],
    'Thyroid': doi_templates['liebert'],
    'Vector Borne Zoonotic Dis': doi_templates['liebert'],

    'N Engl J Med':  'http://www.nejm.org/doi/pdf/{a.doi}',
    # TODO: 'http://www.bioone.org/doi/pdf/{a.doi}',
    #        http://www.bioone.org/action/showPublications?type=byAlphabet

}


# Function to load journal names from a text file
def load_journals_from_file(publisher):
    resource_package = __name__  # Name of the current package
    #resource_path = f'../../publisher_lists/{publisher}.txt'  # Relative path to the resource
    resource_path = f'publisher_lists/{publisher}.txt'  # Relative path to the resource
    print(resource_path)

    try:
        # Check if the file exists in the package
        if not pkg_resources.resource_exists(resource_package, resource_path):
            print(f"File {publisher}.txt not found in the package.")
            return

        journal_names = pkg_resources.resource_string(resource_package, resource_path).decode('utf-8')
        for line in journal_names.splitlines():
            journal_name = line.strip()
            if journal_name:
                simple_formats_doi[journal_name] = doi_templates[publisher]
    except FileNotFoundError:
        print(f"File {publisher}.txt not found.")
        return



# Ingest all of the journals contained in the publisher_list/*.txt files.  
# Add them into the directory according to the templates they require.
for key in doi_templates:
    load_journals_from_file(key)


