"""Tests for OAText dance function - evidence-driven implementation."""

import pytest
from unittest.mock import patch, Mock

from .common import BaseDanceTest
from metapub.findit.dances.oatext import the_oatext_orbit
from metapub.exceptions import NoPDFLink
from tests.fixtures import OATEXT_EVIDENCE_PMIDS


class TestOATextDance(BaseDanceTest):
    """Test suite for OAText dance function."""
    
    def _create_mock_pma(self, doi='10.15761/JSIN.1000229'):
        """Create a mock PubMedArticle object."""
        pma = Mock()
        pma.doi = doi
        return pma

    @patch('metapub.findit.dances.oatext.verify_pdf_url')
    @patch('metapub.findit.dances.oatext.unified_uri_get')
    @patch('metapub.findit.dances.oatext.the_doi_2step')
    def test_oatext_dance_successful_pdf_extraction(self, mock_doi_2step, mock_uri_get, mock_verify):
        """Test successful PDF extraction from OAText article page."""
        
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://www.oatext.com/improving-naltrexone-compliance.php'
        
        # Mock article page HTML based on actual OAText evidence
        article_html = '''<!doctype html>
<html>
<body>
    <div class="row">
        <div class="left">
            <h4 class="left mr20 mt5">Articles</h4>
            <a href="pdf/JSIN-6-229.pdf" target="_blank" class="left mr5">
                <img src="img/icon-pdf.png" alt="">
            </a>
        </div>
    </div>
</body>
</html>'''
        
        # Mock unified_uri_get response
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = article_html
        mock_uri_get.return_value = mock_response
        
        # Mock verification (assume it passes)
        mock_verify.return_value = None
        
        pma = self._create_mock_pma(doi='10.15761/JSIN.1000229')
        result = the_oatext_orbit(pma, verify=True)
        
        assert result == 'https://www.oatext.com/pdf/JSIN-6-229.pdf'
        mock_doi_2step.assert_called_once_with('10.15761/JSIN.1000229')
        mock_uri_get.assert_called_once()
        mock_verify.assert_called_once_with('https://www.oatext.com/pdf/JSIN-6-229.pdf', 'OAText')

    def test_oatext_dance_no_doi_raises_error(self):
        """Test that missing DOI raises appropriate error."""
        
        pma = self._create_mock_pma(doi=None)
        
        with pytest.raises(NoPDFLink, match="MISSING: DOI required for OAText PDF access"):
            the_oatext_orbit(pma)

    @patch('metapub.findit.dances.oatext.unified_uri_get')
    @patch('metapub.findit.dances.oatext.the_doi_2step')
    def test_oatext_dance_doi_resolution_failure(self, mock_doi_2step, mock_uri_get):
        """Test handling of DOI resolution failures."""
        
        # Mock DOI resolution success but page fetch failure
        mock_doi_2step.return_value = 'https://www.oatext.com/not-found.php'
        
        # Mock failed page fetch
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_uri_get.return_value = mock_response
        
        pma = self._create_mock_pma(doi='10.15761/JSIN.1000999')
        
        with pytest.raises(NoPDFLink, match="TXERROR.*Could not fetch OAText article page"):
            the_oatext_orbit(pma)

    @patch('metapub.findit.dances.oatext.unified_uri_get')
    @patch('metapub.findit.dances.oatext.the_doi_2step')
    def test_oatext_dance_no_pdf_link_found(self, mock_doi_2step, mock_uri_get):
        """Test handling when PDF link is not found in article page."""
        
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://www.oatext.com/test-article.php'
        
        # Mock article page without PDF link
        article_html = '''<!doctype html>
<html>
<body>
    <div class="content">
        <p>Article content without PDF link</p>
    </div>
</body>
</html>'''
        
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = article_html
        mock_uri_get.return_value = mock_response
        
        pma = self._create_mock_pma(doi='10.15761/JSIN.1000229')
        
        with pytest.raises(NoPDFLink, match="TXERROR: Could not find PDF link in OAText article page"):
            the_oatext_orbit(pma)

    @patch('metapub.findit.dances.oatext.unified_uri_get')
    @patch('metapub.findit.dances.oatext.the_doi_2step')
    def test_oatext_dance_without_verification(self, mock_doi_2step, mock_uri_get):
        """Test dance function without PDF verification."""
        
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://www.oatext.com/test-article-2.php'
        
        # Mock article page HTML with PDF link
        article_html = '''<!doctype html>
<html>
<body>
    <a href="pdf/JSIN-6-228.pdf" target="_blank" class="pdf-link">Download PDF</a>
</body>
</html>'''
        
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = article_html
        mock_uri_get.return_value = mock_response
        
        pma = self._create_mock_pma(doi='10.15761/JSIN.1000228')
        result = the_oatext_orbit(pma, verify=False)
        
        assert result == 'https://www.oatext.com/pdf/JSIN-6-228.pdf'


def test_oatext_journal_recognition():
    """Test that OAText journals are properly recognized."""
    from metapub.findit.journals.oatext import oatext_journals
    
    # Verify key OAText journals are in the list
    expected_journals = [
        'J Syst Integr Neurosci',
        'Clin Case Rep Rev',
        'HMO',
        'Health Educ Care',
        'Integr Cancer Sci Ther'
    ]
    
    for journal in expected_journals:
        assert journal in oatext_journals, f"Journal '{journal}' should be in oatext_journals"
    
    # Verify reasonable total journal count
    assert len(oatext_journals) >= 37, "OAText should have at least 37 journals"


class TestOATextXMLFixtures:
    """Test OAText dance function with XML fixtures (adapted for limited PubMed representation)."""

    def test_oatext_authentic_metadata_validation(self):
        """Validate authentic metadata structure follows expected OAText patterns."""
        # Note: OAText has limited PubMed indexing, so we use representative patterns
        for pmid, expected in OATEXT_EVIDENCE_PMIDS.items():
            # Validate DOI follows OAText pattern (10.15761/)
            assert expected['doi'].startswith('10.15761/'), f"OAText DOI must start with 10.15761/, got: {expected['doi']}"
            
            # Validate journal name is from OAText portfolio
            journal_name = expected['journal']
            expected_journals = ['J Syst Integr Neurosci', 'Clin Case Rep Rev', 'HMO']
            assert journal_name in expected_journals, f"Journal should be from OAText portfolio: {journal_name}"
            
            print(f"✓ PMID {pmid}: {journal_name} - {expected['doi']}")

    @patch('metapub.findit.dances.oatext.verify_pdf_url')
    @patch('metapub.findit.dances.oatext.unified_uri_get')
    @patch('metapub.findit.dances.oatext.the_doi_2step')
    def test_oatext_url_construction_without_verification(self, mock_doi_2step, mock_uri_get, mock_verify):
        """Test URL construction without verification using representative DOI patterns."""
        # Mock DOI resolution to OAText article page
        mock_doi_2step.return_value = 'https://www.oatext.com/test-article.php'
        
        # Mock article page with PDF link
        article_html = '''<!doctype html>
<html>
<body>
    <div class="row">
        <a href="pdf/JSIN-6-229.pdf" target="_blank" class="pdf-link">
            <img src="img/icon-pdf.png" alt="">
        </a>
    </div>
</body>
</html>'''
        
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = article_html
        mock_uri_get.return_value = mock_response
        
        for pmid, expected in OATEXT_EVIDENCE_PMIDS.items():
            # Create mock PMA with representative DOI pattern
            class MockPMA:
                def __init__(self, doi):
                    self.doi = doi
                    self.journal = expected['journal']
            
            pma = MockPMA(expected['doi'])
            
            # Test URL construction without verification
            result = the_oatext_orbit(pma, verify=False)
            
            # Should construct OAText URL pattern
            assert result is not None
            assert 'oatext.com/pdf/' in result
            assert result.startswith('https://')
            
            print(f"✓ PMID {pmid} URL: {result}")

    @patch('metapub.findit.dances.oatext.verify_pdf_url')
    @patch('metapub.findit.dances.oatext.unified_uri_get')
    @patch('metapub.findit.dances.oatext.the_doi_2step')
    def test_oatext_url_construction_with_mocked_verification(self, mock_doi_2step, mock_uri_get, mock_verify):
        """Test URL construction with mocked verification."""
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://www.oatext.com/test-article.php'
        
        # Mock article page with PDF link
        article_html = '''<!doctype html>
<html>
<body>
    <div class="content">
        <a href="pdf/JSIN-6-229.pdf" target="_blank">Download PDF</a>
    </div>
</body>
</html>'''
        
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = article_html
        mock_uri_get.return_value = mock_response
        
        # Mock successful verification
        mock_verify.return_value = None
        
        for pmid, expected in OATEXT_EVIDENCE_PMIDS.items():
            class MockPMA:
                def __init__(self, doi):
                    self.doi = doi
                    self.journal = expected['journal']
            
            pma = MockPMA(expected['doi'])
            
            result = the_oatext_orbit(pma, verify=True)
            
            assert result is not None
            assert 'oatext.com/pdf/' in result
            mock_verify.assert_called()
            
            print(f"✓ PMID {pmid} verified URL: {result}")

    @patch('metapub.findit.dances.oatext.unified_uri_get')
    @patch('metapub.findit.dances.oatext.the_doi_2step')
    def test_oatext_paywall_handling(self, mock_doi_2step, mock_uri_get):
        """Test paywall detection and error handling."""
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://www.oatext.com/test-article.php'
        
        # Mock paywall response (failed page fetch)
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 403
        mock_uri_get.return_value = mock_response
        
        class MockPMA:
            def __init__(self):
                self.doi = '10.15761/JSIN.1000229'
                self.journal = 'J Syst Integr Neurosci'
        
        pma = MockPMA()
        
        with pytest.raises(NoPDFLink):
            the_oatext_orbit(pma, verify=True)

    def test_oatext_journal_coverage(self):
        """Test journal coverage across different OAText publications."""
        journals_found = set()
        
        for pmid, expected in OATEXT_EVIDENCE_PMIDS.items():
            journals_found.add(expected['journal'])
        
        # Should have multiple different OAText journals
        assert len(journals_found) >= 3, f"Expected at least 3 different journals, got: {journals_found}"
        
        # All should be known OAText journals
        expected_journals = {'J Syst Integr Neurosci', 'Clin Case Rep Rev', 'HMO'}
        assert journals_found == expected_journals, f"Unexpected journals: {journals_found - expected_journals}"

    def test_oatext_doi_pattern_consistency(self):
        """Test that all OAText PMIDs use 10.15761 DOI prefix."""
        doi_prefix = '10.15761'
        
        for pmid, data in OATEXT_EVIDENCE_PMIDS.items():
            assert data['doi'].startswith(doi_prefix), f"PMID {pmid} has unexpected DOI prefix: {data['doi']}"

    def test_oatext_error_handling_missing_doi(self):
        """Test error handling for articles without DOI."""
        class MockPMA:
            def __init__(self):
                self.doi = None
                self.journal = 'J Syst Integr Neurosci'
        
        mock_pma = MockPMA()
        
        with pytest.raises(NoPDFLink) as excinfo:
            the_oatext_orbit(mock_pma)
        
        assert 'MISSING' in str(excinfo.value) or 'DOI required' in str(excinfo.value)

    @patch('metapub.findit.dances.oatext.unified_uri_get')
    @patch('metapub.findit.dances.oatext.the_doi_2step')
    def test_oatext_template_flexibility(self, mock_doi_2step, mock_uri_get):
        """Test template flexibility for OAText URL patterns."""
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://www.oatext.com/test-article.php'
        
        # Mock article page with PDF link
        article_html = '''<!doctype html>
<html>
<body>
    <a href="pdf/JSIN-6-229.pdf" target="_blank">PDF</a>
</body>
</html>'''
        
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = article_html
        mock_uri_get.return_value = mock_response
        
        class MockPMA:
            def __init__(self):
                self.doi = '10.15761/JSIN.1000229'
                self.journal = 'J Syst Integr Neurosci'
        
        pma = MockPMA()
        
        # Test URL construction 
        result = the_oatext_orbit(pma, verify=False)
        
        # Should follow OAText URL pattern
        assert result is not None
        assert 'oatext.com/pdf/' in result
        assert result.startswith('https://')
        assert 'JSIN' in result  # Journal code should be in URL

    def test_oatext_limited_pubmed_representation_acknowledgment(self):
        """Test acknowledgment that OAText has limited PubMed representation."""
        # This test documents the limitation that OAText articles may not be extensively indexed in PubMed
        # The evidence PMIDs use representative DOI patterns from the actual test suite
        
        # Verify we're using representative patterns, not necessarily real PMIDs
        for pmid, expected in OATEXT_EVIDENCE_PMIDS.items():
            # PMIDs starting with 99999 indicate placeholder/representative data
            assert pmid.startswith('99999'), f"PMID {pmid} should be representative/placeholder data"
            
            # But DOI patterns should be authentic OAText patterns
            assert expected['doi'].startswith('10.15761/'), f"DOI pattern should be authentic OAText: {expected['doi']}"
            
            print(f"✓ Representative PMID {pmid}: {expected['journal']} - {expected['doi']}")


class TestOATextRegistryIntegration:
    """Test registry integration for OAText."""
    
    def test_oatext_registry_configuration(self):
        """Test that OAText is properly configured in publisher registry."""
        from metapub.findit.migrate_journals import PUBLISHER_CONFIGS
        
        # Find OAText configuration
        oatext_config = None
        for pub in PUBLISHER_CONFIGS:
            if pub.get('name') == 'oatext':
                oatext_config = pub
                break
        
        assert oatext_config is not None, "OAText should be configured in PUBLISHER_CONFIGS"
        assert oatext_config['dance_function'] == 'the_oatext_orbit'
        assert oatext_config['journals'] is not None
        assert len(oatext_config['journals']) > 0