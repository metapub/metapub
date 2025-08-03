"""Tests for JCI (Journal of Clinical Investigation) dance function."""

from .common import BaseDanceTest
from metapub import FindIt


class TestJCIDance(BaseDanceTest):
    """Test cases for JCI (Journal of Clinical Investigation)."""

    def test_jci_polka(self):
        """Test JCI polka dance function."""
        pmid = 26030226
        source = FindIt(pmid=pmid)
        # Someone at JCI complained about articles being on europepmc.org?
        # TODO: I have no idea what this comment means.  :blush: --@nthmost

        # if source.pma.pmc:
        #     assert source.url.find('europepmc.org') > -1
        # else:
        #     assert source.reason.find('jci.org') > -1