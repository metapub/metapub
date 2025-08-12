__author__ = 'nthmost'

import logging
from ..pubmedfetcher import PubMedFetcher
from ..convert import doi2pmid
from ..exceptions import MetaPubError

from .dances import *
from .registry import JournalRegistry, standardize_journal_name
from .handlers import RegistryBackedLookupSystem
from .journals import (simple_formats_pii, simple_formats_pmid,
                      vip_journals, vip_journals_nonstandard,
                      JOURNAL_CANTDO_LIST)

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

    from ..config import DEFAULT_CACHE_DIR

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
            from ..cache_utils import get_cache_path
            db_path = get_cache_path(cachedir, 'journal_registry.db')
            _registries[cache_key] = JournalRegistry(db_path=db_path)

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

def find_article_from_pma(pma, verify=True, use_nih=False, cachedir=None):
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
    # These are still handled by the old system for now

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
    # Registry-based lookup will handle all BMC journals after this section
    if jrnl.find('BMC') == 0:
        try:
            url = the_bmc_boogie(pma, verify)
        except MetaPubError as error:
            reason = str(error)

    if url:
        return (url, reason)

    # === NEW REGISTRY-BASED LOOKUP === #
    # This replaces the old PUBMED_SWITCHBOARD lookup

    try:
        lookup_system = _get_lookup_system(cachedir=cachedir)
        registry_url, registry_reason = lookup_system.find_pdf_url(pma, verify=verify)

        if registry_url:
            return (registry_url, registry_reason)
        elif registry_reason:
            reason = registry_reason

    except Exception as error:
        log.error("Registry lookup failed for journal '%s': %s", jrnl, error)
        reason = f'REGISTRY_ERROR: {error}'

    # === FALLBACK CHECKS === #

    if jrnl in JOURNAL_CANTDO_LIST:
        reason = f'CANTDO: this journal ({jrnl}) has been marked as unsourceable'

    # aka if url is STILL None...
    if not url and not reason:
        reason = f'NOFORMAT: No URL format for journal "{jrnl}"'

    return (url, reason)


def find_article_from_doi(doi, verify=True, use_nih=False, cachedir=None):
    """ Pull a PubMedArticle based on CrossRef lookup (using doi2pmid),
    then run it through find_article_from_pma.

    :param doi: (string)
    :param cachedir: (str) cache directory for registry database
    :return: (url, reason)
    """
    fetch = PubMedFetcher()
    pma = fetch.article_by_pmid(doi2pmid(doi))
    return find_article_from_pma(pma, verify=verify, use_nih=use_nih, cachedir=cachedir)

