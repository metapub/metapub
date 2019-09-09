from __future__ import absolute_import, print_function, unicode_literals

import os
import requests

from metapub.findit import FindIt
from metapub.exceptions import *

from requests.packages import urllib3
urllib3.disable_warnings()

OUTPUT_DIR = 'findit'
CURL_TIMEOUT = 4000

def try_request(url):
    # verify=False means it ignores bad SSL certs
    OK_STATUS_CODES = [200, 301, 302, 307]
    response = requests.get(url, stream=True, timeout=CURL_TIMEOUT, verify=False)

    if response.status_code in OK_STATUS_CODES:
        if response.headers.get('content-type').find('pdf') > -1:
            return True
    return False

def try_backup_url(pmid):
    source = FindIt(pmid=pmid)
    if not source.pma:
        return
    if source.url:
        print(pmid, source.pma.journal, source.url, try_request(source.url))
    else:
        print(pmid, source.pma.journal, source.reason)
        try:
            if source.backup_url is not None:
                print(pmid, source.pma.journal, source.backup_url, try_request(source.backup_url))
            else:
                print(pmid, source.pma.journal, "no backup url")
        except Exception as err:
            print(pmid, '%r' % err)

if __name__=='__main__':
    import sys
    try:
        start_pmid = int(sys.argv[1])
    except (IndexError, TypeError) as err:
        print("Supply a pubmed ID as the starting point for this script.")
        sys.exit()

    for pmid in range(start_pmid, start_pmid+1000):
        try_backup_url(pmid)


