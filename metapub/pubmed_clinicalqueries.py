from __future__ import absolute_import, unicode_literals
###
#
# This file contains definitions for special methods of 
# forming advanced queries according to the specs on the
# following page:
#
# https://www.ncbi.nlm.nih.gov/books/NBK3827/#pubmedhelp.Clinical_Queries_Filters
#

clinical_query_map = { 

    'therapy_broad': '((clinical[Title/Abstract] AND trial[Title/Abstract]) OR clinical trials as topic[MeSH Terms] OR clinical trial[Publication Type] OR random*[Title/Abstract] OR random allocation[MeSH Terms] OR therapeutic use[MeSH Subheading])',
    'therapy_narrow': '(randomized controlled trial[Publication Type] OR (randomized[Title/Abstract] AND controlled[Title/Abstract] AND trial[Title/Abstract]))',
    'diagnosis_broad': '(sensitiv*[Title/Abstract] OR sensitivity and specificity[MeSH Terms] OR diagnose[Title/Abstract] OR diagnosed[Title/Abstract] OR diagnoses[Title/Abstract] OR diagnosing[Title/Abstract] OR diagnosis[Title/Abstract] OR diagnostic[Title/Abstract] OR diagnosis[MeSH:noexp] OR diagnostic * [MeSH:noexp] OR diagnosis,differential[MeSH:noexp] OR diagnosis[Subheading:noexp])',
    'diagnosis_narrow': '(specificity[Title/Abstract])',
    'etiology_broad': '(risk*[Title/Abstract] OR risk*[MeSH:noexp] OR risk *[MeSH:noexp] OR cohort studies[MeSH Terms] OR group[Text Word] OR groups[Text Word] OR grouped [Text Word])',
    'etiology_narrow': '((relative[Title/Abstract] AND risk*[Title/Abstract]) OR (relative risk[Text Word]) OR risks[Text Word] OR cohort studies[MeSH:noexp] OR (cohort[Title/Abstract] AND study[Title/Abstract]) OR (cohort[Title/Abstract] AND studies[Title/Abstract]))',
    'prognosis_broad': '(incidence[MeSH:noexp] OR mortality[MeSH Terms] OR follow up studies[MeSH:noexp] OR prognos*[Text Word] OR predict*[Text Word] OR course*[Text Word])',
    'prognosis_narrow': '(prognos*[Title/Abstract] OR (first[Title/Abstract] AND episode[Title/Abstract]) OR cohort[Title/Abstract])',
    'prediction_broad': '(predict*[tiab] OR predictive value of tests[mh] OR score[tiab] OR scores[tiab] OR scoring system[tiab] OR scoring systems[tiab] OR observ*[tiab] OR observer variation[mh])',
    'prediction_narrow': '(validation[tiab] OR validate[tiab])',
}


medical_genetics_query_map = {
    'diagnosis': '(Diagnosis AND Genetics)',
    'differential_diagnosis': '(Differential Diagnosis[MeSH] OR Differential Diagnosis[Text Word] AND Genetics)',
    'clinical_description': '(Natural History OR Mortality OR Phenotype OR Prevalence OR Penetrance AND Genetics)',
    'management': '(therapy[Subheading] OR treatment[Text Word] OR treatment outcome OR investigational therapies AND Genetics)',
    'genetic_counseling': '(Genetic Counseling OR Inheritance pattern AND genetics)',
    'molecular_genetics': '(Medical Genetics OR genotype OR genetics[Subheading] AND genetics)',
    'genetic_testing': '(DNA Mutational Analysis OR Laboratory techniques and procedures OR Genetic Markers OR diagnosis OR testing OR test OR screening OR mutagenicity tests OR genetic techniques OR molecular diagnostic techniques AND genetics)',
    'all': '((Diagnosis AND genetics) OR (Differential Diagnosis[MeSH] OR Differential Diagnosis[Text Word] AND genetics) OR (Natural History OR Mortality OR Phenotype OR Prevalence OR Penetrance AND genetics) OR (therapy[Subheading] OR treatment[Text Word] OR treatment outcome OR investigational therapies AND genetics) OR (Genetic Counseling OR Inheritance pattern AND genetics) OR (Medical Genetics OR genotype OR genetics[Subheading] AND genetics) OR (DNA Mutational Analysis OR Laboratory techniques and procedures OR Genetic Markers OR diagnosis OR testing OR test OR screening OR mutagenicity tests OR genetic techniques OR molecular diagnostic techniques AND genetics))',
}


