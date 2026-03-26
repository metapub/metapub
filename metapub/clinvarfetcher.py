""" metapub.clinvarfetcher: tools for interacting with ClinVar data """

# TODO: Add logging

from lxml import etree

from .clinvarvariant import ClinVarVariant
from .exceptions import MetaPubError, BaseXMLError
from .eutils_common import get_eutils_client
from .cache_utils import get_cache_path 
from .base import Borg, parse_elink_response
from .ncbi_errors import diagnose_ncbi_error, NCBIServiceError

class ClinVarFetcher(Borg):
    """ ClinVarFetcher (a Borg singleton object)

    Toolkit for retrieval of ClinVar information. 

    Set optional 'cachedir' parameter to absolute path of preferred directory 
    if desired; cachedir defaults to <current user directory> + /.cache

        clinvar = ClinVarFetcher()

        clinvar = ClinVarFetcher(cachedir='/path/to/cachedir')

    Usage
    -----

    Get ClinVar accession IDs for gene name (switch single_gene to True to filter out 
    results containing more genes than the specified gene being searched, default False).

        cv_ids = clinvar.ids_by_gene('FGFR3', single_gene=True)

    Get ClinVar accession in python dictionary format for given ID:

        cv_subm = clinvar.accession(65533)  # can also submit ID as string 

    Get list of pubmed IDs (pmids) for given ClinVar accession ID:

        pmids = clinvar.pmids_for_id(65533)  # can also submit ID as string

    Get list of pubmed IDs (pmids) for hgvs string:

        pmids = clinvar.pmids_for_hgvs('NM_017547.3:c.1289A>G')

    For more info, see the ClinVar eutils page:
    https://www.ncbi.nlm.nih.gov/clinvar/docs/maintenance_use/
    """

    _cache_filename = 'clinvarfetcher.db'

    def __init__(self, method='eutils', cachedir='default'):
        """Initialize ClinVarFetcher for clinical variant data retrieval.
        
        Args:
            method (str, optional): Service method to use. Currently only 'eutils'
                is supported. Defaults to 'eutils'.
            cachedir (str, optional): Directory for caching responses. Use 'default'
                for system cache directory. Defaults to 'default'.
        
        Raises:
            NotImplementedError: If an unsupported method is specified.
        
        Note:
            This is a Borg singleton - all instances share the same state.
            Provides access to NCBI's ClinVar database for clinical significance
            of genetic variants, gene-disease relationships, and variant literature.
        """
        self.method = method
        self._cache_path = None

        if method=='eutils':
            self._cache_path = get_cache_path(cachedir, self._cache_filename)
            self.qs = get_eutils_client(self._cache_path) 
            self.ids_by_gene = self._eutils_ids_by_gene
            self.get_accession = self._eutils_get_accession
            self.pmids_for_id = self._eutils_pmids_for_id
            self.ids_for_variant = self._eutils_ids_for_variant
            self.ids_by_gene_and_cdot = self._eutils_ids_by_gene_and_cdot
            self.ids_by_gene_and_pdot = self._eutils_ids_by_gene_and_pdot
            self.pmids_for_hgvs = self._eutils_pmids_for_hgvs
            self.variant = self._eutils_get_variant_summary
        else:
            raise NotImplementedError('coming soon: fetch from local clinvar via medgen-mysql.')

    @staticmethod
    def _normalize_dot_change(dot_value, prefix):
        """Normalize c./p. change text into a consistent comparison form."""
        text = (dot_value or '').strip()
        if not text:
            return ''

        lower = text.lower()
        if not lower.startswith(prefix):
            lower = '%s%s' % (prefix, lower)
        return lower

    def _resolve_hgvs_for_gene_and_cdot(self, gene, c_dot):
        """Resolve all matching coding HGVS strings from gene plus c. shorthand input."""
        gene = (gene or '').strip()
        if not gene:
            raise MetaPubError('Gene symbol is required.')

        prefix = 'c.'
        normalized_dot = self._normalize_dot_change(c_dot, prefix)
        if not normalized_dot:
            raise MetaPubError('%s change text is required.' % prefix)

        candidate_ids = self._eutils_ids_by_gene(gene, single_gene=True)
        if not candidate_ids:
            candidate_ids = self._eutils_ids_by_gene(gene, single_gene=False)

        matches = []
        for clinvar_id in candidate_ids:
            try:
                variant = self._eutils_get_variant_summary(clinvar_id)
            except Exception:
                continue

            symbols = [entry.get('Symbol', '').upper() for entry in variant.genes if isinstance(entry, dict)]
            if gene.upper() not in symbols:
                continue

            hgvs_values = variant.hgvs_c
            for hgvs in hgvs_values:
                if ':' not in hgvs:
                    continue
                accession, change = hgvs.split(':', 1)
                if self._normalize_dot_change(change, prefix) == normalized_dot:
                    matches.append(hgvs)

        if not matches:
            raise MetaPubError(
                'No ClinVar HGVS match found for gene %s and %s change %s.'
                % (gene, prefix, c_dot)
            )
        return list(dict.fromkeys(matches))

    def _resolve_hgvs_for_gene_and_pdot(self, gene, p_dot):
        """Resolve all matching protein HGVS strings from gene plus p. shorthand input."""
        gene = (gene or '').strip()
        if not gene:
            raise MetaPubError('Gene symbol is required.')

        prefix = 'p.'
        normalized_dot = self._normalize_dot_change(p_dot, prefix)
        if not normalized_dot:
            raise MetaPubError('%s change text is required.' % prefix)

        candidate_ids = self._eutils_ids_by_gene(gene, single_gene=True)
        if not candidate_ids:
            candidate_ids = self._eutils_ids_by_gene(gene, single_gene=False)

        matches = []
        for clinvar_id in candidate_ids:
            try:
                variant = self._eutils_get_variant_summary(clinvar_id)
            except Exception:
                continue

            symbols = [entry.get('Symbol', '').upper() for entry in variant.genes if isinstance(entry, dict)]
            if gene.upper() not in symbols:
                continue

            hgvs_values = variant.hgvs_p
            for hgvs in hgvs_values:
                if ':' not in hgvs:
                    continue
                accession, change = hgvs.split(':', 1)
                if self._normalize_dot_change(change, prefix) == normalized_dot:
                    matches.append(hgvs)

        if not matches:
            raise MetaPubError(
                'No ClinVar HGVS match found for gene %s and %s change %s.'
                % (gene, prefix, p_dot)
            )
        return list(dict.fromkeys(matches))

    def _eutils_get_accession(self, accession_id):
        """ returns python dict of info for given ClinVar accession ID.

        :param: accession_id (integer or string)
        :return: dictionary
        :raises: NCBIServiceError if ClinVar service is down
        """
        try:
            result = self.qs.esummary({'db': 'clinvar', 'id': accession_id, 'retmode': 'json'})
            return result
        except Exception as e:
            # Handle ClinVar accession lookup errors
            diagnosis = diagnose_ncbi_error(e, 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi')
            if diagnosis['is_service_issue']:
                raise NCBIServiceError(
                    f"Unable to fetch ClinVar accession '{accession_id}': {diagnosis['user_message']}", 
                    diagnosis['error_type'], 
                    diagnosis['suggested_actions']
                ) from e
            else:
                raise

    def _eutils_get_variant_summary(self, accession_id):
        """ returns variant summary XML (<ClinVarResult-Set>) for given ClinVar accession ID.
        (This corresponds to the entry in the clinvar.variant_summary table.)
        """
        result = self.qs.efetch({'db': 'clinvar', 'id': accession_id, 'rettype': 'vcv'})
        try:
            return ClinVarVariant(result)
        except BaseXMLError as error:
            # empty XML document == invalid variant ID
            print(error)
            raise MetaPubError('Invalid ClinVar Variation ID')

    def _eutils_ids_by_gene(self, gene, single_gene=False):
        """
        searches ClinVar for specified gene (HUGO); returns up to 500 matching results.

        :param: gene (string) - gene name in HUGO naming convention.
        :param: single_gene (bool) [default: False] - restrict results to single-gene accessions.
        :return: list of clinvar ids (strings)
        """
        # equivalent esearch:
        # https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=clinvar&term=FGFR3[gene]&retmax=500

        result = self.qs.esearch(
            {
                "db": "clinvar",
                "term": gene + "[gene]",
                "single_gene": single_gene,
                "sort": "relevance",
            }
        )
        dom = etree.fromstring(result)
        ids = []
        idlist = dom.find('IdList')
        for item in idlist.findall('Id'):
            ids.append(item.text.strip())
        return ids

    def _eutils_pmids_for_id(self, clinvar_id):
        """
        example:
        https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=clinvar&db=pubmed&id=9

        :param: clinvar_id (integer or string)
        :return: list of pubmed IDs (strings)
        """
        xmlstr = self.qs.elink({'dbfrom': 'clinvar', 'id': clinvar_id, 'db': 'pubmed'})
        return parse_elink_response(xmlstr)

    def _eutils_ids_for_variant(self, hgvs_c):
        """ returns ClinVar IDs for given HGVS c. string

        :param: hgvs_c (string)
        :return: list of pubmed IDs (strings)
        """
        result = self.qs.esearch(
            {"db": "clinvar", "term": '"%s"' % hgvs_c, "sort": "relevance"}
        )
        dom = etree.fromstring(result)
        ids = []
        idlist = dom.find('IdList')
        for item in idlist.findall('Id'):
            ids.append(item.text.strip())
        return ids

    def _eutils_ids_by_gene_and_cdot(self, gene, c_dot):
        """Return ClinVar IDs from gene + c. notation using HGVS resolution."""
        normalized_cdot = self._normalize_dot_change(c_dot, 'c.')
        hgvs_c_list = self._resolve_hgvs_for_gene_and_cdot(gene, normalized_cdot)
        ids = []
        for hgvs_c in hgvs_c_list:
            ids.extend(self._eutils_ids_for_variant(hgvs_c))
        return list(dict.fromkeys(ids))

    def _eutils_ids_by_gene_and_pdot(self, gene, p_dot):
        """Return ClinVar IDs from gene + p. notation using HGVS resolution."""
        normalized_pdot = self._normalize_dot_change(p_dot, 'p.')
        hgvs_p_list = self._resolve_hgvs_for_gene_and_pdot(gene, normalized_pdot)
        ids = []
        for hgvs_p in hgvs_p_list:
            ids.extend(self._eutils_ids_for_variant(hgvs_p))
        return list(dict.fromkeys(ids))

    def _eutils_pmids_for_hgvs(self, hgvs_text):
        """ returns pubmed IDs for given HGVS c. string

        :param hgvs_text:
        :return: list of pubmed IDs
        """
        ids = self._eutils_ids_for_variant(hgvs_text)
        if len(ids) > 1:
            print('Warning: more than one ClinVar id returned for term %s' % hgvs_text)
        pmids = set()
        for clinvar_id in ids:
            pmids.update(self._eutils_pmids_for_id(clinvar_id))
        return list(pmids)
