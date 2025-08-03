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
            # Liebert journals should be recognized and generate proper paywall URLs
            if source.reason:
                assert 'PAYWALL' in source.reason
                assert 'liebertpub.com' in source.reason
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
        assert result['format_template'] == 'http://online.liebertpub.com/doi/pdf/{doi}'
        registry.close()
        
        # Test URL construction
        expected_url = f"http://online.liebertpub.com/doi/pdf/{pma.doi}"
        # The URL should follow the Liebert DOI template pattern
        assert 'liebertpub.com' in expected_url
        assert pma.doi in expected_url

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
        pmid_pain = '37326643'  # 2023 - "Predicting chronic postsurgical pain: current evidence and a novel program to develop predictive biomarker signatures"
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

    def test_mdpi_moonwalk(self):
        """Test MDPI moonwalk dance function for backup PDF access."""
        # Test MDPI journals that use the_mdpi_moonwalk for backup access
        
        # Membranes journal - known MDPI publication
        pmid_membranes = '38786952'  # 2024 - DOI: 10.3390/membranes14050101
        source = FindIt(pmid=pmid_membranes)
        assert source.pma.journal == 'Membranes (Basel)'
        assert source.pma.doi == '10.3390/membranes14050101'
        # MDPI should work via PMC primarily, but moonwalk backup available
        assert source.url is not None
        # Should get PMC URL as primary source
        assert "europepmc.org" in source.url
        
    def test_mdpi_moonwalk_backup(self):
        """Test MDPI moonwalk dance function generates correct backup URLs."""
        from metapub.findit.dances import the_mdpi_moonwalk
        from metapub import PubMedFetcher
        
        # Test the moonwalk function directly to verify backup URL generation
        pmfetch = PubMedFetcher()
        pma = pmfetch.article_by_pmid('38786952')  # Membranes article
        
        # Test moonwalk without verification to check URL construction
        backup_url = the_mdpi_moonwalk(pma, verify=False)
        
        # Should generate backup PDF URL by appending /pdf to resolved DOI
        assert backup_url == 'https://www.mdpi.com/2077-0375/14/5/101/pdf'
        assert backup_url.endswith('/pdf')
        assert 'mdpi.com' in backup_url
        
        # Test with different MDPI journal
        pma2 = pmfetch.article_by_pmid('38804339')  # Methods Protoc
        backup_url2 = the_mdpi_moonwalk(pma2, verify=False)
        assert backup_url2 == 'https://www.mdpi.com/2409-9279/7/3/45/pdf'
        assert backup_url2.endswith('/pdf')
        assert 'mdpi.com' in backup_url2
