"""Lancet dance function."""

from ...exceptions import NoPDFLink
from ...utils import remove_chars
from .generic import verify_pdf_url


def the_lancet_tango(pma, verify=True):
    '''  :param: pma (PubMedArticle object)
         :param: verify (bool) [default: True]
         :return: url (string)
         :raises: AccessDenied, NoPDFLink
    '''
    if not pma.pii:
        raise NoPDFLink('MISSING: pii needed for Lancet lookup')
    
    # remove any parens or dashes in PII
    pii = remove_chars(pma.pii, '()- ')
    pdfurl = 'http://download.thelancet.com/pdfs/journals/lancet/PIIS%s.pdf?id=4bf3ca1a8e5e8965:e4f0e59:134d2dcdd8a:46d81315044949914' % pii
    if verify:
        verify_pdf_url(pdfurl, 'Lancet')
    return pdfurl