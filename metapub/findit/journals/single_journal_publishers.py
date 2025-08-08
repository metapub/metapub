"""
Single journal publishers with unique URL patterns.

These are high-impact journals that have their own unique URL patterns
and don't fit into larger publisher groups.
"""

# New England Journal of Medicine
nejm_journals = ['N Engl J Med']
nejm_template = 'https://www.nejm.org/doi/pdf/{doi}'

# Science (AAAS Science magazine) - VIP format
science_journals = ['Science']
science_journal_params = {'Science': {'host': 'sciencemag'}}
science_vip_template = 'http://{host}.org/content/{volume}/{issue}/{first_page}.full.pdf'

# Proceedings of the National Academy of Sciences - DOI format
pnas_journals = ['Proc Natl Acad Sci USA']
pnas_template = 'https://www.pnas.org/doi/pdf/{doi}'

# American Journal of Public Health - DOI format
ajph_journals = ['Am J Public Health']
ajph_template = 'http://ajph.aphapublications.org/doi/pdf/{doi}'

# BMJ Open Gastroenterology - DOI format
bmj_open_gastro_journals = ['BMJ Open Gastroenterol']
bmj_open_gastro_template = 'http://bmjopengastro.bmj.com/doi/pdf/{doi}'

# Microbiology Spectrum (ASM) - DOI format  
microbiol_spectr_journals = ['Microbiol Spectr']
microbiol_spectr_template = 'http://www.asmscience.org/content/journal/microbiolspec/{doi}'