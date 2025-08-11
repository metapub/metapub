"""
Evidence-based tests for ACS (American Chemical Society) dance function.

Based on HTML sample analysis from real ACS articles showing:
- Consistent DOI-based pattern: /doi/pdf/{DOI}?ref=article_openPDF
- All DOIs use 10.1021/ prefix (ACS DOI prefix)
- HTTPS enforced (HTTP redirects with 301)
- Uses the_doi_slide generic function with registry-based templates
"""

import pytest
from unittest.mock import patch, Mock
try:
    from .common import BaseDanceTest
except ImportError:
    # For direct execution
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from tests.findit.common import BaseDanceTest
from metapub.findit.dances.generic import the_doi_slide
from metapub.exceptions import AccessDenied, NoPDFLink


class MockResponse:
    """Mock HTTP response for testing."""
    def __init__(self, status_code=200, content_type='application/pdf', url=''):
        self.status_code = status_code
        self.headers = {'content-type': content_type}
        self.url = url


class TestACSTest(BaseDanceTest):
    """Evidence-based test cases for ACS (American Chemical Society) journals."""

    def setUp(self):
        """Set up test fixtures.""" 
        super().setUp()

    def test_acs_journal_recognition(self):
        """Test that ACS journals are properly recognized in the registry."""
        from metapub.findit.registry import JournalRegistry
        
        registry = JournalRegistry()
        
        # Test known ACS journals from evidence samples
        acs_journals = [
            'ACS Med Chem Lett',
            'ACS Medicinal Chemistry Letters', 
            'Chem Rev',
            'Chemical Reviews',
            'ACS Appl Bio Mater',
            'J Am Chem Soc'
        ]
        
        found_count = 0
        for journal in acs_journals:
            publisher_info = registry.get_publisher_for_journal(journal)
            if publisher_info and 'American Chemical Society' in publisher_info.get('name', ''):
                assert publisher_info['dance_function'] == 'the_doi_slide'
                print(f"✓ {journal} correctly mapped to ACS")
                found_count += 1
            else:
                print(f"⚠ {journal} mapped to different publisher: {publisher_info.get('name', 'None') if publisher_info else 'None'}")
        
        registry.close()
        
        # Should find at least some ACS journals
        assert found_count > 0, "No ACS journals found in registry"
        print(f"✓ Found {found_count} properly mapped ACS journals")

    @patch('metapub.findit.dances.generic.verify_pdf_url')
    def test_acs_doi_slide_url_construction(self, mock_verify):
        """Test 1: URL construction with evidence-based DOIs."""
        # Mock PMA with real DOI from HTML sample
        pma = Mock()
        pma.doi = '10.1021/acsmedchemlett.3c00458'  # From evidence sample
        pma.journal = 'ACS Med Chem Lett'
        
        mock_verify.return_value = True
        
        with patch('metapub.findit.dances.generic.JournalRegistry') as mock_registry_class:
            mock_registry = Mock()
            mock_registry_class.return_value = mock_registry
            
            # Mock the registry response with fixed configuration
            mock_registry.get_publisher_for_journal.return_value = {
                'name': 'American Chemical Society',
                'format_template': 'https://pubs.acs.org/doi/pdf/{doi}'
            }
            
            result = the_doi_slide(pma, verify=True)
            
            # Verify URL construction
            expected_url = 'https://pubs.acs.org/doi/pdf/10.1021/acsmedchemlett.3c00458'
            assert result == expected_url
            
            # Verify registry was consulted
            mock_registry.get_publisher_for_journal.assert_called_with('ACS Med Chem Lett')
            mock_registry.close.assert_called_once()
            
            # Verify verification was called
            mock_verify.assert_called_once_with(expected_url)
            
        print(f"Test 1 - URL construction: {result}")

    @patch('metapub.findit.dances.generic.verify_pdf_url')
    def test_acs_verify_false_skips_verification(self, mock_verify):
        """Test 2: verify=False skips PDF verification."""
        pma = Mock()
        pma.doi = '10.1021/acs.chemrev.3c00705'  # From evidence sample
        pma.journal = 'Chem Rev'
        
        with patch('metapub.findit.dances.generic.JournalRegistry') as mock_registry_class:
            mock_registry = Mock()
            mock_registry_class.return_value = mock_registry
            
            mock_registry.get_publisher_for_journal.return_value = {
                'name': 'American Chemical Society',
                'format_template': 'https://pubs.acs.org/doi/pdf/{doi}'
            }
            
            result = the_doi_slide(pma, verify=False)
            
            # Should not call verify when verify=False
            mock_verify.assert_not_called()
            
            expected_url = 'https://pubs.acs.org/doi/pdf/10.1021/acs.chemrev.3c00705'
            assert result == expected_url
            
        print(f"Test 2 - Skip verification: {result}")


    @patch('metapub.findit.dances.generic.verify_pdf_url')
    def test_acs_https_pattern_enforcement(self, mock_verify):
        """Test 4: HTTPS pattern is used (not HTTP)."""
        pma = Mock()
        pma.doi = '10.1021/acsmedchemlett.3c00180'  # From evidence sample
        pma.journal = 'ACS Medicinal Chemistry Letters'
        
        mock_verify.return_value = True
        
        with patch('metapub.findit.dances.generic.JournalRegistry') as mock_registry_class:
            mock_registry = Mock()
            mock_registry_class.return_value = mock_registry
            
            # Mock the fixed registry response with HTTPS
            mock_registry.get_publisher_for_journal.return_value = {
                'name': 'American Chemical Society',
                'format_template': 'https://pubs.acs.org/doi/pdf/{doi}'
            }
            
            result = the_doi_slide(pma, verify=True)
            
            # Verify HTTPS is used
            assert result.startswith('https://'), "ACS URLs should use HTTPS"
            assert 'http://' not in result, "ACS URLs should not use HTTP"
            
            expected_url = 'https://pubs.acs.org/doi/pdf/10.1021/acsmedchemlett.3c00180'
            assert result == expected_url
            
        print(f"Test 4 - HTTPS enforcement: {result}")

    @patch('metapub.findit.dances.generic.verify_pdf_url')
    def test_acs_registry_format_template_usage(self, mock_verify):
        """Test 5: Uses format_template from registry correctly."""
        pma = Mock()
        pma.doi = '10.1021/test.doi'
        pma.journal = 'J Am Chem Soc'
        
        mock_verify.return_value = True
        
        with patch('metapub.findit.dances.generic.JournalRegistry') as mock_registry_class:
            mock_registry = Mock()
            mock_registry_class.return_value = mock_registry
            
            # Mock the registry response
            mock_registry.get_publisher_for_journal.return_value = {
                'name': 'American Chemical Society',
                'format_template': 'https://pubs.acs.org/doi/pdf/{doi}'
            }
            
            result = the_doi_slide(pma, verify=True)
            
            # Verify format template substitution worked
            expected_url = 'https://pubs.acs.org/doi/pdf/10.1021/test.doi'
            assert result == expected_url
            
            # Verify registry interaction
            mock_registry.get_publisher_for_journal.assert_called_with('J Am Chem Soc')
            
        print(f"Test 5 - Registry template usage: {result}")

    @patch('metapub.findit.dances.generic.verify_pdf_url')
    def test_acs_verification_failure_handling(self, mock_verify):
        """Test 6: Verification failure handling (paywall detection)."""
        pma = Mock()
        pma.doi = '10.1021/test.paywall'
        pma.journal = 'ACS Med Chem Lett'
        
        # Mock verification failure
        mock_verify.side_effect = AccessDenied('DENIED: Paywall detected')
        
        with patch('metapub.findit.dances.generic.JournalRegistry') as mock_registry_class:
            mock_registry = Mock()
            mock_registry_class.return_value = mock_registry
            
            mock_registry.get_publisher_for_journal.return_value = {
                'name': 'American Chemical Society',
                'format_template': 'https://pubs.acs.org/doi/pdf/{doi}'
            }
            
            with pytest.raises(AccessDenied) as exc_info:
                the_doi_slide(pma, verify=True)
            
            error_msg = str(exc_info.value)
            assert 'DENIED' in error_msg
            
        print(f"Test 6 - Verification failure: {error_msg}")

    def test_acs_evidence_based_dois_coverage(self):
        """Test 7: Coverage of all evidence DOIs from HTML samples."""
        evidence_dois = [
            '10.1021/acsmedchemlett.3c00458',  # Sample 1
            '10.1021/acsmedchemlett.3c00180',  # Sample 2  
            '10.1021/acs.chemrev.3c00705',    # Sample 3
        ]
        
        for doi in evidence_dois:
            pma = Mock()
            pma.doi = doi
            pma.journal = 'ACS Med Chem Lett' if 'acsmedchemlett' in doi else 'Chem Rev'
            
            with patch('metapub.findit.dances.generic.JournalRegistry') as mock_registry_class:
                mock_registry = Mock()
                mock_registry_class.return_value = mock_registry
                
                mock_registry.get_publisher_for_journal.return_value = {
                    'name': 'American Chemical Society',
                    'format_template': 'https://pubs.acs.org/doi/pdf/{doi}'
                }
                
                result = the_doi_slide(pma, verify=False)
                
                # Verify URL construction for each evidence DOI
                expected_url = f'https://pubs.acs.org/doi/pdf/{doi}'
                assert result == expected_url
                assert doi in result
                
                print(f"✓ Evidence DOI {doi}: {result}")



if __name__ == '__main__':
    # Run basic tests if executed directly
    test_instance = TestACSTest()
    test_instance.setUp()
    
    print("Running ACS dance function tests...")
    print("\\n" + "="*60)
    
    tests = [
        ('test_acs_journal_recognition', 'Journal recognition in registry'),
        ('test_acs_doi_slide_url_construction', 'DOI-based URL construction'),
        ('test_acs_verify_false_skips_verification', 'Skip verification mode'),
        ('test_acs_missing_doi_error', 'Missing DOI error handling'),
        ('test_acs_https_pattern_enforcement', 'HTTPS pattern enforcement'),
        ('test_acs_registry_format_template_usage', 'Registry template usage'),
        ('test_acs_verification_failure_handling', 'Verification failure handling'),
        ('test_acs_evidence_based_dois_coverage', 'Evidence DOIs coverage'),
        ('test_guidelines_compliance', 'Guidelines compliance')
    ]
    
    for test_method, description in tests:
        try:
            getattr(test_instance, test_method)()
            print(f"✓ {description}")
        except Exception as e:
            print(f"✗ {description}: {e}")
    
    print("\\n" + "="*60)
    print("Test suite completed!")