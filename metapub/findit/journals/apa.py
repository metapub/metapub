# American Psychological Association (APA)
# 
# psycnet.apa.org
#
# The American Psychological Association is the leading scientific and professional 
# organization representing psychology in the United States. APA publishes many 
# prestigious journals in psychology and related fields.
#
# URL Pattern:
#   - Articles are hosted on PsycNET: https://psycnet.apa.org/
#   - DOI pattern typically: 10.1037/[journal-code][year]-[issue]-[article]
#   - PDF access may require subscription or institutional access
#
# Notes:
#   - Many APA journals are subscription-based
#   - Some content may be freely available after embargo periods
#   # Articles indexed in PubMed with PMIDs
#   - DOI resolution typically redirects to PsycNET

# APA journals identified from categorized_unknown_journals.txt analysis
# NOTE: This list includes journals clearly published by APA based on psycnet.apa.org domain
# Some journals in the original domain list may belong to other publishers sharing the platform

apa_journals = [
    # Core APA Psychology Journals
    'Am Psychol',                                       # American Psychologist
    'Behav Neurosci',                                   # Behavioral Neuroscience
    'Can J Exp Psychol',                                # Canadian Journal of Experimental Psychology
    'Can J Psychol',                                    # Canadian Journal of Psychology
    'Can Psychol',                                      # Canadian Psychology
    'Clin Pract Pediatr Psychol',                      # Clinical Practice in Pediatric Psychology
    'Clin Psychol',                                     # Clinical Psychology: Science and Practice
    'Consult Psychol J',                                # Consulting Psychology Journal: Practice and Research
    'Couple Family Psychol',                           # Couple and Family Psychology: Research and Practice
    'Cult Divers Ment Health',                         # Cultural Diversity and Mental Health
    'Cultur Divers Ethnic Minor Psychol',              # Cultural Diversity and Ethnic Minority Psychology
    'Decision (Wash D C)',                              # Decision
    'Dev Psychol',                                      # Developmental Psychology
    'Emotion',                                          # Emotion
    'Evol Behav Sci',                                   # Evolutionary Behavioral Sciences
    'Exp Clin Psychopharmacol',                        # Experimental and Clinical Psychopharmacology
    'Fam Syst Health',                                  # Families, Systems, & Health
    'Health Psychol',                                   # Health Psychology
    'Hist Psychol',                                     # History of Psychology
    'J Abnorm Psychol',                                 # Journal of Abnormal Psychology
    'J Appl Psychol',                                   # Journal of Applied Psychology
    'J Appl Res Mem Cogn',                            # Journal of Applied Research in Memory and Cognition
    'J Comp Psychol',                                   # Journal of Comparative Psychology
    'J Consult Clin Psychol',                          # Journal of Consulting and Clinical Psychology
    'J Couns Psychol',                                  # Journal of Counseling Psychology
    'J Divers High Educ',                              # Journal of Diversity in Higher Education
    'J Educ Psychol',                                   # Journal of Educational Psychology
    'J Exp Psychol Anim Learn Cogn',                   # Journal of Experimental Psychology: Animal Learning and Cognition
    'J Exp Psychol Appl',                              # Journal of Experimental Psychology: Applied
    'J Exp Psychol Gen',                               # Journal of Experimental Psychology: General
    'J Exp Psychol Hum Percept Perform',               # Journal of Experimental Psychology: Human Perception and Performance
    'J Exp Psychol Learn Mem Cogn',                    # Journal of Experimental Psychology: Learning, Memory, and Cognition
    'J Fam Psychol',                                    # Journal of Family Psychology
    'J Lat Psychol',                                    # Journal of Latina/o Psychology
    'J Neurosci Psychol Econ',                         # Journal of Neuroscience, Psychology, and Economics
    'J Occup Health Psychol',                          # Journal of Occupational Health Psychology
    'J Pers Soc Psychol',                              # Journal of Personality and Social Psychology
    'J Psychother Integr',                             # Journal of Psychotherapy Integration
    'Law Hum Behav',                                    # Law and Human Behavior
    'Motiv Sci',                                        # Motivation Science
    'Peace Confl',                                      # Peace and Conflict: Journal of Peace Psychology
    'Personal Disord',                                  # Personality Disorders: Theory, Research, and Treatment
    'Pract Innov (Wash D C)',                          # Practice Innovations
    'Prof Psychol Res Pr',                             # Professional Psychology: Research and Practice
    'Psychiatr Rehabil J',                             # Psychiatric Rehabilitation Journal
    'Psychoanal Psychol',                              # Psychoanalytic Psychology
    'Psychol Addict Behav',                            # Psychology of Addictive Behaviors
    'Psychol Aesthet Creat Arts',                      # Psychology of Aesthetics, Creativity, and the Arts
    'Psychol Aging',                                    # Psychology and Aging
    'Psychol Assess',                                   # Psychological Assessment
    'Psychol Bull',                                     # Psychological Bulletin
    'Psychol Conscious (Wash D C)',                    # Psychology of Consciousness: Theory, Research, and Practice
    'Psychol Men Masc',                                # Psychology of Men & Masculinities
    'Psychol Methods',                                  # Psychological Methods
    'Psychol Neurosci',                                # Psychology & Neuroscience
    'Psychol Pop Media Cult',                          # Psychology of Popular Media Culture
    'Psychol Rev',                                      # Psychological Review
    'Psychol Serv',                                     # Psychological Services
    'Psychol Sex Orientat Gend Divers',                # Psychology of Sexual Orientation and Gender Diversity
    'Psychol Trauma',                                   # Psychological Trauma: Theory, Research, Practice, and Policy
    'Psychol Violence',                                 # Psychology of Violence
    'Psycholog Relig Spiritual',                       # Psychology of Religion and Spirituality
    'Psychomusicology',                                # Psychomusicology: Music, Mind, and Brain
    'Psychosoc Rehabil J',                             # Psychosocial Rehabilitation Journal
    'Psychotherapy',                                    # Psychotherapy
    'Qual Psychol',                                     # Qualitative Psychology
    'Rehabil Psychol',                                  # Rehabilitation Psychology
    'Rural Ment Health',                               # Journal of Rural Mental Health
    'Sch Psychol',                                      # School Psychology International
    'Sch Psychol Q',                                    # School Psychology Quarterly
    'Scholarsh Teach Learn Psychol',                   # Scholarship of Teaching and Learning in Psychology
    'Spiritual Clin Pract',                            # Spirituality in Clinical Practice
    'Sport Exerc Perform Psychol',                     # Sport, Exercise, and Performance Psychology
    'Stigma Health',                                    # Stigma and Health
    'Train Educ Prof Psychol',                         # Training and Education in Professional Psychology
    'Transl Issues Psychol Sci',                       # Translational Issues in Psychological Science
    'Traumatology',                                     # Traumatology
    
    # Behavior Analysis Journals (also published by APA)
    'Behav Anal (Wash D C)',                           # Behavior Analysis in Practice
    'Behav Anal Today',                                # Behavior Analysis Today
    'Behav Dev Bull',                                   # Behavior Development Bulletin
    'J Behav Anal Health Sports Fit Med',              # Journal of Behavioral Analysis of Health, Sports, Fitness and Medicine
    'J Early Intensive Behav Interv',                  # Journal of Early and Intensive Behavior Intervention
    
    # Historical/Legacy Journals
    'Am J Orthopsychiatry',                            # American Journal of Orthopsychiatry  
    'Fam Syst Med',                                     # Family Systems Medicine (now Family Systems & Health)
    'J Abnorm Soc Psychol',                            # Journal of Abnormal and Social Psychology (historical)
    'J Consult Psychol',                               # Journal of Consulting Psychology (historical)
    'J Exp Psychol',                                    # Journal of Experimental Psychology (historical, now split)
    'J Exp Psychol Anim Behav Process',                # Journal of Experimental Psychology: Animal Behavior Processes
    'Psychol Monogr',                                   # Psychological Monographs (historical)
]