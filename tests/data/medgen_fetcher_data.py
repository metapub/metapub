# Biomed/api/stuff/gene2disease/$GENE
#
# expected response includes 
#
# SemanticType=='Disease or Syndrome' 
# MedGenUID=='C####' | 'CN####' | #### | Example: 2881
# 
# Subtypes: 
# For this disease, what are the subtypes? 
# Subtype::= MedGenUID 'Disease or Syndrome' where MGREL has_parent==2881  
#
#
# Hypertrophic Cardiomyopathy
# http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=medgen&id=2881
#
# Gene OCRL
# http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=medgen&term=OCRL
# result:

"""<eSearchResult>
<Count>5</Count>
<RetMax>5</RetMax>
<RetStart>0</RetStart>
<IdList>
<Id>763754</Id>
<Id>336867</Id>
<Id>336322</Id>
<Id>168056</Id>
<Id>18145</Id>
</IdList>
<TranslationSet/>
<TranslationStack>
<TermSet>
<Term>OCRL[All Fields]</Term>
<Field>All Fields</Field>
<Count>5</Count>
<Explode>N</Explode>
</TermSet>
<OP>GROUP</OP>
</TranslationStack>
<QueryTranslation>OCRL[All Fields]</QueryTranslation>
</eSearchResult>
"""

# from above list, get summary for id #18145
# http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=medgen&id=18145
# result begins:
"""
<eSummaryResult>
<DocumentSummarySet status="OK">
<DbBuild>Build141124-1357.1</DbBuild>
<DocumentSummary uid="18145">
<ConceptId>C0028860</ConceptId>
<Title>Lowe syndrome</Title>
<Definition>
Lowe syndrome (oculocerebrorenal syndrome) is characterized by involvement of the eyes, central nervous system, and kidneys. Dense congenital cataracts are found in all affected boys and infantile glaucoma in approximately 50%. All boys have impaired vision; corrected acuity is rarely better than 20/100. Generalized hypotonia is noted at birth and is of central (brain) origin. Deep tendon reflexes are usually absent. Hypotonia may slowly improve with age, but normal motor tone and strength are never achieved. Motor milestones are delayed. Almost all affected males have some degree of intellectual disability; 10%-25% function in the low-normal or borderline range, approximately 25% in the mild-to-moderate range, and 50%-65% in the severe-to-profound range of intellectual disability. Affected males have varying degrees of proximal renal tubular dysfunction of the Fanconi type, including bicarbonate wasting and renal tubular acidosis, phosphaturia with hypophosphatemia and renal rickets, aminoaciduria, low molecular-weight (LMW) proteinuria, sodium and potassium wasting, and polyuria. Fanconi syndrome is usually not clinically apparent in the first few months of life, but symptoms may appear by age six to 12 months. Glomerulosclerosis associated with chronic tubular injury usually results in slowly progressive chronic renal failure and end-stage renal disease after age ten to 20 years.
</Definition>
<SemanticId>T047</SemanticId>
<SemanticType>Disease or Syndrome</SemanticType>
<Suppressed/>
<ConceptMeta>
...
STUFF
</ConceptMeta>
<ModificationDate/>
<Merged/>
</DocumentSummary>
</DocumentSummarySet>
</eSummaryResult>
"""


test_gene_list = """
FMR1
SYNE1
SYNE2
TMEM43
CRYAB
PCSK9
APOB
LDLRAP1
LDLR
APOE
F5
LIPC
FOXP3
PTPN22
"""

