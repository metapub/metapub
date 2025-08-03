"""Tests for Wolters Kluwer dance function."""

from .common import BaseDanceTest
from metapub import FindIt


class TestWoltersKluwerDance(BaseDanceTest):
    """Test cases for Wolters Kluwer."""

    def test_wolterskluwer_volta(self):
        """Test Wolters Kluwer dance function for core WK journals."""
        # Test core Wolters Kluwer journals that use the_wolterskluwer_volta
        
        # Pain journal - flagship WK publication
        pmid_pain = '37326643'  # 2023 - "Predicting chronic postsurgical pain: current evidence and a novel program to develop predictive biomarker signatures"
        source = FindIt(pmid=pmid_pain)
        assert source.pma.journal == 'Pain'
        self.assertUrlOrReason(source)
        
        # Neurosurgery - major WK publication
        pmid_neurosurg = '36924482'  # 2023 - "2022 Neurosurgery Paper of the Year" 
        source = FindIt(pmid=pmid_neurosurg)
        assert source.pma.journal == 'Neurosurgery'
        self.assertUrlOrReason(source)
        
        # Critical Care Medicine - high-impact WK journal
        pmid_ccm = '38240510'  # 2023 - CCM Guidelines on Clinical Deterioration
        source = FindIt(pmid=pmid_ccm)
        assert source.pma.journal == 'Crit Care Med'
        self.assertUrlOrReason(source)