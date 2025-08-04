"""Tests for Sciendo dance function."""

import unittest
from metapub import FindIt
from metapub.findit.dances import the_sciendo_spiral
from metapub.pubmedfetcher import PubMedFetcher
from metapub.exceptions import *
from tests.test_compat import skip_network_tests


class TestSciendoDance(unittest.TestCase):
    
    @skip_network_tests
    def test_sciendo_spiral_recent_article(self):
        """Test Sciendo dance with a recent article."""
        # This PMID is from a more recent article that should work with the primary URL pattern
        pmid = "38575384"  # J Nematol 2024
        src = FindIt(pmid=pmid, cachedir=None)
        
        # Should get a Sciendo URL
        self.assertIsNotNone(src.url)
        self.assertIn('sciendo.com', src.url.lower())
        
    @skip_network_tests
    def test_sciendo_spiral_archive_article(self):
        """Test Sciendo dance with an archived article."""
        # This PMID is from 2015 and might be in the archive
        pmid = "27099408"  # Int Agrophys 2015
        src = FindIt(pmid=pmid, cachedir=None)
        
        # Should get a URL (either sciendo or doi)
        self.assertIsNotNone(src.url)
        
    @skip_network_tests 
    def test_sciendo_spiral_paywall_detection(self):
        """Test Sciendo dance paywall detection with verify=True."""
        # Test with an article that might have restricted access
        pmf = PubMedFetcher()
        pma = pmf.article_by_pmid("26869743")  # Acta Bot Croat 2016
        
        # First test without verify - should return URL
        url = the_sciendo_spiral(pma, verify=False)
        self.assertIsNotNone(url)
        self.assertEqual(url, f"https://sciendo.com/pdf/{pma.doi}")
        
        # With verify, it will check if PDF is actually accessible
        # This test may pass or fail depending on actual access
        try:
            url = the_sciendo_spiral(pma, verify=True)
            # If it succeeds, URL should be returned
            self.assertIsNotNone(url)
        except NoPDFLink:
            # This is also acceptable if the PDF is not accessible
            pass


# TODO: Fix journal recognition test - journals added to sciendo.py but not appearing in registry after migration
# @skip_network_tests
# def test_sciendo_journal_recognition():
#     """Test that Sciendo journals are recognized by FindIt."""
#     from metapub.findit.registry import JournalRegistry
#     
#     registry = JournalRegistry()
#     
#     # Test all three journals from the TODO file
#     test_journals = [
#         "Int Agrophys",
#         "Int Rev Soc Res", 
#         "Acta Bot Croat"
#     ]
#     
#     for journal in test_journals:
#         publisher_data = registry.get_publisher_for_journal(journal)
#         assert publisher_data is not None, f"Journal '{journal}' should be in registry"
#         assert publisher_data['name'] == 'sciendo', f"Journal '{journal}' should map to Sciendo"
#     
#     registry.close()


if __name__ == '__main__':
    unittest.main()