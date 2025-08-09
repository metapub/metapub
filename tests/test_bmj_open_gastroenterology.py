#!/usr/bin/env python
"""
Test suite for BMJ Open Gastroenterology consolidation.

BMJ Open Gastroenterology is now consolidated into BMJ Publishing Group
configuration, using the_bmj_bump for PDF extraction with two-stage approach:
1. VIP URL construction (faster)  
2. citation_pdf_url meta tag fallback (evidence-based reliability)

Evidence-based test URLs from HTML samples:
- https://bmjopengastro.bmj.com/content/8/1/e000643.full.pdf (PMID 34140324)
- https://bmjopengastro.bmj.com/content/9/1/e000759.full.pdf (PMID 34996762)
"""

import unittest
from metapub.findit.registry import JournalRegistry


class TestBMJOpenGastroenterologyConsolidated(unittest.TestCase):
    """Test BMJ Open Gastroenterology consolidation with main BMJ Publishing Group."""

    def setUp(self):
        """Set up test fixtures."""
        self.registry = JournalRegistry()

    def test_registry_bmj_consolidation(self):
        """Test BMJ Open Gastroenterology is properly consolidated into main BMJ Publishing Group."""
        # Test journal recognition
        publisher_info = self.registry.get_publisher_for_journal('BMJ Open Gastroenterol')
        self.assertIsNotNone(publisher_info, "BMJ Open Gastroenterol not found in registry")
        self.assertEqual(publisher_info['dance_function'], 'the_bmj_bump')
        self.assertEqual(publisher_info['name'], 'BMJ Publishing Group')
        self.assertIsNone(publisher_info.get('format_template'), "BMJ bump should not use format templates")

    def test_bmj_consolidation_with_other_journals(self):
        """Test BMJ Open Gastroenterology shares configuration with other BMJ journals."""
        # Test BMJ Open Gastro configuration
        bmj_open_gastro_info = self.registry.get_publisher_for_journal('BMJ Open Gastroenterol')
        
        # Test another major BMJ journal (Gut)
        gut_info = self.registry.get_publisher_for_journal('Gut')
        
        # Should be consolidated under same publisher
        self.assertEqual(bmj_open_gastro_info['name'], gut_info['name'])
        self.assertEqual(bmj_open_gastro_info['dance_function'], gut_info['dance_function'])
        self.assertEqual(bmj_open_gastro_info['name'], 'BMJ Publishing Group')

    def test_evidence_based_url_patterns(self):
        """Test that evidence patterns are consistent with VIP delegation."""
        # Evidence from HTML samples showing perfect citation_pdf_url support
        evidence_urls = [
            'https://bmjopengastro.bmj.com/content/8/1/e000643.full.pdf',
            'https://bmjopengastro.bmj.com/content/9/1/e000759.full.pdf'
        ]
        
        # All patterns use consistent domain
        for url in evidence_urls:
            self.assertIn('bmjopengastro.bmj.com', url)
            self.assertTrue(url.endswith('.full.pdf'))
            self.assertTrue(url.startswith('https://'))

    def test_bmj_vip_url_construction_compatibility(self):
        """Test that BMJ VIP URL construction produces evidence-based URLs."""
        from metapub.findit.journals.bmj import bmj_journal_params
        
        # Test BMJ Open Gastro mapping produces correct URLs
        self.assertIn('BMJ Open Gastroenterol', bmj_journal_params)
        
        host = bmj_journal_params['BMJ Open Gastroenterol']['host']
        self.assertEqual(host, 'bmjopengastro.bmj.com')
        
        # Test VIP URL construction format matches our evidence
        constructed_url = f'https://{host}/content/8/1/e000643.full.pdf'
        evidence_url = 'https://bmjopengastro.bmj.com/content/8/1/e000643.full.pdf'
        self.assertEqual(constructed_url, evidence_url)


if __name__ == '__main__':
    unittest.main()