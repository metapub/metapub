import unittest
import tempfile
import os

from metapub import ClinVarFetcher
from metapub.clinvarvariant import ClinVarVariant, PathogenicSummary, ClinSig
from metapub.exceptions import MetaPubError
from metapub.cache_utils import cleanup_dir
import pytest

class TestClinVarFetcher(unittest.TestCase):

    def setUp(self):
        # Create a unique temporary cache directory for each test run
        self.temp_cache = tempfile.mkdtemp(prefix='clinvar_test_cache_')
        self.fetch = ClinVarFetcher(cachedir=self.temp_cache)

    def tearDown(self):
        # Clean up the temporary cache directory
        if hasattr(self, 'temp_cache') and os.path.exists(self.temp_cache):
            cleanup_dir(self.temp_cache)

    def test_variant_12000_vcv_format(self):
        """Test that variant 12000 returns proper data using new VCV format"""
        var = self.fetch.variant(12000)
        
        # Verify basic properties
        self.assertEqual(var.variation_id, '12397')
        self.assertEqual(var.variation_name, 'NM_000548.4(TSC2):c.1832G>A (p.Arg611Gln)')
        self.assertEqual(var.variation_type, 'single nucleotide variant')
        
        # Verify HGVS strings
        self.assertIn('NM_000548.4:c.1832G>A', var.hgvs_c)
        self.assertIn('NC_000016.10:g.2070571G>A', var.hgvs_g)
        self.assertTrue(len(var.hgvs_p) > 0)  # Should have protein HGVS
        
        # Verify gene information
        self.assertEqual(len(var.genes), 1)
        self.assertEqual(var.genes[0]['Symbol'], 'TSC2')
        
        # Verify other properties
        self.assertEqual(var.species, 'Homo sapiens')
        self.assertEqual(var.cytogenic_location, '16p13.3')
        self.assertEqual(var.mode_of_inheritance, 'Autosomal dominant inheritance')
        self.assertEqual(var.modes_of_inheritance, ['Autosomal dominant inheritance'])

    def test_variant_12003_vcv_format(self):
        """Test that variant 12003 returns proper data using new VCV format"""
        var = self.fetch.variant(12003)
        
        # Verify basic properties
        self.assertEqual(var.variation_id, '12400')
        self.assertEqual(var.variation_name, 'NM_000548.4(TSC2):c.1096G>T (p.Glu366Ter)')
        self.assertEqual(var.variation_type, 'single nucleotide variant')
        
        # Verify HGVS strings
        self.assertIn('NM_000548.4:c.1096G>T', var.hgvs_c)
        self.assertIn('NC_000016.10:g.2060790G>T', var.hgvs_g)
        self.assertTrue(len(var.hgvs_p) > 0)  # Should have protein HGVS
        self.assertEqual(var.mode_of_inheritance, None)
        self.assertEqual(var.modes_of_inheritance, [])

    def test_invalid_variant_id(self):
        """Test that invalid variant IDs still raise appropriate errors"""
        with self.assertRaises(MetaPubError) as context:
            self.fetch.variant(99999999)  # Non-existent ID
        
        self.assertIn('Invalid ClinVar Variation ID', str(context.exception))

    def test_to_dict_method(self):
        """Test that the to_dict method works correctly"""
        var = self.fetch.variant(12000)
        var_dict = var.to_dict()
        
        # Verify dictionary contains expected stored attributes (not properties)
        expected_keys = ['variation_id', 'variation_name', 'variation_type', 
                        'genes', 'species', 'hgvs', 'cytogenic_location']
        for key in expected_keys:
            self.assertIn(key, var_dict)
        
        # Verify content element is removed from dict
        self.assertNotIn('content', var_dict)
        
        # Verify properties work correctly (these are computed, not stored)
        self.assertTrue(len(var.hgvs_c) > 0)
        self.assertTrue(len(var.hgvs_g) > 0)
        self.assertTrue(len(var.hgvs_p) > 0)

    def test_clinical_significance_features(self):
        """Test new clinical significance features in VCV format"""
        var = self.fetch.variant(12000)
        
        # Test clinical significance properties (new in VCV format)
        self.assertIsNotNone(var.clinical_significance)
        self.assertIsNotNone(var.review_status)
        self.assertIsNotNone(var.date_last_evaluated)
        self.assertIsInstance(var.number_of_submissions, int)
        self.assertIsInstance(var.number_of_submitters, int)
        
        # Verify clinical significance values are reasonable
        self.assertIn(var.clinical_significance.lower(), 
                     ['pathogenic', 'benign', 'likely pathogenic', 'likely benign', 
                      'uncertain significance', 'conflicting interpretations'])

    def test_vcv_metadata(self):
        """Test VCV record metadata features"""
        var = self.fetch.variant(12000)
        
        # Test VCV record metadata
        self.assertIsNotNone(var.vcv_accession)
        self.assertTrue(var.vcv_accession.startswith('VCV'))
        self.assertEqual(var.record_type, 'classified')
        self.assertIsNotNone(var.most_recent_submission)
        
        # Verify VCV accession format
        self.assertRegex(var.vcv_accession, r'VCV\d+')

    def test_associated_conditions(self):
        """Test associated conditions/diseases feature"""
        var = self.fetch.variant(12000)
        
        # Test associated conditions
        self.assertIsInstance(var.associated_conditions, list)
        if len(var.associated_conditions) > 0:
            condition = var.associated_conditions[0]
            self.assertIn('name', condition)
            self.assertIn('medgen_id', condition)
            self.assertIn('database', condition)
            self.assertIn('rcv_accession', condition)

    def test_enhanced_molecular_data(self):
        """Test enhanced molecular consequences and sequence details"""
        var = self.fetch.variant(12000)
        
        # Test detailed molecular consequences
        self.assertIsInstance(var.molecular_consequences_detailed, list)
        
        # Test enhanced sequence details
        self.assertIsInstance(var.sequence_details, list)
        if len(var.sequence_details) > 0:
            seq_detail = var.sequence_details[0]
            # Should have numeric fields properly converted
            for field in ['start', 'stop', 'display_start', 'display_stop']:
                if field in seq_detail:
                    self.assertIsInstance(seq_detail[field], int)

    def test_gene_dosage_info(self):
        """Test gene dosage sensitivity information"""
        var = self.fetch.variant(12000)
        
        # Test gene dosage information
        self.assertIsInstance(var.gene_dosage_info, list)
        if len(var.gene_dosage_info) > 0:
            dosage = var.gene_dosage_info[0]
            self.assertIn('symbol', dosage)
            # TSC2 should have haploinsufficiency info
            self.assertIn('haploinsufficiency', dosage)
            self.assertIn('classification', dosage['haploinsufficiency'])

    def test_protein_change(self):
        """Test protein change notation"""
        var = self.fetch.variant(12000)
        
        # Test simple protein change notation
        self.assertIsNotNone(var.protein_change)
        self.assertEqual(var.protein_change, 'R611Q')

    def test_citations_and_assertions(self):
        """Test citations and clinical assertions"""
        var = self.fetch.variant(12000)
        
        # Test citations
        self.assertIsInstance(var.citations, list)
        
        # Test clinical assertions
        self.assertIsInstance(var.clinical_assertions, list)
        if len(var.clinical_assertions) > 0:
            assertion = var.clinical_assertions[0]
            self.assertIn('id', assertion)
            self.assertIn('submission_date', assertion)
            # May have submitter information
            if 'submitter_name' in assertion:
                self.assertIsInstance(assertion['submitter_name'], str)

    def test_pmids_for_hgvs(self):
        """Test that pmids_for_hgvs returns a list of PMID strings"""
        pmids = self.fetch.pmids_for_hgvs('NM_000059.4:c.9382C>T')
        self.assertIsInstance(pmids, list)
        for pmid in pmids:
            self.assertIsInstance(pmid, str)
            self.assertTrue(pmid.isdigit())

    @pytest.mark.live_network
    def test_pathogenic_summary_basic(self):
        """Test the pathogenic_summary correctly aggregates submitter classes"""
        var = self.fetch.variant(12000)

        summary = var.pathogenic_summary
        if summary is None:
            self.fail("Pathogenic summary is None")
        self.assertIsInstance(summary, PathogenicSummary, 'pathogenic_summary doesn\'t return a dict')

        # Check counts exists
        counts = summary.counts
        self.assertIsInstance(counts, dict, 'counts property doesn\'t exist')
        for key, value in counts.items():
            self.assertIsInstance(value, int, F'prop {key} in counts doesn\'t have an int')
        
        # Total submitters matches sum of counts
        total = summary.total_submitters
        self.assertEqual(total, sum(counts.values()))

        # Consensus matches the classification with highest count
        consensus = summary.consensus
        if not summary.conflicting:
            self.assertEqual(consensus, max(counts.items(), key=lambda x: x[1])[0], "Consensus doesn't match aggregation")
    
    @pytest.mark.live_network
    def test_pathogenic_summary_conflicted(self):
        """Test multiple known variants and their classification"""
        variants: list[tuple[int, tuple[int, ClinSig, int, bool]]] = [
            # (variant ID, (submitter #, classification, classification count, conflicted))
            (12000, (21, 'pathogenic', 21, False)),
            (4691, (18, 'uncertain significance', 6, True)),
            (4691, (18, 'likely benign', 1, True)),
            (1028857, (2, 'likely pathogenic', 1, False))
        ]
        for (id, (submitters, count_name, count, conflicting)) in variants:
            var = self.fetch.variant(id, id_from='clinvar')
            
            summary = var.pathogenic_summary
            if summary is None:
                self.fail("Summary should not be none")
            self.assertGreaterEqual(summary.total_submitters, submitters, F"{id} variant has >= {submitters} submitters")
            self.assertGreaterEqual(summary.counts[count_name], count, F"{id} variant has >= {count} pathogenic classifications")
            self.assertEqual(summary.conflicting, conflicting, F"{id} variant is has {"" if conflicting else "not"} conflicting submittions")

    def test_pathogenic_summary_offline(self):
        # Read the cached XML file
        xml_file_path = os.path.join(os.path.dirname(__file__), 'data', 'clinvar_vcv_12000.xml')
        self.assertTrue(os.path.exists(xml_file_path), "Cached XML file should exist")
        
        with open(xml_file_path, 'rb') as f:  # Read as bytes to handle XML declaration
            xml_content = f.read()
        
        # Create variant from cached XML
        var = ClinVarVariant(xml_content)

        # Make sure this works the same way live data does
        summary = var.pathogenic_summary
        if summary is None:
            self.fail("Pathogenic summary is None")
        self.assertIsInstance(summary, PathogenicSummary, 'pathogenic_summary doesn\'t return a dict')

        # Check counts exists
        counts = summary.counts
        self.assertIsInstance(counts, dict, 'counts property doesn\'t exist')
        for key, value in counts.items():
            self.assertIsInstance(value, int, F'prop {key} in counts doesn\'t have an int')
        
        # Total submitters matches sum of counts
        total = summary.total_submitters
        self.assertEqual(total, sum(counts.values()))

        # Consensus matches the classification with highest count
        consensus = summary.consensus
        if not summary.conflicting:
            self.assertEqual(consensus, max(counts.items(), key=lambda x: x[1])[0], "Consensus doesn't match aggregation")

    def test_offline_cached_xml(self):
        """Test using cached XML file for offline testing"""
        # Read the cached XML file
        xml_file_path = os.path.join(os.path.dirname(__file__), 'data', 'clinvar_vcv_12000.xml')
        self.assertTrue(os.path.exists(xml_file_path), "Cached XML file should exist")
        
        with open(xml_file_path, 'rb') as f:  # Read as bytes to handle XML declaration
            xml_content = f.read()
        
        # Create variant from cached XML
        var = ClinVarVariant(xml_content)
        
        # Verify it works the same as live data
        self.assertEqual(var.variation_id, '12397')
        self.assertEqual(var.variation_name, 'NM_000548.4(TSC2):c.1832G>A (p.Arg611Gln)')
        self.assertEqual(var.variation_type, 'single nucleotide variant')
        self.assertEqual(var.species, 'Homo sapiens')
        self.assertEqual(var.cytogenic_location, '16p13.3')
        self.assertEqual(var.mode_of_inheritance, 'Autosomal dominant inheritance')
        self.assertEqual(var.modes_of_inheritance, ['Autosomal dominant inheritance'])
        
        # Test all new VCV features work with cached XML
        self.assertIsNotNone(var.clinical_significance)
        self.assertIsNotNone(var.vcv_accession)
        self.assertIsNotNone(var.protein_change)
        self.assertIsInstance(var.associated_conditions, list)
        self.assertIsInstance(var.gene_dosage_info, list)
        self.assertIsInstance(var.pathogenic_summary, PathogenicSummary)
        self.assertEqual(var.rsid, '28934872')
        self.assertEqual(var.rsids, ['28934872'])
        self.assertEqual(var.omim_id, '191092.0006')
        self.assertEqual(var.omim_ids, ['191092.0006'])

        # Orphanet/MedGen xrefs never appear in SimpleAllele/XRefList in real records
        # (they live in condition/RCV sections); see clinvar_vcv_orphanet_medgen.manifest.txt
        self.assertIsNone(var.orphanet_id)
        self.assertEqual(var.orphanet_ids, [])
        self.assertIsNone(var.medgen_id)
        self.assertEqual(var.medgen_ids, [])
        
        # Verify TSC2 gene dosage info is present
        self.assertTrue(len(var.gene_dosage_info) > 0)
        self.assertEqual(var.gene_dosage_info[0]['symbol'], 'TSC2')
        self.assertIn('haploinsufficiency', var.gene_dosage_info[0])

    def _load_fixture(self, filename):
        xml_file_path = os.path.join(os.path.dirname(__file__), 'data', filename)
        with open(xml_file_path, 'rb') as f:
            return ClinVarVariant(f.read())

    def test_xref_list_simple_vcv(self):
        """Simple VCV variant (TSC2, VCV000012397) has 4 xrefs from its single SimpleAllele."""
        var = self._load_fixture('clinvar_vcv_12000.xml')
        xrefs = var.xrefs
        dbs = [x['DB'] for x in xrefs]
        self.assertIn('dbSNP', dbs)
        self.assertIn('OMIM', dbs)
        self.assertEqual(var.rsid, '28934872')
        self.assertEqual(var.omim_id, '191092.0006')

    def test_xref_list_haplotype_collects_all_alleles(self):
        """Haplotype VCV (KCNQ2, VCV004818726) has two SimpleAlleles; xrefs from both must be collected."""
        var = self._load_fixture('clinvar_vcv_haplotype_kcnq2.xml')
        xrefs = var.xrefs
        # Both alleles contribute xrefs — expect 6 total (3 per allele)
        self.assertEqual(len(xrefs), 6)
        # Both dbSNP rsIDs must be present
        dbsnp_ids = [x['ID'] for x in xrefs if x.get('DB') == 'dbSNP']
        self.assertIn('1060500602', dbsnp_ids)
        self.assertIn('2081099943', dbsnp_ids)
        # rsids property returns both
        self.assertIn('1060500602', var.rsids)
        self.assertIn('2081099943', var.rsids)

    def test_xref_list_no_xreflist_returns_empty(self):
        """Variant with no XRefList element (TERT, VCV004819006) must return empty list without crashing."""
        var = self._load_fixture('clinvar_vcv_no_xreflist_tert.xml')
        self.assertEqual(var.xrefs, [])
        self.assertIsNone(var.rsid)
        self.assertEqual(var.rsids, [])

    def test_xref_list_genotype_collects_all_alleles(self):
        """Genotype VCV (synthetic) nests SimpleAlleles under Genotype; xrefs from both must be collected."""
        var = self._load_fixture('clinvar_vcv_genotype_minimal.xml')
        xrefs = var.xrefs
        # Two SimpleAlleles: first has 2 xrefs (dbSNP + OMIM), second has 1 (dbSNP)
        self.assertEqual(len(xrefs), 3)
        dbsnp_ids = [x['ID'] for x in xrefs if x.get('DB') == 'dbSNP']
        self.assertIn('111111111', dbsnp_ids)
        self.assertIn('222222222', dbsnp_ids)
        omim_ids = [x['ID'] for x in xrefs if x.get('DB') == 'OMIM']
        self.assertIn('100001.0001', omim_ids)

    def test_rsid_normalization_and_dedup(self):
        """All four observed dbSNP XRef formats for the same rsID collapse to one bare number.

        The four formats documented in _get_rsids comments:
          Type="rs"       ID="1799945"   -- idiomatic
          Type="rsNumber" ID="1799945"   -- non-standard Type (Type-agnostic collection)
          (no Type)       ID="rs1799945" -- rs prefix joined into ID field
          (no Type)       ID="1799945"   -- bare number, missing Type entirely
        All represent the same variant and must deduplicate to ['1799945'].
        """
        var = self._load_fixture('clinvar_vcv_rsid_formats.xml')
        self.assertEqual(var.rsids, ['1799945'])
        self.assertEqual(var.rsid, '1799945')

    def test_orphanet_and_medgen_ids(self):
        """Orphanet and MedGen IDs in SimpleAllele/XRefList are returned by orphanet_id/medgen_id.

        Note: no real VCV record has these DBs in SimpleAllele/XRefList (they appear only
        in condition/RCV sections). This synthetic fixture tests the filtering code path.
        """
        var = self._load_fixture('clinvar_vcv_orphanet_medgen.xml')
        self.assertEqual(var.orphanet_id, 'ORPHA:123456')
        self.assertEqual(var.orphanet_ids, ['ORPHA:123456', 'ORPHA:789012'])
        self.assertEqual(var.medgen_id, 'C0123456')
        self.assertEqual(var.medgen_ids, ['C0123456'])
        self.assertEqual(var.rsid, '987654321')

    def test_xref_list_old_format(self):
        """Old VariationReport format (TSC2 c.1832G>A, pre-VCV) uses Allele/XRefList path."""
        var = self._load_fixture('clinvar_old_format_minimal.xml')
        xrefs = var.xrefs
        self.assertEqual(len(xrefs), 2)
        dbs = [x['DB'] for x in xrefs]
        self.assertIn('dbSNP', dbs)
        self.assertIn('OMIM', dbs)
        self.assertEqual(var.rsid, '28934872')
        self.assertEqual(var.omim_id, '191092.0006')


    def test_offline_multiple_mode_of_inheritance_inline_xml(self):
        """Test multiple mode-of-inheritance parsing from an inline offline XML snippet modeled off of VCV4071947."""
        multiple_case_xml = (
            b'<?xml version="1.0" encoding="UTF-8"?>'
            b'<ClinVarResult-Set>'
            b'<VariationArchive VariationID="4071947" VariationName="offline multiple mode test" '
            b'VariationType="single nucleotide variant">'
            b'<ClassifiedRecord><SimpleAllele>'
            b'<Attribute Type="ModeOfInheritance">Autosomal dominant inheritance</Attribute>'
            b'<Attribute Type="ModeOfInheritance">Autosomal recessive inheritance</Attribute>'
            b'</SimpleAllele></ClassifiedRecord>'
            b'</VariationArchive></ClinVarResult-Set>'
        )
        multiple_case_var = ClinVarVariant(multiple_case_xml)
        self.assertEqual(multiple_case_var.mode_of_inheritance, 'Autosomal dominant inheritance')
        self.assertEqual(
            multiple_case_var.modes_of_inheritance,
            ['Autosomal dominant inheritance', 'Autosomal recessive inheritance']
        )

    def test_backward_compatibility(self):
        """Test that all existing properties still work with new format"""
        var = self.fetch.variant(12000)
        
        # All legacy properties should still work
        legacy_properties = [
            'variation_id', 'variation_name', 'variation_type',
            'date_created', 'date_last_updated', 'submitter_count',
            'species', 'genes', 'cytogenic_location', 'sequence_locations',
            'hgvs', 'xrefs', 'molecular_consequences', 'allele_frequencies'
        ]
        
        for prop in legacy_properties:
            self.assertTrue(hasattr(var, prop), f"Property '{prop}' should exist")
            # Should not raise exceptions
            getattr(var, prop)
        
        # HGVS convenience properties should still work
        self.assertIsInstance(var.hgvs_c, list)
        self.assertIsInstance(var.hgvs_g, list)
        self.assertIsInstance(var.hgvs_p, list)


if __name__ == '__main__':
    unittest.main()
