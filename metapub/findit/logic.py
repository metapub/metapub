__author__ = 'nthmost'

import logging
from ..pubmedfetcher import PubMedFetcher
from ..convert import doi2pmid
from ..exceptions import MetaPubError
from ..config import DEFAULT_CACHE_DIR

from .dances import *
from .registry import JournalRegistry, standardize_journal_name
from .handlers import RegistryBackedLookupSystem
from .journals import simple_formats_pmid

log = logging.getLogger('metapub.findit.logic')

# Global registry instances - cache by directory to respect user cachedir settings
_registries = {}
_lookup_systems = {}

def _get_lookup_system(cachedir=None):
    """Get or create the lookup system for the specified cache directory.

    Args:
        cachedir: Cache directory path. If None, uses DEFAULT_CACHE_DIR.

    Returns:
        RegistryBackedLookupSystem instance for the specified cache directory.
    """
    global _registries, _lookup_systems

    # Use default if not specified
    if cachedir is None:
        cachedir = DEFAULT_CACHE_DIR

    # Convert to string for consistent cache key
    cache_key = str(cachedir) if cachedir else 'default'

    if cache_key not in _lookup_systems:
        if cachedir is None or cache_key == 'None':
            # Disable caching - create in-memory database
            _registries[cache_key] = JournalRegistry(db_path=':memory:')
        else:
            # Use JournalRegistry's default logic - it prefers shipped database over cache
            _registries[cache_key] = JournalRegistry()

        _lookup_systems[cache_key] = RegistryBackedLookupSystem(_registries[cache_key])
        log.debug("Initialized registry-backed lookup system for cachedir: %s", cache_key)

    return _lookup_systems[cache_key]


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

def _try_lookup_step(step_name, func, pma, *args, **kwargs):
    """Run one FindIt lookup step, turning unexpected failures into a reason.

    Lookup steps signal "no PDF here" with MetaPubError subclasses
    (NoPDFLink / AccessDenied). Anything else -- a transient network error
    (e.g. requests ChunkedEncodingError / ProxyError), a malformed response,
    or a bug in a dance (e.g. UnboundLocalError, TypeError) -- must not
    propagate out of find_article_from_pma and kill a batch run over
    thousands of PMIDs (metapub/metapub#60). It is recorded as a TXERROR
    reason instead, and lookup falls through to the next step, exactly as
    the registry dances already do (see handlers._dispatch_dance_function).

    Returns (url, reason): url is None and reason is a TXERROR string when
    the step failed unexpectedly; (url, None) on success; (None, str(error))
    when the step raised a MetaPubError.
    """
    try:
        url = func(pma, *args, **kwargs)
        return url, None
    except MetaPubError as error:
        return None, str(error)
    except Exception as error:
        log.error("FindIt lookup step %s failed for PMID %s: %s",
                  step_name, getattr(pma, 'pmid', '?'), error)
        return None, 'TXERROR: %s' % error


def find_article_from_pma(pma, verify=True, use_nih=False, cachedir=None,
                        request_timeout=10, max_redirects=3):
    """ The real workhorse of FindIt.

        Based on the contents of the supplied PubMedArticle object, this function
        returns the best possible download link for a Pubmed PDF.

        This version uses the new registry-based lookup system for scalable
        journal handling.

        Be aware that this function no longer performs doi lookups; if you want
        this handled for you, use the FindIt object (which will also record the
        doi score from the lookup for you).

        Returns (url, reason) -- url being self-explanatory, and "reason" containing
        any qualifying message about why the url came back the way it did.

        Reasons may include (but are not limited to):

            "DOI missing from PubMedArticle and CrossRef lookup failed."
            "pii missing from PubMedArticle XML"
            "No URL format for Journal %s"

        Optional params:
            use_nih      -- source PubmedCentral articles from nih.gov (NOT recommended)

        :param pma: PubMedArticle object)
        :param verify: (bool) default: True
        :param use_nih: (bool) default: False
        :param cachedir: (str) cache directory for registry database
        :param request_timeout: (int) HTTP request timeout in seconds, default: 10
        :param max_redirects: (int) maximum redirects to follow, default: 3
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
        url, reason = _try_lookup_step('the_pmc_twist', the_pmc_twist,
                                       pma, verify, use_nih, request_timeout, max_redirects)
        if url:
            return (url, None)

    # === PMID-BASED LOOKUPS === #
    # Still use simple_formats_pmid for journals that can be accessed directly via PMID

    if jrnl in simple_formats_pmid.keys():
        url, step_reason = _try_lookup_step('the_pmid_pogo', the_pmid_pogo,
                                            pma, verify, request_timeout, max_redirects)
        if step_reason:
            reason = step_reason

    if url:
        return (url, reason)

    # === PUBLISHER BASED LISTS === #

    # Many Biomed Central journals start with "BMC", but many more don't.
    # Registry-based lookup will handle all BMC journals after this section
    if jrnl.find('BMC') == 0:
        url, step_reason = _try_lookup_step('the_bmc_boogie', the_bmc_boogie,
                                            pma, verify, request_timeout, max_redirects)
        if step_reason:
            reason = step_reason

    if url:
        return (url, reason)

    lookup_system = _get_lookup_system(cachedir=cachedir)
    url, reason = lookup_system.find_pdf_url(pma, verify=verify, 
                                            request_timeout=request_timeout, 
                                            max_redirects=max_redirects)
    return (url, reason)


def find_article_from_doi(doi, verify=True, use_nih=False, cachedir=None, 
                        request_timeout=10, max_redirects=3):
    """ Pull a PubMedArticle based on CrossRef lookup (using doi2pmid),
    then run it through find_article_from_pma.

    :param doi: (string)
    :param cachedir: (str) cache directory for registry database
    :param request_timeout: (int) HTTP request timeout in seconds, default: 10
    :param max_redirects: (int) maximum redirects to follow, default: 3
    :return: (url, reason)
    """
    fetch = PubMedFetcher()
    pma = fetch.article_by_pmid(doi2pmid(doi))
    return find_article_from_pma(pma, verify=verify, use_nih=use_nih, cachedir=cachedir,
                               request_timeout=request_timeout, max_redirects=max_redirects)

