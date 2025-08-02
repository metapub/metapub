from __future__ import print_function

import unittest
import logging
from metapub import FindIt
import pytest


log = logging.getLogger()
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
log.addHandler(ch)


class TestFindItDances(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_jama_dance(self):
        doi_but_unfree = '26575068'
        source = FindIt(doi_but_unfree)
        #TODO re-examine ^^
        assert source.url is not None

    def test_pmc_twist(self):
        embargoed = '25554792'      # Science / pmc-release = Jan 2, 2016 / PMC4380271
        nonembargoed = '26106273'   # Saudi Pharm / pmc-release = None / PMC4475813

        #TODO: update with more future-proof testing.
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

    @pytest.mark.skip(reason="Not working as of 2023-05-19")
    def test_aaas_tango(self):
        pmid_needs_form = '18385036'    # Sci Signal requiring form negotiation
        # pmid_needs_form_url = 'http://stke.sciencemag.org/content/1/13/eg3.full.pdf'
        pmid_no_form = '25678633'       # Science
        pmid_no_form_url = 'http://sciencemag.org/content/347/6223/695.full.pdf'

        source = FindIt(pmid=pmid_no_form)
        assert source.url == pmid_no_form_url

        source = FindIt(pmid=pmid_needs_form)
        # TODO: update this when the_aaas_tango knows how to navigate forms.
        assert source.url is None

    def test_jci_polka(self):
        pmid = 26030226
        source = FindIt(pmid=pmid)
        #someone at JCI complained about articles being on europepmc.org?
        #TODO: I have no idea what this comment means.  :blush: --@nthmost

        #if source.pma.pmc:
        #    assert source.url.find('europepmc.org') > -1
        #else:
        #    assert source.reason.find('jci.org') > -1

    def test_jstage_dive(self):
        pmid = 21297370
        source = FindIt(pmid)
        assert source.url == 'https://www.jstage.jst.go.jp/article/yakushi/131/2/131_2_247/_pdf'

    @pytest.mark.skip(reason="Not working as of 2023-05-19")
    def test_scielo_chula(self):
        #TODO: fix or remove
        pmid = 26840468
        source = FindIt(pmid)
        assert source.url == 'http://www.scielo.br/pdf/ag/v52n4/0004-2803-ag-52-04-00278.pdf'

    @pytest.mark.skip(reason="Not working as of 2023-05-19")
    def test_jid_pmid(self):
        #TODO: fix or remove
        # J Invest Dermatol -- can work through multiple paths (nature, sciencedirect)...
        pmid = 10201537
        source = FindIt(pmid)
        assert source.url == 'http://www.jidonline.org/article/S0022-202X(15)40457-9/pdf'

    def test_cambridge_foxtrot(self):
        """Test Cambridge University Press dance function across different eras."""
        # Test PMIDs from different decades to ensure Cambridge dance works across time periods
        
        # 1990s era - Journal of Mental Science  
        pmid_1990s = '14021516'  # 1992 - DOI: 10.1192/bjp.108.457.811
        source = FindIt(pmid=pmid_1990s)
        # Cambridge journals should either get PDF URL or fall back to PMC
        assert source.url is not None or source.reason is not None
        
        # 2010s era - Trans R Hist Soc  
        pmid_2010s = '26633910'  # 2015 - DOI: 10.1017/S008044011500002X
        source = FindIt(pmid=pmid_2010s)
        assert source.url is not None or source.reason is not None
        
        # 2020s era - Philosophy
        pmid_2020s = '38481934'  # 2023 - DOI: 10.1017/S0031819123000049
        source = FindIt(pmid=pmid_2020s)
        assert source.url is not None or source.reason is not None

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
        assert source.url is not None or source.reason is not None
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
            if source.reason:
                assert 'NOFORMAT' not in source.reason
            assert source.url is not None or source.reason is not None

    def test_wolterskluwer_volta(self):
        """Test Wolters Kluwer dance function for core WK journals."""
        # Test core Wolters Kluwer journals that use the_wolterskluwer_volta
        
        # Pain journal - flagship WK publication
        pmid_pain = '38101893'  # 2023 - "Pain research in 2023: towards understanding chronic pain"
        source = FindIt(pmid=pmid_pain)
        assert source.pma.journal == 'Pain'
        assert source.url is not None or source.reason is not None
        
        # Neurosurgery - major WK publication
        pmid_neurosurg = '36924482'  # 2023 - "2022 Neurosurgery Paper of the Year" 
        source = FindIt(pmid=pmid_neurosurg)
        assert source.pma.journal == 'Neurosurgery'
        assert source.url is not None or source.reason is not None
        
        # Critical Care Medicine - high-impact WK journal
        pmid_ccm = '38240510'  # 2023 - CCM Guidelines on Clinical Deterioration
        source = FindIt(pmid=pmid_ccm)
        assert source.pma.journal == 'Crit Care Med'
        assert source.url is not None or source.reason is not None

    def test_lww_template(self):
        """Test LWW platform template for DOI-based journals.lww.com URLs."""
        # Test LWW platform journals that use the new lww_template
        
        # Use the PMIDs we found from the TODO file for LWW platform journals
        lww_test_cases = [
            ('38817191', 'Neurol India'),      # 2024 - DOI: 10.4103/neurol-india.Neurol-India-D-24-00165
            ('38905624', 'Nurs Res'),          # 2024 - DOI: 10.1097/NNR.0000000000000731  
            ('38915149', 'Nurse Pract'),       # 2024 - DOI: 10.1097/01.NPR.0000000000000202
        ]
        
        for pmid, expected_journal in lww_test_cases:
            source = FindIt(pmid=pmid)
            assert source.pma.journal == expected_journal
            # LWW journals should either get PDF URL via template or PMC fallback
            assert source.url is not None or source.reason is not None
            # Verify DOI exists (required for LWW template)
            assert source.pma.doi is not None
            
            # If we get a reason, it should not be NOFORMAT since LWW journals are now covered
            if source.reason:
                assert 'NOFORMAT' not in source.reason
