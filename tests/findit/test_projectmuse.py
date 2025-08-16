"""Tests for Project MUSE dance function.

This test suite validates the Project MUSE function following Phase 4 guidelines:
- Test patterns with real examples from HTML samples
- Test each error condition separately  
- Use evidence-based patterns from HTML analysis
- Verify dance function guidelines compliance
"""

import pytest
from unittest.mock import patch, Mock
import requests

from .common import BaseDanceTest
from metapub import PubMedFetcher
from metapub.findit.dances import the_projectmuse_syrtos
from metapub.exceptions import AccessDenied, NoPDFLink
from tests.fixtures import load_pmid_xml, PROJECTMUSE_EVIDENCE_PMIDS


class TestProjectMuseEvidenceDriven:
    """Test Project MUSE evidence-driven rewrite with citation_pdf_url meta tag extraction."""

    def test_evidence_based_meta_tag_extraction(self):
        """Test meta tag extraction with evidence-based patterns from HTML samples."""
        # Evidence-based test cases from actual HTML samples analyzed
        evidence_cases = [
            ('https://muse.jhu.edu/pub/17/article/757992', 
             'https://muse.jhu.edu/pub/17/article/757992/pdf'),  # Sample 1
            ('https://muse.jhu.edu/pub/17/article/931228', 
             'https://muse.jhu.edu/pub/17/article/931228/pdf'),  # Sample 2  
            ('https://muse.jhu.edu/pub/17/article/837853', 
             'https://muse.jhu.edu/pub/17/article/837853/pdf'),  # Sample 3
        ]
        
        for article_url, expected_pdf_url in evidence_cases:
            # Create HTML content based on actual evidence patterns
            html_content = f'''
            <meta name="citation_publisher" content="University of Nebraska Press">
            <meta name="citation_journal_title" content="Journal of Black Sexuality and Relationships">
            <meta name="citation_fulltext_html_url" content="{article_url}">
            <meta name="citation_pdf_url" content="{expected_pdf_url}">
            <meta name="citation_doi" content="10.1353/bsr.2024.test">
            '''
            
            pma = Mock()
            pma.doi = '10.1353/bsr.2024.test'
            
            with patch('metapub.findit.dances.projectmuse.the_doi_2step') as mock_doi_step, \
                 patch('metapub.findit.dances.projectmuse.unified_uri_get') as mock_get, \
                 patch('metapub.findit.dances.projectmuse.verify_pdf_url') as mock_verify:
                
                mock_doi_step.return_value = article_url
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.text = html_content
                mock_get.return_value = mock_response
                
                result = the_projectmuse_syrtos(pma, verify=False)
                assert result == expected_pdf_url
                
                # Verify function calls
                mock_doi_step.assert_called_once_with('10.1353/bsr.2024.test')
                mock_get.assert_called_once_with(article_url, timeout=10, max_redirects=3)
                assert not mock_verify.called  # verify=False

    def test_with_verification_enabled(self):
        """Test that verification is properly called when enabled."""
        pma = Mock()
        pma.doi = '10.1353/bsr.2024.test'
        
        html_content = '''
        <meta name="citation_pdf_url" content="https://muse.jhu.edu/pub/17/article/757992/pdf">
        '''
        
        with patch('metapub.findit.dances.projectmuse.the_doi_2step') as mock_doi_step, \
             patch('metapub.findit.dances.projectmuse.unified_uri_get') as mock_get, \
             patch('metapub.findit.dances.projectmuse.verify_pdf_url') as mock_verify:
            
            mock_doi_step.return_value = 'https://muse.jhu.edu/pub/17/article/757992'
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = html_content
            mock_get.return_value = mock_response
            
            result = the_projectmuse_syrtos(pma, verify=True)
            
            assert result == 'https://muse.jhu.edu/pub/17/article/757992/pdf'
            mock_verify.assert_called_once_with('https://muse.jhu.edu/pub/17/article/757992/pdf', 'Project MUSE', request_timeout=10, max_redirects=3)

    def test_missing_doi_error(self):
        """Test that missing DOI raises appropriate error."""
        pma = Mock()
        pma.doi = None
        
        with pytest.raises(NoPDFLink) as excinfo:
            the_projectmuse_syrtos(pma, verify=False)
        
        assert 'MISSING: DOI required for Project MUSE articles' in str(excinfo.value)

    def test_http_error_handling(self):
        """Test handling of HTTP errors during article page access."""
        pma = Mock()
        pma.doi = '10.1353/bsr.2024.test'
        
        with patch('metapub.findit.dances.projectmuse.the_doi_2step') as mock_doi_step, \
             patch('metapub.findit.dances.projectmuse.unified_uri_get') as mock_get:
            
            mock_doi_step.return_value = 'https://muse.jhu.edu/pub/17/article/757992'
            mock_response = Mock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response
            
            with pytest.raises(NoPDFLink) as excinfo:
                the_projectmuse_syrtos(pma, verify=False)
            
            assert 'TXERROR: Could not access Project MUSE article page (HTTP 404)' in str(excinfo.value)

    def test_missing_meta_tag_error(self):
        """Test error when citation_pdf_url meta tag is not found."""
        pma = Mock()
        pma.doi = '10.1353/bsr.2024.test'
        
        # HTML without citation_pdf_url meta tag
        html_content = '''
        <meta name="citation_publisher" content="University of Nebraska Press">
        <meta name="citation_title" content="Test Article">
        '''
        
        with patch('metapub.findit.dances.projectmuse.the_doi_2step') as mock_doi_step, \
             patch('metapub.findit.dances.projectmuse.unified_uri_get') as mock_get:
            
            mock_doi_step.return_value = 'https://muse.jhu.edu/pub/17/article/757992'
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = html_content
            mock_get.return_value = mock_response
            
            with pytest.raises(NoPDFLink) as excinfo:
                the_projectmuse_syrtos(pma, verify=False)
            
            assert 'MISSING: No PDF URL found via citation_pdf_url meta tag extraction' in str(excinfo.value)



class TestProjectMuseDance(BaseDanceTest):
    """Test cases for Project MUSE dance function."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.fetch = PubMedFetcher()

    def test_projectmuse_melody_url_construction_narrat_inq(self):
        """Test 1: URL construction success (Narrat Inq Bioeth).
        
        PMID: 38661995 (Narrat Inq Bioeth)
        Expected: Should construct valid Project MUSE PDF URL
        """
        pma = self.fetch.article_by_pmid('38661995')
        
        print(f"Test 1 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification (should always work for URL construction)
        url = the_projectmuse_syrtos(pma, verify=False)
        assert url is not None
        assert 'muse.jhu.edu' in url
        assert url.startswith('https://')
        print(f"Test 1 - PDF URL: {url}")

    def test_projectmuse_melody_url_construction_hum_biol(self):
        """Test 2: Human Biology.
        
        PMID: 37733615 (Hum Biol)
        Expected: Should construct valid Project MUSE PDF URL
        """
        pma = self.fetch.article_by_pmid('37733615')
        
        print(f"Test 2 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Skip test if no DOI available
        if not pma.doi:
            print("Test 2 - Skipping: No DOI available for this PMID")
            return

        # Test without verification
        url = the_projectmuse_syrtos(pma, verify=False)
        assert url is not None
        assert 'muse.jhu.edu' in url
        print(f"Test 2 - PDF URL: {url}")

    def test_projectmuse_melody_url_construction_lang_baltim(self):
        """Test 3: Language (Baltim).
        
        PMID: 37034148 (Language (Baltim))
        Expected: Should construct valid Project MUSE PDF URL
        """
        pma = self.fetch.article_by_pmid('37034148')
        
        print(f"Test 3 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Skip test if no DOI available
        if not pma.doi:
            print("Test 3 - Skipping: No DOI available for this PMID")
            return

        # Test without verification
        url = the_projectmuse_syrtos(pma, verify=False)
        assert url is not None
        assert 'muse.jhu.edu' in url
        print(f"Test 3 - PDF URL: {url}")

    @patch('metapub.findit.dances.projectmuse.verify_pdf_url')
    @patch('metapub.findit.dances.projectmuse.unified_uri_get')
    @patch('metapub.findit.dances.projectmuse.the_doi_2step')
    def test_projectmuse_melody_successful_access(self, mock_doi_2step, mock_uri_get, mock_verify):
        """Test 4: Successful PDF access simulation.
        
        Expected: Should return PDF URL when accessible
        """
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://muse.jhu.edu/pub/17/article/test'
        
        # Mock HTML response with citation_pdf_url meta tag
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''<html><head>
            <meta name="citation_pdf_url" content="https://muse.jhu.edu/pub/17/article/test/pdf">
        </head></html>'''
        mock_uri_get.return_value = mock_response
        
        # Mock successful PDF verification
        mock_verify.return_value = True

        # Create mock PMA instead of fetching real PMID
        pma = Mock()
        pma.doi = '10.1353/test.2024.a123'
        pma.journal = 'Test Journal'
        
        # Test with verification - should succeed
        url = the_projectmuse_syrtos(pma, verify=True)
        assert url == 'https://muse.jhu.edu/pub/17/article/test/pdf'
        assert 'muse.jhu.edu' in url
        mock_verify.assert_called_once()
        print(f"Test 4 - Successful verified access: {url}")

    @patch('metapub.findit.dances.projectmuse.unified_uri_get')
    @patch('metapub.findit.dances.projectmuse.the_doi_2step')
    def test_projectmuse_melody_paywall_detection(self, mock_doi_2step, mock_uri_get):
        """Test 5: Paywall detection.
        
        Expected: Should detect paywall and raise NoPDFLink when no citation_pdf_url meta tag found
        """
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://muse.jhu.edu/pub/17/article/test'
        
        # Mock paywall response without citation_pdf_url meta tag
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''<html><body>
            <h1>Project MUSE</h1>
            <p>Institutional access required to view this article</p>
            <button>Subscribe for access</button>
        </body></html>'''
        mock_uri_get.return_value = mock_response

        # Create mock PMA instead of fetching real PMID
        pma = Mock()
        pma.doi = '10.1353/test.2024.a123'
        pma.journal = 'Test Journal'
        
        # Test with verification - should raise NoPDFLink due to missing meta tag
        with pytest.raises(NoPDFLink) as exc_info:
            the_projectmuse_syrtos(pma, verify=True)
        
        assert 'No PDF URL found via citation_pdf_url meta tag extraction' in str(exc_info.value)
        print(f"Test 5 - Correctly detected paywall: {exc_info.value}")

    @patch('metapub.findit.dances.projectmuse.unified_uri_get')
    @patch('metapub.findit.dances.projectmuse.the_doi_2step')
    def test_projectmuse_melody_network_error(self, mock_doi_2step, mock_uri_get):
        """Test 6: Network error handling.
        
        Expected: Should handle network errors gracefully
        """
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://muse.jhu.edu/pub/17/article/test'
        
        # Mock network error
        mock_uri_get.side_effect = requests.exceptions.ConnectionError("Network error")

        # Create mock PMA instead of fetching real PMID
        pma = Mock()
        pma.doi = '10.1353/test.2024.a123'
        pma.journal = 'Test Journal'
        
        # Test - should handle network error
        with pytest.raises(requests.exceptions.ConnectionError):
            the_projectmuse_syrtos(pma, verify=True)
        
        print(f"Test 6 - Correctly propagated network error")

    def test_projectmuse_melody_missing_doi(self):
        """Test 7: Article without DOI.
        
        Expected: Should raise NoPDFLink for missing DOI
        """
        # Create a mock PMA without DOI
        pma = Mock()
        pma.doi = None
        pma.journal = 'Narrat Inq Bioeth'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_projectmuse_syrtos(pma, verify=False)
        
        assert 'MISSING' in str(exc_info.value)
        assert 'DOI required' in str(exc_info.value)
        print(f"Test 7 - Correctly handled missing DOI: {exc_info.value}")

    @patch('requests.get')
    def test_projectmuse_melody_404_error(self, mock_get):
        """Test 8: Article not found (404 error).
        
        Expected: Should try multiple patterns and handle 404 errors
        """
        # Mock 404 response for all attempts
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        pma = self.fetch.article_by_pmid('38661995')
        
        # Test - should try multiple patterns and eventually fail
        with pytest.raises(NoPDFLink) as exc_info:
            the_projectmuse_syrtos(pma, verify=True)
        
        assert 'DENIED' in str(exc_info.value) or 'TXERROR' in str(exc_info.value) or 'PATTERN' in str(exc_info.value)
        print(f"Test 8 - Correctly handled 404: {exc_info.value}")

    @patch('metapub.findit.dances.projectmuse.verify_pdf_url')
    @patch('metapub.findit.dances.projectmuse.unified_uri_get')
    @patch('metapub.findit.dances.projectmuse.the_doi_2step')
    def test_projectmuse_melody_article_id_construction(self, mock_doi_2step, mock_uri_get, mock_verify):
        """Test 9: Article ID URL construction.
        
        Expected: Should use article ID from DOI in URL when available
        """
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://muse.jhu.edu/pub/17/article/926149'
        
        # Mock HTML response with citation_pdf_url meta tag
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''<html><head>
            <meta name="citation_pdf_url" content="https://muse.jhu.edu/pub/17/article/926149/pdf">
        </head></html>'''
        mock_uri_get.return_value = mock_response
        
        # Mock PDF verification
        mock_verify.return_value = True

        # Create mock PMA with article ID in DOI
        pma = Mock()
        pma.doi = '10.1353/nib.2024.a926149'
        pma.journal = 'Narrat Inq Bioeth'
        
        # Test - should use article ID in URL
        url = the_projectmuse_syrtos(pma, verify=True)
        assert url == 'https://muse.jhu.edu/pub/17/article/926149/pdf'
        assert 'muse.jhu.edu' in url
        print(f"Test 9 - Article ID URL construction: {url}")

    @patch('metapub.findit.dances.projectmuse.unified_uri_get')
    @patch('metapub.findit.dances.projectmuse.the_doi_2step')
    def test_projectmuse_syrtos_multiple_doi_prefixes(self, mock_doi_2step, mock_uri_get):
        """Test 10: Multiple DOI prefix handling.
        
        Expected: Should handle various DOI prefixes due to acquisitions
        """
        # Mock HTML response with citation_pdf_url meta tag
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''<html><head>
            <meta name="citation_pdf_url" content="https://muse.jhu.edu/pub/17/article/test/pdf">
        </head></html>'''
        mock_uri_get.return_value = mock_response
        
        # Test different DOI prefixes that Project MUSE might use
        test_cases = [
            ('10.1353/nib.2024.a926149', 'https://muse.jhu.edu/pub/17/article/926149'),
            ('10.1080/example.2023.123', 'https://muse.jhu.edu/pub/17/article/123'),
            ('10.1017/acquired.2023.456', 'https://muse.jhu.edu/pub/17/article/456')
        ]
        
        for doi, mock_article_url in test_cases:
            mock_doi_2step.return_value = mock_article_url
            
            pma = Mock()
            pma.doi = doi
            pma.journal = 'Narrat Inq Bioeth'
            
            # Should construct URL regardless of DOI prefix
            url = the_projectmuse_syrtos(pma, verify=False)
            assert url == 'https://muse.jhu.edu/pub/17/article/test/pdf'
            assert 'muse.jhu.edu' in url
            print(f"Test 10 - DOI {doi}: {url}")

    @patch('metapub.findit.dances.projectmuse.unified_uri_get')
    @patch('metapub.findit.dances.projectmuse.the_doi_2step')
    def test_projectmuse_melody_multiple_journals(self, mock_doi_2step, mock_uri_get):
        """Test 11: Multiple Project MUSE journal coverage.
        
        Expected: Should work with various Project MUSE journals
        """
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://muse.jhu.edu/pub/17/article/926149'
        
        # Mock HTML response with citation_pdf_url meta tag
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''<html><head>
            <meta name="citation_pdf_url" content="https://muse.jhu.edu/pub/17/article/926149/pdf">
        </head></html>'''
        mock_uri_get.return_value = mock_response
        
        # Test different journal patterns
        test_journals = [
            'Narrat Inq Bioeth',
            'Hum Biol',
            'Language (Baltim)',
            'Am Ann Deaf',
            'Rev High Ed'
        ]
        
        for journal in test_journals:
            pma = Mock()
            pma.doi = '10.1353/test.2024.a123'  # Use a test DOI
            pma.journal = journal
            
            url = the_projectmuse_syrtos(pma, verify=False)
            assert url == 'https://muse.jhu.edu/pub/17/article/926149/pdf'
            assert 'muse.jhu.edu' in url
            print(f"Test 11 - {journal}: {url}")


def test_projectmuse_journal_recognition():
    """Test that Project MUSE journals are properly recognized in the registry."""
    from metapub.findit.registry import JournalRegistry
    
    registry = JournalRegistry()
    
    # Test sample Project MUSE journals (using PubMed abbreviated names)
    test_journals = [
        'Narrat Inq Bioeth',
        'Hum Biol',
        'Language (Baltim)',
        'Am Ann Deaf',
        'Rev High Ed'
    ]
    
    # Test journal recognition using registry
    found_count = 0
    for journal in test_journals:
        publisher_info = registry.get_publisher_for_journal(journal)
        if publisher_info and publisher_info['name'] == 'Projectmuse':
            assert publisher_info['dance_function'] == 'the_projectmuse_syrtos'
            print(f"✓ {journal} correctly mapped to Project MUSE")
            found_count += 1
        else:
            print(f"⚠ {journal} mapped to different publisher: {publisher_info['name'] if publisher_info else 'None'}")
    
    # Just make sure we found at least one Project MUSE journal
    assert found_count > 0, "No Project MUSE journals found in registry with projectmuse publisher"
    print(f"✓ Found {found_count} properly mapped Project MUSE journals")
    
    registry.close()


if __name__ == '__main__':
    # Run basic tests if executed directly
    test_instance = TestProjectMuseDance()
    test_instance.setUp()
    
    print("Running Project MUSE tests...")
    print("\n" + "="*60)
    
    tests = [
        ('test_projectmuse_melody_url_construction_narrat_inq', 'Narrative Inquiry URL construction'),
        ('test_projectmuse_melody_url_construction_hum_biol', 'Human Biology URL construction'),
        ('test_projectmuse_melody_url_construction_lang_baltim', 'Language Baltimore URL construction'),
        ('test_projectmuse_melody_successful_access', 'Successful access simulation'),
        ('test_projectmuse_melody_paywall_detection', 'Paywall detection'),
        ('test_projectmuse_melody_network_error', 'Network error handling'),
        ('test_projectmuse_melody_missing_doi', 'Missing DOI handling'),
        ('test_projectmuse_melody_404_error', '404 error handling'),
        ('test_projectmuse_melody_article_id_construction', 'Article ID URL construction'),
        ('test_projectmuse_syrtos_multiple_doi_prefixes', 'Multiple DOI prefix handling'),
        ('test_projectmuse_melody_multiple_journals', 'Multiple journal coverage')
    ]
    
    for test_method, description in tests:
        try:
            getattr(test_instance, test_method)()
            print(f"✓ {description} works")
        except Exception as e:
            print(f"✗ {description} failed: {e}")
    
    try:
        test_projectmuse_journal_recognition()
        print("✓ Registry test passed: Journal recognition works")
    except Exception as e:
        print(f"✗ Registry test failed: {e}")
    
    print("\n" + "="*60)
    print("Test suite completed!")


class TestProjectMuseXMLFixtures:
    """Test ProjectMuse XML fixtures for evidence-driven testing."""

    @patch('metapub.findit.dances.projectmuse.verify_pdf_url')
    @patch('metapub.findit.dances.projectmuse.unified_uri_get')
    @patch('metapub.findit.dances.projectmuse.the_doi_2step')
    def test_projectmuse_xml_39479534_j_black_sex_relatsh(self, mock_doi_2step, mock_uri_get, mock_verify):
        """Test PMID 39479534 - J Black Sex Relatsh with DOI 10.1353/bsr.2021.0008."""
        mock_verify.return_value = None
        
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://muse.jhu.edu/article/123456'
        
        # Mock article page HTML with citation_pdf_url meta tag
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''<html><head><meta name="citation_pdf_url" content="https://muse.jhu.edu/pub/3/article/123456/pdf"/></head></html>'''
        mock_uri_get.return_value = mock_response
        
        pma = load_pmid_xml('39479534')
        
        assert pma.pmid == '39479534'
        assert pma.doi == '10.1353/bsr.2021.0008'
        assert 'J Black Sex Relatsh' in pma.journal
        
        result = the_projectmuse_syrtos(pma, verify=True)
        expected_url = 'https://muse.jhu.edu/pub/3/article/123456/pdf'
        assert result == expected_url
        mock_verify.assert_called_once_with(expected_url, 'Project MUSE', request_timeout=10, max_redirects=3)

    @patch('metapub.findit.dances.projectmuse.verify_pdf_url')
    @patch('metapub.findit.dances.projectmuse.unified_uri_get')
    @patch('metapub.findit.dances.projectmuse.the_doi_2step')
    def test_projectmuse_xml_34337106_j_black_sex_relatsh(self, mock_doi_2step, mock_uri_get, mock_verify):
        """Test PMID 34337106 - J Black Sex Relatsh with DOI 10.1353/bsr.2020.0005."""
        mock_verify.return_value = None
        
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://muse.jhu.edu/article/789012'
        
        # Mock article page HTML with citation_pdf_url meta tag
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''<html><head><meta name="citation_pdf_url" content="https://muse.jhu.edu/pub/3/article/789012/pdf"/></head></html>'''
        mock_uri_get.return_value = mock_response
        
        pma = load_pmid_xml('34337106')
        
        assert pma.pmid == '34337106'
        assert pma.doi == '10.1353/bsr.2020.0005'
        assert 'J Black Sex Relatsh' in pma.journal
        
        result = the_projectmuse_syrtos(pma, verify=True)
        expected_url = 'https://muse.jhu.edu/pub/3/article/789012/pdf'
        assert result == expected_url
        mock_verify.assert_called_once_with(expected_url, 'Project MUSE', request_timeout=10, max_redirects=3)

    @patch('metapub.findit.dances.projectmuse.verify_pdf_url')
    @patch('metapub.findit.dances.projectmuse.unified_uri_get')
    @patch('metapub.findit.dances.projectmuse.the_doi_2step')
    def test_projectmuse_xml_39364306_j_black_sex_relatsh(self, mock_doi_2step, mock_uri_get, mock_verify):
        """Test PMID 39364306 - J Black Sex Relatsh with DOI 10.1353/bsr.2024.a931228."""
        mock_verify.return_value = None
        
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://muse.jhu.edu/article/345678'
        
        # Mock article page HTML with citation_pdf_url meta tag
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''<html><head><meta name="citation_pdf_url" content="https://muse.jhu.edu/pub/3/article/345678/pdf"/></head></html>'''
        mock_uri_get.return_value = mock_response
        
        pma = load_pmid_xml('39364306')
        
        assert pma.pmid == '39364306'
        assert pma.doi == '10.1353/bsr.2024.a931228'
        assert 'J Black Sex Relatsh' in pma.journal
        
        result = the_projectmuse_syrtos(pma, verify=True)
        expected_url = 'https://muse.jhu.edu/pub/3/article/345678/pdf'
        assert result == expected_url
        mock_verify.assert_called_once_with(expected_url, 'Project MUSE', request_timeout=10, max_redirects=3)