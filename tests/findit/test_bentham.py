"""Tests for Bentham Science Publishers (EurekaSelect.com) dance function.

This module tests the_eureka_frug dance function which now handles the architectural
limitation that EurekaSelect requires POST-based downloads incompatible with FindIt's URL model.
"""

import pytest
from unittest.mock import patch, Mock

from .common import BaseDanceTest
from tests.fixtures import load_pmid_xml, BENTHAM_EVIDENCE_PMIDS
from metapub import PubMedFetcher
from metapub.findit.dances import the_eureka_frug
from metapub.exceptions import AccessDenied, NoPDFLink, BadDOI


class TestBenthamEurekaSelect(BaseDanceTest):
    """Test cases for Bentham Science Publishers journal access."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.fetch = PubMedFetcher()

    @patch('metapub.findit.dances.eureka.the_doi_2step')
    @patch('metapub.findit.dances.eureka.unified_uri_get')
    def test_eureka_frug_postonly_error(self, mock_get, mock_doi_step):
        """Test 1: EurekaSelect returns POSTONLY error with article URL.
        
        PMID: 38751602 (Current Genomics)
        Expected: Should resolve DOI and throw POSTONLY error with article URL
        """
        # Mock DOI resolution
        mock_doi_step.return_value = 'https://www.eurekaselect.com/article/139876'
        
        # Mock article page response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.url = 'https://www.eurekaselect.com/article/139876'
        mock_get.return_value = mock_response
        
        pma = self.fetch.article_by_pmid('38751602')
        
        assert pma.journal == 'Curr Genomics'
        assert pma.doi == '10.2174/0113892029284920240212091903'
        
        # Function should throw POSTONLY error
        with pytest.raises(NoPDFLink) as exc_info:
            the_eureka_frug(pma, verify=False)
        
        error_msg = str(exc_info.value)
        assert 'POSTONLY' in error_msg
        assert 'EurekaSelect PDF requires POST request' in error_msg
        assert 'https://www.eurekaselect.com/article/139876' in error_msg
        assert 'Download Article' in error_msg
        print(f"Test 1 - POSTONLY error: {error_msg}")

    @patch('metapub.findit.dances.eureka.the_doi_2step')
    @patch('metapub.findit.dances.eureka.unified_uri_get')
    def test_eureka_frug_postonly_with_verify(self, mock_get, mock_doi_step):
        """Test 2: EurekaSelect returns POSTONLY error even with verify=True.
        
        PMID: 38867537 (Current Molecular Medicine)
        Expected: Should throw POSTONLY error regardless of verification mode
        """
        # Mock DOI resolution
        mock_doi_step.return_value = 'https://www.eurekaselect.com/article/140986'
        
        # Mock article page response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.url = 'https://www.eurekaselect.com/article/140986'
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('38867537')
        
        assert pma.journal == 'Curr Mol Med'
        assert pma.doi == '10.2174/0115665240310818240531080353'
        
        # Function should throw POSTONLY error with verify=True
        with pytest.raises(NoPDFLink) as exc_info:
            the_eureka_frug(pma, verify=True)
        
        error_msg = str(exc_info.value)
        assert 'POSTONLY' in error_msg
        assert 'session data' in error_msg
        assert 'https://www.eurekaselect.com/article/140986' in error_msg
        print(f"Test 2 - POSTONLY with verify=True: {error_msg}")

    @patch('metapub.findit.dances.eureka.the_doi_2step')
    def test_eureka_frug_doi_resolution_error(self, mock_doi_step):
        """Test 3: Handle DOI resolution failure.
        
        Expected: Should raise TXERROR when DOI resolution fails
        """
        # Mock DOI resolution failure
        mock_doi_step.side_effect = BadDOI('DOI resolution failed')
        
        pma = self.fetch.article_by_pmid('38318823')
        
        # Function should handle DOI resolution error
        with pytest.raises(NoPDFLink) as exc_info:
            the_eureka_frug(pma, verify=False)
        
        error_msg = str(exc_info.value)
        assert 'TXERROR' in error_msg
        assert 'Could not resolve EurekaSelect DOI' in error_msg
        print(f"Test 3 - DOI resolution error: {error_msg}")

    def test_eureka_frug_no_doi(self):
        """Test 4: Article without DOI.
        
        Expected: Should raise MISSING error for articles without DOI
        """
        # Create mock PMA without DOI
        pma = Mock()
        pma.doi = None
        pma.journal = 'Test Bentham Journal'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_eureka_frug(pma, verify=False)
        
        error_msg = str(exc_info.value)
        assert 'MISSING' in error_msg
        assert 'DOI required for EurekaSelect journals' in error_msg
        print(f"Test 4 - Missing DOI error: {error_msg}")

    @patch('metapub.findit.dances.eureka.the_doi_2step')
    @patch('metapub.findit.dances.eureka.unified_uri_get')
    def test_eureka_frug_wrong_site(self, mock_get, mock_doi_step):
        """Test 5: DOI resolves to wrong site.
        
        Expected: Should raise TXERROR when DOI doesn't resolve to EurekaSelect
        """
        # Mock DOI resolution to wrong site
        mock_doi_step.return_value = 'https://example.com/article/123'
        
        # Mock response from wrong site
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.url = 'https://example.com/article/123'
        mock_get.return_value = mock_response
        
        pma = Mock()
        pma.doi = '10.2174/test123'
        pma.journal = 'Test Journal'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_eureka_frug(pma, verify=False)
        
        error_msg = str(exc_info.value)
        assert 'TXERROR' in error_msg
        assert 'does not resolve to EurekaSelect article' in error_msg
        assert 'example.com' in error_msg
        print(f"Test 5 - Wrong site error: {error_msg}")

    @patch('metapub.findit.dances.eureka.the_doi_2step')
    @patch('metapub.findit.dances.eureka.unified_uri_get')
    def test_eureka_frug_http_error(self, mock_get, mock_doi_step):
        """Test 6: HTTP error accessing article page.
        
        Expected: Should raise TXERROR for HTTP errors
        """
        # Mock DOI resolution
        mock_doi_step.return_value = 'https://www.eurekaselect.com/article/123'
        
        # Mock HTTP error response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        pma = Mock()
        pma.doi = '10.2174/test123'
        pma.journal = 'Test Journal'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_eureka_frug(pma, verify=False)
        
        error_msg = str(exc_info.value)
        assert 'TXERROR' in error_msg
        assert 'Could not access EurekaSelect article page (HTTP 404)' in error_msg
        print(f"Test 6 - HTTP error: {error_msg}")


def test_bentham_journal_recognition():
    """Test basic function availability and POSTONLY behavior."""
    from metapub import PubMedFetcher
    from metapub.findit.dances import the_eureka_frug
    
    # Just test that the function correctly identifies as POSTONLY
    fetch = PubMedFetcher()
    
    # Test with a known Bentham article
    try:
        pma = fetch.article_by_pmid('38751602')  # Current Genomics
        if pma.doi and '2174' in pma.doi:  # Bentham DOI pattern
            with pytest.raises(NoPDFLink) as exc_info:
                the_eureka_frug(pma, verify=False)
            
            error_msg = str(exc_info.value)
            if 'POSTONLY' in error_msg:
                print(f"✓ EurekaSelect correctly returns POSTONLY error: {error_msg[:100]}...")
            else:
                print(f"⚠ Unexpected error type: {error_msg[:100]}...")
        else:
            print("⚠ Test article doesn't have expected Bentham DOI pattern")
    except Exception as e:
        print(f"⚠ Could not test with real article: {e}")


if __name__ == '__main__':
    # Run basic tests if executed directly
    test_instance = TestBenthamEurekaSelect()
    test_instance.setUp()
    
    print("Running Bentham Science Publishers (EurekaSelect) tests...")
    print("Note: All tests now expect POSTONLY errors due to architectural limitation")
    print("\n" + "=" * 70)
    
    tests = [
        ('test_eureka_frug_postonly_error', 'POSTONLY error with article URL'),
        ('test_eureka_frug_postonly_with_verify', 'POSTONLY error with verify=True'),
        ('test_eureka_frug_doi_resolution_error', 'DOI resolution error handling'),
        ('test_eureka_frug_no_doi', 'Missing DOI error handling'),
        ('test_eureka_frug_wrong_site', 'Wrong site error handling'),
        ('test_eureka_frug_http_error', 'HTTP error handling')
    ]
    
    for test_method, description in tests:
        try:
            getattr(test_instance, test_method)()
            print(f"✓ {description} works")
        except Exception as e:
            print(f"✗ {description} failed: {e}")
    
    try:
        test_bentham_journal_recognition()
        print("✓ Journal recognition test passed")
    except Exception as e:
        print(f"✗ Journal recognition test failed: {e}")
    
    print("\n" + "=" * 70)
    print("Test suite completed!")
    print("\nNote: EurekaSelect now throws POSTONLY errors because it requires")
    print("POST requests with session data, which is incompatible with FindIt's")
    print("URL-based model. Users must visit article pages and click 'Download Article'.")


class TestBenthamXMLFixtures:
    """Test Bentham/EurekaSelect XML fixtures for evidence-driven testing."""

    def test_bentham_xml_32525788_curr_mol_pharmacol(self):
        """Test PMID 32525788 - Curr Mol Pharmacol with DOI 10.2174/1874467213666200611142438."""
        pma = load_pmid_xml('32525788')
        
        assert pma.pmid == '32525788'
        assert pma.doi == '10.2174/1874467213666200611142438'
        assert 'Curr Mol Pharmacol' in pma.journal
        
        # Test that the function raises POSTONLY error as expected for current architecture
        from metapub.exceptions import NoPDFLink
        with pytest.raises(NoPDFLink, match="POSTONLY"):
            the_eureka_frug(pma, verify=False)

    def test_bentham_xml_36635930_recent_pat_biotechnol(self):
        """Test PMID 36635930 - Recent Pat Biotechnol with DOI 10.2174/1872208317666230111105223."""
        pma = load_pmid_xml('36635930')
        
        assert pma.pmid == '36635930'
        assert pma.doi == '10.2174/1872208317666230111105223'
        assert 'Recent Pat Biotechnol' in pma.journal
        
        # Test that the function raises POSTONLY error as expected for current architecture
        from metapub.exceptions import NoPDFLink
        with pytest.raises(NoPDFLink, match="POSTONLY"):
            the_eureka_frug(pma, verify=False)

    def test_bentham_xml_33568043_curr_mol_pharmacol(self):
        """Test PMID 33568043 - Curr Mol Pharmacol with DOI 10.2174/1874467214666210210122628."""
        pma = load_pmid_xml('33568043')
        
        assert pma.pmid == '33568043'
        assert pma.doi == '10.2174/1874467214666210210122628'
        assert 'Curr Mol Pharmacol' in pma.journal
        
        # Test that the function raises POSTONLY error as expected for current architecture
        from metapub.exceptions import NoPDFLink
        with pytest.raises(NoPDFLink, match="POSTONLY"):
            the_eureka_frug(pma, verify=False)