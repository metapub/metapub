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
dovepress_journals = (
    'Adolesc Health Med Ther',                              # Adolescent Health, Medicine and Therapeutics
    'Adv Appl Bioinform Chem',                             # Advances and Applications in Bioinformatics and Chemistry
    'Adv Med Educ Pract',                                  # Advances in Medical Education and Practice
    # 'Biologics',                                          # Biologics: Targets and Therapy (need to verify)
    # 'Blood Lymphat Cancer',                               # Blood and Lymphatic Cancer: Targets and Therapy (need to verify)
    'Breast Cancer (Dove Med Press)',                      # Breast Cancer: Targets and Therapy
    'Cancer Manag Res',                                    # Cancer Management and Research
    'Chronic Wound Care Management Res',                   # Chronic Wound Care Management and Research
    'Clin Exp Gastroenterol',                             # Clinical and Experimental Gastroenterology
    'Clin Epidemiol',                                      # Clinical Epidemiology
    'Clin Interv Aging',                                  # Clinical Interventions in Aging
    'Clin Ophthalmol',                                     # Clinical Ophthalmology
    'Clin Optom (Auckl)',                                 # Clinical Optometry
    'Clin Pharmacol',                                      # Clinical Pharmacology: Advances and Applications
    'Clin Cosmet Investig Dent',                          # Clinical, Cosmetic and Investigational Dentistry
    'Clin Cosmet Investig Dermatol',                      # Clinical, Cosmetic and Investigational Dermatology
    'Clinicoecon Outcomes Res',                           # ClinicoEconomics and Outcomes Research
    'Degener Neurol Neuromuscul Dis',                     # Degenerative Neurological and Neuromuscular Disease
    'Diabetes Metab Syndr Obes',                          # Diabetes, Metabolic Syndrome and Obesity
    'Drug Des Devel Ther',                                # Drug Design, Development and Therapy
    'Drug Healthc Patient Saf',                           # Drug, Healthcare and Patient Safety
    'Eye Brain',                                          # Eye and Brain
    'Hepat Med',                                          # Hepatic Medicine: Evidence and Research
    'HIV AIDS (Auckl)',                                   # HIV/AIDS - Research and Palliative Care
    'Immunotargets Ther',                                 # ImmunoTargets and Therapy
    'Infect Drug Resist',                                 # Infection and Drug Resistance
    'Integr Pharm Res Pract',                            # Integrated Pharmacy Research and Practice
    'Int J Chron Obstruct Pulmon Dis',                   # International Journal of Chronic Obstructive Pulmonary Disease
    'Int J Gen Med',                                      # International Journal of General Medicine
    'Int J Nanomedicine',                                 # International Journal of Nanomedicine
    'Int J Nephrol Renovasc Dis',                        # International Journal of Nephrology and Renovascular Disease
    'Int J Womens Health',                                # International Journal of Women's Health
    'Int Med Case Rep J',                                 # International Medical Case Reports Journal
    'J Asthma Allergy',                                   # Journal of Asthma and Allergy
    'J Blood Med',                                        # Journal of Blood Medicine
    'J Exp Pharmacol',                                    # Journal of Experimental Pharmacology
    'J Healthc Leadersh',                                 # Journal of Healthcare Leadership
    'J Hepatocell Carcinoma',                            # Journal of Hepatocellular Carcinoma
    'J Inflamm Res',                                      # Journal of Inflammation Research
    'J Multidiscip Healthc',                             # Journal of Multidisciplinary Healthcare
    'J Pain Res',                                         # Journal of Pain Research
    'Local Reg Anesth',                                   # Local and Regional Anesthesia
    'Lung Cancer (Auckl)',                               # Lung Cancer: Targets and Therapy
    'Med Devices (Auckl)',                               # Medical Devices: Evidence and Research
    'Nanotechnol Sci Appl',                              # Nanotechnology, Science and Applications
    'Nat Sci Sleep',                                      # Nature and Science of Sleep
    'Neuropsychiatr Dis Treat',                          # Neuropsychiatric Disease and Treatment
    'Nurs Res Rev',                                       # Nursing: Research and Reviews
    'Nutr Diet Suppl',                                    # Nutrition and Dietary Supplements
    'Onco Targets Ther',                                  # OncoTargets and Therapy
    'Open Access Emerg Med',                              # Open Access Emergency Medicine
    'Open Access J Clin Trials',                         # Open Access Journal of Clinical Trials
    'Open Access J Contracept',                          # Open Access Journal of Contraception
    'Open Access J Sports Med',                          # Open Access Journal of Sports Medicine
    'Open Access Rheumatol',                             # Open Access Rheumatology: Research and Reviews
    'Orthop Res Rev',                                     # Orthopedic Research and Reviews
    'Patient Prefer Adherence',                           # Patient Preference and Adherence
    'Patient Relat Outcome Meas',                        # Patient Related Outcome Measures
    'Pediatr Health Med Ther',                           # Pediatric Health, Medicine and Therapeutics
    'Pharmacogenomics Pers Med',                         # Pharmacogenomics and Personalized Medicine
    'Pragmat Obs Res',                                    # Pragmatic and Observational Research
    'Psoriasis (Auckl)',                                 # Psoriasis: Targets and Therapy
    'Psychol Res Behav Manag',                           # Psychology Research and Behavior Management
    'Res Rep Trop Med',                                   # Research and Reports in Tropical Medicine
    'Res Rep Urol',                                       # Research and Reports in Urology
    'Res Rep Clin Cardiol',                              # Research Reports in Clinical Cardiology
    'Risk Manag Healthc Policy',                         # Risk Management and Healthcare Policy
    'Stem Cells Cloning',                                # Stem Cells and Cloning: Advances and Applications
    'Subst Abuse Rehabil',                               # Substance Abuse and Rehabilitation
    'Appl Clin Genet',                                   # The Application of Clinical Genetics
    'Ther Clin Risk Manag',                              # Therapeutics and Clinical Risk Management
    'Vasc Health Risk Manag',                            # Vascular Health and Risk Management
    'Vet Med (Auckl)'                                     # Veterinary Medicine: Research and Reports
)