from __future__ import absolute_import, print_function, unicode_literals

import os
import requests

from metapub.findit import FindIt
from metapub.exceptions import *

from requests.packages import urllib3
urllib3.disable_warnings()

CURL_TIMEOUT = 4000

def try_request(url):
    # verify=False means it ignores bad SSL certs
    OK_STATUS_CODES = [200, 301, 302, 307]
    response = requests.get(url, stream=True, timeout=CURL_TIMEOUT, verify=False)

    if response.status_code in OK_STATUS_CODES:
        if response.headers.get('content-type').find('pdf') > -1:
            return True

def load(pmid, verify=False):
    try:
        source = FindIt(pmid, verify=verify)
    except InvalidPMID:
        return None        

    if source.url:
        print(pmid, source.pma.journal, source.url)      #, try_request(source.url)
        return source.url
    else:
        print(pmid, source.pma.journal, source.reason)
        return None

if __name__=='__main__':
    import sys
    try:
        start_pmid = int(sys.argv[1])
    except (IndexError, TypeError) as err:
        print("Supply a pubmed ID as the starting point for this script.")
        sys.exit()

    try:
        end_pmid = int(sys.argv[2])
    except (IndexError, TypeError) as err:
        end_pmid = start_pmid + 1000

    links = []
    attempts = 0
    for pmid in range(start_pmid, end_pmid):
        attempts += 1
        result = load(pmid, verify=False)
        if result:
            links.append(result)

    print("%i links retrieved out of %i attempts" % (len(links), attempts))
    from IPython import embed; embed()

