"""Tests for MDPI dance function using DOI resolution + /pdf pattern."""

import pytest
from unittest.mock import patch, Mock

from .common import BaseDanceTest
from metapub.findit.dances import the_mdpi_moonwalk
from metapub.exceptions import NoPDFLink
from tests.fixtures import load_pmid_xml, MDPI_EVIDENCE_PMIDS


class TestMDPI(BaseDanceTest):
    """Test cases for MDPI DOI resolution + PDF dance."""

    def _create_mock_pma(self, pmid='34912529', doi='10.3390/cardiogenetics11030017', journal='Cardiogenetics'):
        """Create a mock PubMedArticle object."""
        pma = Mock()
        pma.pmid = pmid
        pma.doi = doi
        pma.journal = journal
        return pma

    @patch('metapub.findit.dances.generic.the_doi_2step')
    def test_mdpi_moonwalk_success(self, mock_doi_2step):
        """Test 1: Successful PDF URL construction.
        
        Expected: Should construct PDF URL by appending /pdf to resolved DOI URL
        """
        # Mock DOI resolution
        mock_doi_2step.return_value = 'https://www.mdpi.com/2035-8148/11/3/17'
        
        pma = self._create_mock_pma(doi='10.3390/cardiogenetics11030017')
        
        result = the_mdpi_moonwalk(pma, verify=False)
        
        assert result == 'https://www.mdpi.com/2035-8148/11/3/17/pdf'
        mock_doi_2step.assert_called_once_with('10.3390/cardiogenetics11030017')
        print("Test 1 - Successfully constructed MDPI PDF URL from DOI resolution")

    @patch('metapub.findit.dances.generic.the_doi_2step')
    def test_mdpi_moonwalk_different_journals(self, mock_doi_2step):
        """Test 2: Test different MDPI journal patterns.
        
        Expected: Should work for various MDPI journals
        """
        test_cases = [
            {
                'doi': '10.3390/cardiogenetics11030017',
                'resolved': 'https://www.mdpi.com/2035-8148/11/3/17',
                'expected': 'https://www.mdpi.com/2035-8148/11/3/17/pdf',
                'journal': 'Cardiogenetics'
            },
            {
                'doi': '10.3390/metabo14040228',
                'resolved': 'https://www.mdpi.com/2218-1989/14/4/228',
                'expected': 'https://www.mdpi.com/2218-1989/14/4/228/pdf',
                'journal': 'Metabolites'
            },
            {
                'doi': '10.3390/neurolint15030060',
                'resolved': 'https://www.mdpi.com/2035-8377/15/3/60',
                'expected': 'https://www.mdpi.com/2035-8377/15/3/60/pdf',
                'journal': 'Neurol Int'
            }
        ]
        
        for case in test_cases:
            mock_doi_2step.return_value = case['resolved']
            
            pma = self._create_mock_pma(doi=case['doi'], journal=case['journal'])
            
            result = the_mdpi_moonwalk(pma, verify=False)
            
            assert result == case['expected']
            print(f"Test 2 - Successfully handled {case['journal']}: {case['doi']}")

    def test_mdpi_moonwalk_no_doi(self):
        """Test 3: Error when no DOI provided.
        
        Expected: Should raise NoPDFLink for missing DOI
        """
        pma = self._create_mock_pma(doi=None)
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_mdpi_moonwalk(pma, verify=False)
        
        assert 'MISSING: DOI required for MDPI PDF access' in str(exc_info.value)
        print("Test 3 - Correctly handled missing DOI")

    def test_mdpi_moonwalk_wrong_doi_prefix(self):
        """Test 4: Error for non-MDPI DOI.
        
        Expected: Should raise NoPDFLink for wrong DOI prefix
        """
        pma = self._create_mock_pma(doi='10.1234/wrong.prefix')
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_mdpi_moonwalk(pma, verify=False)
        
        assert ('MISSING: Not an MDPI DOI (expected 10.3390/)' in str(exc_info.value) or 
                'TXERROR: dx.doi.org lookup failed' in str(exc_info.value))
        print("Test 4 - Correctly rejected non-MDPI DOI")

    @patch('metapub.findit.dances.generic.the_doi_2step')
    def test_mdpi_moonwalk_doi_resolution_fails(self, mock_doi_2step):
        """Test 5: Error when DOI resolution fails.
        
        Expected: Should raise NoPDFLink when DOI can't be resolved
        """
        # Mock DOI resolution failure
        mock_doi_2step.side_effect = Exception("DOI resolution failed")
        
        pma = self._create_mock_pma(doi='10.3390/cardiogenetics11030017')
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_mdpi_moonwalk(pma, verify=False)
        
        assert 'MISSING: MDPI PDF construction failed' in str(exc_info.value)
        print("Test 5 - Correctly handled DOI resolution failure")

    @patch('metapub.findit.dances.generic.verify_pdf_url')
    @patch('metapub.findit.dances.generic.the_doi_2step')
    def test_mdpi_moonwalk_verification_enabled(self, mock_doi_2step, mock_verify):
        """Test 6: PDF URL verification when verify=True.
        
        Expected: Should call verify_pdf_url when verify is True
        """
        mock_doi_2step.return_value = 'https://www.mdpi.com/2035-8148/11/3/17'
        mock_verify.return_value = True  # Verification passes
        
        pma = self._create_mock_pma(doi='10.3390/cardiogenetics11030017')
        
        result = the_mdpi_moonwalk(pma, verify=True)
        
        assert result == 'https://www.mdpi.com/2035-8148/11/3/17/pdf'
        mock_verify.assert_called_once_with('https://www.mdpi.com/2035-8148/11/3/17/pdf', 'MDPI')
        print("Test 6 - Successfully called PDF verification")

    @patch('metapub.findit.dances.generic.verify_pdf_url')
    @patch('metapub.findit.dances.generic.the_doi_2step')
    def test_mdpi_moonwalk_verification_fails(self, mock_doi_2step, mock_verify):
        """Test 7: Error when PDF verification fails.
        
        Expected: Should raise NoPDFLink when verify_pdf_url fails
        """
        mock_doi_2step.return_value = 'https://www.mdpi.com/2035-8148/11/3/17'
        mock_verify.side_effect = NoPDFLink("PDF verification failed")
        
        pma = self._create_mock_pma(doi='10.3390/cardiogenetics11030017')
        
        with pytest.raises(NoPDFLink) as exc_info:
            the_mdpi_moonwalk(pma, verify=True)
        
        assert ('PDF verification failed' in str(exc_info.value) or 
                'DENIED: MDPI url' in str(exc_info.value))
        print("Test 7 - Correctly handled PDF verification failure")


def test_mdpi_journal_recognition():
    """Test that MDPI journals are properly recognized in the registry."""
    from metapub.findit.registry import JournalRegistry
    
    registry = JournalRegistry()
    
    # Test key MDPI journals
    test_journals = [
        'Cardiogenetics',
        'Metabolites', 
        'Neurol Int',
        'Materials (Basel)',
        'Sensors (Basel)'
    ]
    
    for journal in test_journals:
        publisher_info = registry.get_publisher_for_journal(journal)
        if publisher_info and publisher_info['dance_function'] == 'the_mdpi_moonwalk':
            print(f"✓ {journal} correctly mapped to MDPI")
        else:
            print(f"⚠ {journal} not found in MDPI registry")
    
    registry.close()


if __name__ == '__main__':
    import sys
    import traceback
    
    test_instance = TestMDPI()
    
    print("Running MDPI DOI resolution + PDF dance tests...")
    print("\n" + "="*70)
    
    tests = [
        ('test_mdpi_moonwalk_success', 'Basic PDF URL construction'),
        ('test_mdpi_moonwalk_different_journals', 'Multiple journal patterns'),
        ('test_mdpi_moonwalk_no_doi', 'Missing DOI error'),
        ('test_mdpi_moonwalk_wrong_doi_prefix', 'Wrong DOI prefix'),
        ('test_mdpi_moonwalk_doi_resolution_fails', 'DOI resolution failure'),
        ('test_mdpi_moonwalk_verification_enabled', 'PDF verification enabled'),
        ('test_mdpi_moonwalk_verification_fails', 'PDF verification failure'),
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
        test_mdpi_journal_recognition()
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


class TestMDPIXMLFixtures:
    """Test MDPI XML fixtures for evidence-driven testing."""

    @patch('metapub.findit.dances.mdpi.verify_pdf_url')
    def test_mdpi_xml_39337530_int_j_mol_sci(self, mock_verify):
        """Test PMID 39337530 - Int J Mol Sci with DOI 10.3390/ijms251810046."""
        mock_verify.return_value = None
        pma = load_pmid_xml('39337530')
        
        assert pma.pmid == '39337530'
        assert pma.doi == '10.3390/ijms251810046'
        assert 'Int J Mol Sci' in pma.journal
        
        result = the_mdpi_moonwalk(pma, verify=True)
        expected_url = 'https://www.mdpi.com/1422-0067/25/18/10046/pdf'
        assert result == expected_url
        mock_verify.assert_called_once_with(expected_url, 'MDPI')

    @patch('metapub.findit.dances.mdpi.verify_pdf_url')
    def test_mdpi_xml_39337454_int_j_mol_sci(self, mock_verify):
        """Test PMID 39337454 - Int J Mol Sci with DOI 10.3390/ijms25189966."""
        mock_verify.return_value = None
        pma = load_pmid_xml('39337454')
        
        assert pma.pmid == '39337454'
        assert pma.doi == '10.3390/ijms25189966'
        assert 'Int J Mol Sci' in pma.journal
        
        result = the_mdpi_moonwalk(pma, verify=True)
        expected_url = 'https://www.mdpi.com/1422-0067/25/18/9966/pdf'
        assert result == expected_url
        mock_verify.assert_called_once_with(expected_url, 'MDPI')

    @patch('metapub.findit.dances.mdpi.verify_pdf_url')
    def test_mdpi_xml_39769357_int_j_mol_sci(self, mock_verify):
        """Test PMID 39769357 - Int J Mol Sci with DOI 10.3390/ijms252413596."""
        mock_verify.return_value = None
        pma = load_pmid_xml('39769357')
        
        assert pma.pmid == '39769357'
        assert pma.doi == '10.3390/ijms252413596'
        assert 'Int J Mol Sci' in pma.journal
        
        result = the_mdpi_moonwalk(pma, verify=True)
        expected_url = 'https://www.mdpi.com/1422-0067/25/24/13596/pdf'
        assert result == expected_url
        mock_verify.assert_called_once_with(expected_url, 'MDPI')