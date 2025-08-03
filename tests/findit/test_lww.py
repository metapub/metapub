"""Tests for LWW (Lippincott Williams & Wilkins) platform dance function."""

from .common import BaseDanceTest
from metapub import FindIt


class TestLWWDance(BaseDanceTest):
    """Test cases for LWW (Lippincott Williams & Wilkins) platform."""

    def test_lww_template(self):
        """Test LWW platform template for DOI-based journals.lww.com URLs."""
        # Test LWW platform journals that use the new lww_template
        
        # Use the PMIDs we found from the TODO file for LWW platform journals
        lww_test_cases = [
            ('38817191', 'Neurol India'),      # 2024 - DOI: 10.4103/neurol-india.Neurol-India-D-24-00165
            ('38905624', 'Nurs Res'),          # 2024 - DOI: 10.1097/NNR.0000000000000731  
            ('38915149', 'Nurse Pract'),       # 2024 - DOI: 10.1097/01.NPR.0000000000000202
        ]
        
        for pmid, expected_journal in lww_test_cases:
            source = FindIt(pmid=pmid)
            assert source.pma.journal == expected_journal
            # LWW journals should either get PDF URL via template or PMC fallback
            self.assertUrlOrReason(source)
            # Verify DOI exists (required for LWW template)
            assert source.pma.doi is not None
            
            # If we get a reason, it should not be NOFORMAT since LWW journals are now covered
            self.assertNoFormatError(source)