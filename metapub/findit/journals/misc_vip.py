from __future__ import absolute_import, unicode_literals

# vip = Volume-Issue-Page format
#       URLs that have the same format except for the host name
#
# TODO: early release format

vip_format = 'http://{host}/content/{a.volume}/{a.issue}/{a.first_page}.full.pdf'

vip_journals = {
    'Ann Clin Biochem': {'host': 'acb.sagepub.com'},
    'Am J Clin Pathol': {'host': 'ajcp.ascpjournals.org'},
    'Am J Hypertens': {'host': 'ajh.oxfordjournals.org'},
    'Am J Physiol Cell Physiol': {'host': 'ajpcell.physiology.org'},
    'Am J Physiol Endocrinol Metab': {'host': 'ajpendo.physiology.org'},
    'Am J Physiol Gastrointest Liver Physiol': {'host': 'ajpgi.physiology.org'},
    'Am J Physiol Heart Circ Physiol': {'host': 'ajpheart.physiology.org'},
    'Am J Physiol Lung Cell Mol Physiol': {'host': 'ajplung.physiology.org'},
    'Am J Physiol Regul Integr Comp Physiol': {'host': 'ajpregu.physiology.org'},
    'Am J Physiol Renal Physiol': {'host': 'ajprenal.physiology.org'},
    # TODO: the rest of physiology.org. see: http://www.the-aps.org/mm/Publications/Journals
    'Angiology': {'host': 'ang.sagepub.com'}, 
    'Ann Oncol': {'host': 'annonc.oxfordjournals.org'},
    # TODO: backup_url: pmid lookup strategy, e.g.
    # http://aac.asm.org/cgi/pmidlookup?view=long&pmid=7689822
    'Anticancer Res': {'host': 'ar.iiarjournals.org'},
    'Antimicrob Agents Chemother': {'host': 'aac.asm.org'},
    'Appl Environ Microbiol': {'host': 'aem.asm.org'},
    'Arterioscler Thromb Vasc Biol': {'host': 'atvb.ahajournals.org'},
    'Assessment': {'host': 'asm.sagepub.com'},
    'Brain': {'host': 'brain.oxfordjournals.org'},
    'Breast Cancer Res': {'host': 'breast-cancer-research.com'},
    'Br J Anaesth': {'host': 'bja.oxfordjournals.org'},
    'Cancer Discov': {'host': 'cancerdiscovery.aacrjournals.org'},
    'Cancer Epidemiol Biomarkers Prev': {'host': 'cebp.aacrjournals.org'},
    'Cancer Res': {'host': 'cancerres.aacrjournals.org'},
    # TODO: backup_url: pmid lookup strategy, e.g.
    # http://www.cfp.ca/cgi/pmidlookup?view=long&pmid=19282532
    'Can Fam Physician': {'host': 'www.cfp.ca'},
    'Carcinogenesis': {'host': 'carcin.oxfordjournals.org'},
    'Cardiovasc Res': {'host': 'cardiovascres.oxfordjournals.org'},
    'Circulation': {'host': 'circ.ahajournals.org'},
    'Circ Arrhythm Electrophysiol': {'host': 'circep.ahajournals.org'},
    'Circ Cardiovasc Genet': {'host': 'circgenetics.ahajournals.org'},
    'Circ Res': {'host': 'circres.ahajournals.org'},
    'Clin Appl Thromb Hemost': {'host': 'cat.sagepub.com'},
    'Clin Cancer Res': {'host': 'clincancerres.aacrjournals.org'},
    'Clin Chem': {'host': 'clinchem.org'},
    'Clin Infect Dis': {'host': 'cid.oxfordjournals.org'},
    'Clin Microbiol Rev': {'host': 'cmr.asm.org'},
    'Clin Pediatr': {'host': 'cpj.sagepub.com'},
    'Clin Pediatr (Phila)': {'host': 'cpj.sagepub.com'},
    'Clin Vaccine Immunol': {'host': 'cvi.asm.org'},
    'Diabetes': {'host': 'diabetes.diabetesjournals.org'},
    'Diabetes Care': {'host': 'care.diabetesjournals.org'},
    'Drug Metab Dispos': {'host': 'dmd.aspetjournals.org'},
    # TODO: backup_url: pmid lookup strategy,
    # http://emboj.embopress.org/cgi/pmidlookup?view=long&pmid=9501081
    'EMBO J': {'host': 'emboj.embopress.org'},
    'Endocr Relat Cancer': {'host': 'erc.endocrinology-journals.org'},  #TODO this is now https://erc.bioscientifica.com/
    'Environ Entomol': {'host': 'ee.oxfordjournals.org'},
    'Eukaryot Cell': {'host': 'ec.asm.org'},
    'Eur Heart J': {'host': 'eurheartj.oxfordjournals.org'},
    'Eur J Endocrinol': {'host': 'eje-online.org'},
    'Eur Respir J': {'host': 'erj.ersjournals.com'},
    'FASEB J': {'host': 'fasebj.org'},
    'FEMS Microbiol Lett': {'host': 'femsle.oxfordjournals.org'},
    'Genome Announc': {'host': 'genomea.asm.org'},
    'Genome Biol': {'host': 'genomebiology.com'},
    'Genome Res': {'host': 'genome.cshlp.org'},
    'Genes Dev': {'host': 'genesdev.cshlp.org'},
    'Haematologica': {'host': 'haematologica.org'},
    'Hum Mol Genet': {'host': 'hmg.oxfordjournals.org'},
    'Hum Reprod': {'host': 'humrep.oxfordjournals.org'},
    'Hypertension': {'host': 'hyper.ahajournals.org'},
    'Infect Immun': {'host': 'iai.asm.org'},
    'Invest Ophthalmol Vis Sci': {'host': 'www.iovs.org'},
    'IOVS': {'host': 'iovs.org'},
    # TODO: backup_url: pmid lookup strategy,
    # http://jah.sagepub.com/cgi/pmidlookup?view=long&pmid=20056814
    'J Aging Health': {'host': 'jah.sagepub.com'},
    'J Am Soc Nephrol': {'host': 'jasn.asnjournals.org'},
    'J Antimicrob Chemother': {'host': 'jac.oxfordjournals.org'},
    'J Appl Physiol': {'host': 'jap.physiology.org'},
    # TODO: backup_url: pmid lookup strategy,
    # http://jb.asm.org/cgi/pmidlookup?view=long&pmid=7683021
    'J Bacteriol': {'host': 'jb.asm.org'},
    # TODO backup_url: pmid lookup strategy, e.g.
    # http://www.jbc.org/cgi/pmidlookup?view=long&pmid=14722075
    'J Biol Chem': {'host': 'www.jbc.org'},
    'J Bone Joint Surg Am': {'host': 'jbjs.org'},
    'J Cell Biol': {'host': 'jcb.rupress.org'},
    'J Cell Sci': {'host': 'jcs.biologists.org'},
    'J Child Neurol': {'host': 'jcn.sagepub.com'},
    'J Clin Oncol': {'host': 'jco.ascopubs.org'},
    'J Dent Res': {'host': 'jdr.sagepub.com'},
    #'J Endocrinol': {'host': 'joe.endocrinology-journals.org'},   #moved
    #'J Mol Endocrinol': {'host': 'jme.endocrinology-journals.org'}, # moved to endo.py
    'J Exp Med': {'host': 'jem.rupress.org'},
    'J Gerontol A Biol Sci Med Sci': {'host': 'biomedgerontology.oxfordjournals.org'},
    'J Hum Lact': {'host': 'jhl.sagepub.com'},
    'J Immunol': {'host': 'jimmunol.org'},
    'J Infect Dis': {'host': 'jid.oxfordjournals.org'},
    'J Lipid Res': {'host': 'www.jlr.org'},
    'J Clin Microbiol': {'host': 'jcm.asm.org'},
    'J Natl Cancer Inst': {'host': 'jnci.oxfordjournals.org'},
    'J Neurophysiol': {'host': 'jb.physiology.org'},
    'J Neurosci': {'host': 'jneurosci.org'},
    # TODO:  backup_url: pmid lookup strategy,
    # http://jn.nutrition.org/cgi/pmidlookup?view=long&pmid=10736367
    'J Nutr': {'host': 'jn.nutrition.org'},
    'J Pharmacol Exp Ther': {'host': 'jpet.aspetjournals.org'},
    'J Rheumatol': {'host': 'www.jrheum.org'},
    'J Renin Angiotensin Aldosterone Syst': {'host': 'jra.sagepub.com'},
    'J Virol': {'host': 'jvi.asm.org'},
    'Lupus': {'host': 'lup.sagepub.com'},
    'MBio': {'host': 'mbio.asm.org'},
    'mSystems': {'host': 'msystems.asm.org'},
    'mSphere': {'host': 'msphere.asm.org'},
    'Microbiol Mol Biol Rev': {'host': 'mmbr.asm.org'},
    'Mol Biol Cell': {'host': 'molbiolcell.org'},
    'Mol Cell Biol': {'host': 'mcb.asm.org'},
    'Mol Canc Therapeut': {'host': 'mct.aacrjournals.org'},
    'Mol Cancer Ther': {'host': 'mct.aacrjournals.org'},
    'Mol Hum Reprod': {'host': 'molehr.oxfordjournals.org'},
    'Mol Pharmacol': {'host': 'molpharm.aspetjournals.org'},
    'Mutagenesis': {'host': 'mutage.oxfordjournals.org'},
    'Neurology': {'host': 'neurology.org'},
    'Nephrol Dial Transplant': {'host': 'ndt.oxfordjournals.org'},
    'Nucleic Acids Res': {'host': 'nar.oxfordjournals.org'},
    'Orphanet J Rare Dis': {'host': 'ojrd.com'},
    'Pediatrics': {'host': 'pediatrics.aappublications.org'},
    # TODO: backup_url: pmid lookup strategy, e.g.
    # http://physiolgenomics.physiology.org/cgi/pmidlookup?view=long&pmid=15252189
    'Physiology (Bethesda)': {'host': 'physiologyonline.physiology.org'},
    'Physiol Genomics': {'host': 'physiolgenomics.physiology.org'},
    'Physiol Rep': {'host': 'physreports.physiology.org'},
    'Physiol Rev': {'host': 'physrev.physiology.org'},
    # TODO:  backup_url: pmid lookup strategy, e.g.
    # http://www.plantcell.org/cgi/pmidlookup?view=long&pmid=9501112
    'Plant Cell': {'host': 'www.plantcell.org'},
    'Plant Cell Physiol': {'host': 'pcp.oxfordjournals.org'},
    'Proc Natl Acad Sci USA': {'host': 'pnas.org'},
    'Protein Eng': {'host': 'peds.oxfordjournals.org'},
    'Protein Eng Des Sel': {'host': 'peds.oxfordjournals.org'},
    'QJM': {'host': 'qjmed.oxfordjournals.org'},
    'Radiat Res': {'host': 'jrr.oxfordjournals.org'},
    'Rheumatology (Oxford)': {'host': 'rheumatology.oxfordjournals.org'},
    'Science': {'host': 'sciencemag.org'},
    'Stroke': {'host': 'stroke.ahajournals.org'},

    'Acupunct Med': {'host': 'aim.bmj.com'},
    'Arch Dis Child': {'host': 'adc.bmj.com'},
    'Arch Dis Child Fetal Neonatal Ed': {'host': 'fn.bmj.com'},
    'Arch Dis Child Educ Pract Ed': {'host': 'ep.bmj.com'},
    'Ann Rheum Dis': {'host': 'ard.bmj.com'},
    'BMJ Innov': {'host': 'innovations.bmj.com'},
    'BMJ Open': {'host': 'bmjopen.bmj.com'},
    'BMJ Open Diabetes Res Care': {'host': 'drc.bmj.com'},
    'BMJ Open Resp Res': {'host': 'bmjopenrespres.bmj.com'},
    'BMJ Open Sport Exerc Med': {'host': 'bmjopensem.bmj.com'},
    'BMJ Qual Saf': {'host': 'qualitysafety.bmj.com'},
    'BMJ Qual Improv Report': {'host': 'qir.bmj.com'},
    'BMJ STEL': {'host': 'stel.bmj.com'},
    'BMJ Support Palliat Care': {'host': 'spcare.bmj.com'},
    'BMC Ophthalmol': {'host': 'bjo.bmj.com'},
    'Br J Sports Med': {'host': 'bjsm.bmj.com'},
    'Drug Ther Bull': {'host': 'dtb.bmj.com'},
    'Emerg Med J': {'host': 'emj.bmj.com'},
    'End Life J': {'host': 'eolj.bmj.com'},
    'ESMO Open': {'host': 'esmoopen.bmj.com'},
    'Eur J Hosp Pharm': {'host': 'ejhp.bmj.com'},
    'Evid Based Mental Health': {'host': 'ebmh.bmj.com'},
    'Evid Based Med': {'host': 'ebm.bmj.com'},
    'Evid Based Nurs': {'host': 'ebn.bmj.com'},
    'Frontline Gastroenterol': {'host': 'fg.bmj.com'},
    'Gut': {'host': 'gut.bmj.com'},
    'Heart': {'host': 'heart.bmj.com'},
    'Heart Asia': {'host': 'heartasia.bmj.com'},
    'Inj Prev': {'host': 'injuryprevention.bmj.com'},
    'In Pract': {'host': 'inpractice.bmj.com'},
    'J Clin Pathol': {'host': 'jcp.bmj.com'},
    'J Epidemiol Community Health': {'host': 'jech.bmj.com'},
    'J Fam Plann Reprod Health Care': {'host': 'jfprhc.bmj.com'},
    'J Investig Med': {'host': 'jim.bmj.com'},
    'J ISAKOS': {'host': 'jisakos.bmj.com'},
    'J Med Ethics': {'host': 'jme.bmj.com'},
    'J Med Genet': {'host': 'jmg.bmj.com'},
    'J Neurol Neurosurg Psychiatry': {'host': 'jnnp.bmj.com'},
    'J Neurointerv Surg': {'host': 'jnis.bmj.com'}, 
    'J R Army Med Corps': {'host': 'jramc.bmj.com'}, # not in Entrez journal list but has citation pmid 7602561
    'Lupus Sci Med': {'host': 'lupus.bmj.com'},
    'Med Humanities': {'host': 'mh.bmj.com'},
    'Occup Environ Med': {'host': 'oem.bmj.com'},
    'Open Heart': {'host': 'openheart.bmj.com'},
    'Pract Neurol': {'host': 'pn.bmj.com'},
    'RMD Open': {'host': 'rmdopen.bmj.com'},
    'Sex Transm Infect': {'host': 'sti.bmj.com'},
    'Vet Rec': {'host': 'veterinaryrecord.bmj.com'},
    'Vet Rec Case Rep': {'host': 'vetrecordcasereports.bmj.com'},
    'Vet Rec Open': {'host': 'vetrecordopen.bmj.com'},
    'Tob Control': {'host': 'tobaccocontrol.bmj.com'},
    'Postgrad Med J': {'host': 'pmj.bmj.com'},
    'Thorax': {'host': 'thorax.bmj.com'},
}

# volume-issue-page type URLs but with a nonstandard baseurl construction.
# e.g. Blood: http://www.bloodjournal.org/content/bloodjournal/79/10/2507.full.pdf
#      BMJ:   http://www.bmj.com/content/bmj/350/bmj.h3317.full.pdf
# Thorax:
# http://thorax.bmj.com/content/early/2015/06/23/thoraxjnl-2015-207199.full.pdf+html

# no trailing slash in baseurl (please)
vip_journals_nonstandard = {
    # TODO: backup_url: pmid lookup strategy, e.g.
    # http://www.bloodjournal.org/cgi/pmidlookup?view=long&pmid=1586703
    'Blood': 'http://www.bloodjournal.org/content/bloodjournal/{a.volume}/{a.issue}/{a.first_page}.full.pdf',
    'BMJ':   'http://www.bmj.com/content/bmj/{a.volume}/bmj.{a.first_page}.full.pdf',
}

# Non-VIP, not sure where to put yet
# 'BMJ Case Rep': {'host': 'casereports.bmj.com', 'example': 'http://casereports.bmj.com/content/2016/bcr-2015-214310'}
# 


#TODO: The following SAGE journals:

"""
AADE Pract
AERA Open
ASN Neuro
Acad Forensic Pathol
Acta Radiol
Acta Radiol Diagn (Stockh)
Acta Radiol Open
Acta Radiol Short Rep
Acta Radiol Suppl (Stockholm)
Acta radiol
Action Res (Lond)
Adapt Behav
Adm Sci Q
Adm Soc
Adopt Foster
Adsorp Sci Technol
Adult Educ
Adult Educ Q (Am Assoc Adult Contin Educ)
Adv Dent Res
Adv Dev Hum Resour
Adv Methods Pract Psychol Sci
Allergy Rhinol (Providence)
AlterNative (Nga Pae Maramatanga (Organ))
Altern Lab Anim
Alternatives (Boulder)
Am Assoc Ind Nurses J
Am Behav Sci
Am Econ
Am Educ Res J
Am J Alzheimers Dis Other Demen
Am J Eval
Am J Health Promot
Am J Hosp Care
Am J Hosp Palliat Care
Am J Lifestyle Med
Am J Mens Health
Am J Rhinol
Am J Rhinol Allergy
Am J Sports Med
Am Polit Q
Am Rev Public Adm
Am Sociol Rev
Am Surg
Anaesth Intensive Care
Anal Chem Insights
Anglo Am Law Rev
Ann Am Acad Pol Soc Sci
Ann ICRP
Ann Neurosci
Ann Otol Rhinol Laryngol
Ann Otol Rhinol Laryngol Suppl
Ann Pharmacother
Annu Rep R Soc Promot Health
Antivir Chem Chemother
Antivir Ther
Appl Psychol Meas
Appl Spectrosc
Arch Psychol Relig
Armed Forces Soc
Asia Pac J Public Health
Asian Cardiovasc Thorac Ann
Asian Pac Migr J
Assess Eff Interv
Aust J Educ
Aust Med Rec J
Aust N Z J Criminol
Aust N Z J Psychiatry
Aust N Z J Sociol
Australas Psychiatry
Autism
Autism Dev Lang Impair
Avian Biol Res
Behav Cogn Neurosci Rev
Behav Disord
Behav Modif
Behav Sci Res
Big Data Soc
Biochem Insights
Bioinform Biol Insights
Biol Res Nurs
Biomark Cancer
Biomark Insights
Biomed Eng Comput Biol
Biomed Inform Insights
Body Soc
Bone Tissue Regen Insights
Br J Med Surg Urol
Br J Occup Ther
Br J Pain
Br J Perioper Nurs
Br J Polit Int Relat
Br J Theatre Nurs
Br J Vis Impair
Brain Neurosci Adv
Breast Cancer (Auckl)
Build Serv Eng Res Technol
Bull Methodol Sociol
Bull Peace Propos
Bull Sci Technol Soc
Bus Soc
CPJ
Can Assoc Radiol J
Can J Kidney Health Dis
Can J Nurs Res
Can J Occup Ther
Can J Psychiatry
Can J Sch Psychol
Can Pharm J (Ott)
Can Psychiatr Assoc J
Cancer Control
Cancer Growth Metastasis
Cancer Inform
Cardiovasc Thorac Open
Career Dev Transit Except Individ
Cartilage
Cell Med
Cell Transplant
Cephalalgia
Cephalalgia Rep
Child Lang Teach Ther
Child Maltreat
Child Neurol Open
Childhood
Chin J Sociol
China Rep
Chron Respir Dis
Chronic Illn
Chronic Stress (Thousand Oaks)
City Community
Cleft Palate Craniofac J
Clin Case Stud
Clin Child Psychol Psychiatry
Clin EEG Neurosci
Clin Electroencephalogr
Clin Ethics
Clin Med Cardiol
Clin Med Case Rep
Clin Med Circ Respirat Pulm Med
Clin Med Gastroenterol
Clin Med Insights Arthritis Musculoskelet Disord
Clin Med Insights Blood Disord
Clin Med Insights Cardiol
Clin Med Insights Case Rep
Clin Med Insights Circ Respir Pulm Med
Clin Med Insights Ear Nose Throat
Clin Med Insights Endocrinol Diabetes
Clin Med Insights Gastroenterol
Clin Med Insights Oncol
Clin Med Insights Pathol
Clin Med Insights Pediatr
Clin Med Insights Reprod Health
Clin Med Insights Ther
Clin Med Insights Urol
Clin Med Insights Womens Health
Clin Med Oncol
Clin Med Pathol
Clin Med Pediatr
Clin Med Ther
Clin Med Urol
Clin Nurs Res
Clin Pathol
Clin Psychol Sci
Clin Rehabil
Clin Risk
Clin Trials
Commun Disord Q
Community Coll Rev
Comp Polit Stud
Compens Benefits Rev
Compens Rev
Compet Change
Complement Health Pract Rev
Concurr Eng Res Appl
Contact
Contact (Thousand Oaks)
Contemp Drug Probl
Contemp Sociol
Contexts (Berkeley Calif)
Contrib Indian Sociol
Convergence (Lond)
Coop Confl
Cornell Hotel Restaur Adm Q
Couns Psychol
Craniomaxillofac Trauma Reconstr
Creat Nurs
Crim Justice Behav
Crim Justice Policy Rev
Crim Justice Rev
Crime Media Cult
Criminol Crim Justice
Crit Anthropol
Crit Rev Oral Biol Med
Crit Soc Policy
Crit Sociol (Eugene)
Cross Cult Res
Cult Geogr
Cult Psychol
Cult Sociol
Cult Stud Crit Methodol
Curr Bibliogr Afr Aff
Curr Dir Psychol Sci
Curr Sociol
DICP
Dementia
Dementia (London)
Dev Child Welf
Diab Vasc Dis Res
Diabetes Educ
Dialogues Hum Geogr
Digit Health
Discourse Stud
Dose Response
Drug Intell Clin Pharm
Drug Sci Policy Law
Ear Nose Throat J
East Eur Polit Soc
Educ Adm Q
Educ Citizsh Soc Justice
Educ Eval Policy Anal
Educ Policy (Los Altos Calif)
Educ Psychol Meas
Educ Res
Educ Urban Soc
Emerg Adulthood
Emot Rev
Eng Med
Environ Behav
Environ Health Insights
Environ Plan A
Environ Plan B Urban Anal City Sci
Environ Plan D
Environ Plan E Nat Space
Environ Plann B Plann Des
Environ Plann C Gov Policy
Environ Urban
Environ Values
Epigenet Insights
Epilepsy Curr
Ergon Des
Estud Psicol
Ethnicities
Ethnography
Eur Hist Q
Eur J Commun
Eur J Criminol
Eur J Inflamm
Eur J Int Relat
Eur J Mass Spectrom (Chichester)
Eur J Ophthalmol
Eur J Pers
Eur J Political Theory
Eur J Soc Secur
Eur J Womens Stud
Eur Phy Educ Rev
Eur Stroke J
Eur Stud Rev
Eur Union Polit
Eur Urban Reg Stud
Eval Health Prof
Eval J Australas
Eval Q
Eval Rev
Evaluation
Evaluation (Lond)
Evol Bioinform Online
Evol Psychol
Except Child
Exp Biol Med (Maywood)
Expo Times
Fam J Alex Va
Fam Soc
Fem Criminol
Fem Psychol
Fem Rev
Field methods
First Lang
Focus Autism Other Dev Disabl
Food Nutr Bull
Food Sci Technol Int
Foot Ankle
Foot Ankle Int
Foot Ankle Orthop
Foot Ankle Spec
Games Cult
Gazette
Gend Genome
Gene Regul Syst Bio
Genet Epigenet
Genomics Insights
Geriatr Orthop Surg Rehabil
Gerontol Geriatr Med
Gift Child Q
Glob Adv Health Med
Glob Health Promot
Glob Pediatr Health
Glob Qual Nurs Res
Glob Soc Policy
Global Spine J
Group Organ Manag
Group Process Intergroup Relat
HERD
HSS J
Hand
Hand Ther
Health
Health (London)
Health Educ Behav
Health Educ J
Health Educ J (Los Angel)
Health Educ Monogr
Health Educ Q
Health Inf Manag
Health Informatics J
Health Promot Pract
Health Psychol Open
Health Serv Insights
Health Serv Manage Res
Health Serv Res Manag Epidemiol
Healthc Manage Forum
Hip
Hip Int
Hisp Health Care Int
Hisp J Behav Sci
Hist Human Sci
Hist Psychiatry
Hist Sci
Holocene
Home Health Care Manag Pract
Homicide Stud
Hong Kong J Occup Ther
Hosp Pharm
Hum Exp Toxicol
Hum Factors
Hum Relat
Hum Toxicol
Humanity Soc
ICU Dir
Illn Crises Loss
Imagin Cogn Pers
Immunol Immunogenet Insights
Implement Res Pract
Ind Labor Relat Rev
India Q
Indian Econ Soc Hist Rev
Indian Hist Rev
Indian J Gend Stud
Indian J Psychol Med
Indian J Public Adm
Indoor Built Environ
Inf Vis
Infant Child Adolesc Nutr
Infect Dis (Auckl)
Innate Immun
InnovAiT
Innovations
Innovations (Phila)
Inquiry
Inst Child Explor Beyond
Int Commun Gaz
Int Crim Justice Rev
Int J
Int J Adv Robot Syst
Int J Aeroacoust
Int J Aging Hum Dev
Int J Artif Organs
Int J Behav Dev
Int J Billing
Int J Biol Markers
Int J Care Coord
Int J Distrib Sens Netw
Int J Health Serv
Int J High Perform Comput Appl
Int J Immunopathol Pharmacol
Int J Insect Sci
Int J Low Extrem Wounds
Int J Marit Hist
Int J Offender Ther Comp Criminol
Int J Press Polit
Int J Psychiatry Med
Int J Qual Methods
Int J Rob Res
Int J STD AIDS
Int J Soc Psychiatry
Int J Sports Sci Coach
Int J Supercomput Appl
Int J Surg Pathol
Int J Toxicol
Int J Tryptophan Res
Int Migr Rev
Int Q Community Health Educ
Int Reg Sci Rev
Int Rev Qual Res
Int Rev Sociol Sport
Int Rev Vict
Int Sci Rev Ser
Int Soc Work
Int Sociol
Integr Cancer Ther
Integr Med Insights
Interdiscip Sci Rev
Interv Neuroradiol
Interv Sch Clin
Iperception
Ir Econ Soc Hist
Irish Theol Q
J Adolesc Res
J Adv Acad
J Adv Oral Res
J Algorithm Comput Technol
J Am Coll Toxicol
J Am Psychiatr Nurses Assoc
J Am Psychoanal Assoc
J Appl Behav Sci
J Appl Biomater Biomech
J Appl Biomater Funct Mater
J Appl Gerontol
J Appl Soc Sci
J Appl Soc Sci (Boulder)
J Asian Afr Stud
J Assoc Pediatr Oncol Nurses
J Assoc Pers Sev Handicaps
J Asthma Allergy Educ
J Atten Disord
J Bioact Compat Polym
J Biol Rhythms
J Biomater Appl
J Black Psychol
J Black Stud
J Br Menopause Soc
J Brain Dis
J Build Phys
J Bus Tech Commun
J Cardiovasc Pharmacol Ther
J Career Assess
J Career Dev
J Cell Death
J Cent Nerv Syst Dis
J Chem Res
J Child Health Care
J Child Orthop
J Clin Urol
J Cogn Eng Decis Mak
J Coll Stud Ret
J Commonw Lit
J Commun Inq
J Comorb
J Compos Mater
J Concussion
J Conflict Resolut
J Contemp Crim Justice
J Contemp Ethnogr
J Contemp Hist
J Cross Cult Psychol
J Curr Chin Aff
J Cutan Med Surg
J Dance Med Sci
J Dev Soc
J Diabetes Sci Technol
J Diagn Med Sonogr
J Disabil Policy Stud
J Drug Educ
J Drug Issues
J Early Adolesc
J Early Child Res
J Early Interv
J Educ (Boston)
J Educ Behav Stat
J Emot Behav Disord
J Empir Res Hum Res Ethics
J Endometr
J Endometr Pelvic Pain Disord
J Endotoxin Res
J Endovasc Ther
J Eng Linguist
J Environ Dev
J Ethnobiol
J Eur Soc Policy
J Eur Stud
J Evid Based Complementary Altern Med
J Evid Based Integr Med
J Except Child
J Exp Neurosci
J Exp Psychopathol
J Fam Hist
J Fam Issues
J Fam Nurs
J Feline Med Surg
J Fire Sci
J Generic Med
J Geriatr Psychiatry Neurol
J Hand Surg Br
J Hand Surg Eur Vol
J Health Manag
J Health Psychol
J Health Serv Res Policy
J Health Soc Behav
J Hispanic High Educ
J Histochem Cytochem
J Holist Nurs
J Humanist Psychol
J ICRU
J Inborn Errors Metab Screen
J Ind Relat
J Indian Orthod Soc
J Inf Sci
J Infect Prev
J Int Assoc Physicians AIDS Care (Chic)
J Int Assoc Provid AIDS Care
J Int Med Res
J Intell Mater Syst Struct
J Intellect Disabil
J Intensive Care Med
J Intensive Care Soc
J Inter Des
J Interpers Violence
J Investig Med High Impact Case Rep
J Lab Autom
J Lang Soc Psychol
J Leadersh Organ Stud
J Learn Disabil
J Libr
J Lit Res
J Manage
J Mark Res
J Med Biogr
J Med Educ Curric Dev
J Med Screen
J Mens Stud
J Migr Hum Secur
J Mix Methods Res
J Near Infrared Spectrosc
J Off Stat
J Oncol Pharm Pract
J Orthod
J Orthop Surg (Hong Kong)
J Otolaryngol Head Neck Surg
J Palliat Care
J Pastoral Care
J Pastoral Care Counsel
J Patient Exp
J Patient Saf Risk Manag
J Peace Res
J Pediatr Oncol Nurs
J Pediatr Surg Nurs
J Perioper Pract
J Pharm Pract
J Pharm Technol
J Pharmacol Pharmacother
J Plan Educ Res
J Plan Hist
J Plan Lit
J Posit Behav Interv
J Prev Health Promot
J Prim Care Community Health
J Psoriasis Psoriatic Arthritis
J Psychiatry Law
J Psychoeduc Assess
J Psychol Couns Sch
J Psychol Theol
J Psychopharmacol
J Public Health Res
J Public Policy Mark
J R Coll Physicians Edinb
J R Sanit Inst
J R Soc Health
J R Soc Med
J R Soc Promot Health
J Rehabil Assist Technol Eng
J Res Crime Delinq
J Res Nurs
J Sch Leadersh
J Sch Nurs
J Scleroderma Relat Disord
J Serv Res
J Shoulder Elb Arthroplast
J Soc Pers Relat
J Soc Work (Lond)
J Sociol (Melb)
J Spec Educ
J Spec Educ Technol
J Sport Soc Issues
J Sports Econom
J Sports Med
J Strain Anal Eng Des
J Stud Int Educ
J Study New Testam
J Teach Educ
J Telemed Telecare
J Theor Polit
J Tissue Eng
J Transcult Nurs
J Travel Res
J Urban Hist
J Vasc Access
J Vet Dent
J Vet Diagn Invest
J Vib Control
J Vis Impair Blind
J Vitreoretin Dis
J Volunt Action Res
J Wilderness Med
JALA Charlottesv Va
JDR Clin Trans Res
JFMS Open Rep
JRSM Cardiovasc Dis
JRSM Open
JRSM Short Rep
Journal Mass Commun Q
Journal Q
Journalism (Lond)
Jpn Clin Med
Justice Res Policy
Lab Anim
Labor Stud J
Lang Lit (Harlow)
Lang Speech
Lat Am Perspect
Leadership (Lond)
Learn Disabil Q
Learn Disabil Res Pract
Light Res Technol
Linacre Q
Lipid Insights
Lit Research
Local Econ
MDM Policy Pract
Maastrich J Eur Comp Law
Magn Reson Insights
Manag Commun Q
Manag Learn
Margin J Appl Econ Res
Math Mech Solids
Med Care Res Rev
Med Care Rev
Med Decis Making
Med Leg Criminol Rev
Med Leg J
Med Sci Law
Media Cult Soc
Mem Stud
Men Masc
Menopause Int
Method Innov
Microbiol Insights
Migr Dev
Mob Media Commun
Mod China
Mol Imaging
Mol Pain
Mult Scler
Mult Scler J Exp Transl Clin
Music Sci
Music Sci (Lond)
NASN Sch Nurse
NATNEWS
Nanobiomedicine (Rij)
Nasnewsletter
Nat Prod Commun
Neuro
Neurohospitalist
Neuroradiol J
Neurorehabil Neural Repair
Neurosci Insights
Neuroscientist
New Media Soc
New Solut
Newsl Sci Technol Human Values
Newsp Res J
Nonlinearity Biol Toxicol Med
Nonprofit Volunt Sect Q
Nord J Nurs Res
Nordisk Alkohol Nark
Nucl Recept Signal
Nurs Ethics
Nurs Sci Q
Nutr Health
Nutr Metab Insights
OTJR (Thorofare N J)
Obstet Med
Occup Health Nurs
Omega
Omega (Westport)
Open J Cardiovasc Surg
Ophthalmol Eye Dis
Organ Environ
Organ Res Methods
Orthop J Sports Med
Outlook Agric
Pacifica
Palliat Care
Palliat Care Soc Pract
Palliat Med
Party Politics
Pathol Vet
Pedagogy Health Promot
Percept Mot Skills
Perception
Perfusion
Perit Dial Int
Pers Soc Psychol Bull
Pers Soc Psychol Rev
Perspect Medicin Chem
Perspect Psychol Sci
Perspect Public Health
Perspect Vasc Surg Endovasc Ther
Phi Delta Kappan
Philos Soc Crit
Philos Soc Sci
Phlebology
Plast Surg (Oakv)
Pleura (Thousand Oaks)
Police J
Police Q
Policy Insights Behav Brain Sci
Policy Polit Nurs Pract
Polit Philos Econ
Polit Res Q
Polit Soc
Polit Stud (Oxf)
Polit Theory
Post Reprod Health
Prim Dent J
Prison J
Proc Hum Factors Ergon Soc Annu Meet
Proc Inst Mech Eng B J Eng Manuf
Proc Inst Mech Eng C J Mech Eng Sci
Proc Inst Mech Eng F J Rail Rapid Transit
Proc Inst Mech Eng H
Proc Inst Mech Eng O J Risk Reliab
Proc Inst Mech Eng P J Sport Eng Technol
Proc Int Symp Hum Factors Ergon Healthc
Prod Oper Manag
Prog Hum Geogr
Prog Phys Geogr
Prog Transplant
Promot Educ
Proteomics Insights
Psychol Music
Psychol Rep
Psychol Sci
Psychol Sci Public Interest
Psychol Women Q
Psychopathol Rev
Public Finan Q
Public Finance Rev
Public Health Rep
Public Pers Manage
Public Policy Adm
Public Underst Sci
Punishm Soc
Q J Exp Psychol
Q J Exp Psychol (Hove)
Q J Exp Psychol A
Q J Exp Psychol B
Qual Assur Util Rev
Qual Health Res
Qual Inq
Qual Res
Qual Soc Work
R Soc Health J
Race Cl
Race Justice
Rare Tumors
Rehabil Couns Bull
Remedial Spec Educ
Res Aging
Res Comp Int Educ
Res Ethics
Res Pract Persons Severe Disabl
Res Soc Work Pract
Rev Black Polit Econ
Rev Educ Res
Rev Gen Psychol
Rev Hum Factors Ergon
Rev Pain
Rev Psicol Soc
Rev Public Pers Adm
Rev Radic Polit Econ
Rev Relig Res
S Afr J Psychol
SAGE Open Med
SAGE Open Med Case Rep
SAGE Open Nurs
Sage Open
Scand J Public Health
Scand J Public Health Suppl
Scand J Soc Med
Scand J Surg
Scars Burn Heal
Sch Psychol Int
Sci Commun
Sci Prog
Sci Technol Human Values
Scott Med J
Second Lang Res
Secur Dialogue
Semin Cardiothorac Vasc Anesth
Semin Laparosc Surg
Sex Abuse
Sexualities
Shoulder Elbow
Sign Transduct Insights
Simul Games
Simulation
Small Group Res
Soc Compass
Soc Curr
Soc Mar Q
Soc Media Soc
Soc Ment Health
Soc Psychol Personal Sci
Soc Psychol Q
Soc Sci Inf (Paris)
Soc Stud Sci
Sociol Bull
Sociol Educ
Sociol Methodol
Sociol Methods Res
Sociol Perspect
Sociol Race Ethn (Thousand Oaks)
Sociol Res Online
Sociol Rev
Sociol Rev Monogr
Sociol Theory
Sociol Work Occup
Sociology
Socius
South Asia Res
Space Cult
Sports Health
Stat Methods Med Res
Stat Modelling
Stata J
Strateg Organ
Struct Health Monit
Stud Christ Ethics
Stud Hist (Sahibabad)
Stud Relig
Subst Abus
Subst Abuse
Surg Innov
Teach Coll Rec (1970)
Teach Educ Spec Educ
Teach Except Child
Teach Psychol
Teach Sociol
Technol Cancer Res Treat
Text Res J
Theol Today
Theology
Theor Criminol
Theory Cult Soc
Theory Res Educ
Ther Adv Cardiovasc Dis
Ther Adv Chronic Dis
Ther Adv Drug Saf
Ther Adv Endocrinol Metab
Ther Adv Gastrointest Endosc
Ther Adv Hematol
Ther Adv Infect Dis
Ther Adv Med Oncol
Ther Adv Musculoskelet Dis
Ther Adv Neurol Disord
Ther Adv Ophthalmol
Ther Adv Psychopharmacol
Ther Adv Reprod Health
Ther Adv Respir Dis
Ther Adv Urol
Ther Adv Vaccines
Ther Adv Vaccines Immunother
Therap Adv Gastroenterol
Time Soc
Tob Use Insights
Topics Early Child Spec Educ
Tour Stud
Toxicol Ind Health
Toxicol Pathol
Transcult Psychiatry
Transfer (Bruss)
Transp Res Rec
Trauma Violence Abuse
Trends Amplif
Trends Hear
Trop Doct
Ultrason Imaging
Ultrasound
Update
Urban Aff Q
Urban Aff Rev Thousand Oaks Calif
Urban Educ (Beverly Hills Calif)
Urban Stud
Urologia
Vard Nord Utveckl Forsk
Vasc Endovascular Surg
Vasc Surg
Vascular
Vet Pathol
Vikalpa
Violence Against Women
Virology (Auckl)
War Hist
Waste Manag Res
West J Nurs Res
Womens Health (Lond)
Work Employ Soc
Work Occup
Workplace Health Saf
World Futures Rev
World J Pediatr Congenit Heart Surg
Writ Commun
Young
Youth Soc
Youth Violence Juv Justice
"""
