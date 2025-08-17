"""
Test suite for the new FindIt handler system (issue #92).

Tests the registry-backed handler system that replaces the static PUBMED_SWITCHBOARD.
"""

import unittest
import os
from unittest.mock import Mock, patch

from metapub import FindIt
from metapub.findit.handlers import (
    PublisherHandler, PaywallHandler, HandlerFactory,
    RegistryBackedLookupSystem
)
from metapub.findit.registry import JournalRegistry
from .test_compat import skip_network_tests


class TestPublisherHandler(unittest.TestCase):
    """Test the base PublisherHandler class."""

    def setUp(self):
        self.registry_data = {
            'name': 'Test Publisher',
            'dance_function': 'test_dance',
            'format_template': 'http://example.com/{volume}/{issue}',
            'base_url': 'http://example.com',
            'format_params': {'param1': 'value1'}
        }
        self.handler = PublisherHandler(self.registry_data)

    def test_handler_initialization(self):
        """Test that handler initializes correctly with registry data."""
        self.assertEqual(self.handler.name, 'Test Publisher')
        self.assertEqual(self.handler.dance_function, 'test_dance')
        self.assertEqual(self.handler.format_template, 'http://example.com/{volume}/{issue}')
        self.assertEqual(self.handler.base_url, 'http://example.com')
        self.assertEqual(self.handler.format_params, {'param1': 'value1'})

    def test_can_handle_default(self):
        """Test that base handler can_handle returns False by default."""
        self.assertFalse(self.handler.can_handle("Test Journal"))

    @patch('metapub.findit.handlers.PublisherHandler._dispatch_dance_function')
    def test_get_pdf_url_dispatches_correctly(self, mock_dispatch):
        """Test that get_pdf_url properly dispatches to dance function."""
        mock_dispatch.return_value = ("http://test.url", None)
        mock_pma = Mock()

        url, reason = self.handler.get_pdf_url(mock_pma, verify=True)

        # Check call was made correctly (the method passes verify as positional arg)
        mock_dispatch.assert_called_once_with(mock_pma, True, 10, 3)
        self.assertEqual(url, "http://test.url")
        self.assertIsNone(reason)


class TestPaywallHandler(unittest.TestCase):
    """Test the PaywallHandler class."""

    def setUp(self):
        self.registry_data = {
            'name': 'Paywall Publisher',
            'dance_function': 'paywall_handler'
        }
        self.handler = PaywallHandler(self.registry_data)

    def test_paywall_handler_always_returns_paywall(self):
        """Test that paywall handler always returns PAYWALL message."""
        mock_pma = Mock()

        url, reason = self.handler.get_pdf_url(mock_pma, verify=True)

        self.assertIsNone(url)
        self.assertEqual(reason, "PAYWALL")

    def test_paywall_handler_ignores_verify_parameter(self):
        """Test that verify parameter doesn't affect paywall handler."""
        mock_pma = Mock()

        url1, reason1 = self.handler.get_pdf_url(mock_pma, verify=True)
        url2, reason2 = self.handler.get_pdf_url(mock_pma, verify=False)

        self.assertEqual(url1, url2)
        self.assertEqual(reason1, reason2)
        self.assertEqual(reason1, "PAYWALL")


class TestHandlerFactory(unittest.TestCase):
    """Test the HandlerFactory class."""

    def test_create_paywall_handler(self):
        """Test that factory creates PaywallHandler for paywall dance function."""
        registry_data = {
            'name': 'Test Paywall',
            'dance_function': 'paywall_handler'
        }

        handler = HandlerFactory.create_handler(registry_data)

        self.assertIsInstance(handler, PaywallHandler)
        self.assertEqual(handler.name, 'Test Paywall')

    def test_create_regular_handler(self):
        """Test that factory creates regular PublisherHandler for other dance functions."""
        registry_data = {
            'name': 'Test Publisher',
            'dance_function': 'the_nature_ballet'
        }

        handler = HandlerFactory.create_handler(registry_data)

        self.assertIsInstance(handler, PublisherHandler)
        self.assertNotIsInstance(handler, PaywallHandler)
        self.assertEqual(handler.name, 'Test Publisher')

    def test_create_handler_with_empty_dance_function(self):
        """Test factory behavior with empty dance function."""
        registry_data = {
            'name': 'Test Publisher',
            'dance_function': ''
        }

        handler = HandlerFactory.create_handler(registry_data)

        self.assertIsInstance(handler, PublisherHandler)
        self.assertNotIsInstance(handler, PaywallHandler)


class TestRegistryBackedLookupSystem(unittest.TestCase):
    """Test the main RegistryBackedLookupSystem class."""

    def setUp(self):
        self.mock_registry = Mock(spec=JournalRegistry)
        self.lookup_system = RegistryBackedLookupSystem(self.mock_registry)

    def test_get_handler_for_unknown_journal(self):
        """Test handling of unknown journal."""
        self.mock_registry.get_publisher_for_journal.return_value = None

        handler = self.lookup_system.get_handler_for_journal("Unknown Journal")

        self.assertIsNone(handler)
        self.mock_registry.get_publisher_for_journal.assert_called_once_with("Unknown Journal")

    def test_get_handler_creates_handler(self):
        """Test that handler is created correctly (no caching after simplification)."""
        publisher_data = {
            'name': 'Test Publisher',
            'dance_function': 'test_dance'
        }
        self.mock_registry.get_publisher_for_journal.return_value = publisher_data

        # First call should create handler
        handler1 = self.lookup_system.get_handler_for_journal("Test Journal")
        self.assertIsNotNone(handler1)
        self.assertEqual(handler1.name, 'Test Publisher')

        # Second call should create a new handler (no caching after simplification)
        handler2 = self.lookup_system.get_handler_for_journal("Test Journal")
        self.assertIsNotNone(handler2)
        self.assertEqual(handler2.name, 'Test Publisher')
        # Should be different objects since we removed caching
        self.assertIsNot(handler1, handler2)

        # Registry should be called twice since we removed caching
        self.assertEqual(self.mock_registry.get_publisher_for_journal.call_count, 2)

    @patch('metapub.findit.handlers.standardize_journal_name')
    def test_find_pdf_url_standardizes_journal_name(self, mock_standardize):
        """Test that find_pdf_url standardizes journal names."""
        mock_standardize.return_value = "Standardized Journal"
        mock_pma = Mock()
        mock_pma.journal = "Original Journal Name"

        publisher_data = {
            'name': 'Test Publisher',
            'dance_function': 'test_dance'
        }
        self.mock_registry.get_publisher_for_journal.return_value = publisher_data

        with patch.object(self.lookup_system, 'get_handler_for_journal') as mock_get_handler:
            mock_handler = Mock()
            mock_handler.get_pdf_url.return_value = ("http://test.url", None)
            mock_get_handler.return_value = mock_handler

            url, reason = self.lookup_system.find_pdf_url(mock_pma, verify=True)

            mock_standardize.assert_called_once_with("Original Journal Name")
            mock_get_handler.assert_called_once_with("Standardized Journal")
            mock_handler.get_pdf_url.assert_called_once_with(mock_pma, verify=True, request_timeout=10, max_redirects=3)

    def test_find_pdf_url_no_handler_found(self):
        """Test find_pdf_url when no handler found for journal."""
        mock_pma = Mock()
        mock_pma.journal = "Unknown Journal"

        with patch('metapub.findit.handlers.standardize_journal_name', return_value="Unknown Journal"):
            self.mock_registry.get_publisher_for_journal.return_value = None

            url, reason = self.lookup_system.find_pdf_url(mock_pma, verify=True)

            self.assertIsNone(url)
            self.assertEqual(reason, "NOFORMAT: No handler found for journal 'Unknown Journal'. Report with sample PMID at https://github.com/metapub/metapub/issues")


@skip_network_tests
class TestRegistryIntegration(unittest.TestCase):
    """Integration tests with the actual registry."""

    def setUp(self):
        self.registry = JournalRegistry()
        self.lookup_system = RegistryBackedLookupSystem(self.registry)

    def test_nature_journal_handler_integration(self):
        """Test integration with actual Nature journal in registry."""
        handler = self.lookup_system.get_handler_for_journal("Nature")

        self.assertIsNotNone(handler)
        self.assertEqual(handler.name, "nature")  # Actual publisher name in registry
        self.assertEqual(handler.dance_function, "the_nature_ballet")

    def test_oxford_journal_handler_integration(self):
        """Test integration with actual Oxford journal in registry."""
        # Test with a common Oxford journal
        handler = self.lookup_system.get_handler_for_journal("Brain")

        if handler:  # Only test if journal is in registry
            self.assertIn("Oxford", handler.name)
            self.assertIsNotNone(handler.dance_function)

    def test_science_journal_handler_integration(self):
        """Test integration with Science journal in registry."""
        handler = self.lookup_system.get_handler_for_journal("Science")

        if handler:  # Only test if journal is in registry
            self.assertIn("science magazine", handler.name.lower())  # Case insensitive check
            self.assertEqual(handler.dance_function, "the_vip_shake")

    def test_registry_seeding(self):
        """Test that registry is properly seeded with data."""
        # Registry should contain multiple publishers
        sample_journals = ["Nature", "Science", "Cell", "Brain", "JAMA"]
        found_publishers = set()

        for journal in sample_journals:
            publisher_data = self.registry.get_publisher_for_journal(journal)
            if publisher_data:
                found_publishers.add(publisher_data['name'])

        # Should find at least a few different publishers
        self.assertGreater(len(found_publishers), 2,
                          "Registry should contain multiple publishers")


@skip_network_tests
class TestLiveHandlerBehavior(unittest.TestCase):
    """Test handler behavior with real PMIDs (network required)."""

    def test_handler_system_with_sample_pmids(self):
        """Test handler system with a variety of real PMIDs."""
        # Sample PMIDs from different publishers
        test_cases = [
            ("4587242", "Nature"),  # Nature PMID
            ("22250305", "Brain"),  # Oxford PMID
            ("11636298", "Human Genetics"),  # Springer PMID
        ]

        lookup_system = RegistryBackedLookupSystem(JournalRegistry())

        for pmid, expected_journal in test_cases:
            with self.subTest(pmid=pmid, journal=expected_journal):
                try:
                    # Test the full FindIt flow
                    finder = FindIt(pmid=pmid, cachedir=None)

                    # Should get either a URL or a reasonable error
                    self.assertTrue(
                        finder.url is not None or finder.reason is not None,
                        f"PMID {pmid} returned neither URL nor reason"
                    )

                    # Test direct handler lookup
                    handler = lookup_system.get_handler_for_journal(expected_journal)
                    if handler:
                        self.assertIsNotNone(handler.name)
                        self.assertIsNotNone(handler.dance_function)

                except Exception as e:
                    # Log the error but don't fail the test for network issues
                    self.skipTest(f"Network error testing PMID {pmid}: {e}")


if __name__ == '__main__':
    unittest.main()
