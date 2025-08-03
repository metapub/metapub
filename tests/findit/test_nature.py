"""Tests for Nature Publishing Group dance function."""

import pytest
from .common import BaseDanceTest
from metapub import FindIt


class TestNatureDance(BaseDanceTest):
    """Test cases for Nature Publishing Group."""

    @pytest.mark.skip(reason="Not working as of 2023-05-19")
    def test_jid_pmid(self):
        """Test Journal of Investigative Dermatology (Nature) dance function."""
        # TODO: fix or remove
        # J Invest Dermatol -- can work through multiple paths (nature, sciencedirect)...
        pmid = 10201537
        source = FindIt(pmid)
        assert source.url == 'http://www.jidonline.org/article/S0022-202X(15)40457-9/pdf'