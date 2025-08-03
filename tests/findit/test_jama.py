"""Tests for JAMA network journals dance function."""

from .common import BaseDanceTest
from metapub import FindIt


class TestJAMADance(BaseDanceTest):
    """Test cases for JAMA network journals."""

    def test_jama_dance(self):
        """Test JAMA dance function."""
        doi_but_unfree = '26575068'
        source = FindIt(doi_but_unfree)
        # TODO: re-examine this test case
        assert source.url is not None