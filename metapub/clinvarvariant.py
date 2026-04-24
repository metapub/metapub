"""metapub.clinvarvariant -- ClinVarVariant class instantiated by supplying ESummary XML string."""

from datetime import datetime
from typing import Optional, Literal
from dataclasses import dataclass

from .base import MetaPubObject
from .exceptions import MetaPubError, BaseXMLError
from lxml import etree
from .types import XRef, XRefDb, ClinSig, MolecularConsequenceInfo, PathogenicSummary, SPDIInfo

#TODO: Logging

class CanonicalSPDI:
    """Standardized variant notation, relative to the latest genomic assembly."""
    raw: str # raw spdi string, ex: NC_000001.11:230710047:A:G
    # sequence:position:deletion:insertion

    def __init__(self, raw):
        self.raw = raw
    
    def __str__(self):
        return F"SPDI({self.raw})"
    def __dir__(self):
        return F"SPDI({self.raw})"

    def parse(self) -> SPDIInfo:
        # Perform basic parsing on the variant
        nc, *rest = self.raw.upper().split(":")
        if nc.startswith("NC_"):
            try:
                # Parse out the chromosome number
                nc_info = nc.split("_")[1]
                ver = None
                if "." in nc_info:
                    # There is additionally a version specified
                    [chr, ver] = [int(x) for x in nc_info.split(".")]
                else:
                    chr = int(nc.split("_")[1])
                # Get position, deleted, and replaced
                pos, deleted, replaced = rest
                # NC_000012.12:32625058:AGAG:AG
                pos = int(pos)
                return SPDIInfo(chr, pos, deleted, replaced, ver, "GRCh38")
            except Exception as e:
                # Throw error (likely a parsing error)
                raise MetaPubError(F"Unable to parse canonical SPDI: {e}")
        else:
            raise MetaPubError("Unable to parse canonical SPDI")

class ClinVarVariant(MetaPubObject):

    def __init__(self, xmlstr, *args, **kwargs):
        # Try new VCV format first, fall back to old format for backwards compatibility
        try:
            # Parse the full XML document first to determine format
            from lxml import etree
            dom = etree.fromstring(xmlstr)

            if dom.tag == 'ClinVarResult-Set':
                # New VCV format
                self._is_vcv_format = True
                super(ClinVarVariant, self).__init__(xmlstr, None, args, kwargs)  # Parse full document
                self.variation_archive = self.content.find('VariationArchive')
                if self.variation_archive is None:
                    # Check if this is an empty result set (invalid ID)
                    set_elem = self.content.find('set')
                    if set_elem is not None and len(set_elem) == 0:
                        raise BaseXMLError('Empty XML document')  # This will trigger the "Invalid ClinVar Variation ID" error
                    else:
                        raise BaseXMLError('No VariationArchive found in VCV format')
            else:
                # Old format: VariationReport is the root element itself, not a child to find
                self._is_vcv_format = False
                super(ClinVarVariant, self).__init__(xmlstr, None, args, kwargs)
                self.variation_archive = None
        except (etree.XMLSyntaxError, BaseXMLError) as e:
            # If XML parsing fails completely, let it bubble up
            raise BaseXMLError('Invalid XML document: %s' % str(e))

        if self.content is None:
            raise BaseXMLError('Empty XML document')

        if self._get('error'):
            raise MetaPubError('Supplied XML for ClinVarVariant contained explicit error: %s' % self._get('error'))

        # VariationReport basic details
        self.variation_id = self._get_variation_id()
        self.variation_name = self._get_variation_name()
        self.variation_type = self._get_variation_type()
        self.date_created = self._get_date_created()
        self.date_last_updated = self._get_date_last_updated()
        self.submitter_count = self._get_submitter_count()
        self.record_status = self._get_record_status()
        self.version = self._get_version()

        # Species Info
        self.species = self._get_species()
        self.taxonomy_id = self._get_taxonomy_id()

        # Gene List
        self.genes = self._get_gene_list()

        # Allele Info
        self.cytogenic_location = self._get_cytogenic_location()
        self.sequence_locations = self._get_sequence_locations()
        self.hgvs = self._get_hgvs_list()
        self.xrefs = self._get_xref_list()
        self.molecular_consequences = self._get_molecular_consequence_list()
        self.allele_frequencies = self._get_allele_frequency_list()
        # Clinical significance and classifications (new in VCV format)
        self.clinical_significance = self._get_clinical_significance()
        self.review_status = self._get_review_status()
        self.date_last_evaluated = self._get_date_last_evaluated()
        self.number_of_submissions = self._get_number_of_submissions()
        self.number_of_submitters = self._get_number_of_submitters()
        self.pathogenic_summary = self._get_pathogenic_summary()

        # VCV record metadata (new in VCV format)
        self.vcv_accession = self._get_vcv_accession()
        self.record_type = self._get_record_type()
        self.most_recent_submission = self._get_most_recent_submission()

        # Associated conditions/diseases (new in VCV format)
        self.associated_conditions = self._get_associated_conditions()

        # Enhanced molecular consequences (new in VCV format)
        self.molecular_consequences_detailed = self._get_molecular_consequences_detailed()

        # Enhanced sequence details (new in VCV format)
        self.sequence_details = self._get_sequence_details()

        # Enhanced gene information (new in VCV format)
        self.gene_dosage_info = self._get_gene_dosage_info()

        # Protein change summary (new in VCV format)
        self.protein_change = self._get_protein_change()

        # Clinical assertions (new in VCV format)
        self.clinical_assertions = self._get_clinical_assertions()

        # Enhanced citations (new in VCV format)
        self.citations = self._get_citations()

        # Canonical SPDI
        self.spdi = self._get_spdi()

        # Observations


    def to_dict(self):
        """ returns a dictionary composed of all extractable properties of this concept. """
        outd = self.__dict__.copy()
        outd.pop('content')
        return outd

    ### HGVS string convenience properties

    def _get_hgvs_or_empty_list(self, hgvsdict):
        try:
            # Check if this is old format
            if 'AccessionVersion' in hgvsdict and 'Change' in hgvsdict:
                accession = hgvsdict['AccessionVersion']
                change = hgvsdict['Change']
                return [accession + ':' + change]
            # Check if this is new VCV format with separate protein change
            elif 'ProteinAccessionVersion' in hgvsdict and 'ProteinChange' in hgvsdict:
                accession = hgvsdict['ProteinAccessionVersion']
                change = hgvsdict['ProteinChange']
                return [accession + ':' + change]
            else:
                return []
        except KeyError:
            # example of missing Change: ClinVar ID 409
            # example of missing AccessionVersion:  ClinVar ID 11344
            return []

    @property
    def hgvs_c(self):
        """ Returns a list of all coding HGVS strings from the Allelle data. """
        strlist = []
        for hgvsdict in self.hgvs:
            if hgvsdict['Type'].find('coding') > -1:
                strlist = strlist + self._get_hgvs_or_empty_list(hgvsdict)
        return strlist

    @property
    def hgvs_g(self):
        """ Returns a list of all genomic HGVS strings from the Allelle data. """
        strlist = []
        for hgvsdict in self.hgvs:
            if hgvsdict['Type'].find('genomic') > -1:
                strlist = strlist + self._get_hgvs_or_empty_list(hgvsdict)
        return strlist

    @property
    def hgvs_p(self):
        """ Returns a list of all protein effect HGVS strings from the Allelle data. """
        strlist = []
        for hgvsdict in self.hgvs:
            # Look for dedicated protein type entries
            if hgvsdict['Type'].find('protein') > -1:
                strlist = strlist + self._get_hgvs_or_empty_list(hgvsdict)
            # Also look for protein changes in coding entries
            elif hgvsdict['Type'].find('coding') > -1 and 'ProteinAccessionVersion' in hgvsdict:
                try:
                    accession = hgvsdict['ProteinAccessionVersion']
                    change = hgvsdict['ProteinChange']
                    strlist.append(accession + ':' + change)
                except KeyError:
                    pass
        return strlist

    ### VariationReport basic info

    def _get_variation_id(self):
        if self._is_vcv_format:
            return self.variation_archive.get('VariationID')
        else:
            return self.content.get('VariationID')

    def _get_variation_name(self):
        if self._is_vcv_format:
            return self.variation_archive.get('VariationName')
        else:
            return self.content.get('VariationName')

    def _get_variation_type(self):
        if self._is_vcv_format:
            return self.variation_archive.get('VariationType')
        else:
            return self.content.get('VariationType')

    def _get_date_created(self):
        if self._is_vcv_format:
            datestr = self.variation_archive.get('DateCreated')
        else:
            datestr = self.content.get('DateCreated')

        if datestr:
            return datetime.strptime(datestr, '%Y-%m-%d')
        else:
            return None

    def _get_date_last_updated(self):
        if self._is_vcv_format:
            datestr = self.variation_archive.get('DateLastUpdated')
        else:
            datestr = self.content.get('DateLastUpdated')

        if datestr:
            return datetime.strptime(datestr, '%Y-%m-%d')
        else:
            return None

    def _get_submitter_count(self):
        if self._is_vcv_format:
            count_attr = self.variation_archive.get('NumberOfSubmitters')
        else:
            count_attr = self.content.get('SubmitterCount')

        try:
            return int(count_attr) if count_attr else None
        except (TypeError, ValueError):
            return None

    def _get_species(self):
        if self._is_vcv_format:
            species_elem = self.variation_archive.find('Species')
            return species_elem.text if species_elem is not None else None
        else:
            return self._get('Species')

    def _get_taxonomy_id(self):
        if self._is_vcv_format:
            # In VCV format, taxonomy ID is not typically provided in the same way
            return None
        else:
            species_elem = self.content.find('Species')
            return species_elem.get('TaxonomyId') if species_elem is not None else None

    def _get_record_status(self):
        if self._is_vcv_format:
            record_status = self.variation_archive.find('RecordStatus')
        else:
            record_status = self._get('RecordStatus')

        return record_status.text if record_status is not None else None

    def _get_version(self):
        if self._is_vcv_format:
            record_status = self.variation_archive.get('Version')
        else:
            record_status = self.content.get('Version')

        return record_status

    def _get_spdi(self):
        """ Get the SPDI information for this particular variant.

        Returns CanonicalSPDI format; to parse the chromosome/position/etc, use .parse()
        """
        if self._is_vcv_format:
            allele = self.variation_archive.find('ClassifiedRecord/SimpleAllele')
            if allele is not None:
                record_status = allele.find("CanonicalSPDI")
            else:
                record_status = None
        else:
            record_status = None

        return CanonicalSPDI(record_status.text) if record_status is not None else None

    #### GENE LIST

    def _get_gene_list(self):
        """ Returns a list of dictionaries representing each gene associated with this variant.

        Keys in gene dictionary vary by format but include: 'Symbol', 'FullName', 'GeneID', 'HGNC_ID', etc.
        """
        genes = []

        if self._is_vcv_format:
            # In VCV format: VariationArchive/ClassifiedRecord/SimpleAllele/GeneList/Gene
            simple_allele = self.variation_archive.find('ClassifiedRecord/SimpleAllele')
            if simple_allele is not None:
                genelist = simple_allele.find('GeneList')
                if genelist is not None:
                    for gene_elem in genelist.findall('Gene'):
                        gene_dict = dict(gene_elem.items())
                        # Also capture OMIM and Property elements as text
                        omim_elem = gene_elem.find('OMIM')
                        if omim_elem is not None:
                            gene_dict['OMIM'] = omim_elem.text

                        property_elem = gene_elem.find('Property')
                        if property_elem is not None:
                            gene_dict['Property'] = property_elem.text

                        genes.append(gene_dict)
        else:
            # Old format: VariationReport/GeneList/Gene
            genelist = self.content.find('GeneList')
            if genelist is not None:
                for gene_elem in genelist.getchildren():
                    genes.append(dict(gene_elem.items()))

        return genes


    ### ALLELE INFORMATION

    def _get_allele_id(self):
        if self._is_vcv_format:
            simple_allele = self.variation_archive.find('ClassifiedRecord/SimpleAllele')
            return simple_allele.get('AlleleID') if simple_allele is not None else None
        else:
            allele_elem = self.content.find('Allele')
            return allele_elem.get('AlleleID') if allele_elem is not None else None

    def _get_cytogenic_location(self):
        if self._is_vcv_format:
            simple_allele = self.variation_archive.find('ClassifiedRecord/SimpleAllele')
            if simple_allele is not None:
                location = simple_allele.find('Location/CytogeneticLocation')
                return location.text if location is not None else None
        else:
            return self._get('Allele/CytogeneticLocation')
        return None

    def _get_sequence_locations(self):
        seqlocs = []

        if self._is_vcv_format:
            simple_allele = self.variation_archive.find('ClassifiedRecord/SimpleAllele')
            if simple_allele is not None:
                for elem in simple_allele.findall('Location/SequenceLocation'):
                    seqlocs.append(dict(elem.items()))
        else:
            for elem in self.content.findall('Allele/SequenceLocation'):
                seqlocs.append(dict(elem.items()))

        return seqlocs

    def _get_hgvs_list(self):
        hgvs = []

        if self._is_vcv_format:
            # In VCV format: VariationArchive/ClassifiedRecord/SimpleAllele/HGVSlist/HGVS
            simple_allele = self.variation_archive.find('ClassifiedRecord/SimpleAllele')
            if simple_allele is not None:
                hgvs_list = simple_allele.find('HGVSlist')
                if hgvs_list is not None:
                    for hgvs_elem in hgvs_list.findall('HGVS'):
                        hgvs_dict = dict(hgvs_elem.items())

                        # Get NucleotideExpression details
                        nuc_expr = hgvs_elem.find('NucleotideExpression')
                        if nuc_expr is not None:
                            hgvs_dict['AccessionVersion'] = nuc_expr.get('sequenceAccessionVersion', '')
                            hgvs_dict['Change'] = nuc_expr.get('change', '')

                        # Get ProteinExpression details if available
                        prot_expr = hgvs_elem.find('ProteinExpression')
                        if prot_expr is not None:
                            hgvs_dict['ProteinAccessionVersion'] = prot_expr.get('sequenceAccessionVersion', '')
                            hgvs_dict['ProteinChange'] = prot_expr.get('change', '')

                        hgvs.append(hgvs_dict)
        else:
            # Old format: VariationReport/Allele/HGVSlist
            try:
                for elem in self.content.find('Allele/HGVSlist').getchildren():
                    hgvs.append(dict(elem.items()))
            except AttributeError:
                return []

        return hgvs

    def _get_xref_list(self) -> list[XRef]:
        """Return all allele-level ``<XRef>`` elements from this variant's XML.

        For VCV-format records, collects ``<XRef>`` nodes from every
        ``SimpleAllele/XRefList`` regardless of nesting depth — a ``SimpleAllele``
        may be a direct child of ``ClassifiedRecord`` (simple variants) or nested
        inside a ``Haplotype`` or ``Genotype`` element (complex variants). Using
        ``findall('.//SimpleAllele/XRefList')`` ensures xrefs from all constituent
        alleles are collected rather than only the first one.

        For legacy ``VariationReport`` records (retired April 2019), collects from
        ``Allele/XRefList`` instead.

        :return: List of :class:`XRef` dicts, one per ``<XRef>`` element found.
            Returns an empty list when no ``XRefList`` is present.
        :rtype: list[XRef]
        """
        xrefs: list[XRef] = []

        # BG: #126: SimpleAllele may be nested under Haplotype or Genotype for complex variants;
        # BG: #126: .// ensures we collect rsIDs from all constituent alleles.
        # BG: #126: Ex)
        # ClassifiedRecord
        # └── Haplotype
        #     ├── SimpleAllele (AlleleID="404202", c.875T>C)
        #     │   └── XRefList
        #     │       ├── XRef DB="ClinGen"
        #     │       ├── XRef Type="rs" ID="1060500602" DB="dbSNP"
        #     │       └── XRef Type="Interpreted" DB="ClinVar"
        #     └── SimpleAllele (AlleleID="929246", c.877C>T)
        #         └── XRefList
        #             ├── XRef DB="ClinGen"
        #             ├── XRef Type="rs" ID="2081099943" DB="dbSNP"
        #             └── XRef Type="Interpreted" DB="ClinVar"
        path = './/SimpleAllele/XRefList' if self._is_vcv_format else './/Allele/XRefList'
        for xref_list in self.content.findall(path):
            for elem in xref_list:
                xref: XRef = dict(elem.items())
                xrefs.append(xref)

        return xrefs

    def _get_molecular_consequence_list(self):
        molcons = []

        if self._is_vcv_format:
            simple_allele = self.variation_archive.find('ClassifiedRecord/SimpleAllele')
            if simple_allele is not None:
                molcon_list = simple_allele.find('MolecularConsequenceList')
                if molcon_list is not None:
                    for elem in molcon_list.getchildren():
                        molcons.append(dict(elem.items()))
        else:
            try:
                molcon_list = self.content.find('Allele/MolecularConsequenceList')
                if molcon_list is not None:
                    for elem in molcon_list.getchildren():
                        molcons.append(dict(elem.items()))
            except AttributeError:
                return []

        return molcons

    def _get_allele_frequency_list(self):
        freqs = []

        if self._is_vcv_format:
            simple_allele = self.variation_archive.find('ClassifiedRecord/SimpleAllele')
            if simple_allele is not None:
                freq_list = simple_allele.find('AlleleFrequencyList')
                if freq_list is not None:
                    for elem in freq_list.getchildren():
                        freqs.append(dict(elem.items()))
        else:
            try:
                freq_list = self.content.find('Allele/AlleleFrequencyList')
                if freq_list is not None:
                    for elem in freq_list.getchildren():
                        freqs.append(dict(elem.items()))
            except AttributeError:
                return []

        return freqs
    
    @property
    def rsid(self) -> Optional[str]:
        """Return the first dbSNP rsID for this variant as a bare numeric string.

        :return: rsID digits (e.g. ``'28934872'``), or ``None`` if no dbSNP xref is present.
        :rtype: str or None
        """
        rsids = self._get_rsids()
        return rsids[0] if rsids else None

    @property
    def rsids(self) -> list[str]:
        """Return all dbSNP rsIDs for this variant as bare numeric strings.

        :return: List of rsID digit strings (e.g. ``['28934872']``), empty list if none.
        :rtype: list[str]
        """
        return self._get_rsids()

    def _get_rsids(self) -> list[str]:
        """Return all dbSNP xref IDs normalized to bare numeric strings.

        Handles the four ``<XRef DB="dbSNP">`` formats observed in real ClinVar XML:
        ``Type="rs"``, ``Type="rsNumber"``, ``ID="rs1799945"`` (prefix in ID field),
        and bare number with no ``Type`` attribute. All are normalized to plain digits
        (e.g. ``'1799945'``). Deduplication occurs *after* normalization so that
        ``"1799945"`` and ``"rs1799945"`` collapse to a single entry.

        :return: Deduplicated list of rsID digit strings in first-seen order.
        :rtype: list[str]
        """

        # BG: #128: Ensure all rsids are formatted as "<number>"
        # BG: #128: The following formatted strings have been seen from ClinVar XML data:
        # <XRef Type="rs" ID="1555371642" DB="dbSNP"/>      Y (Idiomatic)
        # <XRef Type="rsNumber" ID="1799945" DB="dbSNP"/>  	N (Type mismatch)
        # <XRef ID="rs1799945" DB="dbSNP"/> 			    N (rs joined to ID)
        # <XRef ID="1799945" DB="dbSNP"/> 					N (Missing type)
        # BG: #128: The return type is number as string to maintain consistency in the API surface
        ids = self._get_xref_ids(XRefDb.DBSNP)
        rs_prefix = "rs"

        for i, rsid in enumerate(ids):
            if rsid.startswith(rs_prefix):
                ids[i] = rsid.removeprefix(rs_prefix)

        # BG: Deduplicate with first-seen order preserved
        ids_deduped = list(dict.fromkeys(ids))

        return ids_deduped
    
    @property
    def dbsnp_id(self) -> Optional[str]:
        """Return the first dbSNP ID for this variant. Alias for :attr:`rsid`.

        :return: dbSNP identifier string (e.g. ``'28934872'``), or ``None`` if not present.
        :rtype: str or None
        """
        ids = self._get_rsids()
        return ids[0] if ids else None
    
    @property
    def dbsnp_ids(self) -> list[str]:
        """Return all dbSNP IDs for this variant. Alias for :attr:`rsids`.

        :return: List of dbSNP identifier strings, empty list if none.
        :rtype: list[str]
        """
        return self._get_rsids()

    @property
    def omim_id(self) -> Optional[str]:
        """Return the first OMIM ID for this variant.

        :return: OMIM identifier string (e.g. ``'191092.0006'``), or ``None`` if not present.
        :rtype: str or None
        """
        omim_ids = self._get_xref_ids(XRefDb.OMIM)
        return omim_ids[0] if omim_ids else None

    @property
    def omim_ids(self) -> list[str]:
        """Return all OMIM IDs for this variant.

        :return: List of OMIM identifier strings, empty list if none.
        :rtype: list[str]
        """
        return self._get_xref_ids(XRefDb.OMIM)

    @property
    def orphanet_id(self) -> Optional[str]:
        """Return the first Orphanet ID for this variant.

        .. note::
            As of ``ClinVarVCVRelease_00-latest.xml.gz`` (scanned 2026-04-19),
            Orphanet identifiers appear at the condition level (``RCVList``/``TraitSet``),
            not in ``SimpleAllele/XRefList``, so this property may return ``None``
            on all current VCV records. Use :attr:`associated_conditions` instead.

        :return: Orphanet identifier string, or ``None`` if not present.
        :rtype: str or None
        """
        orphanet_ids = self._get_xref_ids(XRefDb.ORPHANET)
        return orphanet_ids[0] if orphanet_ids else None

    @property
    def orphanet_ids(self) -> list[str]:
        """Return all Orphanet IDs for this variant.

        .. note::
            As of ``ClinVarVCVRelease_00-latest.xml.gz`` (scanned 2026-04-19),
            this may return ``[]`` on all current VCV records. See :attr:`orphanet_id`.

        :return: List of Orphanet identifier strings, empty list if none.
        :rtype: list[str]
        """
        return self._get_xref_ids(XRefDb.ORPHANET)

    @property
    def medgen_id(self) -> Optional[str]:
        """Return the first MedGen ID for this variant.

        .. note::
            As of ``ClinVarVCVRelease_00-latest.xml.gz`` (scanned 2026-04-19),
            MedGen identifiers appear at the condition level (``RCVList``/``TraitSet``),
            not in ``SimpleAllele/XRefList``, so this property may return ``None``
            on all current VCV records. Use :attr:`associated_conditions` instead.

        :return: MedGen identifier string, or ``None`` if not present.
        :rtype: str or None
        """
        medgen_ids = self._get_xref_ids(XRefDb.MEDGEN)
        return medgen_ids[0] if medgen_ids else None

    @property
    def medgen_ids(self) -> list[str]:
        """Return all MedGen IDs for this variant.

        .. note::
            As of ``ClinVarVCVRelease_00-latest.xml.gz`` (scanned 2026-04-19),
            this may return ``[]`` on all current VCV records. See :attr:`medgen_id`.

        :return: List of MedGen identifier strings, empty list if none.
        :rtype: list[str]
        """
        return self._get_xref_ids(XRefDb.MEDGEN)

    def _get_xref_ids(self, db_name: str) -> list[str]:
        """Return allele-level xref IDs for the specified database name.

        Filters :attr:`xrefs` by the ``DB`` attribute, ignoring ``Type`` entirely.
        Deduplicates with first-seen order preserved via ``dict.fromkeys``.

        :param db_name: Database name to filter on (e.g. ``'dbSNP'``, ``'OMIM'``).
            Use :class:`XRefDB` constants for safety.
        :type db_name: str
        :return: Deduplicated list of ``ID`` strings whose ``DB`` matches *db_name*.
        :rtype: list[str]
        """
        ids: list[str] = []

        # BG: Do not pay attention to "Type", just "DB" attribute.
        # BG: Ex) <XRef Type="rs" ID="1555371642" DB="dbSNP"/> 
        for xref in self.xrefs:
            if xref['DB'] == db_name:
                ids.append(xref['ID'])

        # BG: Deduplicate with first-seen order preserved
        ids = list(dict.fromkeys(ids))

        return ids

    ### NEW VCV FORMAT ENHANCEMENTS ###

    def _get_clinical_significance(self) -> Optional[ClinSig]:
        """Get the clinical significance classification (e.g., 'pathogenic', 'benign')
        
        A list of all significance classes is available here: https://www.ncbi.nlm.nih.gov/clinvar/docs/clinsig/
        
        **Note**: in this version of Metapub, clinical significance is represented in lowercase.
        Older versions did NOT do this, so make sure to update your code if necessary!
        """
        if not self._is_vcv_format:
            return None

        # Look in Classifications/GermlineClassification/Description
        classifications = self.variation_archive.find('.//Classifications')
        if classifications is not None:
            germline_class = classifications.find('GermlineClassification')
            if germline_class is not None:
                desc_elem = germline_class.find('Description')
                return (desc_elem.text).lower() if desc_elem is not None else None
        return None

    def _get_review_status(self):
        """Get the review status (e.g., 'criteria provided, multiple submitters, no conflicts')"""
        if not self._is_vcv_format:
            return None

        classifications = self.variation_archive.find('.//Classifications')
        if classifications is not None:
            germline_class = classifications.find('GermlineClassification')
            if germline_class is not None:
                review_elem = germline_class.find('ReviewStatus')
                return review_elem.text if review_elem is not None else None
        return None

    def _get_date_last_evaluated(self):
        """Get the date when the clinical significance was last evaluated"""
        if not self._is_vcv_format:
            return None

        classifications = self.variation_archive.find('.//Classifications')
        if classifications is not None:
            germline_class = classifications.find('GermlineClassification')
            if germline_class is not None:
                date_str = germline_class.get('DateLastEvaluated')
                if date_str:
                    try:
                        return datetime.strptime(date_str, '%Y-%m-%d')
                    except ValueError:
                        return None
        return None

    def _get_number_of_submissions(self):
        """Get the number of submissions for this variant"""
        if not self._is_vcv_format:
            return None

        num_str = self.variation_archive.get('NumberOfSubmissions')
        try:
            return int(num_str) if num_str else None
        except (ValueError, TypeError):
            return None

    def _get_number_of_submitters(self):
        """Get the number of submitters for this variant"""
        if not self._is_vcv_format:
            return None

        num_str = self.variation_archive.get('NumberOfSubmitters')
        try:
            return int(num_str) if num_str else None
        except (ValueError, TypeError):
            return None

    def _get_vcv_accession(self):
        """Get the VCV accession number (e.g., 'VCV000012397')"""
        if not self._is_vcv_format:
            return None
        return self.variation_archive.get('Accession')

    def _get_record_type(self):
        """Get the record type (e.g., 'classified')"""
        if not self._is_vcv_format:
            return None
        return self.variation_archive.get('RecordType')

    def _get_most_recent_submission(self):
        """Get the date of the most recent submission"""
        if not self._is_vcv_format:
            return None

        date_str = self.variation_archive.get('MostRecentSubmission')
        if date_str:
            try:
                return datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                return None
        return None

    def _get_associated_conditions(self):
        """Get list of associated conditions/diseases with their MedGen IDs"""
        if not self._is_vcv_format:
            return []

        conditions = []
        rcv_list = self.variation_archive.find('.//RCVList')
        if rcv_list is not None:
            for rcv in rcv_list.findall('RCVAccession'):
                condition_list = rcv.find('ClassifiedConditionList')
                if condition_list is not None:
                    for condition in condition_list.findall('ClassifiedCondition'):
                        cond_dict = {
                            'name': condition.text,
                            'medgen_id': condition.get('ID'),
                            'database': condition.get('DB'),
                            'rcv_accession': rcv.get('Accession'),
                            'rcv_title': rcv.get('Title')
                        }
                        # Avoid duplicates
                        if cond_dict not in conditions:
                            conditions.append(cond_dict)
        return conditions

    def _get_molecular_consequences_detailed(self):
        """Get detailed molecular consequences with Sequence Ontology terms"""
        if not self._is_vcv_format:
            return []

        consequences = []
        simple_allele = self.variation_archive.find('ClassifiedRecord/SimpleAllele')
        if simple_allele is not None:
            hgvs_list = simple_allele.find('HGVSlist')
            if hgvs_list is not None:
                for hgvs_elem in hgvs_list.findall('HGVS'):
                    for mol_cons in hgvs_elem.findall('MolecularConsequence'):
                        consequence = MolecularConsequenceInfo(
                            type=mol_cons.get('Type'),
                            so_id=mol_cons.get('ID'),
                            database=mol_cons.get('DB')
                        )

                        if consequence not in consequences:
                            consequences.append(consequence)
        return consequences

    def _get_sequence_details(self):
        """Get enhanced sequence location details including VCF coordinates"""
        if not self._is_vcv_format:
            return []

        details = []
        simple_allele = self.variation_archive.find('ClassifiedRecord/SimpleAllele')
        if simple_allele is not None:
            location = simple_allele.find('Location')
            if location is not None:
                for seq_loc in location.findall('SequenceLocation'):
                    detail = dict(seq_loc.items())
                    # Convert numeric fields
                    for field in ['start', 'stop', 'display_start', 'display_stop', 'variantLength', 'positionVCF']:
                        if field in detail:
                            try:
                                detail[field] = int(detail[field])
                            except (ValueError, TypeError):
                                pass
                    details.append(detail)
        return details
    
    def _get_pathogenic_summary(self) -> Optional[PathogenicSummary]:
        """ Return the aggregation of per-submitter clinical germline significance classifications 
        into a readable summary.

        Returns a dataclass in the following format:
        {
          counts: {
            'pathogenic': 3,
            'likely pathogenic': 1,
            'uncertain significance': 0,
          }
          ...
          total_submitters: 4,
          consensus: 'pathogenic',
          conflicting': False,
          review_status: 'criteria provided, multiple submitters, no conflicts'
        }
        """
        if not self._is_vcv_format:
            return None
        
        counts: dict[ClinSig, int] = {}
        total = 0
        
        assertion_list = self.variation_archive.find(".//ClinicalAssertionList")
        if assertion_list is not None:
            for assertion in assertion_list.findall('ClinicalAssertion'):
                # TODO: ContributesToAggregateClassification doesn't seem to be inside ClinicalAssertion.
                classification_info = assertion.find("Classification")
                if classification_info is None:
                    continue
                # TODO: support OncogenicityClassification or SomaticClinicalImpact
                germline = classification_info.find("GermlineClassification")
                if germline is not None:
                    cs = germline.text
                    if not cs:
                        continue

                    key = cs.strip().lower()
                    # if a classification was not provided, skip
                    if key == "not provided":
                        continue
                    counts[key] = counts.get(key, 0) + 1
                    total += 1

        # Determine consensus
        consensus = None
        if counts:
            max_count = max(counts.values())
            top_counts: list[ClinSig] = [k for k, v in counts.items() if v == max_count]
            if len(top_counts) == 1:
                consensus = top_counts[0]

        conflicting = "conflicting" in (self.clinical_significance or "").lower()

        return PathogenicSummary(
            counts=counts,
            total_submitters=total,
            consensus=consensus if not conflicting else None,
            conflicting=conflicting,
            review_status=self.review_status
        )

    def _get_gene_dosage_info(self):
        """Get gene dosage sensitivity information"""
        if not self._is_vcv_format:
            return []

        dosage_info = []
        simple_allele = self.variation_archive.find('ClassifiedRecord/SimpleAllele')
        if simple_allele is not None:
            gene_list = simple_allele.find('GeneList')
            if gene_list is not None:
                for gene in gene_list.findall('Gene'):
                    gene_dosage = {'symbol': gene.get('Symbol')}

                    haplo_elem = gene.find('Haploinsufficiency')
                    if haplo_elem is not None:
                        gene_dosage['haploinsufficiency'] = {
                            'classification': haplo_elem.text,
                            'last_evaluated': haplo_elem.get('last_evaluated'),
                            'clingen_url': haplo_elem.get('ClinGen')
                        }

                    triplo_elem = gene.find('Triplosensitivity')
                    if triplo_elem is not None:
                        gene_dosage['triplosensitivity'] = {
                            'classification': triplo_elem.text,
                            'last_evaluated': triplo_elem.get('last_evaluated'),
                            'clingen_url': triplo_elem.get('ClinGen')
                        }

                    if len(gene_dosage) > 1:  # Only add if we have dosage info
                        dosage_info.append(gene_dosage)
        return dosage_info

    def _get_protein_change(self):
        """Get the simple protein change notation (e.g., 'R611Q')"""
        if not self._is_vcv_format:
            return None

        simple_allele = self.variation_archive.find('ClassifiedRecord/SimpleAllele')
        if simple_allele is not None:
            protein_change = simple_allele.find('ProteinChange')
            return protein_change.text if protein_change is not None else None
        return None

    def _get_citations(self):
        """Get citation information from the clinical classifications"""
        if not self._is_vcv_format:
            return []

        citations = []
        classifications = self.variation_archive.find('.//Classifications')
        if classifications is not None:
            germline_class = classifications.find('GermlineClassification')
            if germline_class is not None:
                for citation in germline_class.findall('Citation'):
                    citation_info = {
                        'type': citation.get('Type'),
                        'ids': []
                    }

                    for id_elem in citation.findall('ID'):
                        citation_info['ids'].append({
                            'source': id_elem.get('Source'),
                            'id': id_elem.text
                        })

                    # Also check for URLs
                    url_elem = citation.find('URL')
                    if url_elem is not None:
                        citation_info['url'] = url_elem.text

                    citations.append(citation_info)
        return citations

    def _get_clinical_assertions(self):
        """Get individual clinical assertions from submitters"""
        if not self._is_vcv_format:
            return []

        assertions = []
        assertion_list = self.variation_archive.find('.//ClinicalAssertionList')
        if assertion_list is not None:
            for assertion in assertion_list.findall('ClinicalAssertion'):
                assertion_info = {
                    'id': assertion.get('ID'),
                    'submission_date': assertion.get('SubmissionDate'),
                    'date_created': assertion.get('DateCreated'),
                    'date_last_updated': assertion.get('DateLastUpdated')
                }

                # Get submitter information
                clinvar_accession = assertion.find('ClinVarAccession')
                if clinvar_accession is not None:
                    assertion_info.update({
                        'accession': clinvar_accession.get('Accession'),
                        'submitter_name': clinvar_accession.get('SubmitterName'),
                        'organization_category': clinvar_accession.get('OrganizationCategory')
                    })

                # Get classification
                classification = assertion.find('Classification')
                if classification is not None:
                    assertion_info['classification'] = {}

                    review_status = classification.find('ReviewStatus')
                    if review_status is not None:
                        assertion_info['classification']['review_status'] = review_status.text

                    germline_class = classification.find('GermlineClassification')
                    if germline_class is not None:
                        assertion_info['classification']['clinical_significance'] = germline_class.text

                    date_evaluated = classification.get('DateLastEvaluated')
                    if date_evaluated:
                        assertion_info['classification']['date_last_evaluated'] = date_evaluated

                # Get observed data
                observed_list = assertion.find('ObservedInList')
                if observed_list is not None:
                    assertion_info['observed_in'] = []
                    for observed in observed_list.findall('ObservedIn'):
                        obs_info = {}

                        sample = observed.find('Sample')
                        if sample is not None:
                            obs_info['sample'] = {
                                'origin': sample.find('Origin').text if sample.find('Origin') is not None else None,
                                'species': sample.find('Species').text if sample.find('Species') is not None else None,
                                'affected_status': sample.find('AffectedStatus').text if sample.find('AffectedStatus') is not None else None
                            }

                            # Number tested
                            num_tested = sample.find('NumberTested')
                            if num_tested is not None:
                                try:
                                    obs_info['sample']['number_tested'] = int(num_tested.text)
                                except (ValueError, TypeError):
                                    obs_info['sample']['number_tested'] = num_tested.text

                        method = observed.find('Method')
                        if method is not None:
                            method_type = method.find('MethodType')
                            if method_type is not None:
                                obs_info['method_type'] = method_type.text

                        assertion_info['observed_in'].append(obs_info)

                assertions.append(assertion_info)

        return assertions

    ### OBSERVATIONS
