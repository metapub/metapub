"""Tests for J-STAGE (Japan Science and Technology Information Aggregator, Electronic) dance function."""

from .common import BaseDanceTest
from metapub import FindIt


class TestJStageDance(BaseDanceTest):
    """Test cases for J-STAGE journals."""

    def test_jstage_dive(self):
        """Test Jstage dive function with expanded journal coverage."""
        # Test with a known working Jstage journal from our expansion
        pmid = '31902831'  # Okajimas Folia Anat Jpn - confirmed working
        source = FindIt(pmid=pmid)
        assert source.pma.journal == 'Okajimas Folia Anat Jpn'
        assert source.pma.doi == '10.2535/ofaj.96.49'
        # Should get Jstage URL via the_jstage_dive function
        assert source.url is not None
        assert 'jstage.jst.go.jp' in source.url
        assert source.url.endswith('_pdf')

    def test_jstage_expansion_coverage(self):
        """Test Jstage expansion with multiple Japanese journals."""
        # Test different types of Japanese journals from our expansion
        jstage_test_cases = [
            ('19037164', 'Nihon Hotetsu Shika Gakkai Zasshi'),  # Japanese dental journal
            ('1363467', 'Endocrinol Jpn'),                      # Japanese endocrinology
        ]
        
        for pmid, expected_journal in jstage_test_cases:
            source = FindIt(pmid=pmid)
            assert source.pma.journal == expected_journal
            # Should either get Jstage URL or proper reason (never NOFORMAT)
            if source.reason:
                assert 'NOFORMAT' not in source.reason
            if source.url:
                assert 'jstage.jst.go.jp' in source.url