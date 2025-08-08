"""RSC XML fixtures tests - following TRANSITION_TESTS_TO_REAL_DATA.md guidelines.

This test file validates the RSC dance function using real PubMed XML data
without any network dependencies. All tests use authentic article metadata
from verified PMIDs covering different RSC journals.

Evidence Coverage:
- Natural Products Reports (2 open access articles with PMC)  
- Environmental Science: Processes & Impacts (6 subscription articles)
- All PMIDs verified with 10.1039/ DOI prefix (RSC pattern)
- All show consistent citation_pdf_url meta tags in HTML samples
"""

import pytest
from unittest.mock import patch, Mock

from tests.fixtures import load_pmid_xml, RSC_EVIDENCE_PMIDS
from metapub.findit.dances import the_rsc_reaction
from metapub.exceptions import NoPDFLink, AccessDenied


class TestRSCXMLFixtures:
    """Test Royal Society of Chemistry dance function with real XML fixtures."""

    def test_rsc_authentic_metadata_validation(self):
        """Test 1: Validate authentic metadata from XML fixtures matches expected patterns.
        
        All RSC articles must have 10.1039/ DOI prefix and correct journal names.
        This test ensures our XML fixtures contain real, verified RSC data.
        """
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

    def test_rsc_url_construction_without_verification(self):
        """Test 2: URL construction without verification using XML fixtures.
        
        Tests the rewritten RSC dance function with verify=False.
        Should delegate to the_vip_shake which extracts citation_pdf_url meta tags.
        """
        test_pmids = ['31712796', '34817495', '35699396']  # Subscription articles
        
        for pmid in test_pmids:
            pma = load_pmid_xml(pmid)
            
            # Mock HTTP request to return HTML with citation_pdf_url meta tag
            expected_url = f"https://pubs.rsc.org/en/content/articlepdf/2020/em/{pma.doi.split('/')[-1]}"
            mock_html = f'<meta content="{expected_url}" name="citation_pdf_url" />'
            
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = mock_html
            
            with patch('metapub.findit.dances.rsc.the_doi_2step', return_value='https://pubs.rsc.org/article/') as mock_doi:
                with patch('metapub.findit.dances.rsc.unified_uri_get', return_value=mock_response) as mock_get:
                    url = the_rsc_reaction(pma, verify=False)
                    
                    # Verify correct function calls
                    mock_doi.assert_called_once_with(pma.doi)
                    mock_get.assert_called_once_with('https://pubs.rsc.org/article/')
                
                # Verify returned URL follows RSC pattern
                assert url == expected_url
                assert 'pubs.rsc.org' in url
                assert '/articlepdf/' in url
                
                print(f"✓ PMID {pmid}: {url}")

    def test_rsc_open_access_articles(self):
        """Test 3: Open access RSC articles (Natural Products Reports).
        
        Tests PMIDs with PMC availability, which should still use RSC URLs.
        """
        open_access_pmids = ['32935693', '38170905']  # Both have PMC
        
        for pmid in open_access_pmids:
            pma = load_pmid_xml(pmid)
            expected_metadata = RSC_EVIDENCE_PMIDS[pmid]
            
            # Verify this is an open access article
            assert 'pmc' in expected_metadata, f"Expected PMC for open access article {pmid}"
            assert pma.journal == 'Nat Prod Rep'
            
            # Mock HTTP request to return HTML with citation_pdf_url meta tag
            expected_url = f"https://pubs.rsc.org/en/content/articlepdf/2021/np/{pma.doi.split('/')[-1]}"
            mock_html = f'<meta content="{expected_url}" name="citation_pdf_url" />'
            
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = mock_html
            
            with patch('metapub.findit.dances.rsc.the_doi_2step', return_value='https://pubs.rsc.org/article/') as mock_doi:
                with patch('metapub.findit.dances.rsc.unified_uri_get', return_value=mock_response) as mock_get:
                    url = the_rsc_reaction(pma, verify=False)
                assert url == expected_url
                
                print(f"✓ Open Access PMID {pmid}: {pma.journal} - {url}")

    def test_rsc_subscription_articles(self):
        """Test 4: Subscription RSC articles (Environmental Science journals).
        
        Tests subscription-based articles that may return paywall responses.
        """
        subscription_pmids = ['31712796', '34817495', '35699396', '37787043']
        
        for pmid in subscription_pmids:
            pma = load_pmid_xml(pmid)
            
            # Verify this is a subscription journal
            assert pma.journal == 'Environ Sci Process Impacts'
            assert pma.doi.startswith('10.1039/')
            
            # Test successful case  
            expected_url = f"https://pubs.rsc.org/en/content/articlepdf/2020/em/{pma.doi.split('/')[-1]}"
            mock_html = f'<meta content="{expected_url}" name="citation_pdf_url" />'
            
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = mock_html
            
            with patch('metapub.findit.dances.rsc.the_doi_2step', return_value='https://pubs.rsc.org/article/') as mock_doi:
                with patch('metapub.findit.dances.rsc.unified_uri_get', return_value=mock_response) as mock_get:
                    url = the_rsc_reaction(pma, verify=False)
                assert url == expected_url
                
                print(f"✓ Subscription PMID {pmid}: {url}")

    def test_rsc_paywall_handling(self):
        """Test 5: Paywall detection and handling.
        
        Tests how the dance function handles subscription-required responses.
        """
        pmid = '31712796'  # Subscription article
        pma = load_pmid_xml(pmid)
        
        # Test paywall response from verify_pdf_url  
        expected_url = f"https://pubs.rsc.org/en/content/articlepdf/2020/em/{pma.doi.split('/')[-1]}"
        mock_html = f'<meta content="{expected_url}" name="citation_pdf_url" />'
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = mock_html
        
        with patch('metapub.findit.dances.rsc.the_doi_2step', return_value='https://pubs.rsc.org/article/'):
            with patch('metapub.findit.dances.rsc.unified_uri_get', return_value=mock_response):
                with patch('metapub.findit.dances.rsc.verify_pdf_url', side_effect=AccessDenied('PAYWALL: RSC requires subscription')) as mock_verify:
                    with pytest.raises(AccessDenied) as exc_info:
                        the_rsc_reaction(pma, verify=True)
                    
                    mock_verify.assert_called_once_with(expected_url, 'RSC')
            assert 'PAYWALL' in str(exc_info.value) or 'subscription' in str(exc_info.value)
            
            print(f"✓ Paywall handling test: {exc_info.value}")

    def test_rsc_missing_doi_error(self):
        """Test 6: Error handling for missing DOI.
        
        Uses real XML fixture but simulates missing DOI condition.
        """
        pmid = '35699396'
        pma = load_pmid_xml(pmid)
        
        # Simulate missing DOI
        pma.doi = None
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_rsc_reaction(pma)
        
        assert 'MISSING: DOI required for RSC journals' in str(exc_info.value)
        print(f"✓ Missing DOI error: {exc_info.value}")

    def test_rsc_invalid_doi_pattern(self):
        """Test 7: Error handling for invalid DOI pattern.
        
        RSC DOIs must start with 10.1039/ - test rejection of other patterns.
        """
        pmid = '37655634'
        pma = load_pmid_xml(pmid)
        
        # Change DOI to non-RSC pattern
        original_doi = pma.doi
        pma.doi = '10.1016/j.example.2023.01.001'  # Elsevier-style DOI
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_rsc_reaction(pma)
        
        assert 'INVALID: DOI must start with 10.1039/ for RSC' in str(exc_info.value)
        assert pma.doi in str(exc_info.value)  # Should show the invalid DOI
        
        print(f"✓ Invalid DOI pattern error: {exc_info.value}")
        
        # Restore original DOI for other tests
        pma.doi = original_doi

    def test_rsc_doi_pattern_coverage(self):
        """Test 8: Verify DOI pattern coverage across all evidence PMIDs.
        
        Ensures all test articles follow RSC DOI patterns and represent
        different RSC journals and time periods.
        """
        journals_found = set()
        years_found = set()
        doi_prefixes_found = set()
        
        for pmid in RSC_EVIDENCE_PMIDS:
            pma = load_pmid_xml(pmid)
            
            # Track journal diversity
            journals_found.add(pma.journal)
            
            # Track publication years (extract from DOI or use current data)
            # RSC DOIs like d0np00027b, c9em00386j contain year indicators
            doi_suffix = pma.doi.split('/')[-1]
            if len(doi_suffix) >= 2:
                year_indicator = doi_suffix[:2]
                # Convert RSC year codes: d0=2020, d1=2021, d2=2022, d3=2023, c9=2019
                year_map = {'d0': '2020', 'd1': '2021', 'd2': '2022', 'd3': '2023', 'c9': '2019'}
                if year_indicator in year_map:
                    years_found.add(year_map[year_indicator])
            
            # Track DOI pattern consistency  
            doi_prefixes_found.add(pma.doi.split('/')[0])
        
        # Validate diversity requirements
        assert len(journals_found) >= 2, f"Need multiple journals, found: {journals_found}"
        assert len(years_found) >= 3, f"Need multiple years, found: {years_found}"
        assert doi_prefixes_found == {'10.1039'}, f"All DOIs must be 10.1039, found: {doi_prefixes_found}"
        
        print(f"✓ Coverage - Journals: {journals_found}")
        print(f"✓ Coverage - Years: {years_found}")
        print(f"✓ Coverage - DOI prefixes: {doi_prefixes_found}")

    def test_rsc_function_compliance(self):
        """Test 9: Verify rewritten function follows DANCE_FUNCTION_GUIDELINES.
        
        Validates that the evidence-driven rewrite meets all requirements:
        - Under 50 lines
        - Single method approach
        - Clear error messages with prefixes
        - Uses most reliable extraction method (citation_pdf_url via vip_shake)
        """
        # Test function length (should be under 50 lines)
        import inspect
        source_lines = inspect.getsourcelines(the_rsc_reaction)[0]
        function_lines = len([line for line in source_lines if line.strip() and not line.strip().startswith('#')])
        assert function_lines <= 50, f"Function should be under 50 lines, got {function_lines}"
        
        # Test single method approach - function should extract citation_pdf_url directly
        pmid = '32935693'
        pma = load_pmid_xml(pmid)
        
        mock_html = '<meta content="https://pubs.rsc.org/pdf/test.pdf" name="citation_pdf_url" />'
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = mock_html
        
        with patch('metapub.findit.dances.rsc.the_doi_2step', return_value='https://pubs.rsc.org/article/'):
            with patch('metapub.findit.dances.rsc.unified_uri_get', return_value=mock_response):
                url = the_rsc_reaction(pma, verify=False)
                assert url == 'https://pubs.rsc.org/pdf/test.pdf'
        
        print(f"✓ Function compliance: {function_lines} lines, direct citation_pdf_url extraction")

    def test_rsc_evidence_based_documentation(self):
        """Test 10: Verify function documents evidence-driven approach.
        
        The rewritten function should reference the HTML sample analysis
        and explain why citation_pdf_url extraction was chosen.
        """
        import inspect
        
        # Check docstring mentions evidence
        docstring = inspect.getdoc(the_rsc_reaction)
        assert 'evidence' in docstring.lower() or 'samples' in docstring.lower()
        assert 'citation_pdf_url' in docstring.lower()
        
        # Check module docstring references evidence
        import metapub.findit.dances.rsc as rsc_module
        module_doc = inspect.getdoc(rsc_module)
        assert 'evidence' in module_doc.lower()
        assert 'HTML samples' in module_doc or 'html samples' in module_doc
        
        print("✓ Evidence-based documentation validated")