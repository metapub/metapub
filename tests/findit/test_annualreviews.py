"""Tests for Annual Reviews dance function."""

import pytest
from unittest.mock import patch, Mock

from .common import BaseDanceTest
from metapub import PubMedFetcher
from metapub.findit.dances import the_annualreviews_round
from metapub.exceptions import AccessDenied, NoPDFLink


class TestAnnualReviewsDance(BaseDanceTest):
    """Test cases for Annual Reviews Inc. publisher."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.fetch = PubMedFetcher()

    def test_annualreviews_round_url_construction_phytopathol(self):
        """Test 1: URL construction success (Annu Rev Phytopathol).
        
        PMID: 38885471 (Annu Rev Phytopathol)
        Expected: Should construct valid Annual Reviews PDF URL directly
        """
        pma = self.fetch.article_by_pmid('38885471')
        
        assert pma.journal == 'Annu Rev Phytopathol'
        assert pma.doi == '10.1146/annurev-phyto-021722-034823'
        print(f"Test 1 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification (should always work for URL construction)
        url = the_annualreviews_round(pma, verify=False)
        assert url is not None
        assert 'annualreviews.org' in url
        assert '/deliver/fulltext/phyto/' in url
        assert 'annurev-phyto-021722-034823.pdf' in url
        print(f"Test 1 - PDF URL: {url}")

    def test_annualreviews_round_url_construction_genomics(self):
        """Test 2: Annual Review of Genomics and Human Genetics article.
        
        PMID: 38724024 (Annu Rev Genomics Hum Genet)
        Expected: Should construct valid Annual Reviews PDF URL directly
        """
        pma = self.fetch.article_by_pmid('38724024')
        
        assert pma.journal == 'Annu Rev Genomics Hum Genet'
        assert pma.doi == '10.1146/annurev-genom-121222-105345'
        print(f"Test 2 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification  
        url = the_annualreviews_round(pma, verify=False)
        assert url is not None
        assert 'annualreviews.org' in url
        assert '/deliver/fulltext/genom/' in url
        assert 'annurev-genom-121222-105345.pdf' in url
        print(f"Test 2 - PDF URL: {url}")

    def test_annualreviews_round_url_construction_marine_sci(self):
        """Test 3: Annual Review of Marine Science article.
        
        PMID: 38896540 (Ann Rev Mar Sci)
        Expected: Should construct valid Annual Reviews PDF URL directly
        """
        pma = self.fetch.article_by_pmid('38896540')
        
        assert pma.journal == 'Ann Rev Mar Sci'
        assert pma.doi == '10.1146/annurev-marine-121422-015323'
        print(f"Test 3 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification
        url = the_annualreviews_round(pma, verify=False)
        assert url is not None
        assert 'annualreviews.org' in url
        assert '/deliver/fulltext/marine/' in url
        assert 'annurev-marine-121422-015323.pdf' in url
        print(f"Test 3 - PDF URL: {url}")

    @patch('metapub.findit.dances.annualreviews.verify_pdf_url')
    def test_annualreviews_round_successful_access_with_verification(self, mock_verify):
        """Test 4: Successful access with verification.
        
        PMID: 38885471 (Annu Rev Phytopathol)
        Expected: Should return PDF URL when verification passes
        """
        # Mock successful PDF verification
        mock_verify.return_value = True

        pma = self.fetch.article_by_pmid('38885471')
        
        # Test with verification - should return PDF URL
        url = the_annualreviews_round(pma, verify=True)
        assert 'annualreviews.org' in url
        assert '/deliver/fulltext/phyto/' in url
        assert '.pdf' in url
        
        # Verify that verify_pdf_url was called
        mock_verify.assert_called_once()
        print(f"Test 4 - Verified PDF URL: {url}")

    @patch('metapub.findit.dances.annualreviews.verify_pdf_url')
    def test_annualreviews_round_paywall_detection(self, mock_verify):
        """Test 5: Paywall detection via verification.
        
        Expected: Should detect paywall when PDF verification fails
        """
        # Mock failed PDF verification (paywall)
        mock_verify.return_value = False

        pma = self.fetch.article_by_pmid('38885471')
        
        # Test with verification - should detect paywall
        with pytest.raises(AccessDenied) as exc_info:
            the_annualreviews_round(pma, verify=True)
        
        assert 'PAYWALL' in str(exc_info.value)
        assert 'subscription' in str(exc_info.value)
        mock_verify.assert_called_once()
        print(f"Test 5 - Correctly detected paywall: {exc_info.value}")

    def test_annualreviews_round_missing_doi(self):
        """Test 6: Article without DOI.
        
        Expected: Should raise NoPDFLink for missing DOI
        """
        # Create a mock PMA without DOI
        pma = Mock()
        pma.doi = None
        pma.journal = 'Annu Rev Phytopathol'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_annualreviews_round(pma, verify=False)
        
        assert 'MISSING' in str(exc_info.value)
        assert 'DOI required' in str(exc_info.value)
        print(f"Test 6 - Correctly handled missing DOI: {exc_info.value}")

    def test_annualreviews_round_invalid_doi(self):
        """Test 7: Article with non-Annual Reviews DOI.
        
        Expected: Should raise NoPDFLink for invalid DOI pattern
        """
        # Create a mock PMA with non-Annual Reviews DOI
        pma = Mock()
        pma.doi = '10.1000/invalid-doi'
        pma.journal = 'Annu Rev Phytopathol'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_annualreviews_round(pma, verify=False)
        
        assert 'INVALID' in str(exc_info.value)
        assert '10.1146/' in str(exc_info.value)
        print(f"Test 7 - Correctly handled invalid DOI: {exc_info.value}")

    def test_annualreviews_round_malformed_doi_suffix(self):
        """Test 8: DOI with malformed suffix (can't extract journal).
        
        Expected: Should raise NoPDFLink for malformed DOI suffix
        """
        # Create a mock PMA with malformed Annual Reviews DOI
        pma = Mock()
        pma.doi = '10.1146/malformed-doi-without-journal'
        pma.journal = 'Annu Rev Phytopathol'
        pma.volume = '62'
        pma.issue = '1'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_annualreviews_round(pma, verify=False)
        
        assert 'INVALID' in str(exc_info.value)
        assert 'Cannot extract journal abbreviation' in str(exc_info.value)
        print(f"Test 8 - Correctly handled malformed DOI: {exc_info.value}")

    def test_annualreviews_round_volume_issue_defaults(self):
        """Test 9: Article without volume/issue (should use defaults).
        
        Expected: Should default to volume=1, issue=1 when missing
        """
        # Create a mock PMA without volume/issue
        pma = Mock()
        pma.doi = '10.1146/annurev-phyto-021722-034823'
        pma.journal = 'Annu Rev Phytopathol'
        pma.volume = None
        pma.issue = None
        
        url = the_annualreviews_round(pma, verify=False)
        assert '/deliver/fulltext/phyto/1/1/' in url
        print(f"Test 9 - Used default volume/issue: {url}")

    def test_annualreviews_round_with_volume_issue(self):
        """Test 10: Article with volume/issue provided.
        
        Expected: Should use provided volume/issue in URL
        """
        # Create a mock PMA with volume/issue
        pma = Mock()
        pma.doi = '10.1146/annurev-phyto-021722-034823'
        pma.journal = 'Annu Rev Phytopathol'
        pma.volume = '62'
        pma.issue = '1'
        
        url = the_annualreviews_round(pma, verify=False)
        assert '/deliver/fulltext/phyto/62/1/' in url
        print(f"Test 10 - Used provided volume/issue: {url}")


def test_annualreviews_journal_recognition():
    """Test that Annual Reviews journals are properly recognized in the registry."""
    from metapub.findit.registry import JournalRegistry
    from metapub.findit.journals.annualreviews import annualreviews_journals
    
    registry = JournalRegistry()
    
    # Test sample Annual Reviews journals
    test_journals = [
        'Annu Rev Phytopathol',
        'Annu Rev Genomics Hum Genet',
        'Ann Rev Mar Sci',
        'Annu Rev Biochem',
        'Annu Rev Neurosci'
    ]
    
    # Test journal recognition
    found_count = 0
    for journal in test_journals:
        if journal in annualreviews_journals:
            publisher_info = registry.get_publisher_for_journal(journal)
            if publisher_info and publisher_info['name'] == 'annualreviews':
                assert publisher_info['dance_function'] == 'the_annualreviews_round'
                print(f"✓ {journal} correctly mapped to Annual Reviews")
                found_count += 1
            else:
                print(f"⚠ {journal} mapped to different publisher: {publisher_info['name'] if publisher_info else 'None'}")
        else:
            print(f"⚠ {journal} not in annualreviews_journals list")
    
    # Just make sure we found at least one Annual Reviews journal
    assert found_count > 0, "No Annual Reviews journals found in registry with annualreviews publisher"
    print(f"✓ Found {found_count} properly mapped Annual Reviews journals")
    
    registry.close()


if __name__ == '__main__':
    # Run basic tests if executed directly
    test_instance = TestAnnualReviewsDance()
    test_instance.setUp()
    
    print("Running Annual Reviews tests...")
    print("\n" + "="*60)
    
    tests = [
        ('test_annualreviews_round_url_construction_phytopathol', 'Annu Rev Phytopathol URL construction'),
        ('test_annualreviews_round_url_construction_genomics', 'Annu Rev Genomics Hum Genet URL construction'),
        ('test_annualreviews_round_url_construction_marine_sci', 'Ann Rev Mar Sci URL construction'),
        ('test_annualreviews_round_successful_access_with_verification', 'Successful access with verification'),
        ('test_annualreviews_round_paywall_detection', 'Paywall detection via verification'),
        ('test_annualreviews_round_missing_doi', 'Missing DOI handling'),
        ('test_annualreviews_round_invalid_doi', 'Invalid DOI pattern handling'),
        ('test_annualreviews_round_malformed_doi_suffix', 'Malformed DOI suffix handling'),
        ('test_annualreviews_round_volume_issue_defaults', 'Volume/issue defaults'),
        ('test_annualreviews_round_with_volume_issue', 'Provided volume/issue usage')
    ]
    
    for test_method, description in tests:
        try:
            getattr(test_instance, test_method)()
            print(f"✓ {description} works")
        except Exception as e:
            print(f"✗ {description} failed: {e}")
    
    try:
        test_annualreviews_journal_recognition()
        print("✓ Registry test passed: Journal recognition works")
    except Exception as e:
        print(f"✗ Registry test failed: {e}")
    
    print("\n" + "="*60)
    print("Test suite completed!")