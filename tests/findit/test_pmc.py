"""Tests for PMC twist dance function."""

from .common import BaseDanceTest
from metapub import FindIt


class TestPMCTwist(BaseDanceTest):
    """Test cases for PMC (PubMed Central) access."""

    def test_pmc_twist(self):
        """Test PMC twist with embargoed and non-embargoed articles."""
        embargoed = '25554792'      # Science / pmc-release = Jan 2, 2016 / PMC4380271
        nonembargoed = '26106273'   # Saudi Pharm / pmc-release = None / PMC4475813

        # TODO: update with more future-proof testing.
        #  Steps:
        #   1. search for pmids within the last 3-4 months in a top publisher (say SAGE)
        #   2. scan pmids for embargoed example
        #   3. test that correct behavior happens with embargoed article.
        #
        #  We can retain these "nonembargoed" PMIDS for testing: 25554792, 26106273

        # test that even if we find an embargo date, if date is passed, we get a PMC url.
        source = FindIt(pmid=embargoed)
        assert source.pma.pmc == '4380271'
        assert source.pma.history['pmc-release'] is not None
        assert "pmc" in source.url

        source = FindIt(pmid=nonembargoed)
        assert source.pma.pmc == '4475813'
        assert source.pma.history.get('pmc-release', None) is not None
        assert "pmc" in source.url