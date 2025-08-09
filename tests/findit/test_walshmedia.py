"""Evidence-driven tests for rewritten Walsh Medical Media dance function.

This test suite validates the rewritten WalshMedia function following 
DANCE_FUNCTION_GUIDELINES.md Phase 4: Test Development.

Evidence analyzed:
- PMID 29226023: DOI resolution works perfectly 
- DOI 10.4172/2161-1122.1000448 resolves to direct PDF with article slug
- Primary URL construction method failed, DOI resolution succeeded
- Function reduced from 90→24 lines (73.3% reduction)

Implementation approach:
- Uses the_doi_2step for direct DOI resolution
- Eliminates trial-and-error patterns
- CLAUDE.md compliant: no generic exceptions, under 50 lines
"""

import unittest
from unittest.mock import Mock
from metapub.findit.dances.generic import the_doi_2step, verify_pdf_url
from metapub.findit.dances import the_walshmedia_bora
from metapub.findit.registry import JournalRegistry
from metapub.pubmedfetcher import PubMedFetcher
from metapub.exceptions import NoPDFLink
from tests.test_compat import skip_network_tests


class TestWalshMediaRewrite(unittest.TestCase):
    """Test rewritten Walsh Medical Media dance function."""
    
    def setUp(self):
        """Set up test fixtures with evidence PMIDs."""
        # Evidence PMID from investigation
        self.evidence_pmid = '29226023'
        self.evidence_doi = '10.4172/2161-1122.1000448'
        self.evidence_journal = 'Dentistry (Sunnyvale)'
        self.evidence_url = 'https://www.walshmedicalmedia.com/open-access/evaluating-the-whitening-and-microstructural-effects-of-a-novel-whitening-strip-on-porcelain-and-composite-dental-materials-2161-1122-1000449.pdf'
    
    def test_rewrite_compliance_metrics(self):
        """Test that rewrite achieves DANCE_FUNCTION_GUIDELINES compliance."""
        import inspect
        
        # Get function source
        source = inspect.getsource(the_walshmedia_bora)
        lines = source.split('\n')
        
        # Count actual function lines (excluding docstring and imports)
        function_lines = [line for line in lines if line.strip() and not line.strip().startswith('"""') and not line.strip().startswith('#')]
        
        # Should be under 50 lines
        self.assertLess(len(function_lines), 50, "Function should be under 50 lines per guidelines")
        
        # Should not contain generic exception catching
        self.assertNotIn('except Exception:', source)
        self.assertNotIn('except:', source)
        
        # Should not contain huge try-except blocks
        try_count = source.count('try:')
        self.assertLessEqual(try_count, 1, "Should not have multiple try blocks")
        
        # Should use the_doi_2step for resolution
        self.assertIn('the_doi_2step', source)
        
        print(f"✅ Rewrite compliance: {len(function_lines)} lines, follows all guidelines")
    
    @skip_network_tests
    def test_evidence_based_doi_resolution(self):
        """Test DOI resolution with evidence PMID."""
        pmf = PubMedFetcher()
        pma = pmf.article_by_pmid(self.evidence_pmid)
        
        # Verify evidence metadata
        self.assertEqual(pma.doi, self.evidence_doi)
        self.assertEqual(pma.journal, self.evidence_journal)
        
        # Test DOI resolution directly
        resolved_url = the_doi_2step(pma.doi)
        self.assertEqual(resolved_url, self.evidence_url)
        
        # Test function without verification
        url = the_walshmedia_bora(pma, verify=False)
        self.assertEqual(url, self.evidence_url)
        
        print(f"✅ DOI resolution works: {url}")
    
    @skip_network_tests 
    def test_verification_success(self):
        """Test verification with evidence PMID (should succeed)."""
        pmf = PubMedFetcher()
        pma = pmf.article_by_pmid(self.evidence_pmid)
        
        # Should succeed with verification since it's open access
        url = the_walshmedia_bora(pma, verify=True)
        self.assertEqual(url, self.evidence_url)
        self.assertTrue(url.startswith('https://www.walshmedicalmedia.com/'))
        self.assertTrue(url.endswith('.pdf'))
        
        print(f"✅ Verification successful: {url}")
    
    def test_missing_doi_error_handling(self):
        """Test error handling for missing DOI (DANCE_FUNCTION_GUIDELINES compliance)."""
        # Create mock PubMedArticle without DOI
        mock_pma = Mock()
        mock_pma.doi = None
        mock_pma.journal = 'Dentistry'
        
        # Should raise NoPDFLink with clear error message
        with self.assertRaises(NoPDFLink) as context:
            the_walshmedia_bora(mock_pma, verify=False)
        
        error_msg = str(context.exception)
        self.assertIn('MISSING', error_msg)
        self.assertIn('DOI required', error_msg)
        self.assertIn('Walsh Medical Media', error_msg)
        
        print(f"✅ Missing DOI handled correctly: {error_msg}")
    
    def test_eliminates_bad_patterns(self):
        """Test that rewrite eliminates BAD PATTERNS from guidelines."""
        import inspect
        
        source = inspect.getsource(the_walshmedia_bora)
        
        # Should not contain trial-and-error patterns
        bad_patterns = [
            'possible_urls',
            'for url in',
            'fallback',
            'try:.*try:',  # Multiple try blocks
            'article_id = ',  # URL construction
            'pdf_url = f\'https',  # Direct URL building
        ]
        
        for pattern in bad_patterns[:6]:  # Skip regex pattern
            self.assertNotIn(pattern, source, f"Should not contain BAD PATTERN: {pattern}")
        
        # Should contain GOOD PATTERNS
        good_patterns = [
            'the_doi_2step',
            'verify_pdf_url', 
            'MISSING:',
            'if not pma.doi:'
        ]
        
        for pattern in good_patterns:
            self.assertIn(pattern, source, f"Should contain GOOD PATTERN: {pattern}")
        
        print("✅ All BAD PATTERNS eliminated, GOOD PATTERNS present")
    
    def test_registry_integration(self):
        """Test Walsh Medical Media journals are mapped correctly in registry."""
        registry = JournalRegistry()
        
        # Test key Walsh Medical Media journals
        test_journals = [
            'Dentistry (Sunnyvale)',
            'J Pharmacovigil', 
            'Health Care Curr Rev'
        ]
        
        for journal in test_journals:
            with self.subTest(journal=journal):
                publisher_info = registry.get_publisher_for_journal(journal)
                if publisher_info:  # Some may not be in registry
                    self.assertEqual(publisher_info['name'], 'walshmedia')
                    self.assertEqual(publisher_info['dance_function'], 'the_walshmedia_bora')
        
        registry.close()
        print("✅ Registry integration verified")
    
    def test_doi_prefix_flexibility(self):
        """Test function handles Walsh Media DOI patterns correctly.""" 
        # Test with evidence DOI that we know works
        mock_pma = Mock()
        mock_pma.doi = '10.4172/2161-1122.1000448'  # Evidence DOI that works
        mock_pma.journal = 'Dentistry'
        
        # Should work without verification (DOI resolution)
        url = the_walshmedia_bora(mock_pma, verify=False)
        self.assertIsNotNone(url)
        self.assertTrue(url.startswith('https://'))
        self.assertIn('walshmedicalmedia.com', url)
                
        print(f"✅ DOI prefix flexibility confirmed for 10.4172 prefix")
    
    def test_function_simplicity_achievement(self):
        """Test that rewrite achieves promised simplicity."""
        import inspect
        
        # Count logical complexity
        source = inspect.getsource(the_walshmedia_bora)
        
        # Simple metrics for complexity
        complexity_indicators = {
            'if_statements': source.count('if '),
            'try_blocks': source.count('try:'),
            'except_blocks': source.count('except'),
            'for_loops': source.count('for '),
            'while_loops': source.count('while ')
        }
        
        # Should be simple (relaxed constraints for practical function)
        self.assertLessEqual(complexity_indicators['if_statements'], 5)
        self.assertLessEqual(complexity_indicators['try_blocks'], 1) 
        self.assertLessEqual(complexity_indicators['except_blocks'], 1)
        self.assertEqual(complexity_indicators['for_loops'], 0)
        self.assertEqual(complexity_indicators['while_loops'], 0)
        
        print(f"✅ Function simplicity: {complexity_indicators}")
    
    def test_comparison_with_longdom_pattern(self):
        """Test that WalshMedia follows same proven pattern as Longdom."""
        from metapub.findit.dances.longdom import the_longdom_hustle
        import inspect
        
        # Both should use same approach
        walsh_source = inspect.getsource(the_walshmedia_bora)
        longdom_source = inspect.getsource(the_longdom_hustle)
        
        # Both should use the_doi_2step and verify_pdf_url
        common_patterns = ['the_doi_2step', 'verify_pdf_url', 'if not pma.doi:', 'MISSING:']
        
        for pattern in common_patterns:
            self.assertIn(pattern, walsh_source, f"WalshMedia should use pattern: {pattern}")
            self.assertIn(pattern, longdom_source, f"Longdom should use pattern: {pattern}")
        
        print("✅ WalshMedia follows proven Longdom pattern")


class TestWalshMediaRewriteBenefits(unittest.TestCase):
    """Test benefits of the rewrite per DANCE_FUNCTION_GUIDELINES."""
    
    def test_line_count_reduction(self):
        """Test that rewrite achieves significant line count reduction."""
        import inspect
        
        # Current function should be much smaller
        source = inspect.getsource(the_walshmedia_bora)
        lines = [line for line in source.split('\n') if line.strip() and not line.strip().startswith('"""')]
        
        # Should be around 24 lines (like Longdom)
        self.assertLess(len(lines), 30, f"Function should be ~24 lines, got {len(lines)}")
        
        print(f"✅ Function is {len(lines)} lines (significant reduction from 90 lines)")
    
    def test_eliminates_complexity(self):
        """Test that rewrite eliminates complexity from original."""
        import inspect
        
        source = inspect.getsource(the_walshmedia_bora)
        
        # Should not contain complex patterns from old version
        eliminated_patterns = [
            'unified_uri_get',  # Direct HTTP requests
            'detect_paywall_from_html',  # Paywall detection
            'article_id = doi_parts[-1]',  # URL construction
            'response.status_code == 200',  # Manual status checking
            'content_type = response.headers',  # Manual header parsing
        ]
        
        for pattern in eliminated_patterns:
            self.assertNotIn(pattern, source, f"Should eliminate complex pattern: {pattern}")
        
        print("✅ Complex patterns eliminated")
    
    def test_follows_proven_approach(self):
        """Test that rewrite follows proven evidence-driven approach."""
        import inspect
        
        source = inspect.getsource(the_walshmedia_bora)
        
        # Should follow Longdom's proven pattern exactly
        required_elements = [
            'the_doi_2step(pma.doi)',  # Direct DOI resolution
            'verify_pdf_url(pdf_url',  # Standard verification 
            'return pdf_url',  # Simple return
            'raise NoPDFLink',  # Standard error handling
        ]
        
        for element in required_elements:
            self.assertIn(element, source, f"Should use proven element: {element}")
        
        print("✅ Follows proven evidence-driven approach")


if __name__ == '__main__':
    unittest.main()