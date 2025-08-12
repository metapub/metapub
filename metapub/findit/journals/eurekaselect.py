"""Bentham Science Publishers (eurekaselect.com) journals.

Bentham Science is an academic publisher specializing in science, technology, and medical journals.
Their journals are hosted on eurekaselect.com and use DOI-based URLs.

Based on investigation, their PDF access appears to be behind a paywall,
but we can attempt DOI-based URL construction for potential access.

URL pattern investigation showed articles redirect from DOI to:
https://www.eurekaselect.com/{ARTICLE_ID}/article

For PDFs, we can try appending '/pdf' or using similar patterns,
but access likely requires subscription.
"""

# DOI-based template for Bentham Science / EurekaSelect
# Based on investigation showing DOI redirects to eurekaselect.com
eurekaselect_template = 'https://www.eurekaselect.com/openurl/openurl.php?genre=article&doi={doi}'

# Bentham Science / EurekaSelect journals from categorized analysis
# These journals showed up as associated with eurekaselect.com domain
eurekaselect_journals = []  # Journal list moved to YAML configuration
