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
        super(ClinVarVariant, self).__init__(xmlstr, 'VariationReport', args, kwargs)

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
        self.species = self._get('Species')
        self.taxonomy_id = self.content.find('Species').get('TaxonomyId')

        # Gene List
        self.genes = self._get_gene_list()

        # Allele Info
        self.cytogenic_location = self._get_cytogenic_location()
        self.sequence_locations = self._get_sequence_locations()
        self.hgvs = self._get_hgvs_list()
        self.xrefs = self._get_xref_list()
        self.molecular_consequences = self._get_molecular_consequence_list()
        self.allele_frequencies = self._get_allele_frequency_list()

        # Observations


    def to_dict(self):
        """ returns a dictionary composed of all extractable properties of this concept. """
        outd = self.__dict__.copy()
        outd.pop('content')
        return outd

    ### HGVS string convenience properties

    def _get_hgvs_or_empty_list(self, hgvsdict):
        try:
            accession = hgvsdict['AccessionVersion']
            change = hgvsdict['Change']
            return [accession + ':' + change]
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
            if hgvsdict['Type'].find('protein') > -1:
                strlist = strlist + self._get_hgvs_or_empty_list(hgvsdict)
        return strlist

    ### VariationReport basic info

    def _get_variation_id(self):
        return self.content.get('VariationID')

    def _get_variation_name(self):
        return self.content.get('VariationName')

    def _get_variation_type(self):
        # e.g. ('VariationType', 'Simple'),
        return self.content.get('VariationType')

    def _get_date_created(self):
        # e.g. ('DateCreated', '2014-01-16'),
        datestr = self.content.get('DateCreated')
        if datestr:
            return datetime.strptime(datestr, '%Y-%m-%d')
        else:
            return None

    def _get_date_last_updated(self):
        # e.g. ('DateLastUpdated', '2016-04-10'),
        datestr = self.content.get('DateLastUpdated')
        if datestr:
            return datetime.strptime(datestr, '%Y-%m-%d')
        else:
            return None

    def _get_submitter_count(self):
        # e.g. ('SubmitterCount', '1')]
        try:
            return int(self.content.get('SubmitterCount'))
        except TypeError:
            return None

    #### GENE LIST

    def _get_gene_list(self):
        """ Returns a list of dictionaries representing each gene associated with this variant.

        Keys in gene dictionary:  'ID', 'Symbol', 'FullName', 'HGNCID', 'strand', 'Type', 'OMIM', 'Property'
        """
        #        <Gene GeneID="6261" Symbol="RYR1" FullName="ryanodine receptor 1" HGNCID="HGNC:10483" strand="+" Type="submitted">
        #           <OMIM>180901</OMIM>
        #           <Property>gene_acmg_incidental_2013</Property>
        #        </Gene>

        genes = []

        genelist = self.content.find('GeneList')
        for gene_elem in genelist.getchildren():
            genes.append(dict(gene_elem.items()))
        return genes
            
    
    ### ALLELE INFORMATION

    def _get_allele_id(self):
        return self.content.find('Allele').get('AlleleID')
    
    def _get_cytogenic_location(self):
        return self._get('Allele/CytogeneticLocation')

    def _get_sequence_locations(self):
        seqlocs = []
        for elem in self.content.findall('Allele/SequenceLocation'):
            seqlocs.append(dict(elem.items()))
        return seqlocs

    def _get_hgvs_list(self):
        hgvs = []
        try:
            for elem in self.content.find('Allele/HGVSlist').getchildren():
                hgvs.append(dict(elem.items()))
        except AttributeError:
            return []
        return hgvs

    def _get_xref_list(self):
        xrefs = []
        for elem in self.content.find('Allele/XRefList').getchildren():
            xrefs.append(dict(elem.items()))
        return xrefs

    def _get_molecular_consequence_list(self):
        molcons = []
        try:
            for elem in self.content.find('Allele/MolecularConsequenceList').getchildren():
                molcons.append(dict(elem.items()))
        except AttributeError:
            return []
        return molcons

    def _get_allele_frequency_list(self):
        freqs = []
        try: 
            for elem in self.content.find('Allele/AlleleFrequencyList').getchildren():
                freqs.append(dict(elem.items()))
        except AttributeError:
            return []
        return freqs

    ### OBSERVATIONS 


