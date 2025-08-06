"""Tests for BioOne dance function using citation_pdf_url extraction."""

import pytest
from unittest.mock import patch, Mock

from .common import BaseDanceTest
from metapub.findit.dances import the_bioone_bounce
from metapub.exceptions import NoPDFLink


class TestBioOne(BaseDanceTest):
    """Test cases for BioOne citation_pdf_url extraction dance."""

    def _create_mock_pma(self, pmid='22942459', doi='10.13158/heia.24.2.2011.315', journal='Herzogia'):
        """Create a mock PubMedArticle object."""
        pma = Mock()
        pma.pmid = pmid
        pma.doi = doi  
        pma.journal = journal
        return pma

    @patch('metapub.findit.dances.bioone.the_vip_shake')
    def test_bioone_bounce_success(self, mock_vip_shake):
        """Test 1: Successful PDF URL extraction via the_vip_shake.
        
        Expected: Should delegate to the_vip_shake and return PDF URL
        """
        mock_vip_shake.return_value = 'https://bioone.org/journals/herzogia/volume-24/issue-2/heia.24.2.2011.315/Epiphytic-Lichen-Mycota-of-the-Virgin-Forest-Reserve-Rajhenavski-Rog/10.13158/heia.24.2.2011.315.pdf'
        
        pma = self._create_mock_pma(doi='10.13158/heia.24.2.2011.315')
        
        result = the_bioone_bounce(pma, verify=True)
        
        expected_url = 'https://bioone.org/journals/herzogia/volume-24/issue-2/heia.24.2.2011.315/Epiphytic-Lichen-Mycota-of-the-Virgin-Forest-Reserve-Rajhenavski-Rog/10.13158/heia.24.2.2011.315.pdf'
        assert result == expected_url
        mock_vip_shake.assert_called_once_with(pma, verify=True)
        print("Test 1 - Successfully extracted BioOne PDF URL via the_vip_shake")

    def test_bioone_bounce_diverse_dois(self):
        """Test 2: Test different BioOne DOI patterns.
        
        Expected: Should work for BioOne's diverse multi-publisher DOI prefixes
        """
        test_cases = [
            {
                'doi': '10.13158/heia.24.2.2011.315',
                'expected_url': 'https://bioone.org/journals/herzogia/volume-24/issue-2/heia.24.2.2011.315/Epiphytic-Lichen-Mycota-of-the-Virgin-Forest-Reserve-Rajhenavski-Rog/10.13158/heia.24.2.2011.315.pdf',
                'journal': 'Herzogia'
            },
            {
                'doi': '10.1656/045.022.0311',
                'expected_url': 'https://bioone.org/journals/northeastern-naturalist/volume-22/issue-3/045.022.0311/Female-Paced-Mating-Does-Not-Affect-Pair-Bond-Expression-by/10.1656/045.022.0311.pdf',
                'journal': 'Northeastern Naturalist' 
            },
            {
                'doi': '10.1647/20-00013',
                'expected_url': 'https://bioone.org/journals/journal-of-avian-medicine-and-surgery/volume-37/issue-1/20-00013/Diagnosis-and-Treatment-of-Gordonia-Species-Infection-in-a-Peach/10.1647/20-00013.pdf',
                'journal': 'Journal of Avian Medicine and Surgery'
            },
            {
                'doi': '10.7589/JWD-D-23-00187',
                'expected_url': 'https://bioone.org/journals/journal-of-wildlife-diseases/volume-60/issue-4/JWD-D-23-00187/Molecular-Detection-of-Anaplasma-marginale-in-Capybara-Hydrochoerus-hydrochaeris-from/10.7589/JWD-D-23-00187.pdf',
                'journal': 'Journal of Wildlife Diseases'
            }
        ]
        
        for case in test_cases:
            with patch('metapub.findit.dances.bioone.the_vip_shake') as mock_vip_shake:
                mock_vip_shake.return_value = case['expected_url']
                
                pma = self._create_mock_pma(doi=case['doi'], journal=case['journal'])
                
                result = the_bioone_bounce(pma, verify=False)
                
                assert result == case['expected_url']
                mock_vip_shake.assert_called_once_with(pma, verify=False)
                print(f"Test 2 - Successfully handled {case['journal']}: {case['doi']}")

    def test_bioone_bounce_no_doi(self):
        """Test 3: Error when no DOI provided.
        
        Expected: Should raise NoPDFLink for missing DOI
        """
        pma = self._create_mock_pma(doi=None)
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_bioone_bounce(pma, verify=False)
        
        assert 'MISSING: DOI required for BioOne PDF access' in str(exc_info.value)
        print("Test 3 - Correctly handled missing DOI")

    @patch('metapub.findit.dances.bioone.the_vip_shake')
    def test_bioone_bounce_vip_shake_error(self, mock_vip_shake):
        """Test 4: Error when the_vip_shake fails.
        
        Expected: Should propagate the_vip_shake errors (paywall, not found, etc.)
        """
        mock_vip_shake.side_effect = NoPDFLink("Citation PDF URL not found")
        
        pma = self._create_mock_pma(doi='10.1656/045.022.0311')
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_bioone_bounce(pma, verify=True)
        
        assert 'Citation PDF URL not found' in str(exc_info.value)
        print("Test 4 - Correctly propagated the_vip_shake error")

    @patch('metapub.findit.dances.bioone.the_vip_shake')
    def test_bioone_bounce_verify_false(self, mock_vip_shake):
        """Test 5: Function with verify=False.
        
        Expected: Should pass verify=False to the_vip_shake
        """
        mock_vip_shake.return_value = 'https://bioone.org/journals/.../test.pdf'
        
        pma = self._create_mock_pma(doi='10.1647/20-00013')
        
        result = the_bioone_bounce(pma, verify=False)
        
        assert result == 'https://bioone.org/journals/.../test.pdf'
        mock_vip_shake.assert_called_once_with(pma, verify=False)
        print("Test 5 - Successfully handled verify=False")

    def test_bioone_bounce_multi_publisher_consistency(self):
        """Test 6: Verify consistent behavior across BioOne's multi-publisher platform.
        
        Expected: Same delegation pattern should work for all BioOne publishers
        """
        publisher_examples = [
            ('Biological Sciences - Ecology', '10.1656/045.022.0311'),
            ('Veterinary Medicine - Avian', '10.1647/20-00013'),  
            ('Mycology - Lichenology', '10.13158/heia.24.2.2011.315'),
            ('Wildlife Biology - Disease', '10.7589/JWD-D-23-00187')
        ]
        
        for publisher_type, doi in publisher_examples:
            with patch('metapub.findit.dances.bioone.the_vip_shake') as mock_vip_shake:
                mock_vip_shake.return_value = f'https://bioone.org/journals/.../sample/{doi}.pdf'
                
                pma = self._create_mock_pma(doi=doi)
                
                result = the_bioone_bounce(pma, verify=False)
                
                assert result.startswith('https://bioone.org/journals/')
                assert doi in result
                assert result.endswith('.pdf')
                mock_vip_shake.assert_called_once_with(pma, verify=False)
                print(f"Test 6 - Successfully handled {publisher_type} publisher")


def test_bioone_journal_recognition():
    """Test that BioOne journals are properly recognized in the registry."""
    from metapub.findit.registry import JournalRegistry
    
    registry = JournalRegistry()
    
    # Test key BioOne journals from different publishers
    test_journals = [
        'Herzogia',
        'Northeastern Naturalist', 
        'Journal of Avian Medicine and Surgery',
        'Journal of Wildlife Diseases',
        'American Midland Naturalist',
        'Southeastern Naturalist'
    ]
    
    for journal in test_journals:
        publisher_info = registry.get_publisher_for_journal(journal)
        if publisher_info and publisher_info['dance_function'] == 'the_bioone_bounce':
            print(f"✓ {journal} correctly mapped to BioOne")
        else:
            print(f"⚠ {journal} not found in BioOne registry")
    
    registry.close()


if __name__ == '__main__':
    import sys
    import traceback
    
    test_instance = TestBioOne()
    
    print("Running BioOne citation_pdf_url extraction tests...")
    print("\n" + "="*70)
    
    tests = [
        ('test_bioone_bounce_success', 'Basic PDF URL extraction'),
        ('test_bioone_bounce_diverse_dois', 'Multiple DOI patterns'),
        ('test_bioone_bounce_no_doi', 'Missing DOI error'),
        ('test_bioone_bounce_vip_shake_error', 'VIP shake error propagation'),
        ('test_bioone_bounce_verify_false', 'Verify false parameter'),
        ('test_bioone_bounce_multi_publisher_consistency', 'Multi-publisher consistency'),
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
        test_bioone_journal_recognition()
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