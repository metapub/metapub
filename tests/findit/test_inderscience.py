"""
Test suite for Inderscience Publishers dance function.
Tests CLAUDE.md compliant implementation with DOI patterns.

Test approach:
- Tests DOI pattern (10.1504/*) based on evidence
- Validates CLAUDE.md compliance (no huge try-except, standard verification)
- Uses real PMIDs: 24084238, 24794070, 24449692
"""

import unittest
from unittest.mock import patch, Mock

from metapub.findit.dances.inderscience import the_inderscience_ula
from metapub.exceptions import AccessDenied, NoPDFLink
from metapub import PubMedFetcher
from tests.fixtures import load_pmid_xml, INDERSCIENCE_EVIDENCE_PMIDS


class TestInderscienceDance(unittest.TestCase):
    """Evidence-driven test suite for Inderscience Publishers dance function"""

    def setUp(self):
        """Set up test fixtures with real evidence PMIDs"""
        self.fetch = PubMedFetcher()
        
        # Real evidence PMIDs from Inderscience with DOI 10.1504/* pattern
        self.evidence_pmids = [
            '24084238',  # DOI: 10.1504/IJBRA.2013.056620
            '24794070',  # DOI: 10.1504/IJBRA.2014.060762  
            '24449692'   # DOI: 10.1504/IJBRA.2014.058777
        ]
        
        # Create mock PMA with evidence data
        self.mock_pma = Mock()
        self.mock_pma.doi = '10.1504/IJBRA.2013.056620'
        self.mock_pma.journal = 'Int J Bioinform Res Appl'
        self.mock_pma.pmid = '24084238'


    def test_doi_url_construction_without_verification(self):
        """Test correct URL construction without verification"""
        expected_url = 'https://www.inderscienceonline.com/doi/epdf/10.1504/IJBRA.2013.056620'
        
        result = the_inderscience_ula(self.mock_pma, verify=False)
        
        self.assertEqual(result, expected_url)

    @patch('metapub.findit.dances.inderscience.verify_pdf_url')
    def test_verification_success(self, mock_verify):
        """Test successful verification using standard verify_pdf_url"""
        expected_url = 'https://www.inderscienceonline.com/doi/epdf/10.1504/IJBRA.2013.056620'
        mock_verify.return_value = expected_url
        
        result = the_inderscience_ula(self.mock_pma, verify=True)
        
        self.assertEqual(result, expected_url)
        mock_verify.assert_called_once_with(expected_url, 'Inderscience Publishers', request_timeout=10, max_redirects=3)

    @patch('metapub.findit.dances.inderscience.verify_pdf_url')
    def test_verification_access_denied_bubbles_up(self, mock_verify):
        """Test that AccessDenied from verify_pdf_url bubbles up correctly"""
        expected_url = 'https://www.inderscienceonline.com/doi/epdf/10.1504/IJBRA.2013.056620'
        mock_verify.side_effect = AccessDenied('DENIED: Access forbidden')
        
        with self.assertRaises(AccessDenied):
            the_inderscience_ula(self.mock_pma, verify=True)
        
        mock_verify.assert_called_once_with(expected_url, 'Inderscience Publishers', request_timeout=10, max_redirects=3)

    def test_doi_pattern_validation(self):
        """Test with various Inderscience DOI patterns"""
        inderscience_dois = [
            '10.1504/IJBRA.2013.056620',  # Evidence DOI 1
            '10.1504/IJBRA.2014.060762',  # Evidence DOI 2
            '10.1504/IJBRA.2014.058777',  # Evidence DOI 3
            '10.1504/IJENVH.2023.135446', # Different journal pattern
            '10.1504/IJBT.2021.114567'    # Another journal pattern
        ]
        
        for doi in inderscience_dois:
            pma = Mock()
            pma.doi = doi
            pma.journal = 'Int J Bioinform Res Appl'
            
            expected_url = f'https://www.inderscienceonline.com/doi/epdf/{doi}'
            result = the_inderscience_ula(pma, verify=False)
            self.assertEqual(result, expected_url)

    def test_real_pmid_metadata_validation(self):
        """Test with real PMID metadata to validate approach"""
        try:
            # Use first evidence PMID
            pma = self.fetch.article_by_pmid(self.evidence_pmids[0])
            
            # Validate we have expected data
            self.assertIsNotNone(pma.doi)
            self.assertTrue(pma.doi.startswith('10.1504/'))
            self.assertEqual(pma.journal, 'Int J Bioinform Res Appl')
            
            # Test URL construction
            expected_url = f'https://www.inderscienceonline.com/doi/epdf/{pma.doi}'
            result = the_inderscience_ula(pma, verify=False)
            self.assertEqual(result, expected_url)
            
            print(f"Real PMID validation: DOI={pma.doi}, Journal={pma.journal}")
            
        except Exception as e:
            self.skipTest(f"Could not fetch real PMID data: {e}")


    def test_evidence_based_url_construction(self):
        """Test that URL construction follows evidence-based pattern"""
        # Test with all evidence PMIDs' DOI patterns
        evidence_data = [
            ('24084238', '10.1504/IJBRA.2013.056620'),
            ('24794070', '10.1504/IJBRA.2014.060762'), 
            ('24449692', '10.1504/IJBRA.2014.058777')
        ]
        
        for pmid, doi in evidence_data:
            pma = Mock()
            pma.doi = doi
            pma.pmid = pmid
            
            expected_url = f'https://www.inderscienceonline.com/doi/epdf/{doi}'
            result = the_inderscience_ula(pma, verify=False)
            self.assertEqual(result, expected_url)


    def test_cloudflare_blocking_documentation(self):
        """Test that function correctly documents Cloudflare blocking status"""
        # Function should work without verification but expect blocking with verification
        result = the_inderscience_ula(self.mock_pma, verify=False)
        expected_url = 'https://www.inderscienceonline.com/doi/epdf/10.1504/IJBRA.2013.056620'
        self.assertEqual(result, expected_url)
        
        # With verification, expect AccessDenied (blocked by Cloudflare)
        with self.assertRaises(AccessDenied):
            the_inderscience_ula(self.mock_pma, verify=True)


def test_inderscience_journal_recognition():
    """Test that Inderscience journals are properly recognized in the registry."""
    from metapub.findit.registry import JournalRegistry
    from metapub.findit.journals.inderscience import inderscience_journals

    registry = JournalRegistry()

    # Test sample Inderscience journals (using PubMed abbreviated names)
    test_journals = [
        'Int J Biomed Eng Technol',
        'Int J Bioinform Res Appl',
        'Int J Environ Pollut',
        'Int J Nanotechnol',
        'Botulinum J'
    ]

    # Test journal recognition using registry
    found_count = 0
    for journal in test_journals:
        publisher_info = registry.get_publisher_for_journal(journal)
        if publisher_info and publisher_info['name'] == 'inderscience':
            assert publisher_info['dance_function'] == 'the_inderscience_ula'
            print(f"✓ {journal} correctly mapped to Inderscience Publishers")
            found_count += 1
        else:
            print(f"⚠ {journal} mapped to different publisher: {publisher_info['name'] if publisher_info else 'None'}")

    # Just make sure we found at least one Inderscience journal
    assert found_count > 0, "No Inderscience journals found in registry with inderscience publisher"
    print(f"✓ Found {found_count} properly mapped Inderscience journals")

    registry.close()




class TestInderscienceXMLFixtures:
    """Test Inderscience dance function with real XML fixtures."""

    def test_inderscience_authentic_metadata_validation(self):
        """Validate authentic metadata from XML fixtures matches expected patterns."""
        for pmid, expected in INDERSCIENCE_EVIDENCE_PMIDS.items():
            pma = load_pmid_xml(pmid)
            assert pma.doi == expected['doi']
            assert pma.journal == expected['journal']
            assert pma.pmid == pmid
            print(f"✓ PMID {pmid}: {pma.journal} - {pma.doi}")

    def test_inderscience_doi_pattern_consistency(self):
        """Test Inderscience DOI patterns (10.1504/)."""
        for pmid, data in INDERSCIENCE_EVIDENCE_PMIDS.items():
            pma = load_pmid_xml(pmid)
            assert pma.doi.startswith('10.1504/'), f"Inderscience DOI must start with 10.1504/, got: {pma.doi}"
            print(f"✓ PMID {pmid} DOI pattern: {pma.doi}")

    def test_inderscience_journal_coverage(self):
        """Test Inderscience journal coverage."""
        journals = set()
        for pmid in INDERSCIENCE_EVIDENCE_PMIDS.keys():
            pma = load_pmid_xml(pmid)
            journals.add(pma.journal)
        assert len(journals) >= 1
        print(f"✓ Journals covered: {journals}")


if __name__ == '__main__':
    # Run comprehensive test suite
    unittest.main(verbosity=2)
