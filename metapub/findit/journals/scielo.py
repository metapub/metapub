# SciELO
# 
# scielo.br 
#
# Publications in Portuguese published in Brazil, often in English.
#
# "The Scientific Electronic Library Online - 
#   SciELO is an electronic library covering a selected 
#   collection of Brazilian scientific journals."
#
# List of journals:
#   http://www.scielo.br/scielo.php?script=sci_alphabetic&lng=en&nrm=iso
#
# Notes:
#   DOI looks like PII, but doi suffix != pii.  Example:
#       [23657305] (10.1590/s0004-28032013000100008) --> 'S0004-28032013000100035'
#
#   PDF url construction depends on journal (argh).  Examples:
#       [23657305] --> http://www.scielo.br/pdf/ag/v50n1/0004-2803-ag-50-01-35.pdf
#       [23055798] --> http://www.scielo.br/pdf/gmb/v35n3/v35n3a09.pdf
#
# Fortunately, quite a lot of scielo articles can be found in Pubmed Central.
#
# Most reliable method: DxDOI resolution -> pdf link aquisition in page <meta>
#   <meta xmlns="" name="citation_pdf_url" language="en" default="true" content="http://www.scielo.br/pdf/etc/etc.pdf">

scielo_format = 'http://www.biomedcentral.com/content/pdf/{aid}.pdf'

#scielo_format = 'http://www.scielo.br/pdf/ag/v50n1/0004-2803-ag-50-01-35.pdf'

scielo_journals = (
    'Arq Gastroenterol',
)

