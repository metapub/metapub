"""Tests for SAGE Publications dance function."""

from .common import BaseDanceTest
from metapub import FindIt


class TestSageDance(BaseDanceTest):
    """Test cases for SAGE Publications."""

    def test_sage_hula(self):
        """Test SAGE Publications dance function."""
        # Test SAGE paywall detection - should either get PMC or access denial
        pmid_sage_paywall = '22295291'  # South Asia Res - typical paywalled SAGE article
        source = FindIt(pmid=pmid_sage_paywall)
        # Should either get PMC URL or SAGE access denial
        if source.url:
            assert "europepmc.org" in source.url
        else:
            assert source.reason is not None
            assert "SAGE" in source.reason or "DENIED" in source.reason
        
        # Test SAGE with PMC availability
        pmid_sage_pmc = '30369646'  # Urban Stud - available in both SAGE and PMC
        source = FindIt(pmid=pmid_sage_pmc)
        # FindIt should prefer PMC over SAGE paywall
        self.assertUrlOrReason(source)
        if source.url:
            assert "europepmc.org" in source.url

    def test_sage_integration_coverage(self):
        """Test SAGE journal coverage across different subject areas."""
        # Test different SAGE journals to ensure registry integration
        sage_test_cases = [
            ('22295291', 'South Asia Res'),     # Political science
            ('38863277', 'Med Sci Law'),        # Medical-legal
            ('37972566', 'Sex Abuse'),          # Psychology
        ]
        
        for pmid, expected_journal in sage_test_cases:
            source = FindIt(pmid=pmid)
            assert source.pma.journal == expected_journal
            assert source.pma.doi.startswith('10.1177/')  # SAGE DOI prefix
            # Should either get PMC URL or SAGE-specific error (never NOFORMAT)
            self.assertNoFormatError(source)
            self.assertUrlOrReason(source)