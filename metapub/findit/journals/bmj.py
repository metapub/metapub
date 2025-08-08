"""
BMJ (British Medical Journal) journal patterns and mappings.

BMJ publishes medical journals with excellent citation_pdf_url meta tags.
This makes PDF extraction extremely simple and reliable.

Evidence-based analysis from HTML samples (2025-08-07):
- VIP URL construction available: https://[journal].bmj.com/content/{volume}/{issue}/{first_page}.full.pdf
- Perfect citation_pdf_url meta tags as backup (100% reliable)
- DOI format: 10.1136/ prefix (consistent across all journals)
- Optimized approach: VIP first (saves page load), meta tag fallback
- Eliminated journal list duplication: bmj_journals generated from bmj_journal_params

Dance Function: the_bmj_bump
"""


# VIP template for BMJ journals (used for primary URL construction)
bmj_vip_template = 'https://{host}/content/{volume}/{issue}/{first_page}.full.pdf'

# Host parameters for each BMJ journal
bmj_journal_params = {
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
    'J R Army Med Corps': {'host': 'jramc.bmj.com'},
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

# Generate journal list from parameters (eliminates duplication)
bmj_journals = list(bmj_journal_params.keys())