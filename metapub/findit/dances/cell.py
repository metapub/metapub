from .generic import *
from ...exceptions import *

from .sciencedirect import the_sciencedirect_disco


def the_cell_pogo(pma, verify=True):
    '''  :param: pma (PubMedArticle object)
         :param: verify (bool) [default: True]
         :return: url
         :raises: AccessDenied, NoPDFLink
    '''
    jrnl = standardize_journal_name(pma.journal)
    if pma.pii:
        # the front door
        url = cell_format.format(a=pma, ja=cell_journals[jrnl]['ja'],
                                     pii=remove_chars(pma.pii, '-()'))
        if verify:
            verify_pdf_url(url, 'Cell')
        return url
    else:
        # let the SD function raise Exceptions
        return the_sciencedirect_disco(pma, verify)

