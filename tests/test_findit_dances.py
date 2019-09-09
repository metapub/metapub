from __future__ import print_function

import unittest
import logging
from metapub import FindIt

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
        #TODO: get a new embargoed PMID
        embargoed = '25554792'      # Science / pmc-release = Jan 2, 2016 / PMC4380271
        embargoed_url = 'http://sciencemag.org/content/347/6217/1258522.full.pdf'

        nonembargoed = '26106273'   # Saudi Pharm / pmc-release = None / PMC4475813

        source = FindIt(pmid=embargoed)
        assert source.pma.pmc == '4380271'
        #assert source.pma.history['pmc-release'] is not None
        #assert source.url == embargoed_url

        source = FindIt(pmid=nonembargoed)
        assert source.pma.pmc == '4475813'
        assert source.pma.history.get('pmc-release', None) is None
        print(source.url)

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
        #if source.pma.pmc:
        #    assert source.url.find('europepmc.org') > -1
        #else:
        #    assert source.reason.find('jci.org') > -1

    def test_jstage_dive(self):
        pmid = 21297370
        source = FindIt(pmid)
        assert source.url == 'https://www.jstage.jst.go.jp/article/yakushi/131/2/131_2_247/_pdf'

    def test_scielo_chula(self):
        pmid = 26840468
        source = FindIt(pmid)
        assert source.url == 'http://www.scielo.br/pdf/ag/v52n4/0004-2803-ag-52-04-00278.pdf'

    #def test_jid_pmid(self):
    #    # J Invest Dermatol -- can work through multiple paths (nature, sciencedirect)...
    #    pmid = 10201537
    #    source = FindIt(pmid)
    #    assert source.url == 'http://www.jidonline.org/article/S0022-202X(15)40457-9/pdf'


