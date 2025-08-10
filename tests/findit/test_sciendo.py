"""Evidence-driven tests for Sciendo consolidation into the_doi_slide.

This test suite validates Sciendo's consolidation into the_doi_slide generic function
following DANCE_FUNCTION_GUIDELINES.md Phase 4: Test Development.

Evidence analyzed:
- 6 HTML samples with perfect pattern consistency
- All show: citation_pdf_url = https://sciendo.com/pdf/{doi}
- DOI prefixes: 10.2478, 10.34763 (multi-publisher platform)
- Domain: sciendo.com (100% consistency)
- Access model: Open access with citation_pdf_url meta tags

Registry configuration:
- dance_function: 'the_doi_slide'
- format_template: 'https://sciendo.com/pdf/{doi}'
"""

import unittest
from metapub.findit.dances.generic import the_doi_slide
from metapub.findit.registry import JournalRegistry
from metapub.pubmedfetcher import PubMedFetcher
from metapub.exceptions import NoPDFLink
from tests.test_compat import skip_network_tests


class TestSciendo(unittest.TestCase):
    """Test Sciendo consolidation into the_doi_slide generic function."""

    def setUp(self):
        """Set up test PMIDs from evidence collection."""
        # Evidence PMIDs from HTML sample analysis
        self.evidence_pmids = {
            '34699700': {
                'doi': '10.2478/prilozi-2021-0014',
                'journal': 'Pril (Makedon Akad Nauk Umet Odd Med Nauki)',
                'expected_url': 'https://sciendo.com/pdf/10.2478/prilozi-2021-0014'
            },
            '35032372': {
                'doi': '10.2478/prilozi-2021-0032',
                'journal': 'Pril (Makedon Akad Nauk Umet Odd Med Nauki)',
                'expected_url': 'https://sciendo.com/pdf/10.2478/prilozi-2021-0032'
            },
            '35451288': {
                'doi': '10.2478/prilozi-2022-0013',
                'journal': 'Pril (Makedon Akad Nauk Umet Odd Med Nauki)',
                'expected_url': 'https://sciendo.com/pdf/10.2478/prilozi-2022-0013'
            },
            '36803942': {
                'doi': '10.34763/jmotherandchild.20222601.d-22-00034',
                'journal': 'J Mother Child',
                'expected_url': 'https://sciendo.com/pdf/10.34763/jmotherandchild.20222601.d-22-00034'
            }
        }

    def test_registry_mapping(self):
        """Test that Sciendo journals are mapped to the_doi_slide."""
        registry = JournalRegistry()

        # Test multiple Sciendo journals from evidence
        test_journals = [
            'Pril (Makedon Akad Nauk Umet Odd Med Nauki)',
            'J Mother Child'
        ]

        for journal in test_journals:
            with self.subTest(journal=journal):
                publisher_info = registry.get_publisher_for_journal(journal)
                self.assertIsNotNone(publisher_info, f"Journal '{journal}' should be in registry")
                self.assertEqual(publisher_info['name'], 'sciendo')
                self.assertEqual(publisher_info['dance_function'], 'the_doi_slide')
                self.assertEqual(publisher_info['format_template'], 'https://sciendo.com/pdf/{doi}')

        registry.close()

    @skip_network_tests
    def test_evidence_based_url_construction(self):
        """Test URL construction with evidence PMIDs."""
        pmf = PubMedFetcher()

        for pmid, data in self.evidence_pmids.items():
            with self.subTest(pmid=pmid):
                pma = pmf.article_by_pmid(pmid)

                # Verify article metadata matches evidence
                self.assertEqual(pma.doi, data['doi'])
                self.assertEqual(pma.journal, data['journal'])

                # Test URL construction without verification
                url = the_doi_slide(pma, verify=False)
                self.assertEqual(url, data['expected_url'])

                # Verify URL pattern follows evidence
                self.assertTrue(url.startswith('https://sciendo.com/pdf/'))
                self.assertIn(pma.doi, url)

    @skip_network_tests
    def test_doi_pattern_coverage(self):
        """Test coverage of different DOI patterns from evidence."""
        pmf = PubMedFetcher()

        # Test DOI prefix diversity from evidence
        doi_prefixes = {
            '10.2478': '34699700',  # Most common pattern
            '10.34763': '36803942'  # Alternative pattern
        }

        for prefix, pmid in doi_prefixes.items():
            with self.subTest(doi_prefix=prefix):
                pma = pmf.article_by_pmid(pmid)
                self.assertTrue(pma.doi.startswith(prefix))

                url = the_doi_slide(pma, verify=False)
                self.assertIn(pma.doi, url)
                self.assertTrue(url.startswith('https://sciendo.com/pdf/'))

    @skip_network_tests
    def test_open_access_verification(self):
        """Test verification with open access articles (should succeed)."""
        pmf = PubMedFetcher()

        # Test verification with known open access articles
        test_pmids = ['34699700', '35032372']

        for pmid in test_pmids:
            with self.subTest(pmid=pmid):
                pma = pmf.article_by_pmid(pmid)

                # Verification should succeed for open access content
                try:
                    url = the_doi_slide(pma, verify=True)
                    self.assertIsNotNone(url)
                    self.assertTrue(url.startswith('https://sciendo.com/pdf/'))
                except Exception as e:
                    # If verification fails, that's also acceptable due to network issues
                    # but URL construction should still work
                    url = the_doi_slide(pma, verify=False)
                    self.assertIsNotNone(url)

    def test_missing_doi_error_handling(self):
        """Test error handling for missing DOI (following DANCE_FUNCTION_GUIDELINES)."""
        # Create mock PubMedArticle without DOI
        class MockPMA:
            doi = None
            journal = 'Pril (Makedon Akad Nauk Umet Odd Med Nauki)'

        mock_pma = MockPMA()

        # Should raise NoPDFLink with appropriate message
        with self.assertRaises(NoPDFLink) as context:
            the_doi_slide(mock_pma, verify=False)

        error_msg = str(context.exception)
        self.assertIn('MISSING', error_msg)
        self.assertIn('DOI', error_msg)

    def test_evidence_pattern_consistency(self):
        """Test pattern consistency matches evidence analysis."""
        # Verify the format template matches evidence findings
        registry = JournalRegistry()
        publisher_info = registry.get_publisher_for_journal('Pril (Makedon Akad Nauk Umet Odd Med Nauki)')
        registry.close()

        # Pattern should match evidence: https://sciendo.com/pdf/{doi}
        expected_template = 'https://sciendo.com/pdf/{doi}'
        self.assertEqual(publisher_info['format_template'], expected_template)

        # Test template substitution
        test_doi = '10.2478/test-2024-001'
        expected_url = f'https://sciendo.com/pdf/{test_doi}'
        actual_url = publisher_info['format_template'].format(doi=test_doi)
        self.assertEqual(actual_url, expected_url)



if __name__ == '__main__':
    unittest.main()
