"""
Allen Press journal list.

Allen Press is a scholarly publishing services company that partners with
scholarly and professional societies to publish their journals and books.
They provide publishing services for journals in medicine, science, education,
and other academic fields.

URL format: https://meridian.allenpress.com/[journal-code]/article-pdf/{doi}
Alternative: https://meridian.allenpress.com/[journal-code]/article/{doi}

DOI patterns: Various (depends on the society/journal)
"""

# Allen Press journals from meridian.allenpress.com cluster (39 journals)
allenpress_journals = (
    'Ment Retard',                                      # Mental Retardation (historical name)
    'Oper Dent',                                        # Operative Dentistry
    'J Am Anim Hosp Assoc',                             # Journal of the American Animal Hospital Association
    'Earth Sci Hist',                                   # Earth Sciences History
    'Am J Ment Retard',                                 # American Journal on Mental Retardation (historical)
    'Appl Anthropol',                                   # Applied Anthropology
    'Am J Intellect Dev Disabil',                       # American Journal on Intellectual and Developmental Disabilities
    'Am Indian Cult Res J',                             # American Indian Culture and Research Journal
    'Am Arch',                                          # American Archaeology
    'Harv Educ Rev',                                    # Harvard Educational Review
    'J Insur Med',                                      # Journal of Insurance Medicine
    'Tex Heart Inst J',                                 # Texas Heart Institute Journal
    'Ethn Dis',                                         # Ethnicity & Disease
    'J Oral Implantol',                                 # Journal of Oral Implantology
    'J Am Mosq Control Assoc',                          # Journal of the American Mosquito Control Association
    'J Grad Med Educ',                                  # Journal of Graduate Medical Education
    'J Pediatr Pharmacol Ther',                         # Journal of Pediatric Pharmacology and Therapeutics
    'Hum Organ',                                        # Human Organization
    'Int Surg',                                         # International Surgery
    'J Chiropr Educ',                                   # Journal of Chiropractic Education
    'Biophysicist (Rockv)',                             # The Biophysicist
    'J Immunother Precis Oncol',                        # Journal for ImmunoTherapy of Cancer: Precision Oncology
    'Inclusion (Wash)',                                 # Inclusion
    'Top Spinal Cord Inj Rehabil',                      # Topics in Spinal Cord Injury Rehabilitation
    'Intellect Dev Disabil',                            # Intellectual and Developmental Disabilities
    'Pract Anthropol',                                  # Practical Anthropology
    'Int J MS Care',                                    # International Journal of MS Care
    'Wildl Dis',                                        # Wildlife Disease (historical)
    'Ment Health Clin',                                 # Mental Health Clinician
    'J Clin Exerc Physiol',                             # Journal of Clinical Exercise Physiology
    'Arch Pathol Lab Med',                              # Archives of Pathology & Laboratory Medicine
    'J Athl Train',                                     # Journal of Athletic Training
    'Angle Orthod',                                     # The Angle Orthodontist
    'Adv Pulm Hypertens',                               # Advances in Pulmonary Hypertension
    'Int J Yoga Therap',                                # International Journal of Yoga Therapy
    'J Ment Health Couns',                              # Journal of Mental Health Counseling
    'Mobilization',                                     # Mobilization
    'Tire Sci Technol',                                 # Tire Science and Technology
    'J Med Regul',                                      # Journal of Medical Regulation
)

# Allen Press URL format - will need to determine specific journal codes
allenpress_format = 'https://meridian.allenpress.com/{journal_code}/article-pdf/{doi}'