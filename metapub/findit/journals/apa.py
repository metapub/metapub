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

# APA DOI-based template
apa_template = 'https://psycnet.apa.org/fulltext/{doi}.pdf'

apa_journals = []  # Journal list moved to YAML configuration
