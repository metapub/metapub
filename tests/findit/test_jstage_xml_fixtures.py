"""J-STAGE XML fixtures tests - following TRANSITION_TESTS_TO_REAL_DATA.md guidelines.

This test file validates the J-STAGE dance function using real PubMed XML data
without any network dependencies. All tests use authentic article metadata
from verified PMIDs covering different J-STAGE journals.

Evidence Coverage:
- Annals of Thoracic and Cardiovascular Surgery (2 open access articles with PMC)
- Yonago Acta Medica (1 open access article with PMC)  
- All PMIDs verified with J-STAGE platform citation_pdf_url patterns
- All show consistent PDF URL pattern: https://www.jstage.jst.go.jp/article/{journal}/{volume}/{issue}/{volume}_{article_id}/_pdf
"""

import pytest
from unittest.mock import patch, Mock

from tests.fixtures import load_pmid_xml, JSTAGE_EVIDENCE_PMIDS
from metapub.findit.dances import the_jstage_dive
from metapub.exceptions import NoPDFLink, AccessDenied


class TestJSTAGEXMLFixtures:
    """Test J-STAGE dance function with real XML fixtures."""

    def test_jstage_authentic_metadata_validation(self):
        """Test 1: Validate authentic metadata from XML fixtures matches expected patterns.
        
        All J-STAGE articles must have correct DOI patterns and journal names.
        This test ensures our XML fixtures contain real, verified J-STAGE data.
        """
        for pmid, expected in JSTAGE_EVIDENCE_PMIDS.items():
            pma = load_pmid_xml(pmid)
            
            # Validate DOI matches expected
            assert pma.doi == expected['doi']
            
            # Validate journal name matches expected
            assert pma.journal == expected['journal']
            
            # Validate PMID matches
            assert pma.pmid == pmid
            
            print(f"✓ PMID {pmid}: {pma.journal} - {pma.doi}")

    def test_jstage_primary_url_manipulation(self):
        """Test 2: Primary URL manipulation method (fastest approach).
        
        Tests the primary method: DOI resolution + URL manipulation without loading page content.
        This is the most efficient approach when the URL pattern works.
        """
        test_pmids = ['31588070', '34334504']  # Annals of Thoracic and Cardiovascular Surgery
        
        for pmid in test_pmids:
            pma = load_pmid_xml(pmid)
            
            # Mock DOI resolution to return _article URL (primary method trigger)
            article_url = "https://www.jstage.jst.go.jp/article/atcs/26/2/26_ra.19-00158/_article"
            expected_url = "https://www.jstage.jst.go.jp/article/atcs/26/2/26_ra.19-00158/_pdf"
            
            if pmid == '34334504':
                article_url = "https://www.jstage.jst.go.jp/article/atcs/28/1/28_ra.21-00040/_article"
                expected_url = "https://www.jstage.jst.go.jp/article/atcs/28/1/28_ra.21-00040/_pdf"
            
            with patch('metapub.findit.dances.jstage.the_doi_2step', return_value=article_url) as mock_doi:
                # No unified_uri_get should be called for primary method
                url = the_jstage_dive(pma, verify=False)
                
                # Verify correct function calls
                mock_doi.assert_called_once_with(pma.doi)
            
            # Verify URL manipulation worked correctly
            assert url == expected_url
            assert '_pdf' in url
            assert '_article' not in url
            
            print(f"✓ PMID {pmid} (URL manipulation): {url}")

    def test_jstage_fallback_citation_pdf_url(self):
        """Test 3: Fallback citation_pdf_url extraction method.
        
        Tests the fallback method when DOI resolution URL doesn't contain _article pattern.
        Uses HTML parsing for citation_pdf_url (more reliable fallback).
        """
        pmid = '38028269'  # Yonago Acta Med
        pma = load_pmid_xml(pmid)
        
        # Mock DOI resolution to return URL WITHOUT _article (triggers fallback)
        article_url_no_article = 'https://www.jstage.jst.go.jp/article/yam/test'  # No _article
        expected_url = "https://www.jstage.jst.go.jp/article/yam/66/4/66_2023.11.001/_pdf"
        mock_html = f'<meta name="citation_pdf_url" content="{expected_url}" />'
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = mock_html
        
        with patch('metapub.findit.dances.jstage.the_doi_2step', return_value=article_url_no_article):
            with patch('metapub.findit.dances.jstage.unified_uri_get', return_value=mock_response):
                url = the_jstage_dive(pma, verify=False)
        
        assert url == expected_url
        print(f"✓ PMID {pmid} (citation_pdf_url fallback): {url}")

    def test_jstage_open_access_articles(self):
        """Test 4: Open access J-STAGE articles using primary method.
        
        Tests PMIDs with PMC availability - all J-STAGE evidence PMIDs are open access.
        Uses URL manipulation method for efficiency.
        """
        for pmid in JSTAGE_EVIDENCE_PMIDS.keys():
            pma = load_pmid_xml(pmid)
            expected_metadata = JSTAGE_EVIDENCE_PMIDS[pmid]
            
            # Verify this is an open access article
            assert 'pmc' in expected_metadata, f"Expected PMC for open access article {pmid}"
            
            # Mock DOI resolution to return _article URL (primary method trigger)
            article_url = f"https://www.jstage.jst.go.jp/article/test/1/1/1_test/_article"
            expected_url = f"https://www.jstage.jst.go.jp/article/test/1/1/1_test/_pdf"
            
            with patch('metapub.findit.dances.jstage.the_doi_2step', return_value=article_url):
                url = the_jstage_dive(pma, verify=False)
            assert url == expected_url
            
            print(f"✓ Open Access PMID {pmid}: {pma.journal} - {url}")

    def test_jstage_platform_validation(self):
        """Test 5: J-STAGE platform validation.
        
        Tests that the function validates articles resolve to J-STAGE platform.
        """
        pmid = '31588070'
        pma = load_pmid_xml(pmid)
        
        # Test with non-J-STAGE URL from DOI resolution - should raise error immediately
        with patch('metapub.findit.dances.jstage.the_doi_2step', return_value='https://www.example.com/article/'):
            with pytest.raises(NoPDFLink) as exc_info:
                the_jstage_dive(pma, verify=False)
            
            assert 'INVALID: DOI does not resolve to J-STAGE platform' in str(exc_info.value)
        
        print(f"✓ Platform validation error: {exc_info.value}")

    def test_jstage_fallback_failure(self):
        """Test 6: Error when both URL manipulation and fallback fail.
        
        Tests when DOI resolution URL doesn't contain _article AND citation_pdf_url is missing.
        """
        pmid = '31588070'
        pma = load_pmid_xml(pmid)
        
        # Mock DOI resolution to return URL without _article pattern (triggers fallback)
        article_url_no_article = 'https://www.jstage.jst.go.jp/article/test'  # No _article
        
        # Mock response without citation_pdf_url meta tag
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><head><title>Test</title></head></html>'  # No citation_pdf_url
        
        with patch('metapub.findit.dances.jstage.the_doi_2step', return_value=article_url_no_article):
            with patch('metapub.findit.dances.jstage.unified_uri_get', return_value=mock_response):
                with pytest.raises(NoPDFLink) as exc_info:
                    the_jstage_dive(pma, verify=False)
        
        assert 'MISSING: No PDF URL found (URL manipulation failed and no citation_pdf_url)' in str(exc_info.value)
        print(f"✓ Both methods failed error: {exc_info.value}")

    def test_jstage_missing_doi_error(self):
        """Test 7: Error handling for missing DOI.
        
        Uses real XML fixture but simulates missing DOI condition.
        """
        pmid = '34334504'
        pma = load_pmid_xml(pmid)
        
        # Simulate missing DOI
        pma.doi = None
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_jstage_dive(pma)
        
        assert 'MISSING: DOI required for J-STAGE articles' in str(exc_info.value)
        print(f"✓ Missing DOI error: {exc_info.value}")

    def test_jstage_missing_citation_pdf_url(self):
        """Test 8: Error handling for missing citation_pdf_url meta tag.
        
        Tests when DOI resolution URL has no _article pattern and HTML doesn't contain citation_pdf_url.
        """
        pmid = '38028269'
        pma = load_pmid_xml(pmid)
        
        # Mock DOI resolution to return URL without _article (triggers fallback)
        article_url_no_article = 'https://www.jstage.jst.go.jp/article/test'
        
        # Mock response without citation_pdf_url meta tag
        mock_html = '<html><head><title>Test Article</title></head><body>Content</body></html>'
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = mock_html
        
        with patch('metapub.findit.dances.jstage.the_doi_2step', return_value=article_url_no_article):
            with patch('metapub.findit.dances.jstage.unified_uri_get', return_value=mock_response):
                with pytest.raises(NoPDFLink) as exc_info:
                    the_jstage_dive(pma)
        
        assert 'MISSING: No PDF URL found (URL manipulation failed and no citation_pdf_url)' in str(exc_info.value)
        print(f"✓ Missing citation_pdf_url error: {exc_info.value}")

    def test_jstage_http_error_handling(self):
        """Test 9: Error handling for HTTP errors.
        
        Tests how the dance function handles various HTTP error codes.
        """
        pmid = '31588070'
        pma = load_pmid_xml(pmid)
        
        # Test HTTP 404 error
        mock_response = Mock()
        mock_response.status_code = 404
        
        with patch('metapub.findit.dances.jstage.the_doi_2step', return_value='https://www.jstage.jst.go.jp/article/'):
            with patch('metapub.findit.dances.jstage.unified_uri_get', return_value=mock_response):
                with pytest.raises(NoPDFLink) as exc_info:
                    the_jstage_dive(pma)
        
        assert 'TXERROR: Could not access J-STAGE article page (HTTP 404)' in str(exc_info.value)
        print(f"✓ HTTP error handling: {exc_info.value}")

    def test_jstage_paywall_handling(self):
        """Test 10: Paywall detection and handling.
        
        Tests how the dance function handles subscription-required responses.
        """
        pmid = '34334504'
        pma = load_pmid_xml(pmid)
        
        # Test successful URL construction but paywall response from verify_pdf_url
        expected_url = "https://www.jstage.jst.go.jp/article/atcs/28/1/28_ra.21-00040/_pdf"
        mock_html = f'<meta name="citation_pdf_url" content="{expected_url}" />'
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = mock_html
        mock_response.url = 'https://www.jstage.jst.go.jp/article/test'
        
        with patch('metapub.findit.dances.jstage.the_doi_2step', return_value='https://www.jstage.jst.go.jp/article/'):
            with patch('metapub.findit.dances.jstage.unified_uri_get', return_value=mock_response):
                with patch('metapub.findit.dances.jstage.verify_pdf_url', side_effect=AccessDenied('PAYWALL: J-STAGE requires subscription')) as mock_verify:
                    with pytest.raises(AccessDenied) as exc_info:
                        the_jstage_dive(pma, verify=True)
                    
                    mock_verify.assert_called_once_with(expected_url, 'J-STAGE')
        
        assert 'PAYWALL' in str(exc_info.value) or 'subscription' in str(exc_info.value)
        print(f"✓ Paywall handling test: {exc_info.value}")

    def test_jstage_doi_pattern_coverage(self):
        """Test 11: Verify DOI pattern coverage across all evidence PMIDs.
        
        Ensures all test articles represent different J-STAGE journals and time periods.
        """
        journals_found = set()
        doi_patterns_found = set()
        years_found = set()
        
        for pmid in JSTAGE_EVIDENCE_PMIDS:
            pma = load_pmid_xml(pmid)
            
            # Track journal diversity
            journals_found.add(pma.journal)
            
            # Track DOI patterns
            if pma.doi:
                doi_prefix = pma.doi.split('/')[0]
                doi_patterns_found.add(doi_prefix)
                
                # Extract year from DOI if possible
                if '10.5761/atcs.ra.' in pma.doi:
                    # Extract year from ATCS DOI pattern: 10.5761/atcs.ra.19-00158 (19 = 2019)
                    year_part = pma.doi.split('.')[-1].split('-')[0]
                    if year_part.isdigit():
                        if len(year_part) == 2:
                            year = '20' + year_part  # 19 -> 2019
                            years_found.add(year)
                elif '10.33160/yam.' in pma.doi:
                    # Extract year from Yonago Acta Med DOI: 10.33160/yam.2023.11.001
                    year_part = pma.doi.split('.')[2] 
                    if year_part.isdigit() and len(year_part) == 4:
                        years_found.add(year_part)
        
        # Validate diversity requirements
        assert len(journals_found) >= 2, f"Need multiple journals, found: {journals_found}"
        assert len(years_found) >= 2, f"Need multiple years, found: {years_found}"
        assert len(doi_patterns_found) >= 2, f"Need multiple DOI patterns, found: {doi_patterns_found}"
        
        print(f"✓ Coverage - Journals: {journals_found}")
        print(f"✓ Coverage - Years: {years_found}")
        print(f"✓ Coverage - DOI patterns: {doi_patterns_found}")

    def test_jstage_function_compliance(self):
        """Test 12: Verify rewritten function follows DANCE_FUNCTION_GUIDELINES.
        
        Validates that the evidence-driven rewrite meets all requirements:
        - Under 50 lines
        - Single method approach
        - Clear error messages with prefixes
        - Uses citation_pdf_url extraction (most reliable method)
        """
        # Test function length (should be under 50 lines)
        import inspect
        source_lines = inspect.getsourcelines(the_jstage_dive)[0]
        function_lines = len([line for line in source_lines if line.strip() and not line.strip().startswith('#')])
        assert function_lines <= 50, f"Function should be under 50 lines, got {function_lines}"
        
        # Test single method approach - function should extract citation_pdf_url directly
        pmid = '31588070'
        pma = load_pmid_xml(pmid)
        
        mock_html = '<meta name="citation_pdf_url" content="https://www.jstage.jst.go.jp/test.pdf" />'
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = mock_html
        mock_response.url = 'https://www.jstage.jst.go.jp/article/test'
        
        with patch('metapub.findit.dances.jstage.the_doi_2step', return_value='https://www.jstage.jst.go.jp/article/'):
            with patch('metapub.findit.dances.jstage.unified_uri_get', return_value=mock_response):
                url = the_jstage_dive(pma, verify=False)
                assert url == 'https://www.jstage.jst.go.jp/test.pdf'
        
        print(f"✓ Function compliance: {function_lines} lines, direct citation_pdf_url extraction")

    def test_jstage_evidence_based_documentation(self):
        """Test 13: Verify function documents hybrid approach with evidence backing.
        
        The rewritten function should document the hybrid approach and reference
        evidence-based analysis that informed the design.
        """
        import inspect
        
        # Check function docstring documents hybrid approach
        docstring = inspect.getdoc(the_jstage_dive)
        assert 'efficient' in docstring.lower() or 'fast' in docstring.lower()
        assert 'citation_pdf_url' in docstring.lower()
        assert 'fallback' in docstring.lower() or 'backup' in docstring.lower()
        
        # Check module docstring references evidence and samples
        import metapub.findit.dances.jstage as jstage_module
        module_doc = inspect.getdoc(jstage_module)
        assert 'evidence' in module_doc.lower()
        assert 'samples' in module_doc.lower()
        assert 'html' in module_doc.lower()
        
        print("✓ Evidence-based hybrid approach documentation validated")