from __future__ import absolute_import, unicode_literals


# CrossRef publisher -> DOI prefixes:  http://www.crossref.org/06members/50go-live.html
# independent CSV map of same (3 years ago): https://gist.github.com/hubgit/5974843
# a short list of major publishers: https://webhome.weizmann.ac.il/home/comartin/doi.html

HOSTNAME_TO_DOI_PREFIX_MAP = {'cancerres.aacrjournals.org': '10.1158',  #TODO: *.aacrjournals.org
                              'jcs.biologists.org': '10.1242',
                              'fasebj.org': '10.1096',
                              'ajcn.nutrition.org': '10.3945',
                              'mcponline.org': '10.1074',
                              'karger.com': '10.1159',
                              '*.biomedcentral.com': '10.1186',
                              'haematologica.org': '10.3324',
                              'genesdev.cshlp.org': '10.1101',
                              '*.bmj.com': '10.1136',
                              'jbc.org': '10.1074',
                              '*.oxfordjournals.org': '10.1093',
                              'eje-online.org': '10.1530',
                              'jimmunol.org': '10.4049',
                              '*.asm.org': '10.1128',
                              'elifesciences.org': '10.7554',
                              }

