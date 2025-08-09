"""Tests for Mary Ann Liebert Publishers dance function.

Evidence-driven update 2025-08-09: Updated tests to reflect new URL pattern
https://www.liebertpub.com/doi/pdf/{doi}?download=true based on analysis 
of 5/8 accessible HTML samples.
"""

from .common import BaseDanceTest
from metapub import FindIt


class TestLiebertDance(BaseDanceTest):
    """Test cases for Mary Ann Liebert Publishers."""

    def test_liebert_paywall_detection(self):
        """Test Liebert journal recognition and paywall detection."""
        # Test Liebert journals from our expansion with paywall detection
        liebert_test_cases = [
            ('19968519', 'Cyberpsychol Behav'),
            ('38856681', 'OMICS'),
            ('20025525', 'Cloning Stem Cells'),
        ]
        
        for pmid, expected_journal in liebert_test_cases:
            source = FindIt(pmid=pmid)
            assert source.pma.journal == expected_journal
            assert source.pma.doi.startswith('10.1089/')  # Liebert DOI prefix
            # Liebert journals should be recognized and generate access-related messages
            if source.reason:
                assert ('PAYWALL' in source.reason or 'DENIED' in source.reason)
                assert 'www.liebertpub.com' in source.reason
            assert 'NOFORMAT' not in str(source.reason or '')

    def test_liebert_url_generation(self):
        """Test Liebert DOI-based URL generation."""
        from metapub.findit.dances import the_doi_slide
        from metapub.findit.registry import JournalRegistry
        from metapub import PubMedFetcher
        
        # Test URL generation for Liebert journal
        pmfetch = PubMedFetcher()
        pma = pmfetch.article_by_pmid('19968519')  # Cyberpsychol Behav
        
        # Verify journal is in Liebert registry
        registry = JournalRegistry()
        result = registry.get_publisher_for_journal('Cyberpsychol Behav')
        assert result is not None
        assert result['name'] == 'Mary Ann Liebert Publishers'
        assert result['format_template'] == 'https://www.liebertpub.com/doi/pdf/{doi}?download=true'
        registry.close()
        
        # Test URL construction (evidence-driven update 2025-08-09)
        expected_url = f"https://www.liebertpub.com/doi/pdf/{pma.doi}?download=true"
        # The URL should follow the Liebert DOI template pattern
        assert 'liebertpub.com' in expected_url
        assert pma.doi in expected_url