"""
OAText Publishing journal list.

OAText is an open access academic publisher specializing in medical, 
scientific, and healthcare journals. They publish peer-reviewed journals
across various medical and scientific disciplines.

URL format: https://www.oatext.com/[article-title].php
Alternative: https://oatext.com/pdf/[JOURNAL_CODE]-[VOLUME]-[ARTICLE_ID].pdf

DOI patterns: Various (need to determine specific patterns)
"""

# OAText journals from oatext.com cluster (41 journals)
oatext_journals = (
    'J Syst Integr Neurosci',                           # Journal of Systems and Integrative Neuroscience
    'Clin Case Rep Rev',                                # Clinical Case Reports and Reviews
    'HMO',                                              # HMO (specific journal)
    'Health Educ Care',                                 # Health Education and Care
    'Integr Cancer Sci Ther',                          # Integrative Cancer Science and Therapy
    'Clin Res Trials',                                 # Clinical Research and Trials
    'Integr Mol Med',                                   # Integrative Molecular Medicine
    'Integr Obes Diabetes',                            # Integrative Obesity and Diabetes
    'Prev Med Community Health',                        # Preventive Medicine and Community Health
    'Front Womens Health',                              # Frontiers in Women's Health
    'Pulm Crit Care Med',                              # Pulmonary and Critical Care Medicine
    'New Front Ophthalmol',                            # New Frontiers in Ophthalmology
    'J Integr Cardiol',                                # Journal of Integrative Cardiology
    'Transl Brain Rhythm',                             # Translational Brain Rhythmicity
    'Pediatr Dimens',                                  # Pediatric Dimensions
    'Glob Vaccines Immunol',                           # Global Vaccines and Immunology
    'Biomed Genet Genom',                              # Biomedical Genetics and Genomics
    'Glob Surg',                                       # Global Surgery
    'Biomed Res Rev',                                  # Biomedical Research and Reviews
    'Integr Food Nutr Metab',                          # Integrative Food, Nutrition and Metabolism
    'Dent Oral Craniofac Res',                         # Dental, Oral and Craniofacial Research
    'Forensic Sci Criminol',                           # Forensic Science and Criminology
    'Biol Eng Med',                                    # Biological Engineering Medicine
    'Ment Health Addict Res',                          # Mental Health and Addiction Research
    'Trends Diabetes Metab',                           # Trends in Diabetes and Metabolism
    'Trends Res',                                      # Trends in Research
    'Anaesth Anaesth',                                 # Anaesthesia & Anaesthesia (sic)
    'Glob Imaging Insights',                           # Global Imaging Insights
    'Clin Microbiol Infect Dis',                      # Clinical Microbiology and Infectious Diseases
    'Med Res Innov',                                   # Medical Research and Innovation
    'Pharmacol Drug Dev Ther',                         # Pharmacology, Drug Development and Therapy
    'Glob Drugs Ther',                                 # Global Drugs and Therapeutics
    'Cancer Rep Rev',                                  # Cancer Reports and Reviews
    'Glob Anesth Perioper Med',                        # Global Anesthesia and Perioperative Medicine
    'Integr Clin Med',                                 # Integrative Clinical Medicine
    'Nucl Med Biomed Imaging',                         # Nuclear Medicine and Biomedical Imaging
    'Contemp Behav Health Care',                       # Contemporary Behavioral Health Care
    'Otorhinolaryngol Head Neck Surg',                # Otorhinolaryngology and Head & Neck Surgery
    'Hematol Med Oncol',                               # Hematology and Medical Oncology
    'Trauma Emerg Care',                               # Trauma and Emergency Care
    'Biomed Res Clin Pract',                          # Biomedical Research and Clinical Practice
)

# OAText URL format - will need to determine the exact pattern
oatext_format = 'https://www.oatext.com/pdf/{article_id}.pdf'