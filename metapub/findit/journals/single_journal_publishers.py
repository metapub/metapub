"""
Single journal publishers - publishers that have exactly ONE journal.

This module contains configurations for publishers that publish exactly
one journal and use generic functions (the_doi_slide, the_vip_shake)
rather than custom dance functions.

These are true single-journal publishers, not multi-journal publishers
that happen to use simple patterns.
"""

# NEJM - Single high-impact medical journal
nejm_journals = ['N Engl J Med']
nejm_template = 'https://www.nejm.org/doi/pdf/{doi}'

# Science (AAAS) - Single journal (Science magazine)
science_journals = ['Science']
science_vip_template = 'https://science.org/doi/reader/{doi}'

# PNAS - Single prestigious multidisciplinary journal
pnas_journals = ['Proc Natl Acad Sci USA']
pnas_template = 'https://www.pnas.org/doi/pdf/{doi}'

# AJPH - American Journal of Public Health (single journal publisher)
ajph_journals = ['Am J Public Health']
ajph_template = 'https://ajph.aphapublications.org/doi/pdf/{doi}'

# BMJ Open Gastroenterology - Single specialized medical journal
bmj_open_gastro_journals = ['BMJ Open Gastroenterol']
bmj_open_gastro_template = 'https://bmjopengastro.bmj.com/content/bmjgast/{year}/{volume}/{issue}/{article}.full.pdf'

# Microbiology Spectrum - Single ASM journal (not multi-journal ASM publisher)
microbiol_spectr_journals = ['Microbiol Spectr']
microbiol_spectr_template = 'https://journals.asm.org/doi/pdf/{doi}?download=true'