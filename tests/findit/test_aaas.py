"""Tests for AAAS (Science) journals dance function."""

import pytest
from .common import BaseDanceTest
from metapub import FindIt


class TestAAASTest(BaseDanceTest):
    """Test cases for AAAS (American Association for the Advancement of Science) journals."""

    @pytest.mark.skip(reason="Not working as of 2023-05-19")
    def test_aaas_twist(self):
        """Test AAAS twist dance function."""
        pmid_needs_form = '18385036'    # Sci Signal requiring form negotiation
        # pmid_needs_form_url = 'http://stke.sciencemag.org/content/1/13/eg3.full.pdf'
        pmid_no_form = '25678633'       # Science
        pmid_no_form_url = 'http://sciencemag.org/content/347/6223/695.full.pdf'

        source = FindIt(pmid=pmid_no_form)
        assert source.url == pmid_no_form_url

        source = FindIt(pmid=pmid_needs_form)
        # TODO: update this when the_aaas_twist knows how to navigate forms.
        assert source.url is None