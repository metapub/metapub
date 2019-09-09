#  Endo Journals: part of Oxford Academic now.  
#  VIP format with journal abbreviations and ?serial number? at end.
#
#   Use dx.doi.org to resolve
#
#  See https://academic.oup.com
#
#  All require an initial page load (non-pdf) and then scrape for dynamic URL for PDF.
#

# DATA:
# Journal of the Endocrine Society:  https://academic.oup.com/jes/article/3/7/1375/5487346
# Endocrine Reviews: 
# Endocrinology:
# Journal of Molecular Endocrinology (1987–2016): https://academic.oup.com/mend
# 
# EXAMPLES (Endocrine Reviews):
#
#   From PMID:
#   30500870 --> 10.1210/er.2018-00166 --> https://academic.oup.com/edrv/article-abstract/40/2/558/5214057
#
#   From DOI:
#   https://doi.org/10.1210/er.2017-00103 --> https://academic.oup.com/edrv/article/39/1/36/4788769
#   

# de novo URL construction now superceded by use of DOI.
endo_journals = {
    'Endocrinology': {'ja':'endo', 'host':'https://academic.oup.com/endo/article/{a.volume}/{a.issue}/{a.firstpage}/5526759' },
    'Endocr Rev': {'ja':'edrv', 'host':'https://academic.oup.com/edrv/article/{a.volume}/{a.issue}/{a.firstpage}/4788769' },
    'Mol Endocrinol': {'ja':'mend', 'host':'https://academic.oup.com/mend/article/{a.volume}/{a.issue}/{a.firstpage}/2556328' },
    'J Clin Endocrinol Metab': {'ja': 'jcem', 'host': 'https://academic.oup.com/mend/article/{a.volume}/{a.issue}/{a.firstpage}/2556328' },
}

