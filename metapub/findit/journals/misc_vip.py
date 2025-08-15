# vip = Volume-Issue-Page format
#       URLs that have the same format except for the host name
#
# TODO (maybe): early release format
#
# Import Oxford journals from the oxford.py module and merge them into vip_journals

from .oxford import oxford_journal_params

vip_format = 'http://{host}/content/{a.volume}/{a.issue}/{a.first_page}.full.pdf'

vip_journals = {
    'Am J Clin Pathol': {'host': 'ajcp.ascpjournals.org'},
    # TODO: the rest of physiology.org. see: http://www.the-aps.org/mm/Publications/Journals
    # TODO: backup_url: pmid lookup strategy, e.g.
    # http://aac.asm.org/cgi/pmidlookup?view=long&pmid=7689822
    'Anticancer Res': {'host': 'ar.iiarjournals.org'},
    'Breast Cancer Res': {'host': 'breast-cancer-research.com'},
    # TODO: backup_url: pmid lookup strategy, e.g.
    # http://www.cfp.ca/cgi/pmidlookup?view=long&pmid=19282532
    'Can Fam Physician': {'host': 'www.cfp.ca'},
    'Clin Chem': {'host': 'clinchem.org'},
    'Diabetes': {'host': 'diabetes.diabetesjournals.org'},
    'Diabetes Care': {'host': 'care.diabetesjournals.org'},
    'Drug Metab Dispos': {'host': 'dmd.aspetjournals.org'},
    # TODO: backup_url: pmid lookup strategy,
    # http://emboj.embopress.org/cgi/pmidlookup?view=long&pmid=9501081
    'EMBO J': {'host': 'emboj.embopress.org'},
    'Endocr Relat Cancer': {'host': 'erc.endocrinology-journals.org'},  #TODO this is now https://erc.bioscientifica.com/
    'Eur J Endocrinol': {'host': 'eje-online.org'},
    'Eur Respir J': {'host': 'erj.ersjournals.com'},
    'FASEB J': {'host': 'fasebj.org'},
    'Genome Biol': {'host': 'genomebiology.com'},
    'Genome Res': {'host': 'genome.cshlp.org'},
    'Genes Dev': {'host': 'genesdev.cshlp.org'},
    'Haematologica': {'host': 'haematologica.org'},
    'Invest Ophthalmol Vis Sci': {'host': 'www.iovs.org'},
    'IOVS': {'host': 'iovs.org'},
    # TODO: backup_url: pmid lookup strategy,
    # http://jah.sagepub.com/cgi/pmidlookup?view=long&pmid=20056814
    'J Am Soc Nephrol': {'host': 'jasn.asnjournals.org'},
    # TODO: backup_url: pmid lookup strategy,
    # http://jb.asm.org/cgi/pmidlookup?view=long&pmid=7683021
    # TODO backup_url: pmid lookup strategy, e.g.
    # http://www.jbc.org/cgi/pmidlookup?view=long&pmid=14722075
    'J Biol Chem': {'host': 'www.jbc.org'},
    'J Bone Joint Surg Am': {'host': 'jbjs.org'},
    'J Cell Biol': {'host': 'jcb.rupress.org'},
    'J Cell Sci': {'host': 'jcs.biologists.org'},
    'J Clin Oncol': {'host': 'jco.ascopubs.org'},
    'J Exp Med': {'host': 'jem.rupress.org'},
    'J Immunol': {'host': 'jimmunol.org'},
    'J Lipid Res': {'host': 'www.jlr.org'},
    'J Neurosci': {'host': 'jneurosci.org'},
    # TODO:  backup_url: pmid lookup strategy,
    # http://jn.nutrition.org/cgi/pmidlookup?view=long&pmid=10736367
    'J Nutr': {'host': 'jn.nutrition.org'},
    'J Pharmacol Exp Ther': {'host': 'jpet.aspetjournals.org'},
    'J Rheumatol': {'host': 'www.jrheum.org'},
    'Mol Biol Cell': {'host': 'molbiolcell.org'},
    'Mol Pharmacol': {'host': 'molpharm.aspetjournals.org'},
    'Neurology': {'host': 'neurology.org'},
    'Pediatrics': {'host': 'pediatrics.aappublications.org'},
    # TODO: backup_url: pmid lookup strategy, e.g.
    # http://physiolgenomics.physiology.org/cgi/pmidlookup?view=long&pmid=15252189
    # TODO:  backup_url: pmid lookup strategy, e.g.
    # http://www.plantcell.org/cgi/pmidlookup?view=long&pmid=9501112
    'Plant Cell': {'host': 'www.plantcell.org'},
    'Proc Natl Acad Sci USA': {'host': 'pnas.org'},
    'Science': {'host': 'sciencemag.org'},
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
}

# Non-VIP, not sure where to put yet
# 'BMJ Case Rep': {'host': 'casereports.bmj.com', 'example': 'http://casereports.bmj.com/content/2016/bcr-2015-214310'}
#

