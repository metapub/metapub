"""Tests for SciELO (Scientific Electronic Library Online) dance function."""

import pytest
from .common import BaseDanceTest
from metapub import FindIt


class TestScieloDance(BaseDanceTest):
    """Test cases for SciELO (Scientific Electronic Library Online)."""

    @pytest.mark.skip(reason="Not working as of 2023-05-19")
    def test_scielo_chula(self):
        """Test SciELO chula dance function."""
        # TODO: fix or remove
        pmid = 26840468
        source = FindIt(pmid)
        assert source.url == 'http://www.scielo.br/pdf/ag/v52n4/0004-2803-ag-52-04-00278.pdf'