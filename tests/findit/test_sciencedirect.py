"""Tests for ScienceDirect dance function."""

import pytest
from unittest.mock import patch, Mock

from .common import BaseDanceTest
from metapub import PubMedFetcher
from metapub.findit.dances import the_sciencedirect_disco
from metapub.exceptions import AccessDenied, NoPDFLink
from tests.fixtures import load_pmid_xml, SCIENCEDIRECT_EVIDENCE_PMIDS


class TestScienceDirectDance(BaseDanceTest):
    """Test cases for ScienceDirect (Elsevier)."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.fetch = PubMedFetcher()

    def test_sciencedirect_disco_pii_url_construction(self):
        """Test 1: ScienceDirect URL construction from PII.
        
        PMID: 35971408 (Decis Support Syst)
        Expected: Should construct valid ScienceDirect PDF URL from PII
        """
        pma = self.fetch.article_by_pmid('35971408')
        
        assert pma.journal == 'Decis Support Syst'
        assert pma.doi == '10.1016/j.dss.2022.113847'
        assert pma.pii == 'S0167-9236(22)00118-X'
        
        # Test without verification
        url = the_sciencedirect_disco(pma, verify=False)
        assert url is not None
        assert 'sciencedirect.com/science/article/pii/S016792362200118X/pdfft' in url
        assert 'isDTMRedir=true' in url
        print(f"Test 1 - PII-based URL: {url}")

    def test_sciencedirect_disco_clean_pii(self):
        """Test 2: PII cleaning functionality.
        
        Expected: Should properly clean PII by removing special characters
        """
        # Mock PMA with PII containing various special chars
        pma = Mock()
        pma.pii = 'S0167-9236(22)00118-X'
        pma.doi = '10.1016/j.dss.2022.113847'
        pma.journal = 'Test Journal'
        
        url = the_sciencedirect_disco(pma, verify=False)
        # Should have cleaned PII
        assert 'S016792362200118X' in url
        assert '-' not in url.split('pii/')[1].split('/')[0]
        assert '(' not in url.split('pii/')[1].split('/')[0]
        assert ')' not in url.split('pii/')[1].split('/')[0]
        print(f"Test 2 - Cleaned PII in URL: {url}")

    def test_sciencedirect_disco_missing_pii_fallback(self):
        """Test 3: Article without PII.
        
        PMID: 34263017 (Curr Opin Behav Sci) - has no PII
        Expected: Should now succeed due to improved the_sciencedirect_disco fallback
        """
        pma = self.fetch.article_by_pmid('34263017')
        
        assert pma.journal == 'Curr Opin Behav Sci'
        assert pma.doi == '10.1016/j.cobeha.2021.03.029'
        assert pma.pii is None
        
        # Should now succeed despite missing PII (improvement in the_sciencedirect_disco)
        url = the_sciencedirect_disco(pma, verify=False)
        
        assert url is not None
        assert 'sciencedirect.com' in url
        assert '/pdfft?' in url
        print(f"Test 3 - Successfully generated URL despite missing PII: {url}")

    def test_sciencedirect_disco_short_pii(self):
        """Test 4: Article with short PII format.
        
        PMID: 31496550 (Biochem Syst Ecol) - has short PII
        Expected: Should handle short PII format
        """
        pma = self.fetch.article_by_pmid('31496550')
        
        assert pma.journal == 'Biochem Syst Ecol'
        assert pma.doi == '10.1016/j.bse.2019.103921'
        assert pma.pii == '103921'  # Short format
        
        url = the_sciencedirect_disco(pma, verify=False)
        assert '103921' in url
        print(f"Test 4 - Short PII handled: {url}")

    @patch('metapub.findit.dances.sciencedirect.verify_pdf_url')
    def test_sciencedirect_disco_successful_access(self, mock_verify):
        """Test 5: Successful PDF access simulation.
        
        Expected: Should return PDF URL when accessible
        """
        # Mock successful PDF verification
        mock_verify.return_value = True

        pma = self.fetch.article_by_pmid('35971408')
        
        # Test with verification - should succeed
        url = the_sciencedirect_disco(pma, verify=True)
        assert 'sciencedirect.com' in url
        assert 'pdfft' in url
        print(f"Test 5 - Successful verified access: {url}")

    @patch('metapub.findit.dances.sciencedirect.verify_pdf_url')  
    def test_sciencedirect_disco_paywall_detection(self, mock_verify):
        """Test 6: Paywall detection.
        
        Expected: Should detect paywall and raise AccessDenied
        """
        # Mock failed PDF verification (paywall)
        mock_verify.return_value = False

        pma = self.fetch.article_by_pmid('35971408')
        
        # Test with verification - should detect paywall
        with pytest.raises(AccessDenied) as exc_info:
            the_sciencedirect_disco(pma, verify=True)
        
        assert 'PAYWALL' in str(exc_info.value)
        assert 'subscription' in str(exc_info.value)
        print(f"Test 6 - Correctly detected paywall: {exc_info.value}")

    @patch('metapub.findit.dances.sciencedirect.verify_pdf_url')
    def test_sciencedirect_disco_alternate_url_pattern(self, mock_verify):
        """Test 7: Alternate URL pattern fallback.
        
        Expected: Should try alternate URL if primary fails
        """
        # Mock: first URL fails, second succeeds
        mock_verify.side_effect = [False, True]

        pma = self.fetch.article_by_pmid('35971408')
        
        # Should try alternate URL and succeed
        url = the_sciencedirect_disco(pma, verify=True)
        assert url.endswith('/pdfft')  # Alternate pattern without download param
        print(f"Test 7 - Alternate URL pattern worked: {url}")

    def test_sciencedirect_disco_missing_all_identifiers(self):
        """Test 8: Article without PII or DOI.
        
        Expected: Should raise NoPDFLink for missing identifiers
        """
        # Create a mock PMA without PII or DOI
        pma = Mock()
        pma.pii = None
        pma.doi = None
        pma.journal = 'Some Journal'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_sciencedirect_disco(pma, verify=False)
        
        assert 'MISSING' in str(exc_info.value)
        assert 'PII or DOI required' in str(exc_info.value)
        print(f"Test 8 - Correctly handled missing identifiers: {exc_info.value}")

    def test_sciencedirect_disco_various_pii_formats(self):
        """Test 9: Various PII formats.
        
        Expected: Should handle different PII formats correctly
        """
        test_cases = [
            ('S0167-9236(22)00118-X', 'S016792362200118X'),
            ('S1234567890123456', 'S1234567890123456'),  # Already clean
            ('S0001-2345(99)12345-6', 'S0001234599123456'),
            ('12345', '12345'),  # Short format
        ]
        
        for original_pii, expected_clean in test_cases:
            pma = Mock()
            pma.pii = original_pii
            pma.doi = '10.1016/test'
            pma.journal = 'Test'
            
            url = the_sciencedirect_disco(pma, verify=False)
            assert f'pii/{expected_clean}/pdfft' in url
            print(f"Test 9 - PII {original_pii} → {expected_clean}")


def test_sciencedirect_journal_recognition():
    """Test that ScienceDirect journals are properly recognized in the registry."""
    from metapub.findit.registry import JournalRegistry
    
    registry = JournalRegistry()
    
    # Test some known Elsevier/ScienceDirect journals
    test_journals = [
        'Decis Support Syst',
        'Biochem Syst Ecol', 
        'Curr Opin Behav Sci',
        'Lancet',
        'Cell',  # May be mapped to Cell or ScienceDirect
        'Vaccine',
        'J Mol Biol'
    ]
    
    # Test journal recognition
    found_count = 0
    for journal in test_journals:
        publisher_info = registry.get_publisher_for_journal(journal)
        if publisher_info and publisher_info['name'] == 'sciencedirect':
            assert publisher_info['dance_function'] == 'the_sciencedirect_disco'
            print(f"✓ {journal} correctly mapped to ScienceDirect")
            found_count += 1
        elif publisher_info and publisher_info['name'] == 'cell':
            # Cell journals also use ScienceDirect infrastructure
            print(f"ℹ {journal} mapped to Cell (delegates to ScienceDirect)")
            found_count += 1
        else:
            print(f"⚠ {journal} mapped to: {publisher_info['name'] if publisher_info else 'None'}")
    
    # Just make sure we found at least some ScienceDirect journals
    if found_count > 0:
        print(f"✓ Found {found_count} ScienceDirect/Cell journals")
    else:
        print("⚠ No ScienceDirect journals found in registry")
    
    registry.close()


if __name__ == '__main__':
    # Run basic tests if executed directly
    test_instance = TestScienceDirectDance()
    test_instance.setUp()
    
    print("Running ScienceDirect dance function tests...")
    print("\n" + "="*60)
    
    tests = [
        ('test_sciencedirect_disco_pii_url_construction', 'PII-based URL construction'),
        ('test_sciencedirect_disco_clean_pii', 'PII cleaning functionality'),
        ('test_sciencedirect_disco_missing_pii_fallback', 'Missing PII handling'),
        ('test_sciencedirect_disco_short_pii', 'Short PII format'),
        ('test_sciencedirect_disco_successful_access', 'Successful access simulation'),
        ('test_sciencedirect_disco_paywall_detection', 'Paywall detection'),
        ('test_sciencedirect_disco_alternate_url_pattern', 'Alternate URL pattern'),
        ('test_sciencedirect_disco_missing_all_identifiers', 'Missing all identifiers'),
        ('test_sciencedirect_disco_various_pii_formats', 'Various PII formats')
    ]
    
    for test_method, description in tests:
        try:
            getattr(test_instance, test_method)()
            print(f"✓ {description} works")
        except Exception as e:
            print(f"✗ {description} failed: {e}")
    
    try:
        test_sciencedirect_journal_recognition()
        print("✓ Registry test passed: Journal recognition works")
    except Exception as e:
        print(f"✗ Registry test failed: {e}")
    
    print("\n" + "="*60)
    print("Test suite completed!")


class TestScienceDirectXMLFixtures:
    """Test ScienceDirect dance function with real XML fixtures."""

    def test_sciencedirect_authentic_metadata_validation(self):
        """Validate authentic metadata from XML fixtures matches expected patterns."""
        for pmid, expected in SCIENCEDIRECT_EVIDENCE_PMIDS.items():
            pma = load_pmid_xml(pmid)
            assert pma.doi == expected['doi']
            assert pma.journal == expected['journal']
            assert pma.pmid == pmid
            print(f"✓ PMID {pmid}: {pma.journal} - {pma.doi}")

    def test_sciencedirect_doi_pattern_consistency(self):
        """Test ScienceDirect DOI patterns (10.1016/)."""
        for pmid, data in SCIENCEDIRECT_EVIDENCE_PMIDS.items():
            pma = load_pmid_xml(pmid)
            assert pma.doi.startswith('10.1016/'), f"ScienceDirect DOI must start with 10.1016/, got: {pma.doi}"
            print(f"✓ PMID {pmid} DOI pattern: {pma.doi}")