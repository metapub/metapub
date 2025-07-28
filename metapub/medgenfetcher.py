from __future__ import absolute_import, unicode_literals

"""metapub.MedGenFetcher -- tools to deal with NCBI's E-utilities interface to the MedGen db"""

from lxml import etree

from .eutils_common import get_eutils_client
from .cache_utils import get_cache_path 
from .exceptions import MetaPubError
from .medgenconcept import MedGenConcept
from .base import Borg, parse_elink_response
from .config import DEFAULT_EMAIL
from .ncbi_errors import diagnose_ncbi_error, NCBIServiceError


class MedGenFetcher(Borg):
    """ MedGenFetcher (a Borg singleton object)

    An interaction layer for querying to return MedGenConcept objects.
    
    Currently available methods: eutils

    Basic Usage:

        fetch = MedGenFetcher()
    
    To specify a service method (more coming soon):

        fetch = MedGenFetcher('eutils')

    To return a MedGenConcept from a known UID:

        concept = fetch.concept_by_uid(known_UID)

    To return a list of UIDs relevant to a given term known in medgen:

        uids = fetch.uids_by_term(some_term)

    To get a medgen UID given a known Concept ID (cui):

        uid = fetch.uid_for_cui(known_cui)
    """

    _cache_filename = 'medgenfetcher.db'

    def __init__(self, method='eutils', cachedir='default'):
        """Initialize MedGenFetcher for medical genetics concept retrieval.
        
        Args:
            method (str, optional): Service method to use. Currently only 'eutils'
                is supported. Defaults to 'eutils'.
            cachedir (str, optional): Directory for caching responses. Use 'default'
                for system cache directory. Defaults to 'default'.
        
        Raises:
            NotImplementedError: If an unsupported method is specified.
        
        Note:
            This is a Borg singleton - all instances share the same state.
            Provides access to NCBI's MedGen database for medical genetics concepts,
            diseases, and gene-phenotype relationships.
        """
        self.method = method
        self._cache_path = None

        if method == 'eutils':
            self._cache_path = get_cache_path(cachedir, self._cache_filename)
            self.qs = get_eutils_client(self._cache_path)
            self.uids_by_term = self._eutils_uids_by_term
            self.concept_by_uid = self._eutils_concept_by_uid
            self.concept_by_cui = self._eutils_concept_by_cui
            self.uid_for_cui = self._eutils_uid_for_cui
            self.pubmeds_for_uid = self._eutils_pubmeds_for_uid
            self.pubmeds_for_cui = self._eutils_pubmeds_for_cui
        else:
            raise NotImplementedError('coming soon: fetch from local medgen via medgen-mysql.')

    def _eutils_uids_by_term(self, term):
        """ Wraps results of an medgen efetch term lookup, returning IDs of related MedGenConcepts.

        :param term: (str)
        :return uids: list of medgen uids
        :rtype: list
        :raises: NCBIServiceError if MedGen service is down
        """
        try:
            # http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=medgen&term=OCRL
            result = self.qs.esearch({"db": "medgen", "term": term, "sort": "relevance"})
            dom = etree.fromstring(result)
            uids = []
            idlist = dom.find('IdList')
            if idlist is not None:
                for item in idlist.findall('Id'):
                    uids.append(item.text.strip())
            return uids
        except Exception as e:
            # Handle MedGen search errors with intelligent diagnosis
            diagnosis = diagnose_ncbi_error(e, 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi')
            if diagnosis['is_service_issue']:
                raise NCBIServiceError(
                    f"Unable to search MedGen for term '{term}': {diagnosis['user_message']}", 
                    diagnosis['error_type'], 
                    diagnosis['suggested_actions']
                ) from e
            else:
                raise

    def _eutils_uid_for_cui(self, cui):
        """ Given a ConceptID (cui), return a medgen ID.

        :param cui: (str)
        :return uid: (str)
        :rtype: str
        :raises: NCBIServiceError if MedGen service is down
        """
        # http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=medgen&term=C0000039
        if not cui.startswith('C'):
            raise MetaPubError('Invalid CUID: must start with C (e.g. C0000039)')

        try:
            result = self.qs.esearch({"db": "medgen", "term": cui, "sort": "relevance"})
            root = etree.fromstring(result).getroottree()
            try:
                uid = root.find('IdList').find('Id').text.strip()
            except AttributeError:
                raise MetaPubError('Invalid CUID: did not return MedGen id.')
            return uid
        except NCBIServiceError:
            raise  # Re-raise service errors
        except MetaPubError:
            raise  # Re-raise validation errors
        except Exception as e:
            # Handle MedGen CUI lookup errors
            diagnosis = diagnose_ncbi_error(e, 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi')
            if diagnosis['is_service_issue']:
                raise NCBIServiceError(
                    f"Unable to lookup MedGen CUI '{cui}': {diagnosis['user_message']}", 
                    diagnosis['error_type'], 
                    diagnosis['suggested_actions']
                ) from e
            else:
                raise

    def _eutils_concept_by_uid(self, uid):
        """ Returns MedGenConcept result of lookup of medgen uid.
        
        :param uid: (string or int) medgen uid
        :return: MedGenConcept or None
        :rtype: MedGenConcept object
        :raises: NCBIServiceError if MedGen service is down
        """
        try:
            # http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=medgen&id=336867
            uid = str(uid)
            result = self.qs.esummary({'db': 'medgen', 'id': uid})
            return MedGenConcept(result)
        except Exception as e:
            # Handle MedGen concept lookup errors
            diagnosis = diagnose_ncbi_error(e, 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi')
            if diagnosis['is_service_issue']:
                raise NCBIServiceError(
                    f"Unable to fetch MedGen concept for UID '{uid}': {diagnosis['user_message']}", 
                    diagnosis['error_type'], 
                    diagnosis['suggested_actions']
                ) from e
            else:
                raise

    def _eutils_concept_by_cui(self, cui):
        """ Returns MedGenConcept result of lookup of CUI.
        
        :param cui: (string) Concept id (CUI)
        :return: MedGenConcept or None
        :rtype: MedGenConcept object
        """
        uid = self._eutils_uid_for_cui(cui)
        return self._eutils_concept_by_uid(uid)

    def _eutils_pubmeds_for_uid(self, uid):
        """ Returns list of pubmed IDs linked to this Medgen UID.

        :param uid: (str) Medgen UID
        :return: list of pubmed IDs (strings) or empty list
        :rtype: list
        """
        response = self.qs.elink({'dbfrom': 'medgen', 'id': uid, 'db': 'pubmed'})
        ids = parse_elink_response(response)
        return ids

    def _eutils_pubmeds_for_cui(self, cui):
        """ Given a ConceptID (cui), return a list of related pubmed article IDs.

        :param cui: (str) Medgen Concept ID (CUI)
        :return: list of pubmed IDs (strings) or empty list
        :rtype: list
        """
        uid = self._eutils_uid_for_cui(cui)
        return self._eutils_pubmeds_for_uid(uid)
