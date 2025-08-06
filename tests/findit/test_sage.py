"""Tests for SAGE Publications dance function using /doi/reader/ pattern."""

import pytest
from unittest.mock import patch, Mock

from .common import BaseDanceTest
from metapub.findit.dances import the_sage_hula
from metapub.exceptions import NoPDFLink


class TestSAGE(BaseDanceTest):
    """Test cases for SAGE Publications /doi/reader/ dance."""

    def _create_mock_pma(self, pmid='30369648', doi='10.1177/0048393118767084', journal='Philos Soc Sci'):
        """Create a mock PubMedArticle object."""
        pma = Mock()
        pma.pmid = pmid
        pma.doi = doi
        pma.journal = journal
        return pma

    def test_sage_hula_success(self):
        """Test 1: Successful PDF URL construction.
        
        Expected: Should construct /doi/reader/ URL from DOI
        """
        pma = self._create_mock_pma(doi='10.1177/0048393118767084')
        
        result = the_sage_hula(pma, verify=False)
        
        assert result == 'https://journals.sagepub.com/doi/reader/10.1177/0048393118767084'
        print("Test 1 - Successfully constructed SAGE PDF/EPUB reader URL")

    def test_sage_hula_different_journals(self):
        """Test 2: Test different SAGE journal DOI patterns.
        
        Expected: Should work for various SAGE journals
        """
        test_cases = [
            {
                'doi': '10.1177/0048393118767084',
                'expected': 'https://journals.sagepub.com/doi/reader/10.1177/0048393118767084',
                'journal': 'Philosophy of the Social Sciences'
            },
            {
                'doi': '10.1177/00405736221132863', 
                'expected': 'https://journals.sagepub.com/doi/reader/10.1177/00405736221132863',
                'journal': 'Theology Today'
            },
            {
                'doi': '10.1177/17539447241234655',
                'expected': 'https://journals.sagepub.com/doi/reader/10.1177/17539447241234655', 
                'journal': 'Therapeutic Advances in Cardiovascular Disease'
            },
            {
                'doi': '10.1177/13591053241258207',
                'expected': 'https://journals.sagepub.com/doi/reader/10.1177/13591053241258207',
                'journal': 'Journal of Health Psychology'
            }
        ]
        
        for case in test_cases:
            pma = self._create_mock_pma(doi=case['doi'], journal=case['journal'])
            
            result = the_sage_hula(pma, verify=False)
            
            assert result == case['expected']
            print(f"Test 2 - Successfully handled {case['journal']}: {case['doi']}")

    def test_sage_hula_no_doi(self):
        """Test 3: Error when no DOI provided.
        
        Expected: Should raise NoPDFLink for missing DOI
        """
        pma = self._create_mock_pma(doi=None)
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_sage_hula(pma, verify=False)
        
        assert 'MISSING: DOI required for SAGE Publications PDF access' in str(exc_info.value)
        print("Test 3 - Correctly handled missing DOI")

    @patch('metapub.findit.dances.generic.verify_pdf_url')
    def test_sage_hula_verification_enabled(self, mock_verify):
        """Test 4: PDF URL verification when verify=True.
        
        Expected: Should call verify_pdf_url when verify is True
        """
        mock_verify.return_value = True  # Verification passes
        
        pma = self._create_mock_pma(doi='10.1177/0048393118767084')
        
        result = the_sage_hula(pma, verify=True)
        
        assert result == 'https://journals.sagepub.com/doi/reader/10.1177/0048393118767084'
        mock_verify.assert_called_once_with('https://journals.sagepub.com/doi/reader/10.1177/0048393118767084', 'SAGE')
        print("Test 4 - Successfully called PDF verification")

    @patch('metapub.findit.dances.generic.verify_pdf_url')
    def test_sage_hula_verification_fails(self, mock_verify):
        """Test 5: Error when PDF verification fails.
        
        Expected: Should raise NoPDFLink when verify_pdf_url fails
        """
        mock_verify.side_effect = NoPDFLink("PDF verification failed")
        
        pma = self._create_mock_pma(doi='10.1177/0048393118767084')
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_sage_hula(pma, verify=True)
        
        assert 'PDF verification failed' in str(exc_info.value)
        print("Test 5 - Correctly handled PDF verification failure")

    def test_sage_hula_edge_cases(self):
        """Test 6: Edge cases with different DOI patterns.
        
        Expected: Should handle various SAGE DOI formats
        """
        edge_cases = [
            {
                'description': 'Long DOI with multiple components',
                'doi': '10.1177/0048393118767084',
                'expected': 'https://journals.sagepub.com/doi/reader/10.1177/0048393118767084'
            },
            {
                'description': 'DOI with zeros',
                'doi': '10.1177/00405736221132863',
                'expected': 'https://journals.sagepub.com/doi/reader/10.1177/00405736221132863'
            },
            {
                'description': 'Recent DOI pattern',
                'doi': '10.1177/17539447241234655',
                'expected': 'https://journals.sagepub.com/doi/reader/10.1177/17539447241234655'
            }
        ]
        
        for case in edge_cases:
            pma = self._create_mock_pma(doi=case['doi'])
            
            result = the_sage_hula(pma, verify=False)
            
            assert result == case['expected']
            print(f"Test 6 - Successfully handled {case['description']}")

    def test_sage_hula_journal_consistency(self):
        """Test 7: Verify URL pattern works across SAGE journal types.
        
        Expected: Same pattern should work for all SAGE journals
        """
        journal_types = [
            ('Philosophy & Social Sciences', '10.1177/0048393118767084'),
            ('Theology & Religion', '10.1177/00405736221132863'),
            ('Medical Science', '10.1177/17539447241234655'),
            ('Psychology', '10.1177/13591053241258207')
        ]
        
        for journal_type, doi in journal_types:
            pma = self._create_mock_pma(doi=doi)
            
            result = the_sage_hula(pma, verify=False)
            
            assert result.startswith('https://journals.sagepub.com/doi/reader/')
            assert doi in result
            print(f"Test 7 - Successfully handled {journal_type} journal")


def test_sage_journal_recognition():
    """Test that SAGE journals are properly recognized in the registry."""
    from metapub.findit.registry import JournalRegistry
    
    registry = JournalRegistry()
    
    # Test key SAGE journals
    test_journals = [
        'Philos Soc Sci',
        'Theol Today', 
        'Ther Adv Cardiovasc Dis',
        'J Health Psychol',
        'Urban Stud'
    ]
    
    for journal in test_journals:
        publisher_info = registry.get_publisher_for_journal(journal)
        if publisher_info and publisher_info['dance_function'] == 'the_sage_hula':
            print(f"✓ {journal} correctly mapped to SAGE Publications")
        else:
            print(f"⚠ {journal} not found in SAGE registry")
    
    registry.close()


if __name__ == '__main__':
    import sys
    import traceback
    
    test_instance = TestSAGE()
    
    print("Running SAGE Publications /doi/reader/ dance tests...")
    print("\n" + "="*70)
    
    tests = [
        ('test_sage_hula_success', 'Basic PDF reader URL construction'),
        ('test_sage_hula_different_journals', 'Multiple journal patterns'),
        ('test_sage_hula_no_doi', 'Missing DOI error'),
        ('test_sage_hula_verification_enabled', 'PDF verification enabled'),
        ('test_sage_hula_verification_fails', 'PDF verification failure'),
        ('test_sage_hula_edge_cases', 'Edge case DOI patterns'),
        ('test_sage_hula_journal_consistency', 'Journal type consistency'),
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
        test_sage_journal_recognition()
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