from __future__ import absolute_import, unicode_literals

try:
    from urlparse import urlparse
except ImportError:
    # assume python3
    from urllib.parse import urlparse

from metapub.findit.journals import misc_vip, misc_pii
from metapub.findit.journals import biochemsoc, aaas 

from metapub import PubMedFetcher

fetch = PubMedFetcher()

fh = open('metapub/urlreverse/hostname2jrnl.py', 'w')

fh.write('from __future__ import absolute_import, unicode_literals\n')
fh.write('\n')
fh.write('HOSTNAME_TO_JOURNAL_MAP = {\n')

def write_one_mapping(hostname, jrnl):
    if hostname.startswith('www'):
        hostname = hostname.replace('www.', '')
    fh.write("\t\t'%s': '%s',\n" % (hostname, jrnl))

# Volume-Issue-Page format
for jrnl, value in misc_vip.vip_journals.items():
    write_one_mapping(value['host'], jrnl)

# Nonstandard VIP format
for jrnl, url in misc_vip.vip_journals_nonstandard.items():
    hostname = urlparse(url).hostname
    write_one_mapping(hostname, jrnl)

# PII based
for jrnl, url in misc_pii.simple_formats_pii.items():
    hostname = urlparse(url).hostname
    write_one_mapping(hostname, jrnl)

# BIOCHEMSOC (VIP format)
for jrnl, value in biochemsoc.biochemsoc_journals.items():
    write_one_mapping(value['host'], jrnl)

# AAAS (VIP format)

# dummy pma for formatting
pma = fetch.article_by_pmid(27095592)
for jrnl, value in aaas.aaas_journals.items():
    hostname = urlparse(aaas.aaas_format.format(ja=value['ja'], a=pma)).hostname
    write_one_mapping(hostname, jrnl)


# One-offs we know about
write_one_mapping('joponline.org', 'J Periodontol')
write_one_mapping('medicinabuenosaires.com', 'Medicina (B Aires)')

fh.write('}\n')


# More complicated reversals...

# JAMA? 

# JSTAGE: mostly free (yay)
# Examples:
# J Biochem: https://www.jstage.jst.go.jp/article/biochemistry1922/125/4/125_4_803/_pdf
# Drug Metab Pharmacokinet:
# https://www.jstage.jst.go.jp/article/dmpk/20/2/20_2_144/_article -->
#        Vol. 20 (2005) No. 2 P 144-151 

# mysql> select url from FindIt where url like '%jstage%' limit 10;
#+------------------------------------------------------------------+
#| url                                                              |
#+------------------------------------------------------------------+
#| https://www.jstage.jst.go.jp/article/jat/16/3/16_E125/_pdf       |
#| https://www.jstage.jst.go.jp/article/bpb/27/5/27_5_621/_pdf      |
#| https://www.jstage.jst.go.jp/article/jat/18/6/18_7377/_pdf       |
#| https://www.jstage.jst.go.jp/article/yoken/66/4/66_306/_pdf      |
#| https://www.jstage.jst.go.jp/article/tjem/223/4/223_4_253/_pdf   |
#| https://www.jstage.jst.go.jp/article/jat/18/1/18_5702/_pdf       |
#| https://www.jstage.jst.go.jp/article/jvms/73/3/73_10-0156/_pdf   |
#| https://www.jstage.jst.go.jp/article/jmi/52/1,2/52_1,2_41/_pdf   |
#| https://www.jstage.jst.go.jp/article/jea/14/3/14_3_94/_pdf       |
#| https://www.jstage.jst.go.jp/article/jphs/111/3/111_09202FP/_pdf |
#+------------------------------------------------------------------+
#10 rows in set (0.00 sec)
#

# KARGER
# {kid} comes from the final nonzero numbers of the article's DOI.
#karger_format = 'http://www.karger.com/Article/Pdf/{kid}'
#
# mysql> select url from FindIt where url like '%karger%' limit 10;
#+------------------------------------------+
#| url                                      |
#+------------------------------------------+
#| http://www.karger.com/Article/Pdf/319536 |
#| http://www.karger.com/Article/Pdf/340030 |
#| http://www.karger.com/Article/Pdf/214861 |
#| http://www.karger.com/Article/Pdf/338781 |
#| http://www.karger.com/Article/Pdf/342851 |
#| http://www.karger.com/Article/Pdf/330763 |
#| http://www.karger.com/Article/Pdf/90912  |
#| http://www.karger.com/Article/Pdf/319663 |
#| http://www.karger.com/Article/Pdf/215738 |
#| http://www.karger.com/Article/Pdf/329345 |
#+------------------------------------------+
#10 rows in set (0.01 sec)


# CELL
#cell_format = 'http://www.cell.com{ja}/pdf/{pii}.pdf'
#cell_journals = {
#   'Am J Hum Genet': {'ja': '/AJHG'},
#   'Biophys J': {'ja': '/biophysj'},
#   ...
# }    

# Nature (VIP)
# # nature journals -- see http://www.nature.com/siteindex/index.html
# nature_format = 'http://www.nature.com/{ja}/journal/v{a.volume}/n{a.issue}/pdf/{a.pii}.pdf'
#nature_journals = {
#    'Am J Gastroenterol': {'ja': 'ajg'},
#

# Sciencedirect:  'http://www.sciencedirect.com/science/article/pii/{piit}'

# Spandidos (VIP)
# spandidos_format = 'http://www.spandidos-publications.com/{ja}/{a.volume}/{a.issue}/{a.first_page}/download'
# spandidos_journals = {
#    'Int J Oncol': {'ja': 'ijo'},
#    'Int J Mol Med': {'ja': 'ijmm'},
#    'Oncol Lett': {'ja': 'ol'},
#    'Oncol Rep': {'ja': 'or'},
#}  

# Springer: DOI based 

# Wiley: should have DOI, but it may require more careful attention...
# mysql> select url from FindIt where url like '%wiley%' limit 10;
#+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
#| url                                                                                                                                                                               |
#+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
#| http://onlinelibrary.wiley.com/store/10.1111/j.1601-183X.2011.00756.x/asset/j.1601-183X.2011.00756.x.pdf?v=1&t=ibq5nopd&s=c466e3ae90d3a70460833c4b3afb8997382c8dbb                |
#| http://onlinelibrary.wiley.com/store/10.1038/oby.2003.86/asset/oby.2003.86.pdf?v=1&t=ibt6p5ad&s=158358ce28883b5abe4bd175547503df37d0b1b7                                          |
#| http://onlinelibrary.wiley.com/store/10.1111/jnc.12717/asset/jnc12717.pdf?v=1&t=iblv4dkr&s=fc798cf8ed5cce0f6728e5dc8b075ff5d36b9b6f                                               |
#| http://onlinelibrary.wiley.com/store/10.1002/asia.201100523/asset/2803_ftp.pdf?v=1&t=ibt6rbsm&s=2a1058501bec97cf5ac141ce1d8f76e2897e1caa                                          |
#| http://onlinelibrary.wiley.com/store/10.1111/j.1365-2141.2012.09043.x/asset/bjh9043.pdf?v=1&t=iblv60w8&s=5fe47378834c37a6e72b2a39fcc557446c811f30                                 |
#| http://onlinelibrary.wiley.com/store/10.1111/j.1471-4159.2010.06572.x/asset/j.1471-4159.2010.06572.x.pdf?v=1&t=iblv6zae&s=6f18cf486e8c4dfa6402fdda213dcbc454b5a09d                |
#| http://onlinelibrary.wiley.com/store/10.1002/(SICI)1097-0061(19980130)14:2<161::AID-YEA208>3.0.CO;2-Y/asset/208_ftp.pdf?v=1&t=ibqsvd4r&s=d74396a1e55e0a7b1bb08f297ce23c220d713d6f |
#| http://onlinelibrary.wiley.com/store/10.1002/lt.22235/asset/22235_ftp.pdf?v=1&t=ibt6u0i6&s=6559b0196867edd79e9bfaf8bd56b0b80dd17218                                               |
#| http://onlinelibrary.wiley.com/store/10.1053/jhep.2001.29374/asset/510340616_ftp.pdf?v=1&t=iblv988f&s=43778bc4a2e54248721b0bb35ee39f793f02c821                                    |
#| http://onlinelibrary.wiley.com/store/10.1111/j.1365-2036.2007.03272.x/asset/j.1365-2036.2007.03272.x.pdf?v=1&t=ibt6ucpe&s=2d018ceef53266378563ffee1e3214181c83fb66                |
#+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
#10 rows in set (0.00 sec)

# Wolter-Skluwer: pretty ugly
#
# mysql> select url from FindIt where url like '%lww%' limit 10;
#+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
#| url                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
#+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
#| http://pdfs.journals.lww.com/epidem/2005/09000/Environmental_Tobacco_Smoke_and_Risk_of_Adult.12.pdf?token=method|ExpireAbsolute;source|Journals;ttl|1440498090496;payload|mY8D3u1TCCsNvP5E421JYK6N6XICDamxByyYpaNzk7FKjTaa1Yz22MivkHZqjGP4kdS2v0J76WGAnHACH69s21Csk0OpQi3YbjEMdSoz2UhVybFqQxA7lKwSUlA502zQZr96TQRwhVlocEp/sJ586aVbcBFlltKNKo+tbuMfL73hiPqJliudqs17cHeLcLbV/CqjlP3IO0jGHlHQtJWcICDdAyGJMnpi6RlbEJaRheGeh5z5uvqz3FLHgPKVXJzdEsJoL23OlUp6auHczW/sYVAA9y9aLQ/ViUNWz8NymjA=;hash|GSaSldj7UllaFaF1v0XOHA==                                |
#| http://pdfs.journals.lww.com/co-oncology/2013/01000/Lessons_from_tumor_reversion_for_cancer_treatment.12.pdf?token=method|ExpireAbsolute;source|Journals;ttl|1440501727815;payload|mY8D3u1TCCsNvP5E421JYK6N6XICDamxByyYpaNzk7FKjTaa1Yz22MivkHZqjGP4kdS2v0J76WGAnHACH69s21Csk0OpQi3YbjEMdSoz2UhVybFqQxA7lKwSUlA502zQZr96TQRwhVlocEp/sJ586aVbcBFlltKNKo+tbuMfL73hiPqJliudqs17cHeLcLbV/CqjlP3IO0jGHlHQtJWcICDdAyGJMnpi6RlbEJaRheGeh5z5uvqz3FLHgPKVXJzd1e6uV2h8gb8tPnf1XZERZzCUv/8RvRhaVcbCdl8irQ4cu6USW478KeZmcJ2ckEc6;hash|ibWNzLUpXY4OCwEbjAxz0w==   |
#| http://pdfs.journals.lww.com/co-obgyn/2013/02000/Research_and_clinical_applications_of_cancer.3.pdf?token=method|ExpireAbsolute;source|Journals;ttl|1440512705777;payload|mY8D3u1TCCsNvP5E421JYK6N6XICDamxByyYpaNzk7FKjTaa1Yz22MivkHZqjGP4kdS2v0J76WGAnHACH69s21Csk0OpQi3YbjEMdSoz2UhVybFqQxA7lKwSUlA502zQZr96TQRwhVlocEp/sJ586aVbcBFlltKNKo+tbuMfL73hiPqJliudqs17cHeLcLbV/CqjlP3IO0jGHlHQtJWcICDdAyGJMnpi6RlbEJaRheGeh5z5uvqz3FLHgPKVXJzdRYj1f91FVlpiZnhtACuRa5kJ033xApDsdqExjCW6tlA=;hash|dUINF7KE3OLrAGB+99aUZQ==                                |
#| http://pdfs.journals.lww.com/co-hematology/2009/03000/Umbilical_cord_blood_transplantation_for_acute.11.pdf?token=method|ExpireAbsolute;source|Journals;ttl|1440533661430;payload|mY8D3u1TCCsNvP5E421JYK6N6XICDamxByyYpaNzk7FKjTaa1Yz22MivkHZqjGP4kdS2v0J76WGAnHACH69s21Csk0OpQi3YbjEMdSoz2UhVybFqQxA7lKwSUlA502zQZr96TQRwhVlocEp/sJ586aVbcBFlltKNKo+tbuMfL73hiPqJliudqs17cHeLcLbV/CqjlP3IO0jGHlHQtJWcICDdAyGJMnpi6RlbEJaRheGeh5z5uvqz3FLHgPKVXJzd684cnptYbe3g+YiEWGB3VS7bR5R7a3ZYHeJsUbErWYHZxSAHid5PYeQ4gxm9WoG1;hash|AbT6SsXM9WscjwFa4cZRwQ==    |
#| http://pdfs.journals.lww.com/pidj/2015/01000/Pneumococcal_Conjugate_Vaccine_Administration.16.pdf?token=method|ExpireAbsolute;source|Journals;ttl|1440544950891;payload|mY8D3u1TCCsNvP5E421JYK6N6XICDamxByyYpaNzk7FKjTaa1Yz22MivkHZqjGP4kdS2v0J76WGAnHACH69s21Csk0OpQi3YbjEMdSoz2UhVybFqQxA7lKwSUlA502zQZr96TQRwhVlocEp/sJ586aVbcBFlltKNKo+tbuMfL73hiPqJliudqs17cHeLcLbV/CqjlP3IO0jGHlHQtJWcICDdAyGJMnpi6RlbEJaRheGeh5z5uvqz3FLHgPKVXJzd9fRUIW1maLlkTEujSt+XQo5IVJBd3daCSHoX6mWGxuQ=;hash|SPVhiHX2hW5UZR30GU6zRA==                                  |
#| http://pdfs.journals.lww.com/co-hematology/2009/03000/Impact_of_new_prognostic_markers_in_treatment.8.pdf?token=method|ExpireAbsolute;source|Journals;ttl|1440565162828;payload|mY8D3u1TCCsNvP5E421JYK6N6XICDamxByyYpaNzk7FKjTaa1Yz22MivkHZqjGP4kdS2v0J76WGAnHACH69s21Csk0OpQi3YbjEMdSoz2UhVybFqQxA7lKwSUlA502zQZr96TQRwhVlocEp/sJ586aVbcBFlltKNKo+tbuMfL73hiPqJliudqs17cHeLcLbV/CqjlP3IO0jGHlHQtJWcICDdAyGJMnpi6RlbEJaRheGeh5z5uvqz3FLHgPKVXJzd684cnptYbe3g+YiEWGB3VXpggSWZdO5vqVlkYqaxmcahTYSQSk+x6AkNp/uOBTtg;hash|x1c2Ask8dM5xyljwl1pdyg==      |
#| http://pdfs.journals.lww.com/co-hematology/2009/03000/Differentiation_therapy_of_acute_myeloid_leukemia_.6.pdf?token=method|ExpireAbsolute;source|Journals;ttl|1440568236857;payload|mY8D3u1TCCsNvP5E421JYK6N6XICDamxByyYpaNzk7FKjTaa1Yz22MivkHZqjGP4kdS2v0J76WGAnHACH69s21Csk0OpQi3YbjEMdSoz2UhVybFqQxA7lKwSUlA502zQZr96TQRwhVlocEp/sJ586aVbcBFlltKNKo+tbuMfL73hiPqJliudqs17cHeLcLbV/CqjlP3IO0jGHlHQtJWcICDdAyGJMnpi6RlbEJaRheGeh5z5uvqz3FLHgPKVXJzd684cnptYbe3g+YiEWGB3VXpggSWZdO5vqVlkYqaxmcYK0Wb8bAE+S3G3LDOzJpQ6;hash|Q1CkEa9fO/W35LcjbWrdHg== |
#| http://pdfs.journals.lww.com/greenjournal/1972/08000/Primary_Lymphoma_of_the_Vagina_.18.pdf?token=method|ExpireAbsolute;source|Journals;ttl|1440584143160;payload|mY8D3u1TCCsNvP5E421JYK6N6XICDamxByyYpaNzk7FKjTaa1Yz22MivkHZqjGP4kdS2v0J76WGAnHACH69s21Csk0OpQi3YbjEMdSoz2UhVybFqQxA7lKwSUlA502zQZr96TQRwhVlocEp/sJ586aVbcBFlltKNKo+tbuMfL73hiPqJliudqs17cHeLcLbV/CqjlP3IO0jGHlHQtJWcICDdAyGJMnpi6RlbEJaRheGeh5z5uvqz3FLHgPKVXJzddI9yZMOXhrzL4hhvIuyRpfwlGsI0aV9D5EepbhXm2qOpr4A3kRopeMSXkqMYx0io;hash|StaEYARRR8WeQ6PIuo5BdA==                    |
#| http://pdfs.journals.lww.com/aidsonline/2013/01140/Non_AIDS_defining_hematological_malignancies_in.17.pdf?token=method|ExpireAbsolute;source|Journals;ttl|1440585495558;payload|mY8D3u1TCCsNvP5E421JYK6N6XICDamxByyYpaNzk7FKjTaa1Yz22MivkHZqjGP4kdS2v0J76WGAnHACH69s21Csk0OpQi3YbjEMdSoz2UhVybFqQxA7lKwSUlA502zQZr96TQRwhVlocEp/sJ586aVbcBFlltKNKo+tbuMfL73hiPqJliudqs17cHeLcLbV/CqjlP3IO0jGHlHQtJWcICDdAyGJMnpi6RlbEJaRheGeh5z5uvqz3FLHgPKVXJzdN2ziiHhY6wPF9tfA80junmOIFzAowSMVHiXG9vuUxPY=;hash|1qtdSq8EdxmqGhbWJU8/yA==                          |
#| http://pdfs.journals.lww.com/md-journal/2015/04030/Busulfan_and_Fludarabine_Conditioning_Regimen.15.pdf?token=method|ExpireAbsolute;source|Journals;ttl|1440599517380;payload|mY8D3u1TCCsNvP5E421JYK6N6XICDamxByyYpaNzk7FKjTaa1Yz22MivkHZqjGP4kdS2v0J76WGAnHACH69s21Csk0OpQi3YbjEMdSoz2UhVybFqQxA7lKwSUlA502zQZr96TQRwhVlocEp/sJ586aVbcBFlltKNKo+tbuMfL73hiPqJliudqs17cHeLcLbV/CqjlP3IO0jGHlHQtJWcICDdAyGJMnpi6RlbEJaRheGeh5z5uvqz3FLHgPKVXJzddFRrD2hcIwdDP9eSnSkfszWK8zxXjmDK7WJbKc0sCrg=;hash|kAw9ndFW3iNYxJqF2hiHWg==                            |
#+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
#10 rows in set (0.06 sec)

