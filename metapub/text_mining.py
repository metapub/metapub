import re

import requests

from .utils import remove_html_markup

# examples of real DOIs:
#         10.1002/(SICI)1098-1004(1999)14:1<91::AID-HUMU21>3.0.CO;2-B
#         10.1007/s12020-014-0368-x
#         10.1101/gad.14.3.278
#         10.1016/S0898-1221(00)00204-2

# example of DOI returned by the regular expression that is incorrect:
#         10.1002/ajmg.b.30585).

re_doi = re.compile(r'(10[.][0-9]{2,}(?:[.][0-9]+)*/(?:(?!["&\'])\S)+)')
re_doi_ws = re.compile(r'(10[.][0-9]{2,}(?:[.][0-9]+)*\s+/\s+(?:(?!["&\'])\S)+)')

re_pmid = re.compile('\d+')
re_numbers = re_pmid    # for now, until there's a better idea about parsing PMIDs...

re_matching_quotes = re.compile(r"\"([^\"]+)\"|\'([^\']+)\'")

# other IDs
re_ncbi_bookID = re.compile('NBK[0-9]+')
re_pmcID = re.compile('PMC[0-9]+')

def findall_ncbi_bookIDs(text):
    """ GeneReviews books look like this: NBK1210  (see https://www.ncbi.nlm.nih.gov/pubmed/?term=NBK1210 )

    :param text:
    :returns book_ids: list of IDs (possibly empty)
    """
    return re_ncbi_bookID.findall(text)


def is_ncbi_bookID(book_id):
    """ Returns whether supplied book_id appears to be an NCBI book ID (e.g. "NBK1010"). """
    if book_id in findall_ncbi_bookIDs(book_id):
        return True
    return False


def findall_pmcIDs(text):
    """ PubmedCentral IDs look like this: PMC123456

    :param text:
    :returns pmc_ids: list of IDs (possibly empty)
    """
    return re_pmcID.findall(text)


def is_pmcid(pmcid):
    """ Returns boolean on whether supplied pmcid looks like a PubMedCentral ID (e.g. "PMC31345"). """
    if pmcid in findall_pmcIDs(pmcid):
        return True
    return False


def pick_pmid(text):
    """ return longest numerical string from text (string) as the pmid.
        if text is empty or there are no pmids, return None.

    :param text: (str)
    :return: pmid (str) or None
    """
    pmids = re_pmid.findall(text)
    if pmids:
        longest = ''
        for num in pmids:
            if len(num) > len(longest):
                longest = num
        return longest
    else:
        return None


def _doi_pass_2(doi):
    """Recursive function that trims junk characters that often accompany DOIs
    scraped out of academic articles and web pages.
    """
    if doi.endswith('.') or doi.endswith(','):
        return _doi_pass_2(doi[:-1])
    elif doi.endswith(')'):
        if doi.count('(') == doi.count(')'):
            return doi
        else:
            return _doi_pass_2(doi[:-1])
    else:
        return doi.replace(' ', '')


def findall_dois_in_text(inp, whitespace=False):
    """ Returns all seen DOIs in submitted text.

        if `whitespace` arg set to True, look for DOIs like the following:
             10.1002 / pd.354
        ...but return with whitespace stripped:
             10.1002/pd.354

    :param inp: (str)
    :param whitespace: (bool)
    :return: list of DOIs found in inp
    """
    if whitespace:
        dois = re_doi_ws.findall(inp)
    else:
        dois = re_doi.findall(inp)
    return [_doi_pass_2(doi) for doi in dois]


def find_doi_in_string(inp, whitespace=False):
    """ Returns the first seen DOI in the input string.

    :param inp: (str)
    :param whitespace: (bool)
    :return: string containing first found DOI, or None
    """
    try:
        doi = findall_dois_in_text(inp, whitespace)[0]
    except IndexError:
        return None
    return _doi_pass_2(doi)


def scrape_doi_from_article_page(url):
    """ Takes an article link (url), loads its page, and searches its content for DOIs, returning
    the first one it finds.

    The first DOI found on the page being the correct one for the article at hand seems to be a
    reasonable and workable assumption in general.

    :param url: (str)
    :return: doi or None
    """
    response = requests.get(url)
    if response.ok:
        dois = findall_dois_in_text(response.text)
        if dois:
            return remove_html_markup(dois[0])
    return None


# NOT TESTED and probably not working #####
def get_pmc_fulltext_filename_for_PubMedArticle(pma):
    fmt = '{journal}/{journal}_{year}_{month}_{day}_{voliss}_{pages}'
    return fmt.format(**pma.to_dict())

