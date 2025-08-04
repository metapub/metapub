# Emerald Publishing
# 
# emerald.com
#
# Emerald Publishing is a digital-first publisher of management, business,
# education, library science, information management research, and health care journals.
# Founded in 1967, it publishes over 300 journals and more than 2,500 books.
#
# URL Pattern:
#   - Article view: https://www.emerald.com/insight/content/doi/[DOI]/full/html
#   - PDF download: https://www.emerald.com/insight/content/doi/[DOI]/full/pdf
#
# DOI Pattern:
#   - 10.1108/[JOURNAL_CODE]-[DATE]-[ID]
#
# Notes:
#   - Many articles are behind paywall but some are open access
#   - Articles are indexed in PubMed with PMIDs
#   - DOI resolution typically redirects to article pages
#   - PDF access requires subscription or institutional access

# URL format template - will be used in the dance function
emerald_format = 'https://www.emerald.com/insight/content/doi/{doi}/full/pdf'

# Complete list of Emerald journals (68 total)
# NOTE: Using PubMed abbreviated journal names to match PMA data
emerald_journals = (
    'Adv Dual Diagn',                                       # Advances in Dual Diagnosis
    'Adv Group Process',                                    # Advances in Group Processes
    'Adv Health Care Manag',                               # Advances in Health Care Management
    'Adv Health Econ Health Serv Res',                     # Advances in Health Economics and Health Services Research
    'Adv Med Sociol',                                      # Advances in Medical Sociology
    'Adv Ment Health Intellect Disabil',                   # Advances in Mental Health and Intellectual Disabilities
    'Adv Motiv Achiev',                                    # Advances in Motivation and Achievement
    'Aslib Proc',                                          # Aslib Proceedings
    'Br Food J',                                           # British Food Journal
    'Clin Gov',                                            # Clinical Governance
    'Digit Libr Perspect',                                 # Digital Library Perspectives
    'Drugs Alcohol Today',                                 # Drugs and Alcohol Today
    'Eng Comput (Swansea)',                               # Engineering Computations
    'Ethn Inequal Health Soc Care',                       # Ethnicity and Inequalities in Health and Social Care
    'Eur J Mark',                                          # European Journal of Marketing
    'Gend Manag',                                          # Gender in Management
    'Health Manpow Manage',                                # Health Manpower Management
    'Ind Rob',                                             # Industrial Robot
    'Inf Discov Deliv',                                    # Information Discovery and Delivery
    'Int J Clim Chang Strateg Manag',                      # International Journal of Climate Change Strategies and Management
    'Int J Disaster Resil Built Environ',                  # International Journal of Disaster Resilience in the Built Environment
    'Int J Health Care Qual Assur',                        # International Journal of Health Care Quality Assurance
    'Int J Health Care Qual Assur Inc Leadersh Health Serv', # International Journal of Health Care Quality Assurance Inc Leadership in Health Services
    'Int J Hum Rights Healthc',                            # International Journal of Human Rights in Healthcare
    'Int J Manpow',                                        # International Journal of Manpower
    'Int J Migr Health Soc Care',                          # International Journal of Migration, Health and Social Care
    'Int J Numer Methods Heat Fluid Flow',                 # International Journal of Numerical Methods for Heat and Fluid Flow
    'Int J Pharm Healthc Mark',                            # International Journal of Pharmaceutical and Healthcare Marketing
    'Int J Prison Health',                                 # International Journal of Prison Health
    'Int J Soc Econ',                                      # International Journal of Social Economics
    'Int J Sociol Soc Policy',                             # International Journal of Sociology and Social Policy
    'Int J Workplace Health Manag',                        # International Journal of Workplace Health Management
    'J Aggress Confl Peace Res',                          # Journal of Aggression, Conflict and Peace Research
    'J Agribus Dev Emerg Econ',                           # Journal of Agribusiness in Developing and Emerging Economies
    'J Assist Technol',                                    # Journal of Assistive Technologies
    'J Bus Strategy',                                      # Journal of Business Strategy
    'J Child Serv',                                        # Journal of Children's Services
    'J Consum Mark',                                       # Journal of Consumer Marketing
    'J Crim Psychol',                                      # Journal of Criminal Psychology
    'J Doc',                                               # Journal of Documentation
    'J Econ Stud',                                         # Journal of Economic Studies
    'J Enabling Technol',                                  # Journal of Enabling Technologies
    'J Financ Crime',                                      # Journal of Financial Crime
    'J Health Organ Manag',                               # Journal of Health Organization and Management
    'J Integr Care (Brighton)',                           # Journal of Integrated Care
    'J Intellect Disabil Offending Behav',                # Journal of Intellectual Disabilities and Offending Behaviour
    'J Manag Med',                                         # Journal of Management in Medicine
    'J Public Ment Health',                               # Journal of Public Mental Health
    'J Qual Maint Eng',                                   # Journal of Quality in Maintenance Engineering
    'J Soc Mark',                                          # Journal of Social Marketing
    'J Workplace Learn',                                   # Journal of Workplace Learning
    'Leadersh Health Serv (Bradf Engl)',                  # Leadership in Health Services
    'Libr Rev (Lond)',                                     # Library Review
    'Ment Health Rev (Brighton)',                          # Mental Health Review Journal
    'Ment Illn',                                           # Mental Illness
    'Nutr Food Sci',                                       # Nutrition & Food Science
    'Policing',                                            # Policing
    'Qual Ageing',                                         # Quality Ageing
    'Qual Ageing Older Adults',                           # Quality Ageing and Older Adults
    'Rapid Prototyp J',                                    # Rapid Prototyping Journal
    'Ref Serv Rev',                                        # Reference Services Review
    'Res Econ Inequal',                                    # Research in Economic Inequality
    'Res Sociol Educ',                                     # Research in Sociology of Education
    'Res Sociol Health Care',                              # Research in the Sociology of Health Care
    'Res Sociol Work',                                     # Research in the Sociology of Work
    'Sociol Stud Child Youth',                            # Sociological Studies of Children and Youth
    'Ther Communities',                                     # Therapeutic Communities
    'Work Older People',                                    # Working with Older People
)