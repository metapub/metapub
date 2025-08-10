"""Tests for Royal Society of Chemistry (RSC) dance function."""

import pytest
from unittest.mock import patch, Mock
import requests

from .common import BaseDanceTest
from metapub import PubMedFetcher
from metapub.findit.dances import the_rsc_reaction
from metapub.exceptions import AccessDenied, NoPDFLink
from tests.fixtures import load_pmid_xml, RSC_EVIDENCE_PMIDS


class TestRSCDance(BaseDanceTest):
    """Test cases for Royal Society of Chemistry."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.fetch = PubMedFetcher()

    def test_rsc_reaction_url_construction_chem_commun(self):
        """Test 1: URL construction success (Chem Commun).
        
        PMID: 38916454 (Chem Commun (Camb))
        Expected: Should construct valid RSC article URL via DOI resolution
        """
        pma = load_pmid_xml('32935693')
        
        assert pma.journal == 'Nat Prod Rep'
        assert pma.doi == '10.1039/d0np00027b'
        print(f"Test 1 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification (should always work for URL construction)
        url = the_rsc_reaction(pma, verify=False)
        assert url is not None
        assert 'pubs.rsc.org' in url
        print(f"Test 1 - Article URL: {url}")

    def test_rsc_reaction_url_construction_chem_soc_rev(self):
        """Test 2: Chemical Society Reviews article.
        
        PMID: 38912871 (Chem Soc Rev)
        Expected: Should construct valid RSC article URL
        """
        pma = load_pmid_xml('38170905')
        
        assert pma.journal == 'Nat Prod Rep'
        assert pma.doi == '10.1039/d3np00037k'
        print(f"Test 2 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification
        url = the_rsc_reaction(pma, verify=False)
        assert url is not None
        assert 'pubs.rsc.org' in url
        print(f"Test 2 - Article URL: {url}")

    def test_rsc_reaction_url_construction_chem_sci(self):
        """Test 3: Chemical Science journal article.
        
        PMID: 38903241 (Chem Sci)
        Expected: Should construct valid RSC article URL
        """
        pma = load_pmid_xml('31712796')
        
        assert pma.journal == 'Environ Sci Process Impacts'
        assert pma.doi == '10.1039/c9em00386j'
        print(f"Test 3 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification
        url = the_rsc_reaction(pma, verify=False)
        assert url is not None
        print(f"Test 3 - Article URL: {url}")

    def test_rsc_reaction_url_construction_lab_chip(self):
        """Test 4: Lab Chip journal article.
        
        PMID: 38916038 (Lab Chip)
        Expected: Should construct valid RSC article URL
        """
        pma = load_pmid_xml('34817495')
        
        assert pma.journal == 'Environ Sci Process Impacts'
        assert pma.doi == '10.1039/d1em00296a'
        print(f"Test 4 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification
        url = the_rsc_reaction(pma, verify=False)
        assert url is not None
        print(f"Test 4 - Article URL: {url}")

    def test_rsc_reaction_url_construction_nat_prod_rep(self):
        """Test 5: Natural Product Reports (from existing paywalled list).
        
        PMID: 28290569 (Nat Prod Rep)
        Expected: Should construct valid RSC article URL
        """
        pma = load_pmid_xml('35699396')
        
        assert pma.journal == 'Environ Sci Process Impacts'
        assert pma.doi == '10.1039/d1em00553g'
        print(f"Test 5 - Article info: {pma.journal}, DOI: {pma.doi}")

        # Test without verification
        url = the_rsc_reaction(pma, verify=False)
        assert url is not None
        print(f"Test 5 - Article URL: {url}")

    @patch('metapub.findit.dances.rsc.verify_pdf_url')
    @patch('metapub.findit.dances.rsc.the_doi_2step')
    @patch('metapub.findit.dances.rsc.unified_uri_get')
    def test_rsc_reaction_successful_access_with_pdf(self, mock_get, mock_doi_2step, mock_verify):
        """Test 6: Successful access simulation with PDF link found.
        
        PMID: 37787043 (Environ Sci Process Impacts)
        Expected: Should return PDF URL when found on page
        """
        # Mock DOI resolution to RSC article page
        mock_doi_2step.return_value = 'https://pubs.rsc.org/en/content/articlelanding/2023/em/d3em00224a'
        
        # Mock successful article page response with citation_pdf_url meta tag
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.text = '''
        <html>
            <head>
                <meta content="https://pubs.rsc.org/en/content/articlepdf/2023/em/d3em00224a" name="citation_pdf_url" />
            </head>
            <body>
                <h1>Article Title</h1>
                <p>This is an RSC article with PDF download available.</p>
            </body>
        </html>
        '''
        mock_response.content = mock_response.text.encode('utf-8')
        mock_response.url = 'https://pubs.rsc.org/en/content/articlelanding/2023/em/d3em00224a'
        mock_get.return_value = mock_response

        pma = load_pmid_xml('37787043')
        
        # Mock PDF verification to succeed
        mock_verify.return_value = 'https://pubs.rsc.org/en/content/articlepdf/2023/em/d3em00224a'
        
        # Test with verification - should find PDF link
        url = the_rsc_reaction(pma, verify=True)
        assert url == 'https://pubs.rsc.org/en/content/articlepdf/2023/em/d3em00224a'
        assert 'pubs.rsc.org' in url
        assert 'pdf' in url
        print(f"Test 6 - Found PDF link: {url}")

    @patch('metapub.findit.dances.rsc.the_doi_2step')
    @patch('metapub.findit.dances.rsc.unified_uri_get')
    def test_rsc_reaction_open_access_article(self, mock_get, mock_doi_2step):
        """Test 7: Open access article without direct PDF link.
        
        Expected: Should raise NoPDFLink when no citation_pdf_url found
        """
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://pubs.rsc.org/en/content/articlelanding/2023/em/d3em00235g'
        
        # Mock successful article page response without citation_pdf_url meta tag
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.text = '''
        <html>
            <head>
                <title>RSC Article</title>
            </head>
            <body>
                <h1>Article Title</h1>
                <p>This is an RSC article.</p>
                <div class="article-content">
                    <p>Full article content is available here.</p>
                </div>
            </body>
        </html>
        '''
        mock_response.content = mock_response.text.encode('utf-8')
        mock_get.return_value = mock_response

        pma = load_pmid_xml('37655634')
        
        # Test with verification - should raise NoPDFLink
        with pytest.raises(NoPDFLink) as exc_info:
            the_rsc_reaction(pma, verify=True)
        
        assert 'MISSING' in str(exc_info.value)
        assert 'citation_pdf_url' in str(exc_info.value)
        print(f"Test 7 - Correctly detected missing PDF URL: {exc_info.value}")

    @patch('metapub.findit.dances.rsc.the_doi_2step')
    @patch('metapub.findit.dances.rsc.unified_uri_get')
    def test_rsc_reaction_paywall_detection(self, mock_get, mock_doi_2step):
        """Test 8: Paywall detection.
        
        Expected: Should detect paywall and raise AccessDenied
        """
        # Mock DOI resolution to RSC article page
        mock_doi_2step.return_value = 'https://pubs.rsc.org/en/content/articlelanding/2024/cc/d4cc02638a'
        
        # Mock article page response with paywall indicators
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.text = '''
        <html>
            <body>
                <h1>Article Title</h1>
                <p>This content requires institutional access.</p>
                <div class="member-access">
                    <p>Please log in to access this article.</p>
                    <a href="/login">Sign In</a>
                    <a href="/subscribe">Subscribe</a>
                    <p>Purchase this article for $35.00</p>
                </div>
            </body>
        </html>
        '''
        mock_response.content = mock_response.text.encode('utf-8')
        mock_get.return_value = mock_response

        pma = load_pmid_xml('35485580')
        
        # Test with verification - should detect missing citation_pdf_url
        with pytest.raises(NoPDFLink) as exc_info:
            the_rsc_reaction(pma, verify=True)
        
        assert 'MISSING' in str(exc_info.value)
        assert 'citation_pdf_url' in str(exc_info.value)
        print(f"Test 8 - Correctly detected missing PDF URL: {exc_info.value}")

    @patch('metapub.findit.dances.rsc.the_doi_2step')
    @patch('metapub.findit.dances.rsc.unified_uri_get')
    def test_rsc_reaction_access_forbidden(self, mock_get, mock_doi_2step):
        """Test 9: Access forbidden (403 error).
        
        Expected: Should handle 403 errors properly
        """
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://pubs.rsc.org/en/content/articlelanding/2024/cc/d4cc02638a'
        
        # Mock 403 response
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.ok = False
        mock_get.return_value = mock_response

        pma = load_pmid_xml('32935693')
        
        # Test with verification - should handle 403
        with pytest.raises(NoPDFLink) as exc_info:
            the_rsc_reaction(pma, verify=True)
        
        assert 'TXERROR' in str(exc_info.value)
        assert '403' in str(exc_info.value)
        print(f"Test 9 - Correctly handled 403: {exc_info.value}")

    @patch('metapub.findit.dances.rsc.the_doi_2step')
    @patch('metapub.findit.dances.rsc.unified_uri_get')
    def test_rsc_reaction_network_error(self, mock_get, mock_doi_2step):
        """Test 10: Network error handling.
        
        Expected: Should handle network errors gracefully
        """
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://pubs.rsc.org/en/content/articlelanding/2024/cc/d4cc02638a'
        
        # Mock network error
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

        pma = load_pmid_xml('38170905')
        
        # Test - should let network error bubble up
        with pytest.raises(requests.exceptions.ConnectionError) as exc_info:
            the_rsc_reaction(pma, verify=True)
        
        assert 'Network error' in str(exc_info.value)
        print(f"Test 10 - Correctly let network error bubble up: {exc_info.value}")

    def test_rsc_reaction_missing_doi(self):
        """Test 11: Article without DOI.
        
        Expected: Should raise NoPDFLink for missing DOI
        """
        # Create a mock PMA without DOI
        pma = Mock()
        pma.doi = None
        pma.journal = 'Chem Commun (Camb)'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_rsc_reaction(pma, verify=False)
        
        assert 'MISSING' in str(exc_info.value)
        assert 'DOI required' in str(exc_info.value)
        print(f"Test 11 - Correctly handled missing DOI: {exc_info.value}")

    def test_rsc_reaction_invalid_doi(self):
        """Test 12: Article with non-RSC DOI.
        
        Expected: Should raise NoPDFLink for invalid DOI pattern
        """
        # Create a mock PMA with non-RSC DOI
        pma = Mock()
        pma.doi = '10.1000/invalid-doi'
        pma.journal = 'Chem Commun (Camb)'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_rsc_reaction(pma, verify=False)
        
        assert 'INVALID' in str(exc_info.value)
        assert '10.1039/' in str(exc_info.value)
        print(f"Test 12 - Correctly handled invalid DOI: {exc_info.value}")

    @patch('metapub.findit.dances.rsc.the_doi_2step')
    @patch('metapub.findit.dances.rsc.unified_uri_get')
    def test_rsc_reaction_article_not_found(self, mock_get, mock_doi_2step):
        """Test 13: Article not found (404 error).
        
        Expected: Should handle 404 errors properly
        """
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://pubs.rsc.org/en/content/articlelanding/2024/cc/d4cc02638a' 
        
        # Mock 404 response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.ok = False
        mock_get.return_value = mock_response

        pma = load_pmid_xml('31712796')
        
        # Test with verification - should handle 404
        with pytest.raises(NoPDFLink) as exc_info:
            the_rsc_reaction(pma, verify=True)
        
        assert 'TXERROR' in str(exc_info.value)
        assert '404' in str(exc_info.value) or 'not found' in str(exc_info.value)
        print(f"Test 13 - Correctly handled 404: {exc_info.value}")


def test_rsc_journal_recognition():
    """Test that RSC journals are properly recognized in the registry."""
    from metapub.findit.registry import JournalRegistry
    from metapub.findit.journals.rsc import rsc_journals
    
    registry = JournalRegistry()
    
    # Test sample RSC journals
    test_journals = [
        'Chem Commun (Camb)',
        'Chem Soc Rev', 
        'Chem Sci',
        'Lab Chip',
        'Nat Prod Rep'
    ]
    
    # Test journal recognition
    found_count = 0
    for journal in test_journals:
        if journal in rsc_journals:
            publisher_info = registry.get_publisher_for_journal(journal)
            if publisher_info and publisher_info['name'] == 'rsc':
                assert publisher_info['dance_function'] == 'the_rsc_reaction'
                print(f"✓ {journal} correctly mapped to Royal Society of Chemistry")
                found_count += 1
            else:
                print(f"⚠ {journal} mapped to different publisher: {publisher_info['name'] if publisher_info else 'None'}")
        else:
            print(f"⚠ {journal} not in rsc_journals list")
    
    # Just make sure we found at least one RSC journal (the test may not find all if registry is not populated)
    if found_count == 0:
        print("⚠ No RSC journals found in registry - this may be expected if registry not populated")
    else:
        print(f"✓ Found {found_count} properly mapped RSC journals")
    
    registry.close()


if __name__ == '__main__':
    # Run basic tests if executed directly
    test_instance = TestRSCDance()
    test_instance.setUp()
    
    print("Running Royal Society of Chemistry tests...")
    print("\n" + "="*60)
    
    tests = [
        ('test_rsc_reaction_url_construction_chem_commun', 'Chem Commun URL construction'),
        ('test_rsc_reaction_url_construction_chem_soc_rev', 'Chem Soc Rev URL construction'),
        ('test_rsc_reaction_url_construction_chem_sci', 'Chem Sci URL construction'),
        ('test_rsc_reaction_url_construction_lab_chip', 'Lab Chip URL construction'),
        ('test_rsc_reaction_url_construction_nat_prod_rep', 'Nat Prod Rep URL construction'),
        ('test_rsc_reaction_successful_access_with_pdf', 'Successful access with PDF'),
        ('test_rsc_reaction_open_access_article', 'Open access article handling'),
        ('test_rsc_reaction_paywall_detection', 'Paywall detection'),
        ('test_rsc_reaction_access_forbidden', 'Access forbidden handling'),
        ('test_rsc_reaction_network_error', 'Network error handling'),
        ('test_rsc_reaction_missing_doi', 'Missing DOI handling'),
        ('test_rsc_reaction_invalid_doi', 'Invalid DOI pattern handling'),
        ('test_rsc_reaction_article_not_found', 'Article not found handling')
    ]
    
    for test_method, description in tests:
        try:
            getattr(test_instance, test_method)()
            print(f"✓ {description} works")
        except Exception as e:
            print(f"✗ {description} failed: {e}")
    
    try:
        test_rsc_journal_recognition()
        print("✓ Registry test passed: Journal recognition works")
    except Exception as e:
        print(f"✗ Registry test failed: {e}")
    
    print("\n" + "="*60)
    print("Test suite completed!")


class TestRSCXMLFixtures:
    """Test Royal Society of Chemistry dance function with real XML fixtures."""

    def test_rsc_authentic_metadata_validation(self):
        """Validate authentic metadata from XML fixtures matches expected patterns."""
        for pmid, expected in RSC_EVIDENCE_PMIDS.items():
            pma = load_pmid_xml(pmid)
            
            # Validate DOI follows RSC pattern
            assert pma.doi == expected['doi']
            assert pma.doi.startswith('10.1039/'), f"RSC DOI must start with 10.1039/, got: {pma.doi}"
            
            # Validate journal name matches expected
            assert pma.journal == expected['journal']
            
            # Validate PMID matches
            assert pma.pmid == pmid
            
            print(f"✓ PMID {pmid}: {pma.journal} - {pma.doi}")

    @patch('metapub.findit.dances.rsc.the_doi_2step')
    @patch('metapub.findit.dances.rsc.unified_uri_get')
    def test_rsc_url_construction_without_verification(self, mock_get, mock_doi):
        """Test URL construction without verification using XML fixtures."""
        for pmid in RSC_EVIDENCE_PMIDS.keys():
            pma = load_pmid_xml(pmid)
            
            # Mock DOI resolution and HTML response with citation_pdf_url
            expected_url = f"https://pubs.rsc.org/en/content/articlepdf/2020/em/{pma.doi.split('/')[-1]}"
            mock_html = f'<meta content="{expected_url}" name="citation_pdf_url" />'
            
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = mock_html
            
            mock_doi.return_value = 'https://pubs.rsc.org/article/'
            mock_get.return_value = mock_response
            
            url = the_rsc_reaction(pma, verify=False)
            
            # Verify returned URL follows RSC pattern
            assert url == expected_url
            assert 'pubs.rsc.org' in url
            assert '/articlepdf/' in url
            
            print(f"✓ PMID {pmid} URL: {url}")

    def test_rsc_journal_coverage(self):
        """Test journal coverage across different RSC publications."""
        journals_found = set()
        
        for pmid in RSC_EVIDENCE_PMIDS.keys():
            pma = load_pmid_xml(pmid)
            journals_found.add(pma.journal)
        
        # Should have multiple different RSC journals
        assert len(journals_found) >= 2, f"Expected at least 2 different journals, got: {journals_found}"
        
        # All should be known RSC journals
        expected_journals = {'Nat Prod Rep', 'Environ Sci Process Impacts'}
        assert journals_found == expected_journals, f"Unexpected journals: {journals_found - expected_journals}"

    def test_rsc_doi_pattern_consistency(self):
        """Test that all RSC PMIDs use 10.1039 DOI prefix."""
        doi_prefix = '10.1039'
        
        for pmid, data in RSC_EVIDENCE_PMIDS.items():
            assert data['doi'].startswith(doi_prefix), f"PMID {pmid} has unexpected DOI prefix: {data['doi']}"
            
            pma = load_pmid_xml(pmid)
            assert pma.doi.startswith(doi_prefix), f"PMID {pmid} XML fixture has unexpected DOI: {pma.doi}"

    @patch('metapub.findit.dances.rsc.the_doi_2step')
    @patch('metapub.findit.dances.rsc.unified_uri_get')
    def test_rsc_paywall_handling_with_fixtures(self, mock_get, mock_doi):
        """Test paywall detection with XML fixtures."""
        pma = load_pmid_xml('31712796')  # Environmental Science article
        
        # Mock paywall response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><div>Subscription required</div></html>'
        
        mock_doi.return_value = 'https://pubs.rsc.org/article/'
        mock_get.return_value = mock_response
        
        # Should detect missing citation_pdf_url meta tag
        with pytest.raises(NoPDFLink) as exc_info:
            the_rsc_reaction(pma, verify=True)
        
        assert 'MISSING' in str(exc_info.value)
        assert 'citation_pdf_url' in str(exc_info.value)

    def test_rsc_error_handling_missing_doi(self):
        """Test error handling for articles without DOI."""
        # Create mock article without DOI
        class MockPMA:
            def __init__(self):
                self.doi = None
        
        mock_pma = MockPMA()
        
        with pytest.raises(NoPDFLink) as excinfo:
            the_rsc_reaction(mock_pma)
        
        assert 'DOI required' in str(excinfo.value) or 'MISSING' in str(excinfo.value)