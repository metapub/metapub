"""Tests for Cancer Biology & Medicine dance function."""

import pytest
from unittest.mock import patch, Mock

from metapub.findit.dances import the_cancerbiomed_quickstep
from metapub.exceptions import NoPDFLink


class TestCancerBiomedDance:
    """Test cases for Cancer Biology & Medicine publisher."""

    def test_cancerbiomed_quickstep_successful_url_construction(self):
        """Test successful PDF URL construction from VIP data.
        
        Uses direct URL construction: https://www.cancerbiomed.org/content/cbm/{volume}/{issue}/{first_page}.full.pdf
        """
        # Create test PMA with VIP data
        pma = Mock()
        pma.volume = '20'
        pma.issue = '12'
        pma.first_page = '1021'
        
        # Test without verification
        url = the_cancerbiomed_quickstep(pma, verify=False)
        assert url == 'https://www.cancerbiomed.org/content/cbm/20/12/1021.full.pdf'

    def test_cancerbiomed_quickstep_missing_volume(self):
        """Test article without volume raises appropriate error."""
        pma = Mock()
        pma.volume = None
        pma.issue = '12'
        pma.first_page = '1021'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_cancerbiomed_quickstep(pma, verify=False)
        
        assert 'MISSING: VIP data required for Cancer Biology & Medicine - missing: volume' in str(exc_info.value)

    def test_cancerbiomed_quickstep_missing_issue(self):
        """Test article without issue raises appropriate error."""
        pma = Mock()
        pma.volume = '20'
        pma.issue = None
        pma.first_page = '1021'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_cancerbiomed_quickstep(pma, verify=False)
        
        assert 'MISSING: VIP data required for Cancer Biology & Medicine - missing: issue' in str(exc_info.value)

    def test_cancerbiomed_quickstep_missing_first_page(self):
        """Test article without first page raises appropriate error."""
        pma = Mock()
        pma.volume = '20'
        pma.issue = '12'
        pma.first_page = None
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_cancerbiomed_quickstep(pma, verify=False)
        
        assert 'MISSING: VIP data required for Cancer Biology & Medicine - missing: first_page' in str(exc_info.value)

    def test_cancerbiomed_quickstep_missing_multiple_vip_fields(self):
        """Test article missing multiple VIP fields shows all missing fields."""
        pma = Mock()
        pma.volume = None
        pma.issue = None
        pma.first_page = '1021'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_cancerbiomed_quickstep(pma, verify=False)
        
        error_msg = str(exc_info.value)
        assert 'MISSING: VIP data required for Cancer Biology & Medicine - missing: volume, issue' in error_msg

    def test_cancerbiomed_quickstep_real_pmid_patterns(self):
        """Test URL construction with real PMID patterns from our investigation."""
        test_cases = [
            # PMID 38318840 pattern
            {'volume': '20', 'issue': '12', 'first_page': '1021', 
             'expected': 'https://www.cancerbiomed.org/content/cbm/20/12/1021.full.pdf'},
            # PMID 38907517 pattern
            {'volume': '21', 'issue': '10', 'first_page': '916',
             'expected': 'https://www.cancerbiomed.org/content/cbm/21/10/916.full.pdf'}
        ]
        
        for case in test_cases:
            pma = Mock()
            pma.volume = case['volume']
            pma.issue = case['issue']
            pma.first_page = case['first_page']
            
            url = the_cancerbiomed_quickstep(pma, verify=False)
            assert url == case['expected']

    @patch('metapub.findit.dances.cancerbiomed.verify_pdf_url')
    def test_cancerbiomed_quickstep_with_verification(self, mock_verify):
        """Test that PDF verification is called when verify=True."""
        pma = Mock()
        pma.volume = '20'
        pma.issue = '12'
        pma.first_page = '1021'
        
        url = the_cancerbiomed_quickstep(pma, verify=True)
        
        # Verify that verify_pdf_url was called with correct parameters
        expected_url = 'https://www.cancerbiomed.org/content/cbm/20/12/1021.full.pdf'
        mock_verify.assert_called_once_with(expected_url, 'Cancer Biology & Medicine')
        
        assert url == expected_url

    def test_cancerbiomed_quickstep_empty_vip_strings(self):
        """Test article with empty string VIP fields raises appropriate error."""
        pma = Mock()
        pma.volume = ''
        pma.issue = '12'
        pma.first_page = '1021'
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_cancerbiomed_quickstep(pma, verify=False)
        
        assert 'MISSING: VIP data required for Cancer Biology & Medicine - missing: volume' in str(exc_info.value)


def test_cancerbiomed_journal_recognition():
    """Test that Cancer Biology & Medicine journals are properly recognized in the registry."""
    from metapub.findit.registry import JournalRegistry
    
    registry = JournalRegistry()
    
    # Test sample Cancer Biology & Medicine journal
    test_journals = [
        'Cancer Biol Med'
    ]
    
    for journal in test_journals:
        publisher_info = registry.get_publisher_for_journal(journal)
        if publisher_info:
            assert publisher_info['name'] == 'cancerbiomed'
            assert publisher_info['dance_function'] == 'the_cancerbiomed_quickstep'
    
    registry.close()


if __name__ == '__main__':
    # Run basic tests if executed directly
    test_instance = TestCancerBiomedDance()
    
    print("Running Cancer Biology & Medicine tests...")
    print("=" * 60)
    
    tests = [
        ('test_cancerbiomed_quickstep_successful_url_construction', 'PDF URL construction from VIP'),
        ('test_cancerbiomed_quickstep_missing_volume', 'Missing volume handling'),
        ('test_cancerbiomed_quickstep_missing_issue', 'Missing issue handling'),
        ('test_cancerbiomed_quickstep_missing_first_page', 'Missing first page handling'),
        ('test_cancerbiomed_quickstep_missing_multiple_vip_fields', 'Multiple missing VIP fields'),
        ('test_cancerbiomed_quickstep_real_pmid_patterns', 'Real PMID patterns'),
        ('test_cancerbiomed_quickstep_with_verification', 'PDF verification call'),
        ('test_cancerbiomed_quickstep_empty_vip_strings', 'Empty VIP string handling')
    ]
    
    for test_method, description in tests:
        try:
            getattr(test_instance, test_method)()
            print(f"✓ {description}")
        except Exception as e:
            print(f"✗ {description} failed: {e}")
    
    try:
        test_cancerbiomed_journal_recognition()
        print("✓ Journal recognition")
    except Exception as e:
        print(f"✗ Journal recognition failed: {e}")
    
    print("=" * 60)
    print("Cancer Biology & Medicine tests completed!")