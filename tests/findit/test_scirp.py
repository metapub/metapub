"""Tests for SCIRP dance function."""

import pytest
from unittest.mock import patch, Mock

from metapub import PubMedFetcher
from metapub.findit.dances import the_scirp_timewarp
from metapub.exceptions import NoPDFLink
from tests.fixtures import load_pmid_xml, SCIRP_EVIDENCE_PMIDS


class TestSCIRPDance:
    """Test cases for SCIRP publisher."""

    def setUp(self):
        """Set up test fixtures."""
        self.fetch = PubMedFetcher()

    def test_scirp_timewarp_successful_pdf_extraction(self):
        """Test successful PDF URL extraction from SCIRP HTML.
        
        Uses the reliable <link rel="alternate"> pattern we discovered.
        """
        # Mock DOI resolution
        with patch('metapub.findit.dances.scirp.the_doi_2step') as mock_doi_2step:
            mock_doi_2step.return_value = 'https://www.scirp.org/journal/paperinformation?paperid=129647'
            
            # Mock successful article page response with PDF link
            with patch('metapub.findit.dances.scirp.unified_uri_get') as mock_get:
                mock_response = Mock()
                mock_response.status_code = 200
                # Use the actual SCIRP HTML pattern we found
                mock_response.text = '''
                <head>
                    <link rel="alternate" type="application/pdf" title="PDF Full-Text" href="//www.scirp.org/pdf/jep_2023120516310166.pdf" />
                </head>
                <body>
                    <h1>Article Title</h1>
                </body>
                '''
                mock_get.return_value = mock_response

                # Create test PMA
                pma = Mock()
                pma.doi = '10.4236/jep.2023.1412052'
                
                # Test without verification
                url = the_scirp_timewarp(pma, verify=False)
                assert url == 'https://www.scirp.org/pdf/jep_2023120516310166.pdf'


    def test_scirp_timewarp_article_page_not_found(self):
        """Test handling when article page returns non-200 status."""
        with patch('metapub.findit.dances.scirp.the_doi_2step') as mock_doi_2step:
            mock_doi_2step.return_value = 'https://www.scirp.org/journal/paperinformation?paperid=999999'
            
            with patch('metapub.findit.dances.scirp.unified_uri_get') as mock_get:
                mock_response = Mock()
                mock_response.status_code = 404
                mock_get.return_value = mock_response

                pma = Mock()
                pma.doi = '10.4236/test.404'
                
                with pytest.raises(NoPDFLink) as exc_info:
                    the_scirp_timewarp(pma, verify=False)
                
                assert 'TXERROR: Could not access SCIRP article page (HTTP 404)' in str(exc_info.value)

    def test_scirp_timewarp_no_pdf_link_in_html(self):
        """Test handling when no PDF link is found in HTML."""
        with patch('metapub.findit.dances.scirp.the_doi_2step') as mock_doi_2step:
            mock_doi_2step.return_value = 'https://www.scirp.org/journal/paperinformation?paperid=129647'
            
            with patch('metapub.findit.dances.scirp.unified_uri_get') as mock_get:
                mock_response = Mock()
                mock_response.status_code = 200
                # HTML without the PDF link pattern
                mock_response.text = '''
                <head>
                    <title>Article Title</title>
                </head>
                <body>
                    <h1>Article Title</h1>
                    <p>No PDF link here</p>
                </body>
                '''
                mock_get.return_value = mock_response

                pma = Mock()
                pma.doi = '10.4236/test.nopdf'
                
                with pytest.raises(NoPDFLink) as exc_info:
                    the_scirp_timewarp(pma, verify=False)
                
                assert 'MISSING: No PDF link found in SCIRP article HTML' in str(exc_info.value)

    @patch('metapub.findit.dances.scirp.verify_pdf_url')
    def test_scirp_timewarp_with_verification(self, mock_verify):
        """Test that PDF verification is called when verify=True."""
        with patch('metapub.findit.dances.scirp.the_doi_2step') as mock_doi_2step:
            mock_doi_2step.return_value = 'https://www.scirp.org/journal/paperinformation?paperid=129647'
            
            with patch('metapub.findit.dances.scirp.unified_uri_get') as mock_get:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.text = '''
                <head>
                    <link rel="alternate" type="application/pdf" title="PDF Full-Text" href="//www.scirp.org/pdf/test.pdf" />
                </head>
                '''
                mock_get.return_value = mock_response

                pma = Mock()
                pma.doi = '10.4236/test.verify'
                
                url = the_scirp_timewarp(pma, verify=True)
                
                # Verify that verify_pdf_url was called with correct parameters
                mock_verify.assert_called_once_with(
                    'https://www.scirp.org/pdf/test.pdf', 
                    'SCIRP', 
                    referrer='https://www.scirp.org/journal/paperinformation?paperid=129647',
                    request_timeout=10,
                    max_redirects=3
                )
                
                assert url == 'https://www.scirp.org/pdf/test.pdf'


def test_scirp_journal_recognition():
    """Test that SCIRP journals are properly recognized in the registry."""
    from metapub.findit.registry import JournalRegistry
    
    registry = JournalRegistry()
    
    # Test a sample SCIRP journal
    publisher_info = registry.get_publisher_for_journal('J Environ Prot (Irvine, Calif)')
    if publisher_info:
        assert publisher_info['name'] == 'scirp'
        assert publisher_info['dance_function'] == 'the_scirp_timewarp'
    
    registry.close()


if __name__ == '__main__':
    # Run basic tests if executed directly
    test_instance = TestSCIRPDance()
    test_instance.setUp()
    
    print("Running SCIRP tests...")
    print("=" * 60)
    
    tests = [
        ('test_scirp_timewarp_successful_pdf_extraction', 'PDF extraction from HTML'),
        ('test_scirp_timewarp_article_page_not_found', 'Article page not found'),
        ('test_scirp_timewarp_no_pdf_link_in_html', 'No PDF link in HTML'),
        ('test_scirp_timewarp_with_verification', 'PDF verification call')
    ]
    
    for test_method, description in tests:
        try:
            getattr(test_instance, test_method)()
            print(f"✓ {description}")
        except Exception as e:
            print(f"✗ {description} failed: {e}")
    
    try:
        test_scirp_journal_recognition()
        print("✓ Journal recognition")
    except Exception as e:
        print(f"✗ Journal recognition failed: {e}")
    
    print("=" * 60)
    print("SCIRP tests completed!")


class TestSCIRPXMLFixtures:
    """Test SciRP dance function with real XML fixtures."""

    def test_scirp_authentic_metadata_validation(self):
        """Validate authentic metadata from XML fixtures matches expected patterns."""
        for pmid, expected in SCIRP_EVIDENCE_PMIDS.items():
            pma = load_pmid_xml(pmid)
            assert pma.doi == expected['doi']
            assert pma.journal == expected['journal']
            assert pma.pmid == pmid
            print(f"✓ PMID {pmid}: {pma.journal} - {pma.doi}")

    def test_scirp_doi_pattern_consistency(self):
        """Test SciRP DOI patterns (10.4236/)."""
        for pmid, data in SCIRP_EVIDENCE_PMIDS.items():
            pma = load_pmid_xml(pmid)
            assert pma.doi.startswith('10.4236/'), f"SciRP DOI must start with 10.4236/, got: {pma.doi}"
            print(f"✓ PMID {pmid} DOI pattern: {pma.doi}")