from __future__ import absolute_import, unicode_literals

# vip = Volume-Issue-Page format
#       URLs that have the same format except for the host name
#
# TODO: early release format

vip_format = 'http://{host}/content/{a.volume}/{a.issue}/{a.first_page}.full.pdf'

vip_journals = {
    'Am J Clin Pathol': {'host': 'ajcp.ascpjournals.org'},
    'Am J Physiol Cell Physiol': {'host': 'ajpcell.physiology.org'},
    'Am J Physiol Endocrinol Metab': {'host': 'ajpendo.physiology.org'},
    'Am J Physiol Gastrointest Liver Physiol': {'host': 'ajpgi.physiology.org'},
    'Am J Physiol Heart Circ Physiol': {'host': 'ajpheart.physiology.org'},
    'Am J Physiol Lung Cell Mol Physiol': {'host': 'ajplung.physiology.org'},
    'Am J Physiol Regul Integr Comp Physiol': {'host': 'ajpregu.physiology.org'},
    'Am J Physiol Renal Physiol': {'host': 'ajprenal.physiology.org'},
    # TODO: the rest of physiology.org. see: http://www.the-aps.org/mm/Publications/Journals
    # TODO: backup_url: pmid lookup strategy, e.g.
    # http://aac.asm.org/cgi/pmidlookup?view=long&pmid=7689822
    'Anticancer Res': {'host': 'ar.iiarjournals.org'},
    'Antimicrob Agents Chemother': {'host': 'aac.asm.org'},
    'Appl Environ Microbiol': {'host': 'aem.asm.org'},
    'Arterioscler Thromb Vasc Biol': {'host': 'atvb.ahajournals.org'},
    'Breast Cancer Res': {'host': 'breast-cancer-research.com'},
    'Cancer Discov': {'host': 'cancerdiscovery.aacrjournals.org'},
    'Cancer Epidemiol Biomarkers Prev': {'host': 'cebp.aacrjournals.org'},
    'Cancer Res': {'host': 'cancerres.aacrjournals.org'},
    # TODO: backup_url: pmid lookup strategy, e.g.
    # http://www.cfp.ca/cgi/pmidlookup?view=long&pmid=19282532
    'Can Fam Physician': {'host': 'www.cfp.ca'},
    'Circulation': {'host': 'circ.ahajournals.org'},
    'Circ Arrhythm Electrophysiol': {'host': 'circep.ahajournals.org'},
    'Circ Cardiovasc Genet': {'host': 'circgenetics.ahajournals.org'},
    'Circ Res': {'host': 'circres.ahajournals.org'},
    'Clin Cancer Res': {'host': 'clincancerres.aacrjournals.org'},
    'Clin Chem': {'host': 'clinchem.org'},
    'Clin Microbiol Rev': {'host': 'cmr.asm.org'},
    'Clin Vaccine Immunol': {'host': 'cvi.asm.org'},
    'Diabetes': {'host': 'diabetes.diabetesjournals.org'},
    'Diabetes Care': {'host': 'care.diabetesjournals.org'},
    'Drug Metab Dispos': {'host': 'dmd.aspetjournals.org'},
    # TODO: backup_url: pmid lookup strategy,
    # http://emboj.embopress.org/cgi/pmidlookup?view=long&pmid=9501081
    'EMBO J': {'host': 'emboj.embopress.org'},
    'Endocr Relat Cancer': {'host': 'erc.endocrinology-journals.org'},  #TODO this is now https://erc.bioscientifica.com/
    'Eukaryot Cell': {'host': 'ec.asm.org'},
    'Eur J Endocrinol': {'host': 'eje-online.org'},
    'Eur Respir J': {'host': 'erj.ersjournals.com'},
    'FASEB J': {'host': 'fasebj.org'},
    'Genome Announc': {'host': 'genomea.asm.org'},
    'Genome Biol': {'host': 'genomebiology.com'},
    'Genome Res': {'host': 'genome.cshlp.org'},
    'Genes Dev': {'host': 'genesdev.cshlp.org'},
    'Haematologica': {'host': 'haematologica.org'},
    'Hypertension': {'host': 'hyper.ahajournals.org'},
    'Infect Immun': {'host': 'iai.asm.org'},
    'Invest Ophthalmol Vis Sci': {'host': 'www.iovs.org'},
    'IOVS': {'host': 'iovs.org'},
    # TODO: backup_url: pmid lookup strategy,
    # http://jah.sagepub.com/cgi/pmidlookup?view=long&pmid=20056814
    'J Am Soc Nephrol': {'host': 'jasn.asnjournals.org'},
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
    'J Clin Oncol': {'host': 'jco.ascopubs.org'},
    #'J Endocrinol': {'host': 'joe.endocrinology-journals.org'},   #moved
    #'J Mol Endocrinol': {'host': 'jme.endocrinology-journals.org'}, # moved to endo.py
    'J Exp Med': {'host': 'jem.rupress.org'},
    'J Immunol': {'host': 'jimmunol.org'},
    'J Lipid Res': {'host': 'www.jlr.org'},
    'J Clin Microbiol': {'host': 'jcm.asm.org'},
    'J Neurophysiol': {'host': 'jb.physiology.org'},
    'J Neurosci': {'host': 'jneurosci.org'},
    # TODO:  backup_url: pmid lookup strategy,
    # http://jn.nutrition.org/cgi/pmidlookup?view=long&pmid=10736367
    'J Nutr': {'host': 'jn.nutrition.org'},
    'J Pharmacol Exp Ther': {'host': 'jpet.aspetjournals.org'},
    'J Rheumatol': {'host': 'www.jrheum.org'},
    'J Virol': {'host': 'jvi.asm.org'},
    'MBio': {'host': 'mbio.asm.org'},
    'mSystems': {'host': 'msystems.asm.org'},
    'mSphere': {'host': 'msphere.asm.org'},
    'Microbiol Mol Biol Rev': {'host': 'mmbr.asm.org'},
    'Mol Biol Cell': {'host': 'molbiolcell.org'},
    'Mol Cell Biol': {'host': 'mcb.asm.org'},
    'Mol Canc Therapeut': {'host': 'mct.aacrjournals.org'},
    'Mol Cancer Ther': {'host': 'mct.aacrjournals.org'},
    'Mol Pharmacol': {'host': 'molpharm.aspetjournals.org'},
    'Neurology': {'host': 'neurology.org'},
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
    'Proc Natl Acad Sci USA': {'host': 'pnas.org'},
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

    # Oxford Academic journals (1.0 confidence + manually approved)

    # Nature journals removed - already handled by dedicated nature.py file
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

