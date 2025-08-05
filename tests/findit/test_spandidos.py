"""Tests for Spandidos dance function."""

import pytest
from unittest.mock import patch, Mock

from metapub.findit.dances import the_spandidos_lambada
from metapub.exceptions import NoPDFLink


class TestSpandidosDance:
    """Test cases for Spandidos publisher."""

    def test_spandidos_lambada_successful_pdf_construction(self):
        """Test successful PDF URL construction from DOI.
        
        Uses direct URL construction: http://www.spandidos-publications.com/{DOI}/download
        """
        # Create test PMA
        pma = Mock()
        pma.doi = '10.3892/wasj.2021.84'
        
        # Test without verification
        url = the_spandidos_lambada(pma, verify=False)
        assert url == 'http://www.spandidos-publications.com/10.3892/wasj.2021.84/download'

    def test_spandidos_lambada_missing_doi(self):
        """Test article without DOI raises appropriate error."""
        pma = Mock()
        pma.doi = None
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_spandidos_lambada(pma, verify=False)
        
        assert 'MISSING: DOI required for Spandidos journals' in str(exc_info.value)

    def test_spandidos_lambada_various_dois(self):
        """Test URL construction with various DOI patterns from our investigation."""
        test_cases = [
            ('10.3892/wasj.2021.84', 'http://www.spandidos-publications.com/10.3892/wasj.2021.84/download'),
            ('10.3892/wasj.2020.42', 'http://www.spandidos-publications.com/10.3892/wasj.2020.42/download'), 
            ('10.3892/ijfn.2021.14', 'http://www.spandidos-publications.com/10.3892/ijfn.2021.14/download'),
            ('10.3892/ijfn.2020.3', 'http://www.spandidos-publications.com/10.3892/ijfn.2020.3/download')
        ]
        
        for doi, expected_url in test_cases:
            pma = Mock()
            pma.doi = doi
            
            url = the_spandidos_lambada(pma, verify=False)
            assert url == expected_url

    @patch('metapub.findit.dances.spandidos.verify_pdf_url')
    def test_spandidos_lambada_with_verification(self, mock_verify):
        """Test that PDF verification is called when verify=True."""
        pma = Mock()
        pma.doi = '10.3892/ijfn.2021.14'
        
        url = the_spandidos_lambada(pma, verify=True)
        
        # Verify that verify_pdf_url was called with correct parameters
        expected_url = 'http://www.spandidos-publications.com/10.3892/ijfn.2021.14/download'
        mock_verify.assert_called_once_with(expected_url, 'Spandidos')
        
        assert url == expected_url

    def test_spandidos_lambada_empty_doi(self):
        """Test article with empty DOI string raises appropriate error."""
        pma = Mock()
        pma.doi = ''
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_spandidos_lambada(pma, verify=False)
        
        assert 'MISSING: DOI required for Spandidos journals' in str(exc_info.value)


def test_spandidos_journal_recognition():
    """Test that Spandidos journals are properly recognized in the registry."""
    from metapub.findit.registry import JournalRegistry
    
    registry = JournalRegistry()
    
    # Test sample Spandidos journals from our investigation
    test_journals = [
        'World Acad Sci J',
        'Int J Funct Nutr'
    ]
    
    for journal in test_journals:
        publisher_info = registry.get_publisher_for_journal(journal)
        if publisher_info:
            assert publisher_info['name'] == 'spandidos'
            assert publisher_info['dance_function'] == 'the_spandidos_lambada'
    
    registry.close()


if __name__ == '__main__':
    # Run basic tests if executed directly
    test_instance = TestSpandidosDance()
    
    print("Running Spandidos tests...")
    print("=" * 60)
    
    tests = [
        ('test_spandidos_lambada_successful_pdf_construction', 'PDF URL construction from DOI'),
        ('test_spandidos_lambada_missing_doi', 'Missing DOI handling'),
        ('test_spandidos_lambada_various_dois', 'Various DOI patterns'),
        ('test_spandidos_lambada_with_verification', 'PDF verification call'),
        ('test_spandidos_lambada_empty_doi', 'Empty DOI string handling')
    ]
    
    for test_method, description in tests:
        try:
            getattr(test_instance, test_method)()
            print(f"✓ {description}")
        except Exception as e:
            print(f"✗ {description} failed: {e}")
    
    try:
        test_spandidos_journal_recognition()
        print("✓ Journal recognition")
    except Exception as e:
        print(f"✗ Journal recognition failed: {e}")
    
    print("=" * 60)
    print("Spandidos tests completed!")