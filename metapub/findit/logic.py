__author__ = 'nthmost'

from ..pubmedfetcher import PubMedFetcher
from ..convert import doi2pmid
from ..exceptions import MetaPubError

from .dances import *


PUBMED_SWITCHBOARD = {
    'jstage':   {'journals': jstage_journals, 'dance': the_jstage_dive,     },
    'springer': {'journals': springer_journals, 'dance': the_springer_shag, },
    'wiley':    {'journals': wiley_journals, 'dance': the_wiley_shuffle,    },
    'jama':     {'journals': jama_journals, 'dance': the_jama_dance,        },
    'aaas':     {'journals': aaas_journals, 'dance': the_aaas_tango,        },
    'spandidos': {'journals': spandidos_journals, 'dance': the_spandidos_lambada, },
    'jci':      {'journals': jci_journals, 'dance': the_jci_jig,            },
    'scielo':   {'journals': scielo_journals, 'dance': the_scielo_chula,    },
    'najms':    {'journals': najms_journals, 'dance': the_najms_mazurka,    },
    'biomchemsoc': {'journals': biochemsoc_journals, 'dance': the_biochemsoc_saunter,   },
    'nature':   {'journals': nature_journals, 'dance': the_nature_ballet,   },
    'cell':     {'journals': cell_journals, 'dance': the_cell_pogo,         },
    'lancet':   {'journals': lancet_journals, 'dance': the_lancet_tango,    },
    'sciencedirect': {'journals': sciencedirect_journals, 'dance': the_sciencedirect_disco, },
    'karger':   {'journals': karger_journals, 'dance': the_karger_conga,    },
    'wolterskluwer': {'journals': wolterskluwer_journals, 'dance': the_wolterskluwer_volta, },
}


""" findit/logic.py

        The get_pdf_from_pma function selects possible PDF links for the
        given article represented in a PubMedArticle object.

        These links are built (not crawled) by selecting a likely-to-work URL
        pattern based on the NLM journal name abbreviation taken from the
        PubMedArticle object.

        It's recommended to use the FindIt object as the primary interface
        to this code.

        See the find_article_from_pma docstring for more info.

        *** IMPORTANT NOTE ***

        In many cases, this code performs intermediary HTTP requests in order to
        scrape a PDF url out of a page, and sometimes tests the url to make sure
        that what's being sent back is in fact a PDF.

        NO PDF DOWNLOAD IS PERFORMED; however some websites will block your IP
        address when you are performing several information lookups within a
        relatively short span of time (e.g. informa blocks if 25 HTTP connections
        are made within 5 minutes).

        If you would like these requests to go through a proxy (e.g. if you would
        like to prevent making multiple requests of the same servers, which may have
        effects like getting your IP shut off from PubMedCentral), set the
        HTTP_PROXY environment variable in your code or on the command line before
        using any FindIt functionality.
"""

def find_article_from_pma(pma, verify=True, use_nih=False):
    """ The real workhorse of FindIt.

        Based on the contents of the supplied PubMedArticle object, this function
        returns the best possible download link for a Pubmed PDF.

        Be aware that this function no longer performs doi lookups; if you want
        this handled for you, use the FindIt object (which will also record the
        doi score from the lookup for you).

        Returns (url, reason) -- url being self-explanatory, and "reason" containing
        any qualifying message about why the url came back the way it did.

        Reasons may include (but are not limited to):

            "DOI missing from PubMedArticle and CrossRef lookup failed."
            "pii missing from PubMedArticle XML"
            "No URL format for Journal %s"
            "TODO format"

        Optional params:
            use_nih      -- source PubmedCentral articles from nih.gov (NOT recommended)

        :param pma: PubMedArticle object)
        :param verify: (bool) default: True
        :param use_nih: (bool) default: False
        :return: (url, reason)
    """
    reason = ''
    url = None
    jrnl = standardize_journal_name(pma.journal)

    # === Pubmed Central: ideally we get the article from PMC if it has a PMC id.
    #
    #   Note: we're using europepmc.org rather than nih.gov (see the_pmc_twist function).
    #
    #   If we can't get the article from a PMC site, it may be that the paper is
    #   temporarily embargoed.  In that case, we may be able to fall back on retrieval
    #   from a publisher link.

    if pma.pmc:
        try:
            url = the_pmc_twist(pma, verify, use_nih)
            return (url, None)
        except MetaPubError as error:
            reason = str(error)

    # === IDENTIFIER-BASED LISTS === #

    if jrnl in simple_formats_pii.keys():
        try:
            url = the_pii_polka(pma, verify)
        except MetaPubError as error:
            reason = str(error)

    elif jrnl in simple_formats_pmid.keys():
        try:
            url = the_pmid_pogo(pma, verify)
        except MetaPubError as error:
            reason = str(error)

    elif jrnl in simple_formats_doi.keys():
        try:
            url = the_doi_slide(pma, verify)
        except MetaPubError as error:
            reason = str(error)

    elif jrnl in vip_journals.keys():
        try:
            url = the_vip_shake(pma, verify)
        except MetaPubError as error:
            reason = str(error)

    elif jrnl in vip_journals_nonstandard.keys():
        try:
            url = the_vip_nonstandard_shake(pma, verify)
        except MetaPubError as error:
            reason = str(error)

    if url:
        return (url, reason)

    # === PUBLISHER BASED LISTS === #

    # Many Biomed Central journals start with "BMC", but many more don't.
    if jrnl.find('BMC') == 0 or jrnl in BMC_journals:
        try:
            url = the_biomed_calypso(pma, verify)
        except MetaPubError as error:
            reason = str(error)

    for publisher in list(PUBMED_SWITCHBOARD.keys()):
        if jrnl in PUBMED_SWITCHBOARD[publisher]['journals']:
            try:
                url = PUBMED_SWITCHBOARD[publisher]['dance'](pma)
            except MetaPubError as error:
                reason = str(error)

    if url:
        return (url, reason)

    #if jrnl in paywall_journals:
    #    reason = 'PAYWALL: this journal has been marked in a list as "never free"'

    elif jrnl in todo_journals:
        reason = 'TODO: format example: %s' % todo_journals[jrnl]['example']

    elif jrnl in JOURNAL_CANTDO_LIST:
        reason = 'CANTDO: this journal has been marked as unsourceable'

    # aka if url is STILL None...
    if not url and not reason:
        reason = 'NOFORMAT: No URL format for journal "%s"' % jrnl

    return (url, reason)


def find_article_from_doi(doi, verify=True, use_nih=False):
    """ Pull a PubMedArticle based on CrossRef lookup (using doi2pmid),
    then run it through find_article_from_pma.

    :param doi: (string)
    :return: (url, reason)
    """
    fetch = PubMedFetcher()
    pma = fetch.article_by_pmid(doi2pmid(doi))
    return find_article_from_pma(pma, verify=verify, use_nih=use_nih)

