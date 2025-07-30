import unittest
import tempfile
import os

from metapub import ClinVarFetcher
from metapub.clinvarvariant import ClinVarVariant
from metapub.exceptions import MetaPubError
from metapub.cache_utils import cleanup_dir


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
        
        # Test all new VCV features work with cached XML
        self.assertIsNotNone(var.clinical_significance)
        self.assertIsNotNone(var.vcv_accession)
        self.assertIsNotNone(var.protein_change)
        self.assertIsInstance(var.associated_conditions, list)
        self.assertIsInstance(var.gene_dosage_info, list)
        
        # Verify TSC2 gene dosage info is present
        self.assertTrue(len(var.gene_dosage_info) > 0)
        self.assertEqual(var.gene_dosage_info[0]['symbol'], 'TSC2')
        self.assertIn('haploinsufficiency', var.gene_dosage_info[0])

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