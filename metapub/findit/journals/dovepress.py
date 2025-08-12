# DovePress (Dove Medical Press)
# 
# dovepress.com
#
# DovePress is an academic publisher of open-access peer-reviewed scientific 
# and medical journals, acquired by Taylor & Francis Group in 2017.
# Specializes in open access medical and scientific publishing.
#
# URL Pattern:
#   - Article view: https://www.dovepress.com/[article-title]-peer-reviewed-fulltext-article-[JOURNAL_CODE]
#   - PDF download: https://www.dovepress.com/article/download/[ARTICLE_ID]
#
# DOI Pattern:
#   - 10.2147/[JOURNAL_CODE].S[ID]
#
# Journal Codes:
#   - IJN: International Journal of Nanomedicine
#   - OPTH: Clinical Ophthalmology
#   - CMAR: Cancer Management and Research
#   - DDDT: Drug Design, Development and Therapy
#   - NDT: Neuropsychiatric Disease and Treatment
#   - And many others...
#
# Notes:
#   - Most DovePress articles are freely accessible (open access)
#   - Articles are indexed in PubMed with PMIDs
#   - DOI resolution typically redirects to article pages
#   - PDF access may require parsing the article page for download links

# URL format template - will be used in the dance function
dovepress_format = 'https://www.dovepress.com/article/download/{article_id}'

# Complete list of DovePress journals (68 total)
# NOTE: Using PubMed abbreviated journal names to match PMA data
# DOVEPRESS template
dovepress_template = 'https://www.dovepress.com/article/download/{article_id}'

dovepress_journals = []  # Journal list moved to YAML configuration
