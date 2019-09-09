from __future__ import absolute_import, unicode_literals

# Portlan Press Biochemical Society journals: mostly VIP
biochemsoc_format = 'http://{host}/content/{ja}/{a.volume}/{a.issue}/{a.first_page}.full.pdf'
biochemsoc_journals = {'Biochem J': {'host': 'www.biochemj.org', 'ja': 'ppbiochemj'},
                       'Clin Sci': {'host': 'www.clinsci.org', 'ja': 'ppclinsci'},
                       }
