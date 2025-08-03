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
    # Original journal
    'Arq Gastroenterol',
    
    # Additional Brazilian SciELO journals from scielo.br domain
    'Acta Amazon',
    'Acta Cir Bras',
    'Acta Ortop Bras',
    'An Acad Bras Cienc',
    'Anim Reprod',
    'Arq Bras Cir Dig',
    'Arq Bras Endocrinol Metabol',
    'Arq Bras Oftalmol',
    'Braz Dent J',
    'Braz J Biol',
    'Braz J Med Biol Res',
    'Braz Oral Res',
    'Cad Saude Colet',
    'Cad Saude Publica',
    'Cien Saude Colet',
    'Codas',
    'Dement Neuropsychol',
    'Dental Press J Orthod',
    'Educ Soc',
    'Epidemiol Serv Saude',
    'Fractal',
    'Genet Mol Biol',
    'Hist Cienc Saude Manguinhos',
    'Int Braz J Urol',
    'J Appl Oral Sci',
    'J Bras Nefrol',
    'J Bras Psiquiatr',
    'J Soc Bras Fonoaudiol',
    'J Vasc Bras',
    'J Venom Anim Toxins Incl Trop Dis',
    'Mem Inst Oswaldo Cruz',
    'Motriz',
    'Nova Econ',
    'Pesqui Agropecu Bras',
    'Pesqui Odontol Bras',
    'Physis',
    'Pro Fono',
    'Psicol Estud',
    'Quim Nova',
    'Radiol Bras',
    'Rev Assoc Med Bras',
    'Rev Bras Biol',
    'Rev Bras Educ Med',
    'Rev Bras Enferm',
    'Rev Bras Epidemiol',
    'Rev Bras Fisioter',
    'Rev Bras Hist',
    'Rev Bras Parasitol Vet',
    'Rev Col Bras Cir',
    'Rev Esc Enferm USP',
    'Rev Gaucha Enferm',
    'Rev Hosp Clin Fac Med Sao Paulo',
    'Rev Inst Med Trop Sao Paulo',
    'Rev Lat Am Enfermagem',
    'Rev Paul Pediatr',
    'Rev Psiquiatr Clin',
    'Rev Soc Bras Med Trop',
    'Sex Salud Soc',
    'Vibrant',
)

