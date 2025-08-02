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



    # http://www.bioone.org/action/showPublications?type=byAlphabet
    # TODO: 'http://www.bioone.org/doi/pdf/{a.doi}',



}
