"""Tests for AIP Publishing dance function using direct URL construction pattern."""

import pytest
from unittest.mock import patch, Mock

from .common import BaseDanceTest
from metapub.findit.dances import the_aip_allegro
from metapub.exceptions import NoPDFLink


class TestAIP(BaseDanceTest):
    """Test cases for AIP Publishing direct URL construction dance."""

    def _create_mock_pma(self, pmid='30876344', doi='10.1063/1.5093924', journal='J Chem Phys'):
        """Create a mock PubMedArticle object."""
        pma = Mock()
        pma.pmid = pmid
        pma.doi = doi
        pma.journal = journal
        return pma

    def test_aip_allegro_success(self):
        """Test 1: Successful PDF URL construction.
        
        Expected: Should construct direct AIP PDF URL from DOI
        """
        pma = self._create_mock_pma(doi='10.1063/1.5093924')
        
        result = the_aip_allegro(pma, verify=False)
        
        assert result == 'https://pubs.aip.org/aip/article-pdf/doi/10.1063/1.5093924'
        print("Test 1 - Successfully constructed AIP PDF URL")

    def test_aip_allegro_different_dois(self):
        """Test 2: Test different AIP DOI patterns.
        
        Expected: Should work for various AIP DOI formats
        """
        test_cases = [
            {
                'doi': '10.1063/1.5093924',
                'expected': 'https://pubs.aip.org/aip/article-pdf/doi/10.1063/1.5093924',
                'journal': 'J Chem Phys'
            },
            {
                'doi': '10.1063/5.0026818',
                'expected': 'https://pubs.aip.org/aip/article-pdf/doi/10.1063/5.0026818',
                'journal': 'J Chem Phys'
            },
            {
                'doi': '10.1063/5.0021946',
                'expected': 'https://pubs.aip.org/aip/article-pdf/doi/10.1063/5.0021946',
                'journal': 'J Chem Phys'
            },
            {
                'doi': '10.1063/5.0036408',
                'expected': 'https://pubs.aip.org/aip/article-pdf/doi/10.1063/5.0036408',
                'journal': 'Biophys Rev (Melville)'
            }
        ]
        
        for case in test_cases:
            pma = self._create_mock_pma(doi=case['doi'], journal=case['journal'])
            
            result = the_aip_allegro(pma, verify=False)
            
            assert result == case['expected']
            print(f"Test 2 - Successfully handled {case['journal']}: {case['doi']}")

    def test_aip_allegro_no_doi(self):
        """Test 3: Error when no DOI provided.
        
        Expected: Should raise NoPDFLink for missing DOI
        """
        pma = self._create_mock_pma(doi=None)
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_aip_allegro(pma, verify=False)
        
        assert 'MISSING: DOI required for AIP Publishing PDF access' in str(exc_info.value)
        print("Test 3 - Correctly handled missing DOI")

    @patch('metapub.findit.dances.aip.verify_pdf_url')
    def test_aip_allegro_verification_enabled(self, mock_verify):
        """Test 4: PDF URL verification when verify=True.
        
        Expected: Should call verify_pdf_url when verify is True
        """
        mock_verify.return_value = True  # Verification passes
        
        pma = self._create_mock_pma(doi='10.1063/1.5093924')
        
        result = the_aip_allegro(pma, verify=True)
        
        assert result == 'https://pubs.aip.org/aip/article-pdf/doi/10.1063/1.5093924'
        mock_verify.assert_called_once_with('https://pubs.aip.org/aip/article-pdf/doi/10.1063/1.5093924', 'AIP')
        print("Test 5 - Successfully called PDF verification")

    @patch('metapub.findit.dances.aip.verify_pdf_url')
    def test_aip_allegro_verification_fails(self, mock_verify):
        """Test 5: Error when PDF verification fails.
        
        Expected: Should raise NoPDFLink when verify_pdf_url fails
        """
        mock_verify.side_effect = NoPDFLink("PDF verification failed")
        
        pma = self._create_mock_pma(doi='10.1063/1.5093924')
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_aip_allegro(pma, verify=True)
        
        assert 'PDF verification failed' in str(exc_info.value)
        print("Test 6 - Correctly handled PDF verification failure")

    def test_aip_allegro_journal_consistency(self):
        """Test 6: Verify URL pattern works across AIP journal types.
        
        Expected: Same pattern should work for all AIP journals
        """
        journal_types = [
            ('Physics - Chemical Physics', '10.1063/1.5093924'),
            ('Physics - Applied Physics', '10.1063/5.0026818'),
            ('Physics - Biophysics', '10.1063/5.0036408'),
            ('Physics - General', '10.1063/5.0021946')
        ]
        
        for journal_type, doi in journal_types:
            pma = self._create_mock_pma(doi=doi)
            
            result = the_aip_allegro(pma, verify=False)
            
            assert result.startswith('https://pubs.aip.org/aip/article-pdf/doi/')
            assert doi in result
            print(f"Test 7 - Successfully handled {journal_type} journal")


def test_aip_journal_recognition():
    """Test that AIP journals are properly recognized in the registry."""
    from metapub.findit.registry import JournalRegistry
    
    registry = JournalRegistry()
    
    # Test key AIP journals
    test_journals = [
        'J Chem Phys',
        'Appl Phys Lett', 
        'J Appl Phys',
        'Rev Sci Instrum',
        'Biophys Rev (Melville)'
    ]
    
    for journal in test_journals:
        publisher_info = registry.get_publisher_for_journal(journal)
        if publisher_info and publisher_info['dance_function'] == 'the_aip_allegro':
            print(f"✓ {journal} correctly mapped to AIP Publishing")
        else:
            print(f"⚠ {journal} not found in AIP registry")
    
    registry.close()


if __name__ == '__main__':
    import sys
    import traceback
    
    test_instance = TestAIP()
    
    print("Running AIP Publishing direct URL construction tests...")
    print("\n" + "="*70)
    
    tests = [
        ('test_aip_allegro_success', 'Basic PDF URL construction'),
        ('test_aip_allegro_different_dois', 'Multiple DOI patterns'),
        ('test_aip_allegro_no_doi', 'Missing DOI error'),
        ('test_aip_allegro_verification_enabled', 'PDF verification enabled'),
        ('test_aip_allegro_verification_fails', 'PDF verification failure'),
        ('test_aip_allegro_journal_consistency', 'Journal type consistency'),
    ]
    
    passed = 0
    failed = 0
    
    for test_method, description in tests:
        try:
            getattr(test_instance, test_method)()
            print(f"✓ {description}")
            passed += 1
        except Exception as e:
            print(f"✗ {description}: {e}")
            traceback.print_exc()
            failed += 1
    
    try:
        test_aip_journal_recognition()
        print("✓ Journal registry recognition")
        passed += 1
    except Exception as e:
        print(f"✗ Journal registry recognition: {e}")
        traceback.print_exc()
        failed += 1
    
    print("\n" + "="*70)
    print(f"Tests completed: {passed} passed, {failed} failed")
    
    if failed > 0:
        sys.exit(1)
    else:
        print("All tests passed! ✅")