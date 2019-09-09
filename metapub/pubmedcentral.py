from lxml import etree

import requests

from .config import PKGNAME, DEFAULT_EMAIL

PMC_ID_CONVERSION_URI = 'https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?tool='+PKGNAME+'&email='+DEFAULT_EMAIL+'&ids=%s'

__doc__="""An assortment of functions providing access to various web APIs.

    The pubmedcentral.* functions abstract the submission of one of the following
    acceptable IDs to the Pubmed Central ID Conversion API as a lookup to
    get another ID mapping to the same pubmed article:

        * doi       Digital Object Identifier
        * pmid      Pubmed ID
        * pmcid     Pubmed Central ID (includes Versioned Identifier)

    Available functions:

        get_pmid_for_otherid(string)
    
        get_doi_for_otherid(string)

        get_pmcid_for_otherid(string)
"""

def _pmc_id_conversion_api(input_id):
    xml = requests.get(PMC_ID_CONVERSION_URI % input_id).content
    root = etree.fromstring(xml)
    record = root.find('record')
    return record

def get_pmid_for_otherid(otherid):
    """ Use the PMC ID conversion API to attempt to convert either PMCID or DOI to a PMID.
    Returns PMID if successful, or None if there is no 'pmid' item in the response.

    :param otherid: (str)
    :return pmid: (str)
    :rtype: str
    """
    record = _pmc_id_conversion_api(otherid)
    return record.get('pmid')

def get_pmcid_for_otherid(otherid):
    """ Use the PMC ID conversion API to attempt to convert either PMID or DOI to a PMCID.
    Returns PMCID if successful, or None if there is no 'pmcid' item in the response.

    :param otherid: (str)
    :return pmcid: (str)
    :rtype: str
    """
    record = _pmc_id_conversion_api(otherid)
    return record.get('pmcid')

def get_doi_for_otherid(otherid):
    """ Use the PMC ID conversion API to attempt to convert either PMID or PMCID to a DOI.
    Returns DOI if successful, or None if there is no 'doi' item in the response.

    Note: this method has a very low success rate for retrieving DOIs. Check out the
    CrossRef object, i.e. `from metapub import CrossRef` which excels at resolving citations
    into DOIs (and DOIs into citations).

    :param otherid: (str)
    :return doi: (str)
    :rtype: str
    """
    record = _pmc_id_conversion_api(otherid)
    return record.get('doi')


# PMID: https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?tool=my_tool&email=my_email@example.com&ids=23193287
# PMCID: https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?tool=my_tool&email=my_email@example.com&ids=PMC3531190
# Manuscript ID: https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?tool=my_tool&email=my_email@example.com&ids=NIHMS311352
# DOI: https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?tool=my_tool&email=my_email@example.com&ids=10.1093/nar/gks1195
# Versioned identifier: https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?tool=my_tool&email=my_email@example.com&ids=PMC2808187.1


