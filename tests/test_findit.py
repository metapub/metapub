import unittest
import os

from metapub import FindIt
from metapub.findit import SUPPORTED_JOURNALS
from metapub.findit.findit import CACHE_FILENAME
from .test_compat import skip_network_tests

SAMPLE_PMIDS = {'embargoed': ['25575644', '25700512', '25554792', '25146281', '25766237', '25370453'],
                'nonembargoed': ['26098888'],
                'non_pmc': ['26111251', '17373727']
                }

# Sample PMIDs from different publishers for comprehensive testing
PUBLISHER_SAMPLE_PMIDS = {
    'oxford': ['34191879', '19317042', '22250305', '20684116', '34393662'],
    'nature': ['4587242', '4357309', '8668361', '8584298', '38914718'],
    'springer': ['11636298', '11636296', '38463537', '34483379', '38911049'],
    'wiley': ['17373727'],  # Known Wiley PMID from existing tests
    'science': ['25575644', '25554792'],  # Science PMIDs from embargoed list
    # Consolidated publishers (now use generic functions)
    'bioone': ['22942459', '28747648'],  # Herzogia, J Avian Med Surg → the_vip_shake
    'frontiers': ['37465203', '38405267'],  # Front Young Minds articles → the_doi_slide  
    'sage': ['12345678'],  # Assessment → the_doi_slide (placeholder PMID)
    'aip': ['38318840', '38907517'],  # AIP journals → the_doi_slide
    'emerald': ['35123456', '36234567'],  # Emerald journals → the_doi_slide (placeholders)
    'cancerbiomed': ['38318840', '38907517'],  # Cancer Biol Med → the_vip_shake
    'spandidos': ['37166210', '36000726'],  # Spandidos journals → the_doi_slide
    'springer': ['37891234', '36789567'],  # Springer journals → the_doi_slide (placeholders)
}

TEST_CACHEDIR = "/tmp/metapub_test"

# HTD (Hard-to-do):
# http://rheumatology.oxfordjournals.org/content/48/6/704.2.full.pdf --> 19304793


class TestFindIt(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        #cleanup the test cache
        #os.remove(os.path.join(TEST_CACHEDIR, CACHE_FILENAME))
        #os.rmdir(TEST_CACHEDIR)
        pass

    def test_skipping_cache(self):
        "Test skipping the cache using cachedir=None"
        # use a known working, non-PMC pubmed ID
        src = FindIt(pmid=26111251, cachedir=None)
        assert src._cache is None
        assert src.url is not None
        assert not src.reason

    def test_using_cache(self):
        "Test that cached entries provide the same information as freshly pulled ones."
        src = FindIt(pmid=SAMPLE_PMIDS['nonembargoed'][0], cachedir=TEST_CACHEDIR)
        assert os.path.exists(os.path.join(TEST_CACHEDIR, CACHE_FILENAME))

        assert src.url is not None
        assert src._cache is not None

        # source from the same pmid. check that result is same as if we used no cache.
        cached_src = FindIt(pmid=SAMPLE_PMIDS['nonembargoed'][0])
        fresh_src = FindIt(pmid=SAMPLE_PMIDS['nonembargoed'][0], cachedir=None)

        assert cached_src.url == fresh_src.url
        assert cached_src.pma.title == fresh_src.pma.title
        assert cached_src.pma.journal == fresh_src.pma.journal


    def test_supported_journals_list(self):
        "Test that SUPPORTED_JOURNALS list exists and has entries."
        assert len(SUPPORTED_JOURNALS) > 10000
        assert "Cell" in SUPPORTED_JOURNALS
        assert "Nature" in SUPPORTED_JOURNALS

    def test_embargoed_pmid(self):
        "Test that FindIt redirects currently embargoed PMC article to publisher."
        pass
        # TODO: stock with currently embargoed articles
        # src = FindIt(pmid=SAMPLE_PMIDS['embargoed'][0], cachedir=None)
        # assert src.url is None
        # assert src.reason.startswith('DENIED')

    @skip_network_tests
    def test_oxford_journals_handler(self):
        """Test FindIt with Oxford Academic journals using new handler system."""
        for pmid in PUBLISHER_SAMPLE_PMIDS['oxford'][:2]:  # Test first 2 to avoid overloading
            with self.subTest(pmid=pmid):
                src = FindIt(pmid=pmid, cachedir=None)
                # Should find a URL or have a reasonable reason for failure
                self.assertTrue(src.url is not None or src.reason is not None)
                if src.url:
                    # Oxford URLs can be oxford.com or europepmc.org for PMC content
                    self.assertTrue('oxford' in src.url.lower() or 'europepmc.org' in src.url.lower())

    @skip_network_tests
    def test_nature_journals_handler(self):
        """Test FindIt with Nature Publishing Group journals using new handler system."""
        for pmid in PUBLISHER_SAMPLE_PMIDS['nature'][:2]:  # Test first 2 to avoid overloading
            with self.subTest(pmid=pmid):
                src = FindIt(pmid=pmid, cachedir=None)
                # Should find a URL or have a reasonable reason for failure
                self.assertTrue(src.url is not None or src.reason is not None)
                if src.url:
                    # Nature URLs can be nature.com or europepmc.org for PMC content
                    self.assertTrue('nature.com' in src.url.lower() or 'europepmc.org' in src.url.lower())

    @skip_network_tests
    def test_springer_journals_handler(self):
        """Test FindIt with Springer journals using new handler system."""
        for pmid in PUBLISHER_SAMPLE_PMIDS['springer'][:2]:  # Test first 2 to avoid overloading
            with self.subTest(pmid=pmid):
                src = FindIt(pmid=pmid, cachedir=None)
                # Should find a URL or have a reasonable reason for failure
                self.assertTrue(src.url is not None or src.reason is not None)
                if src.url:
                    self.assertTrue('springer' in src.url.lower() or 'europepmc.org' in src.url.lower())

    @skip_network_tests
    def test_science_journals_handler(self):
        """Test FindIt with Science/AAAS journals."""
        for pmid in PUBLISHER_SAMPLE_PMIDS['science'][:1]:  # Test only 1 to avoid overloading
            with self.subTest(pmid=pmid):
                src = FindIt(pmid=pmid, cachedir=None)
                # Should find a URL or have a reasonable reason for failure
                self.assertTrue(src.url is not None or src.reason is not None)
                # Science articles often redirect to PMC due to embargo policies
                if src.url:
                    self.assertTrue(any(domain in src.url.lower() for domain in
                                      ['science.org', 'sciencemag.org', 'europepmc.org']))

    def test_handler_registry_integration(self):
        """Test that the new handler system integrates properly with registry."""
        # Test with a known journal that should have a handler
        from metapub.findit.handlers import RegistryBackedLookupSystem
        from metapub.findit.registry import JournalRegistry

        registry = JournalRegistry()
        lookup_system = RegistryBackedLookupSystem(registry)

        # Test handler creation for known journal
        handler = lookup_system.get_handler_for_journal("Nature")
        self.assertIsNotNone(handler)
        # Publisher name should contain "nature" (case insensitive)
        self.assertIn("nature", handler.name.lower())

        # Test no caching behavior (after simplification)
        handler2 = lookup_system.get_handler_for_journal("Nature")
        self.assertIsNotNone(handler2)
        self.assertIn("nature", handler2.name.lower())
        # Should be different objects since we removed caching for simplification
        self.assertIsNot(handler, handler2)

    def test_paywall_handler(self):
        """Test that paywall handler returns appropriate response."""
        from metapub.findit.handlers import PaywallHandler

        # Create a mock registry data for paywall publisher
        registry_data = {
            'name': 'Test Paywall Publisher',
            'dance_function': 'paywall_handler'
        }

        handler = PaywallHandler(registry_data)
        url, reason = handler.get_pdf_url(None)  # pma not needed for paywall

        self.assertIsNone(url)
        self.assertEqual(reason, "PAYWALL")

    @skip_network_tests
    def test_registry_has_major_publishers(self):
        """Test that the registry includes major publishers and their key journals."""
        from metapub.findit.registry import JournalRegistry

        registry = JournalRegistry()

        # Test that key publishers are represented in the registry
        # These are journals we know should be in the registry based on the VIP and other data
        expected_journals = [
            ("Nature", "nature"),              # Nature Publishing Group
            ("Science", "Science Magazine"),   # Science Magazine (corrected from aaas)
            ("Cell", "sciencedirect"),         # Cell Press (consolidated into ScienceDirect)
            ("Lancet", "sciencedirect"),       # Lancet journals (consolidated into ScienceDirect)
            ("JAMA", "jama"),                  # JAMA network
            ("J Clin Invest", "jci"),          # JCI
        ]

        for journal_name, expected_publisher in expected_journals:
            with self.subTest(journal=journal_name):
                publisher_data = registry.get_publisher_for_journal(journal_name)
                self.assertIsNotNone(publisher_data,
                                   f"Journal '{journal_name}' should be in registry")
                self.assertEqual(publisher_data['name'], expected_publisher,
                               f"Journal '{journal_name}' should map to publisher '{expected_publisher}'")

        # Test that registry has substantial coverage (not empty)
        import sqlite3
        conn = sqlite3.connect(registry.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM journals")
        journal_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM publishers")
        publisher_count = cursor.fetchone()[0]

        conn.close()

        # Should have substantial data after seeding
        self.assertGreater(journal_count, 1000,
                          f"Registry should have substantial journal coverage, got {journal_count}")
        self.assertGreater(publisher_count, 20,
                          f"Registry should have substantial publisher coverage, got {publisher_count}")
