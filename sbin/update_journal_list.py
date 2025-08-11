import requests

from downloader import Downloader
from config import JOURNAL_LIST_URL, JOURNAL_LIST_FILENAME

def retrieve_journal_list():
    '''Uses Downloader.mirror function to grab JOURNAL_LIST_URL (if different).

    Returns:
        DownloadResult object
    '''
    dldr = Downloader()
    result = dldr.mirror(JOURNAL_LIST_URL, JOURNAL_LIST_FILENAME)
    print(result)

if __name__ == '__main__':
    retrieve_journal_list()

