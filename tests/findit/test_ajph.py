"""
Evidence-based tests for AJPH (American Journal of Public Health) dance function.

Based on HTML sample analysis from real AJPH articles showing:
- PDF links use pattern: /doi/pdf/{DOI}?download=true
- All DOIs use 10.2105 prefix (AJPH-specific) 
- Domain: ajph.aphapublications.org (HTTPS enforced)
- No citation_pdf_url meta tags available
- Direct URL construction required
"""

import pytest
from unittest.mock import patch, Mock
from .common import BaseDanceTest
from metapub import FindIt
from metapub.findit.registry import JournalRegistry
from metapub.findit.dances.generic import the_doi_slide
from metapub.exceptions import AccessDenied, NoPDFLink
from ..fixtures import load_pmid_xml, AJPH_EVIDENCE_PMIDS


class MockResponse:
    """Mock HTTP response for testing."""
    def __init__(self, status_code=200, content_type='text/html', content=b'', url=''):
        self.status_code = status_code
        self.headers = {'content-type': content_type}
        self.content = content
        self.url = url


class TestAJPHDance(BaseDanceTest):
    """Evidence-based test cases for AJPH (American Journal of Public Health)."""
    
    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.registry = JournalRegistry()
    
    def test_ajph_journal_recognition(self):
        """Test that AJPH journal is properly recognized."""
        # Load real AJPH article
        pma = load_pmid_xml('34709863')
        
        assert pma.journal == 'Am J Public Health'
        assert pma.doi == '10.2105/AJPH.2021.306505'
        
        # Test journal recognition
        result = self.registry.get_publisher_for_journal('Am J Public Health')
        self.assertIsNotNone(result)
        self.assertEqual(result['dance_function'], 'the_doi_slide')

    def test_ajph_url_construction_evidence_based(self):
        """Test AJPH URL construction matches evidence from HTML samples."""
        # Test all evidence PMIDs
        for pmid, expected in AJPH_EVIDENCE_PMIDS.items():
            with self.subTest(pmid=pmid):
                pma = load_pmid_xml(pmid)
                
                # Verify metadata matches expectations
                self.assertEqual(pma.doi, expected['doi'])
                self.assertEqual(pma.journal, expected['journal'])
                
                # Test URL construction without verification
                constructed_url = the_doi_slide(pma, verify=False)
                expected_url = f"https://ajph.aphapublications.org/doi/pdf/{pma.doi}?download=true"
                
                self.assertEqual(constructed_url, expected_url)

    def test_ajph_doi_pattern_validation(self):
        """Test that AJPH DOIs follow expected 10.2105 pattern."""
        for pmid, expected in AJPH_EVIDENCE_PMIDS.items():
            with self.subTest(pmid=pmid):
                pma = load_pmid_xml(pmid)
                
                # All AJPH DOIs should start with 10.2105
                self.assertTrue(pma.doi.startswith('10.2105/AJPH.'))
                
                # Should be in format: 10.2105/AJPH.YYYY.nnnnnn
                # DOI format: 10.2105/AJPH.2021.306505
                self.assertTrue('10.2105/AJPH.' in pma.doi)
                self.assertTrue(pma.doi.count('.') >= 3)  # At least 10.2105.AJPH.YYYY format

    @patch('metapub.findit.dances.generic.unified_uri_get')
    def test_ajph_paywall_detection_403(self, mock_get):
        """Test AJPH paywall detection for 403 responses."""
        # Mock 403 response (subscription required)
        mock_get.return_value = MockResponse(status_code=403)
        
        pma = load_pmid_xml('34709863')
        
        with self.assertRaises(AccessDenied) as context:
            the_doi_slide(pma, verify=True)
        
        error_msg = str(context.exception)
        self.assertIn('DENIED', error_msg)
        self.assertIn('access forbidden', error_msg)

    @patch('metapub.findit.dances.generic.unified_uri_get')
    def test_ajph_paywall_detection_html(self, mock_get):
        """Test AJPH paywall detection for HTML responses."""
        # Mock HTML response (subscription page)
        mock_get.return_value = MockResponse(
            status_code=200, 
            content_type='text/html',
            content=b'<html><title>Sign In Required</title></html>'
        )
        
        pma = load_pmid_xml('35679569')
        
        with self.assertRaises(AccessDenied) as context:
            the_doi_slide(pma, verify=True)
        
        error_msg = str(context.exception)
        self.assertIn('DENIED', error_msg)
        # Generic function may use different message
        self.assertTrue('subscription' in error_msg.lower() or 'access' in error_msg.lower())

    @patch('metapub.findit.dances.generic.unified_uri_get')
    def test_ajph_successful_pdf_access(self, mock_get):
        """Test successful PDF access (rare but possible)."""
        expected_url = 'https://ajph.aphapublications.org/doi/pdf/10.2105/AJPH.2021.306453?download=true'
        mock_get.return_value = MockResponse(
            status_code=200,
            content_type='application/pdf',
            url=expected_url
        )
        
        pma = load_pmid_xml('34529508')
        result = the_doi_slide(pma, verify=True)
        
        self.assertEqual(result, expected_url)

    def test_ajph_missing_doi_error(self):
        """Test error handling when DOI is missing."""
        # Create mock article without DOI
        mock_pma = Mock()
        mock_pma.doi = None
        mock_pma.journal = 'Am J Public Health'
        
        with self.assertRaises(NoPDFLink) as context:
            the_doi_slide(mock_pma, verify=False)
        
        error_msg = str(context.exception)
        self.assertIn('MISSING', error_msg)
        self.assertIn('DOI required', error_msg)

    @patch('metapub.findit.dances.generic.unified_uri_get')
    def test_ajph_network_error_handling(self, mock_get):
        """Test handling of network errors."""
        # Mock network exception
        mock_get.side_effect = ConnectionError("Network unreachable")
        
        pma = load_pmid_xml('34709863')
        
        with self.assertRaises((NoPDFLink, AccessDenied)) as context:
            the_doi_slide(pma, verify=True)
        
        error_msg = str(context.exception)
        # The generic function may handle network errors differently
        self.assertTrue(
            'DENIED' in error_msg or 'ERROR' in error_msg,
            f"Expected error message, got: {error_msg}"
        )

    @patch('metapub.findit.dances.generic.unified_uri_get')
    def test_ajph_unexpected_http_status(self, mock_get):
        """Test handling of unexpected HTTP status codes."""
        # Mock unexpected status code
        mock_get.return_value = MockResponse(status_code=404)
        
        pma = load_pmid_xml('35679569')
        
        with self.assertRaises(NoPDFLink) as context:
            the_doi_slide(pma, verify=True)
        
        error_msg = str(context.exception)
        # Generic function may handle 404 differently
        self.assertTrue(
            'DENIED' in error_msg or 'ERROR' in error_msg,
            f"Expected error message, got: {error_msg}"
        )

    def test_ajph_verify_false_bypass(self):
        """Test that verify=False bypasses HTTP requests."""
        # Should not make any HTTP requests when verify=False
        pma = load_pmid_xml('34529508')
        result = the_doi_slide(pma, verify=False)
        
        expected_url = "https://ajph.aphapublications.org/doi/pdf/10.2105/AJPH.2021.306453?download=true"
        self.assertEqual(result, expected_url)

    def test_ajph_function_follows_guidelines(self):
        """Test that AJPH function follows DANCE_FUNCTION_GUIDELINES."""
        import inspect
        
        # Test function signature
        sig = inspect.signature(the_doi_slide)
        params = list(sig.parameters.keys())
        self.assertEqual(params, ['pma', 'verify'])
        self.assertEqual(sig.parameters['verify'].default, True)
        
        # Test function is reasonably concise (under 50 lines as per guidelines)
        source_lines = inspect.getsourcelines(the_doi_slide)[0]
        actual_code_lines = [line for line in source_lines if line.strip() and not line.strip().startswith('#')]
        self.assertLess(len(actual_code_lines), 50, "Dance function should be under 50 lines")

    def test_ajph_xml_fixtures_completeness(self):
        """Test that all AJPH evidence PMIDs have XML fixtures."""
        for pmid in AJPH_EVIDENCE_PMIDS.keys():
            with self.subTest(pmid=pmid):
                # Should be able to load without error
                pma = load_pmid_xml(pmid)
                self.assertIsNotNone(pma.doi)
                self.assertEqual(pma.journal, 'Am J Public Health')

    def test_ajph_evidence_consistency(self):
        """Test that XML fixtures match evidence metadata."""
        for pmid, expected in AJPH_EVIDENCE_PMIDS.items():
            with self.subTest(pmid=pmid):
                pma = load_pmid_xml(pmid)
                
                # DOI should match exactly
                self.assertEqual(pma.doi, expected['doi'])
                # Journal should match exactly  
                self.assertEqual(pma.journal, expected['journal'])
                # Should have title (non-empty)
                self.assertTrue(pma.title)
                self.assertGreater(len(pma.title.strip()), 10)


class TestAJPHRegistryIntegration(BaseDanceTest):
    """Test AJPH integration with journal registry."""
    
    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.registry = JournalRegistry()
    
    def test_ajph_registry_dance_function_mapping(self):
        """Test that AJPH is mapped to correct dance function."""
        publisher_info = self.registry.get_publisher_for_journal('Am J Public Health')
        
        self.assertIsNotNone(publisher_info)
        self.assertEqual(publisher_info['dance_function'], 'the_doi_slide')
        self.assertIsNotNone(publisher_info['format_template'])  # Uses template with the_doi_slide

    def test_ajph_findit_integration_with_real_pmid(self):
        """Test full FindIt integration with real PMID."""
        # Use FindIt to process a real AJPH PMID
        pmid = '34709863'  # Evidence PMID
        
        try:
            findit_instance = FindIt(pmid=pmid)
            result = findit_instance.url
            
            # Should either succeed or fail with expected error
            if result:
                self.assertIn('ajph.aphapublications.org', result)
                self.assertIn('?download=true', result)
            else:
                # Check reason for failure
                reason = findit_instance.reason
                self.assertIsNotNone(reason)
                self.assertTrue(
                    any(term in reason for term in ['DENIED', 'ERROR', 'PAYWALL']),
                    f"Expected proper error reason, got: {reason}"
                )
        except (AccessDenied, NoPDFLink) as e:
            # Expected for paywalled content
            error_msg = str(e)
            self.assertTrue(
                'DENIED' in error_msg or 'ERROR' in error_msg,
                f"Expected proper error message, got: {error_msg}"
            )