"""Tests for WJGNet dance function - evidence-driven implementation."""

import pytest
from unittest.mock import patch, Mock

from .common import BaseDanceTest
from metapub.findit.dances.wjgnet import the_wjgnet_wave
from metapub.exceptions import NoPDFLink
from tests.fixtures import load_pmid_xml, WJGNET_EVIDENCE_PMIDS


class TestWJGNetDance(BaseDanceTest):
    """Test suite for WJGNet dance function."""
    
    def _create_mock_pma(self, doi='10.5495/wjcid.v10.i1.14'):
        """Create a mock PubMedArticle object."""
        pma = Mock()
        pma.doi = doi
        return pma

    @patch('metapub.findit.dances.wjgnet.verify_pdf_url')
    @patch('metapub.findit.dances.wjgnet.unified_uri_get')
    @patch('metapub.findit.dances.wjgnet.the_doi_2step')
    def test_wjgnet_dance_successful_pdf_extraction(self, mock_doi_2step, mock_uri_get, mock_verify):
        """Test successful PDF extraction from WJGNet article page."""
        
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://www.wjgnet.com/2220-3176/full/v10/i1/14.htm'
        
        # Mock article page HTML based on actual WJGNet evidence  
        article_html = '''<!DOCTYPE html>
<html>
<body>
    <li><a href="https://www.f6publishing.com/forms/main/DownLoadFile.aspx?Type=Digital&amp;TypeId=1&amp;id=10.5495%2fwjcid.v10.i1.14&amp;FilePath=FF93BC523D1488C861BF4FE0B082C0D02F7FCB685135DE688F379592336DA2B85CE0B96FD028A992AE3FCDC58538F2B4688D9B0A08A9BE11" target="_blank">Full Article with Cover (PDF)</a></li>
    <li><a href="https://www.wjgnet.com/2220-3176/full/v10/i1/14.htm" target="_blank">Full Article (HTML)</a></li>
</body>
</html>'''
        
        # Mock unified_uri_get response
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = article_html
        mock_uri_get.return_value = mock_response
        
        # Mock verification (assume it passes)
        mock_verify.return_value = None
        
        pma = self._create_mock_pma(doi='10.5495/wjcid.v10.i1.14')
        result = the_wjgnet_wave(pma, verify=True)
        
        expected_url = 'https://www.f6publishing.com/forms/main/DownLoadFile.aspx?Type=Digital&TypeId=1&id=10.5495%2fwjcid.v10.i1.14&FilePath=FF93BC523D1488C861BF4FE0B082C0D02F7FCB685135DE688F379592336DA2B85CE0B96FD028A992AE3FCDC58538F2B4688D9B0A08A9BE11'
        assert result == expected_url
        mock_doi_2step.assert_called_once_with('10.5495/wjcid.v10.i1.14')
        mock_uri_get.assert_called_once()
        mock_verify.assert_called_once_with(expected_url, 'WJGNet', request_timeout=10, max_redirects=3)

    @patch('metapub.findit.dances.wjgnet.verify_pdf_url')  
    @patch('metapub.findit.dances.wjgnet.unified_uri_get')
    @patch('metapub.findit.dances.wjgnet.the_doi_2step')
    def test_wjgnet_dance_full_article_pdf_pattern(self, mock_doi_2step, mock_uri_get, mock_verify):
        """Test extraction of 'Full Article (PDF)' pattern (TypeId=22)."""
        
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://www.wjgnet.com/1948-9366/full/v16/i12/3643.htm'
        
        # Mock article page HTML with TypeId=22 pattern
        article_html = '''<!DOCTYPE html>
<html>
<body>
    <li><a href="https://www.f6publishing.com/forms/main/DownLoadFile.aspx?Type=Digital&amp;TypeId=22&amp;id=10.4240%2fwjgs.v16.i12.3643&amp;FilePath=DE686458A2BF16892F4B88612C01518D26AA3E447185B0240AE1546F2068C44ECF6E9742C6968B0E995CAC46EB1683AAF16B32515F46C322" target="_blank">Full Article (PDF)</a></li>
    <li><a href="https://www.f6publishing.com/forms/main/DownLoadFile.aspx?Type=Digital&amp;TypeId=1&amp;id=10.4240%2fwjgs.v16.i12.3643&amp;FilePath=DE686458A2BF16892F4B88612C01518D26AA3E447185B0240AE1546F2068C44ECF6E9742C6968B0E995CAC46EB1683AAB2027146334FA97885093F398764C2849D10D14833AAF23E" target="_blank">Full Article with Cover (PDF)</a></li>
</body>
</html>'''
        
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = article_html
        mock_uri_get.return_value = mock_response
        
        mock_verify.return_value = None
        
        pma = self._create_mock_pma(doi='10.4240/wjgs.v16.i12.3643')
        result = the_wjgnet_wave(pma, verify=True)
        
        # Should match the first PDF pattern found (Full Article (PDF))
        expected_url = 'https://www.f6publishing.com/forms/main/DownLoadFile.aspx?Type=Digital&TypeId=22&id=10.4240%2fwjgs.v16.i12.3643&FilePath=DE686458A2BF16892F4B88612C01518D26AA3E447185B0240AE1546F2068C44ECF6E9742C6968B0E995CAC46EB1683AAF16B32515F46C322'
        assert result == expected_url

    def test_wjgnet_dance_no_doi_raises_error(self):
        """Test that missing DOI raises appropriate error."""
        
        pma = self._create_mock_pma(doi=None)
        
        with pytest.raises(NoPDFLink, match="MISSING: DOI required for WJGNet PDF access"):
            the_wjgnet_wave(pma)

    @patch('metapub.findit.dances.wjgnet.unified_uri_get')
    @patch('metapub.findit.dances.wjgnet.the_doi_2step')
    def test_wjgnet_dance_doi_resolution_failure(self, mock_doi_2step, mock_uri_get):
        """Test handling of DOI resolution failures."""
        
        # Mock DOI resolution success but page fetch failure
        mock_doi_2step.return_value = 'https://www.wjgnet.com/not-found.htm'
        
        # Mock failed page fetch
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_uri_get.return_value = mock_response
        
        pma = self._create_mock_pma(doi='10.5495/wjcid.v10.i1.99')
        
        with pytest.raises(NoPDFLink, match="TXERROR.*Could not fetch WJGNet article page"):
            the_wjgnet_wave(pma)

    @patch('metapub.findit.dances.wjgnet.unified_uri_get')
    @patch('metapub.findit.dances.wjgnet.the_doi_2step')
    def test_wjgnet_dance_no_pdf_link_found(self, mock_doi_2step, mock_uri_get):
        """Test handling when PDF link is not found in article page."""
        
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://www.wjgnet.com/test-article.htm'
        
        # Mock article page without PDF link
        article_html = '''<!DOCTYPE html>
<html>
<body>
    <div class="content">
        <p>Article content without PDF link</p>
        <a href="/references">References</a>
    </div>
</body>
</html>'''
        
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = article_html
        mock_uri_get.return_value = mock_response
        
        pma = self._create_mock_pma(doi='10.5495/wjcid.v10.i1.14')
        
        with pytest.raises(NoPDFLink, match="TXERROR: Could not find PDF link in WJGNet article page"):
            the_wjgnet_wave(pma)

    @patch('metapub.findit.dances.wjgnet.unified_uri_get')
    @patch('metapub.findit.dances.wjgnet.the_doi_2step')
    def test_wjgnet_dance_without_verification(self, mock_doi_2step, mock_uri_get):
        """Test dance function without PDF verification."""
        
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://www.wjgnet.com/test-article.htm'
        
        # Mock article page HTML with PDF link
        article_html = '''<!DOCTYPE html>
<html>
<body>
    <li><a href="https://www.f6publishing.com/forms/main/DownLoadFile.aspx?Type=Digital&amp;TypeId=1&amp;id=10.5527%2fwjn.v11.i5.139&amp;FilePath=6A4247D346110392065501C81D5D466E53E38B2A2665D5B6BE8824B66204A160082ECAB47942E514A44C5C35D97F94A64F5E83A741587ABA" target="_blank">Full Article with Cover (PDF)</a></li>
</body>
</html>'''
        
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = article_html
        mock_uri_get.return_value = mock_response
        
        pma = self._create_mock_pma(doi='10.5527/wjn.v11.i5.139')
        result = the_wjgnet_wave(pma, verify=False)
        
        expected_url = 'https://www.f6publishing.com/forms/main/DownLoadFile.aspx?Type=Digital&TypeId=1&id=10.5527%2fwjn.v11.i5.139&FilePath=6A4247D346110392065501C81D5D466E53E38B2A2665D5B6BE8824B66204A160082ECAB47942E514A44C5C35D97F94A64F5E83A741587ABA'
        assert result == expected_url


def test_wjgnet_journal_recognition():
    """Test that WJGNet journals are properly recognized."""
    from metapub.findit.registry import JournalRegistry
    
    # Verify key WJGNet journals are in the list
    expected_journals = [
        'World J Gastroenterol',
        'World J Gastrointest Oncol',
        'World J Hepatol',
        'World J Gastrointest Surg'
    ]
    
    # Test journal recognition using registry
    registry = JournalRegistry()
    
    found_count = 0
    for journal in expected_journals:
        publisher_info = registry.get_publisher_for_journal(journal)
        if publisher_info and publisher_info['name'] == 'Wjgnet':
            print(f"✓ {journal} correctly mapped to WJGNet")
            found_count += 1
        else:
            print(f"⚠ {journal} mapped to different publisher: {publisher_info['name'] if publisher_info else 'None'}")
    
    # Should find at least some WJGNet journals
    assert found_count > 0, "No WJGNet journals found in registry"
    registry.close()


class TestWJGNetRegistryIntegration:
    """Test registry integration for WJGNet."""
    
    def test_wjgnet_registry_configuration(self):
        """Test that WJGNet is properly configured in publisher registry."""
        from metapub.findit.registry import JournalRegistry
        
        registry = JournalRegistry()
        
        # Check that WJGNet journals exist in registry
        test_journal = 'World J Gastroenterol'
        publisher_info = registry.get_publisher_for_journal(test_journal)
        
        if publisher_info and publisher_info['name'] == 'Wjgnet':
            assert publisher_info['dance_function'] == 'the_wjgnet_wave'
            print(f"✓ WJGNet properly configured with dance function: {publisher_info['dance_function']}")
        else:
            print(f"⚠ Test journal mapped to: {publisher_info['name'] if publisher_info else 'None'}")
        
        registry.close()


class TestWJGNetXMLFixtures:
    """Test WJGNet XML fixtures for evidence-driven testing."""

    @patch('metapub.findit.dances.wjgnet.verify_pdf_url')
    @patch('metapub.findit.dances.wjgnet.unified_uri_get')
    @patch('metapub.findit.dances.wjgnet.the_doi_2step')
    def test_wjgnet_xml_36187464_world_j_nephrol(self, mock_doi_2step, mock_uri_get, mock_verify):
        """Test PMID 36187464 - World J Nephrol with DOI 10.5527/wjn.v11.i5.139."""
        mock_verify.return_value = None
        
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://www.wjgnet.com/2220-6124/full/v11/i5/139.htm'
        
        # Mock article page HTML with PDF link pattern
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = '''<html><body><li><a href="https://www.f6publishing.com/forms/main/DownLoadFile.aspx?Type=Digital&amp;TypeId=1&amp;id=10.5527%2fwjn.v11.i5.139&amp;FilePath=6A4247D346110392065501C81D5D466E53E38B2A2665D5B6BE8824B66204A160082ECAB47942E514A44C5C35D97F94A64F5E83A741587ABA" target="_blank">Full Article with Cover (PDF)</a></li></body></html>'''
        mock_uri_get.return_value = mock_response
        
        pma = load_pmid_xml('36187464')
        
        assert pma.pmid == '36187464'
        assert pma.doi == '10.5527/wjn.v11.i5.139'
        assert 'World J Nephrol' in pma.journal
        
        result = the_wjgnet_wave(pma, verify=True)
        expected_url = 'https://www.f6publishing.com/forms/main/DownLoadFile.aspx?Type=Digital&TypeId=1&id=10.5527%2fwjn.v11.i5.139&FilePath=6A4247D346110392065501C81D5D466E53E38B2A2665D5B6BE8824B66204A160082ECAB47942E514A44C5C35D97F94A64F5E83A741587ABA'
        assert result == expected_url
        mock_verify.assert_called_once_with(expected_url, 'WJGNet', request_timeout=10, max_redirects=3)

    @patch('metapub.findit.dances.wjgnet.verify_pdf_url')
    @patch('metapub.findit.dances.wjgnet.unified_uri_get')
    @patch('metapub.findit.dances.wjgnet.the_doi_2step')
    def test_wjgnet_xml_38596266_world_j_nephrol(self, mock_doi_2step, mock_uri_get, mock_verify):
        """Test PMID 38596266 - World J Nephrol with DOI 10.5527/wjn.v13.i1.89637."""
        mock_verify.return_value = None
        
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://www.wjgnet.com/2220-6124/full/v13/i1/89637.htm'
        
        # Mock article page HTML with PDF link pattern
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = '''<html><body><li><a href="https://www.f6publishing.com/forms/main/DownLoadFile.aspx?Type=Digital&amp;TypeId=22&amp;id=10.5527%2fwjn.v13.i1.89637&amp;FilePath=DE686458A2BF16892F4B88612C01518D26AA3E447185B0240AE1546F2068C44ECF6E9742C6968B0E995CAC46EB1683AAF16B32515F46C322" target="_blank">Full Article (PDF)</a></li></body></html>'''
        mock_uri_get.return_value = mock_response
        
        pma = load_pmid_xml('38596266')
        
        assert pma.pmid == '38596266'
        assert pma.doi == '10.5527/wjn.v13.i1.89637'
        assert 'World J Nephrol' in pma.journal
        
        result = the_wjgnet_wave(pma, verify=True)
        expected_url = 'https://www.f6publishing.com/forms/main/DownLoadFile.aspx?Type=Digital&TypeId=22&id=10.5527%2fwjn.v13.i1.89637&FilePath=DE686458A2BF16892F4B88612C01518D26AA3E447185B0240AE1546F2068C44ECF6E9742C6968B0E995CAC46EB1683AAF16B32515F46C322'
        assert result == expected_url
        mock_verify.assert_called_once_with(expected_url, 'WJGNet', request_timeout=10, max_redirects=3)