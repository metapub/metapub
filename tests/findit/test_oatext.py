"""Tests for OAText dance function - evidence-driven implementation."""

import pytest
from unittest.mock import patch, Mock

from .common import BaseDanceTest
from metapub.findit.dances.oatext import the_oatext_orbit
from metapub.exceptions import NoPDFLink


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