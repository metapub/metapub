"""metapub.clinvarvariant -- ClinVarVariant class instantiated by supplying ESummary XML string."""

import logging
from datetime import datetime

from lxml import etree

from .base import MetaPubObject
from .exceptions import MetaPubError, BaseXMLError

#TODO: Logging

#TODO: Check against recent Clinvar DB changes.

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
                # Old format
                self._is_vcv_format = False
                super(ClinVarVariant, self).__init__(xmlstr, 'VariationReport', args, kwargs)
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

    def _get_xref_list(self):
        xrefs = []
        
        if self._is_vcv_format:
            simple_allele = self.variation_archive.find('ClassifiedRecord/SimpleAllele')
            if simple_allele is not None:
                xref_list = simple_allele.find('XRefList')
                if xref_list is not None:
                    for elem in xref_list.getchildren():
                        xrefs.append(dict(elem.items()))
        else:
            xref_list = self.content.find('Allele/XRefList')
            if xref_list is not None:
                for elem in xref_list.getchildren():
                    xrefs.append(dict(elem.items()))
        
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

    ### NEW VCV FORMAT ENHANCEMENTS ###
    
    def _get_clinical_significance(self):
        """Get the clinical significance classification (e.g., 'Pathogenic', 'Benign')"""
        if not self._is_vcv_format:
            return None
            
        # Look in Classifications/GermlineClassification/Description
        classifications = self.variation_archive.find('.//Classifications')
        if classifications is not None:
            germline_class = classifications.find('GermlineClassification')
            if germline_class is not None:
                desc_elem = germline_class.find('Description')
                return desc_elem.text if desc_elem is not None else None
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
                        consequence = {
                            'type': mol_cons.get('Type'),
                            'so_id': mol_cons.get('ID'),
                            'database': mol_cons.get('DB')
                        }
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


