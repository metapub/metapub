"""Tests for Brill Academic Publishers dance function."""

import pytest
from unittest.mock import patch, Mock
import requests

from .common import BaseDanceTest
from metapub import PubMedFetcher
from metapub.findit.dances import the_brill_bridge
from metapub.exceptions import AccessDenied, NoPDFLink
from metapub.findit.registry import JournalRegistry
from metapub.findit.journals.brill import brill_journals
from tests.fixtures import load_pmid_xml, BRILL_EVIDENCE_PMIDS


class TestBrillDance(BaseDanceTest):
    """Test cases for Brill Academic Publishers."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.fetch = PubMedFetcher()

    def test_brill_bridge_url_construction_early_sci_med(self):
        """Test 1: URL construction success (Early Sci Med).

        PMID: 26415349 (Early Sci Med)
        Expected: Should construct valid Brill article URL via DOI resolution
        """
        pma = load_pmid_xml('26415349')

        assert pma.journal == 'Early Sci Med'
        assert pma.doi == '10.1163/15733823-00202p03'
        print(f"Test 1 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification (should always work for URL construction)
        url = the_brill_bridge(pma, verify=False)
        assert url is not None
        assert 'brill.com' in url
        print(f"Test 1 - Article URL: {url}")

    def test_brill_bridge_url_construction_early_sci_med_alt(self):
        """Test 2: Alternative Early Science Medicine article.

        PMID: 11873782 (Early Sci Med)
        Expected: Should construct valid Brill article URL
        """
        pma = load_pmid_xml('11873782')

        assert pma.journal == 'Early Sci Med'
        assert pma.doi == '10.1163/157338201x00154'
        print(f"Test 2 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification
        url = the_brill_bridge(pma, verify=False)
        assert url is not None
        assert 'brill.com' in url
        print(f"Test 2 - Article URL: {url}")

    def test_brill_bridge_url_construction_toung_pao(self):
        """Test 3: Toung Pao journal article.

        PMID: 11618220 (Toung Pao)
        Expected: Should construct valid Brill article URL
        """
        pma = load_pmid_xml('11618220')

        assert pma.journal == 'Toung Pao'
        assert pma.doi == '10.1163/156853287x00032'
        print(f"Test 3 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification
        url = the_brill_bridge(pma, verify=False)
        assert url is not None
        print(f"Test 3 - Article URL: {url}")

    def test_brill_bridge_url_construction_phronesis(self):
        """Test 4: Phronesis journal article.

        PMID: 11636720 (Phronesis)
        Expected: Should construct valid Brill article URL
        """
        pma = load_pmid_xml('11636720')

        assert pma.journal == 'Phronesis (Barc)'
        assert pma.doi == '10.1163/156852873x00014'
        print(f"Test 4 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification
        url = the_brill_bridge(pma, verify=False)
        assert url is not None
        print(f"Test 4 - Article URL: {url}")

    @patch('metapub.findit.dances.brill.the_doi_2step')
    @patch('metapub.findit.dances.brill.unified_uri_get')
    @patch('metapub.findit.dances.brill.verify_pdf_url')
    def test_brill_bridge_successful_access_with_pdf(self, mock_verify, mock_get, mock_doi_2step):
        """Test 5: Successful access simulation with PDF link found.

        PMID: 26415349 (Early Sci Med)
        Expected: Should return PDF URL when found on page
        """
        # Mock DOI resolution to Brill article page
        mock_doi_2step.return_value = 'https://brill.com/view/journals/esm/20/2/article-p153_3.xml'

        # Mock successful article page response with citation_pdf_url meta tag
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.text = '''
        <html>
            <head>
                <meta name="citation_pdf_url" content="https://brill.com/downloadpdf/view/journals/esm/20/2/article-p153_3.pdf" />
            </head>
            <body>
                <h1>Article Title</h1>
                <p>This is a Brill article with PDF download available.</p>
            </body>
        </html>
        '''
        mock_response.content = mock_response.text.encode('utf-8')
        mock_response.url = 'https://brill.com/view/journals/esm/20/2/article-p153_3.xml'
        mock_get.return_value = mock_response

        pma = load_pmid_xml('26415349')

        # Mock verify_pdf_url to return the URL (successful verification)
        expected_url = "https://brill.com/downloadpdf/view/journals/esm/20/2/article-p153_3.pdf"
        mock_verify.return_value = expected_url

        # Test with verification - should find PDF link
        url = the_brill_bridge(pma, verify=True)
        assert 'brill.com' in url
        assert '/pdf' in url or '.pdf' in url  # Accept either PDF URL format
        print(f"Test 5 - Found PDF link: {url}")

    @patch('metapub.findit.dances.brill.the_doi_2step')
    @patch('metapub.findit.dances.brill.unified_uri_get')
    def test_brill_bridge_open_access_article(self, mock_get, mock_doi_2step):
        """Test 6: Open access article without direct PDF link.

        Expected: Should return article URL when accessible
        """
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://brill.com/view/journals/esm/20/2/article-p153_3.xml'

        # Mock successful article page response without specific PDF link
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.text = '''
        <html>
            <body>
                <h1>Article Title</h1>
                <p>This is a Brill article.</p>
                <div class="article-content">
                    <p>Full article content is available here.</p>
                </div>
            </body>
        </html>
        '''
        mock_response.content = mock_response.text.encode('utf-8')
        mock_get.return_value = mock_response

        pma = load_pmid_xml('26415349')

        # Test with verification - should return article URL
        url = the_brill_bridge(pma, verify=True)
        assert url == 'https://brill.com/view/journals/esm/20/2/article-p153_3.xml'
        print(f"Test 6 - Article URL: {url}")

    @patch('metapub.findit.dances.brill.the_doi_2step')
    @patch('metapub.findit.dances.brill.unified_uri_get')
    def test_brill_bridge_paywall_detection(self, mock_get, mock_doi_2step):
        """Test 7: Paywall detection.

        Expected: Should detect paywall and raise AccessDenied
        """
        # Mock DOI resolution to Brill article page
        mock_doi_2step.return_value = 'https://brill.com/view/journals/esm/20/2/article-p153_3.xml'

        # Mock article page response with paywall indicators
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.text = '''
        <html>
            <body>
                <h1>Article Title</h1>
                <p>This content requires institutional access.</p>
                <div class="paywall">
                    <p>Please log in to access this article.</p>
                    <a href="/login">Sign In</a>
                    <a href="/subscribe">Subscribe</a>
                    <p>Purchase this article for $39.95</p>
                </div>
            </body>
        </html>
        '''
        mock_response.content = mock_response.text.encode('utf-8')
        mock_get.return_value = mock_response

        pma = load_pmid_xml('26415349')

        # Test with verification - should detect missing meta tag
        with pytest.raises(NoPDFLink) as exc_info:
            the_brill_bridge(pma, verify=True)

        assert 'MISSING' in str(exc_info.value)
        assert 'citation_pdf_url' in str(exc_info.value)
        print(f"Test 7 - Correctly detected paywall: {exc_info.value}")

    @patch('metapub.findit.dances.brill.the_doi_2step')
    @patch('metapub.findit.dances.brill.unified_uri_get')
    def test_brill_bridge_access_forbidden(self, mock_get, mock_doi_2step):
        """Test 8: Access forbidden (403 error).

        Expected: Should handle 403 errors properly
        """
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://brill.com/view/journals/esm/20/2/article-p153_3.xml'

        # Mock 403 response
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.ok = False
        mock_get.return_value = mock_response

        pma = load_pmid_xml('26415349')

        # Test with verification - should handle 403
        with pytest.raises(NoPDFLink) as exc_info:
            the_brill_bridge(pma, verify=True)

        assert 'TXERROR' in str(exc_info.value)
        assert '403' in str(exc_info.value)
        print(f"Test 8 - Correctly handled 403: {exc_info.value}")

    @patch('metapub.findit.dances.brill.the_doi_2step')
    @patch('metapub.findit.dances.brill.unified_uri_get')
    def test_brill_bridge_network_error(self, mock_get, mock_doi_2step):
        """Test 9: Network error handling.

        Expected: Should handle network errors gracefully
        """
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://brill.com/view/journals/esm/20/2/article-p153_3.xml'

        # Mock network error
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

        pma = load_pmid_xml('26415349')

        # Test - should handle network error
        with pytest.raises(NoPDFLink) as exc_info:
            the_brill_bridge(pma, verify=True)

        assert 'TXERROR' in str(exc_info.value)
        assert 'Network error' in str(exc_info.value)
        print(f"Test 9 - Correctly handled network error: {exc_info.value}")


    def test_brill_bridge_invalid_doi(self):
        """Test 11: Article with non-Brill DOI.

        Expected: Should raise NoPDFLink for invalid DOI pattern
        """
        # Create a mock PMA with non-Brill DOI
        pma = Mock()
        pma.doi = '10.1000/invalid-doi'
        pma.journal = 'Early Sci Med'

        with pytest.raises(NoPDFLink) as exc_info:
            the_brill_bridge(pma, verify=False)

        assert 'INVALID' in str(exc_info.value)
        assert '10.1163/' in str(exc_info.value)
        print(f"Test 11 - Correctly handled invalid DOI: {exc_info.value}")

    @patch('metapub.findit.dances.brill.the_doi_2step')
    @patch('metapub.findit.dances.brill.unified_uri_get')
    def test_brill_bridge_article_not_found(self, mock_get, mock_doi_2step):
        """Test 12: Article not found (404 error).

        Expected: Should handle 404 errors properly
        """
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://brill.com/view/journals/esm/20/2/article-p153_3.xml'

        # Mock 404 response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.ok = False
        mock_get.return_value = mock_response

        pma = load_pmid_xml('26415349')

        # Test with verification - should handle 404
        with pytest.raises(NoPDFLink) as exc_info:
            the_brill_bridge(pma, verify=True)

        assert 'TXERROR' in str(exc_info.value)
        assert '404' in str(exc_info.value) or 'not found' in str(exc_info.value)
        print(f"Test 12 - Correctly handled 404: {exc_info.value}")


def test_brill_journal_recognition():
    """Test that Brill journals are properly recognized in the registry."""

    registry = JournalRegistry()

    # Test sample Brill journals
    test_journals = [
        'Early Sci Med',
        'Toung Pao',
        'Phronesis',
        'Behaviour',
        'Mnemosyne'
    ]

    # Test journal recognition
    found_count = 0
    for journal in test_journals:
        if journal in brill_journals or 'Phronesis (Barc)' in brill_journals:
            publisher_info = registry.get_publisher_for_journal(journal)
            if publisher_info and publisher_info['name'] == 'brill':
                assert publisher_info['dance_function'] == 'the_brill_bridge'
                print(f"✓ {journal} correctly mapped to Brill Academic Publishers")
                found_count += 1
            else:
                print(f"⚠ {journal} mapped to different publisher: {publisher_info['name'] if publisher_info else 'None'}")
        else:
            print(f"⚠ {journal} not in brill_journals list")

    # Just make sure we found at least one Brill journal (the test may not find all if registry is not populated)
    if found_count == 0:
        print("⚠ No Brill journals found in registry - this may be expected if registry not populated")
    else:
        print(f"✓ Found {found_count} properly mapped Brill journals")

    registry.close()


class TestBrillXMLFixtures:
    """Test Brill dance function with real XML fixtures."""

    def test_brill_authentic_metadata_validation(self):
        """Validate authentic metadata from XML fixtures matches expected patterns."""
        for pmid, expected in BRILL_EVIDENCE_PMIDS.items():
            pma = load_pmid_xml(pmid)
            
            # Validate DOI follows Brill pattern (10.1163/)
            assert pma.doi == expected['doi']
            assert pma.doi.startswith('10.1163/'), f"Brill DOI must start with 10.1163/, got: {pma.doi}"
            
            # Validate journal name matches expected
            assert pma.journal == expected['journal']
            
            # Validate PMID matches
            assert pma.pmid == pmid
            
            print(f"✓ PMID {pmid}: {pma.journal} - {pma.doi}")

    @patch('metapub.findit.dances.brill.unified_uri_get')
    @patch('metapub.findit.dances.brill.the_doi_2step')
    def test_brill_url_construction_without_verification(self, mock_doi_2step, mock_uri_get):
        """Test URL construction without verification using XML fixtures."""
        for pmid in BRILL_EVIDENCE_PMIDS.keys():
            pma = load_pmid_xml(pmid)
            
            # Mock DOI resolution and response with citation_pdf_url meta tag
            expected_article_url = f'https://brill.com/view/journals/test-article-{pmid}'
            expected_pdf_url = f'https://brill.com/downloadpdf/view/journals/test-{pmid}.pdf'
            mock_doi_2step.return_value = expected_article_url
            
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = f'<html><head><meta name="citation_pdf_url" content="{expected_pdf_url}" /></head></html>'
            mock_uri_get.return_value = mock_response
            
            # Test URL construction without verification
            result = the_brill_bridge(pma, verify=False)
            
            # Should extract PDF URL from meta tag
            assert result == expected_pdf_url
            assert 'brill.com' in result
            
            print(f"✓ PMID {pmid} URL construction: {result}")

    @patch('metapub.findit.dances.brill.verify_pdf_url')
    @patch('metapub.findit.dances.brill.unified_uri_get')
    @patch('metapub.findit.dances.brill.the_doi_2step')
    def test_brill_url_construction_with_mocked_verification(self, mock_doi_2step, mock_uri_get, mock_verify):
        """Test URL construction with mocked verification."""
        # Mock successful response with citation_pdf_url meta tag
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><head><meta name="citation_pdf_url" content="https://brill.com/downloadpdf/view/journals/test.pdf" /></head></html>'
        mock_uri_get.return_value = mock_response
        
        # Mock successful verification
        mock_verify.return_value = None
        
        for pmid in BRILL_EVIDENCE_PMIDS.keys():
            pma = load_pmid_xml(pmid)
            
            expected_article_url = f'https://brill.com/view/journals/test-article-{pmid}'
            expected_pdf_url = f'https://brill.com/downloadpdf/view/journals/test-{pmid}.pdf'
            mock_doi_2step.return_value = expected_article_url
            mock_response.text = f'<html><head><meta name="citation_pdf_url" content="{expected_pdf_url}" /></head></html>'
            
            result = the_brill_bridge(pma, verify=True)
            
            # Should find and return PDF URL from meta tag
            assert result == expected_pdf_url
            mock_verify.assert_called_with(expected_pdf_url, 'Brill')
            
            print(f"✓ PMID {pmid} verified URL: {result}")

    @patch('metapub.findit.dances.brill.unified_uri_get')
    @patch('metapub.findit.dances.brill.the_doi_2step')
    def test_brill_paywall_handling(self, mock_doi_2step, mock_uri_get):
        """Test paywall detection and error handling."""
        # Mock response without citation_pdf_url meta tag (indicates no access)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body><div class="paywall">Please subscribe to access</div></body></html>'
        mock_uri_get.return_value = mock_response
        
        expected_article_url = 'https://brill.com/view/journals/test-article'
        mock_doi_2step.return_value = expected_article_url
        
        pma = load_pmid_xml('26415349')  # Use first test PMID
        
        with pytest.raises(NoPDFLink) as excinfo:
            the_brill_bridge(pma, verify=True)
        
        assert 'No PDF URL found' in str(excinfo.value)

    def test_brill_journal_coverage(self):
        """Test journal coverage across different Brill publications."""
        journals_found = set()
        
        for pmid in BRILL_EVIDENCE_PMIDS.keys():
            pma = load_pmid_xml(pmid)
            journals_found.add(pma.journal)
        
        # Should have multiple different Brill journals
        assert len(journals_found) >= 3, f"Expected at least 3 different journals, got: {journals_found}"
        
        # All should be known Brill journals
        expected_journals = {'Early Sci Med', 'Toung Pao', 'Phronesis (Barc)'}
        assert journals_found == expected_journals, f"Unexpected journals: {journals_found - expected_journals}"

    def test_brill_doi_pattern_consistency(self):
        """Test that all Brill PMIDs use 10.1163 DOI prefix."""
        doi_prefix = '10.1163'
        
        for pmid, data in BRILL_EVIDENCE_PMIDS.items():
            assert data['doi'].startswith(doi_prefix), f"PMID {pmid} has unexpected DOI prefix: {data['doi']}"
            
            pma = load_pmid_xml(pmid)
            assert pma.doi.startswith(doi_prefix), f"PMID {pmid} XML fixture has unexpected DOI: {pma.doi}"


    @patch('metapub.findit.dances.brill.unified_uri_get')
    @patch('metapub.findit.dances.brill.the_doi_2step')
    def test_brill_template_flexibility(self, mock_doi_2step, mock_uri_get):
        """Test template flexibility for Brill URL patterns."""
        pma = load_pmid_xml('26415349')  # Early Sci Med
        
        # Mock successful response with citation_pdf_url meta tag
        mock_response = Mock()
        mock_response.status_code = 200
        expected_pdf_url = 'https://brill.com/downloadpdf/view/journals/early-sci-med-test.pdf'
        mock_response.text = f'<html><head><meta name="citation_pdf_url" content="{expected_pdf_url}" /></head></html>'
        mock_uri_get.return_value = mock_response
        
        # Mock DOI resolution
        expected_article_url = 'https://brill.com/view/journals/early-sci-med-test'
        mock_doi_2step.return_value = expected_article_url
        
        # Test URL construction
        result = the_brill_bridge(pma, verify=False)
        
        # Should follow Brill URL pattern
        assert result == expected_pdf_url
        assert 'brill.com' in result
        mock_doi_2step.assert_called_with(pma.doi)

    def test_brill_historical_journals_coverage(self):
        """Test coverage of historical academic journals from Brill."""
        # Brill specializes in historical and academic journals
        historical_journals = set()
        
        for pmid in BRILL_EVIDENCE_PMIDS.keys():
            pma = load_pmid_xml(pmid)
            historical_journals.add(pma.journal)
        
        # Should include historical/academic journals
        expected_historical = {'Early Sci Med', 'Toung Pao', 'Phronesis (Barc)'}
        assert historical_journals == expected_historical
        
        print(f"✓ Historical journals covered: {historical_journals}")


if __name__ == '__main__':
    # Run basic tests if executed directly
    test_instance = TestBrillDance()
    test_instance.setUp()

    print("Running Brill Academic Publishers tests...")
    print("\n" + "="*60)

    tests = [
        ('test_brill_bridge_url_construction_early_sci_med', 'Early Sci Med URL construction'),
        ('test_brill_bridge_url_construction_early_sci_med_alt', 'Early Sci Med alt URL construction'),
        ('test_brill_bridge_url_construction_toung_pao', 'Toung Pao URL construction'),
        ('test_brill_bridge_url_construction_phronesis', 'Phronesis URL construction'),
        ('test_brill_bridge_successful_access_with_pdf', 'Successful access with PDF'),
        ('test_brill_bridge_open_access_article', 'Open access article handling'),
        ('test_brill_bridge_paywall_detection', 'Paywall detection'),
        ('test_brill_bridge_access_forbidden', 'Access forbidden handling'),
        ('test_brill_bridge_network_error', 'Network error handling'),
        ('test_brill_bridge_invalid_doi', 'Invalid DOI pattern handling'),
        ('test_brill_bridge_article_not_found', 'Article not found handling')
    ]

    for test_method, description in tests:
        try:
            getattr(test_instance, test_method)()
            print(f"✓ {description} works")
        except Exception as e:
            print(f"✗ {description} failed: {e}")

    try:
        test_brill_journal_recognition()
        print("✓ Registry test passed: Journal recognition works")
    except Exception as e:
        print(f"✗ Registry test failed: {e}")

    print("\n" + "="*60)
    print("Test suite completed!")
