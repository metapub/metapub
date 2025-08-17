"""Publisher handlers for the new FindIt system.

This module provides the interface between the registry and the dance functions,
replacing the static PUBMED_SWITCHBOARD with a dynamic handler system.
"""

import logging
from typing import Optional, Tuple, Dict, Any
from ..exceptions import MetaPubError
from .registry import standardize_journal_name

log = logging.getLogger('metapub.findit.handlers')

class PublisherHandler:
    """Base class for publisher-specific PDF finding logic."""

    def __init__(self, registry_data: Dict[str, Any]):
        """Initialize handler with registry data.

        Args:
            registry_data: Dictionary from registry containing publisher info
        """
        self.name = registry_data['name']
        self.dance_function = registry_data['dance_function']
        self.format_template = registry_data.get('format_template')
        self.base_url = registry_data.get('base_url')
        self.format_params = registry_data.get('format_params')

    def can_handle(self, journal_name: str) -> bool:
        """Check if this handler can process the given journal.

        Args:
            journal_name: Journal name to check

        Returns:
            True if this handler can process the journal
        """
        # This will be overridden by registry lookup
        return False

    def get_pdf_url(self, pma, verify: bool = True, request_timeout: int = 10, 
                   max_redirects: int = 3) -> Tuple[Optional[str], Optional[str]]:
        """Get PDF URL for the given PubMed article.

        Args:
            pma: PubMedArticle object
            verify: Whether to verify the URL
            request_timeout: HTTP request timeout in seconds
            max_redirects: Maximum number of redirects to follow

        Returns:
            Tuple of (url, reason)
        """
        return self._dispatch_dance_function(pma, verify, request_timeout, max_redirects)

    def _dispatch_dance_function(self, pma, verify: bool = True, request_timeout: int = 10,
                               max_redirects: int = 3) -> Tuple[Optional[str], Optional[str]]:
        """Dispatch to the appropriate dance function.

        Args:
            pma: PubMedArticle object
            verify: Whether to verify the URL
            request_timeout: HTTP request timeout in seconds
            max_redirects: Maximum number of redirects to follow

        Returns:
            Tuple of (url, reason)
        """
        try:
            # Dynamically get the dance function by name
            from . import dances
            dance_func = getattr(dances, self.dance_function)

            log.debug("Calling dance function: %s for journal: %s (PMID: %s, Publisher: %s)",
                     self.dance_function, pma.journal, pma.pmid, self.name)
            result = dance_func(pma, verify=verify, request_timeout=request_timeout, 
                              max_redirects=max_redirects)

            # Normalize return value to always be (url, reason) tuple
            if isinstance(result, tuple):
                return result
            elif isinstance(result, str):
                return result, None  # URL found, no error reason
            else:
                return None, f"HANDLER_ERROR: Unexpected return type from {self.dance_function}"

        # Dev note for LLMs: don't bother catching ImportError or AttributeError because (1) we
        #     have control over the dance functions and (2) lack of dance function is a major
        #     breaking error that we should fix, not simply log.
        except Exception as e:
            # Check if this is a normal access denial (not a real error)
            error_msg = str(e)
            if error_msg.startswith('DENIED:') or error_msg.startswith('PAYWALL'):
                # This is normal operation - publisher denied access or requires subscription
                log.debug("Dance function %s: %s", self.dance_function, error_msg)
                return None, error_msg
            else:
                # This is an unexpected error that should be logged with full context
                log.error("Dance function %s failed for PMID %s, journal '%s', publisher '%s': %s", 
                         self.dance_function, pma.pmid, pma.journal, self.name, e)
                return None, f"TXERROR: {e}"


class PaywallHandler(PublisherHandler):
    """Special handler for paywalled publishers."""

    def get_pdf_url(self, pma, verify: bool = True, request_timeout: int = 10,
                   max_redirects: int = 3) -> Tuple[Optional[str], Optional[str]]:
        """Always returns paywall message for paywalled journals."""
        return None, "PAYWALL"


class HandlerFactory:
    """Factory for creating appropriate handlers based on registry data."""

    @staticmethod
    def create_handler(registry_data: Dict[str, Any]) -> PublisherHandler:
        """Create appropriate handler for the given registry data.

        Args:
            registry_data: Publisher data from registry

        Returns:
            Appropriate PublisherHandler instance
        """
        dance_function = registry_data.get('dance_function', '')

        if dance_function == 'paywall_handler':
            return PaywallHandler(registry_data)
        else:
            return PublisherHandler(registry_data)


class RegistryBackedLookupSystem:
    """Main system that uses the registry to find handlers for journals."""

    def __init__(self, registry):
        """Initialize with a JournalRegistry instance.

        Args:
            registry: JournalRegistry instance for lookups
        """
        self.registry = registry

    def get_handler_for_journal(self, journal_name: str) -> Optional[PublisherHandler]:
        """Get appropriate handler for a journal.

        Args:
            journal_name: Name of the journal to look up

        Returns:
            PublisherHandler instance or None if not found
        """
        # Look up in registry
        publisher_data = self.registry.get_publisher_for_journal(journal_name)
        if not publisher_data:
            return None

        # Create handler
        handler = HandlerFactory.create_handler(publisher_data)
        return handler

    def find_pdf_url(self, pma, verify: bool = True, request_timeout: int = 10,
                    max_redirects: int = 3) -> Tuple[Optional[str], Optional[str]]:
        """Find PDF URL for a PubMed article using the registry system.

        Args:
            pma: PubMedArticle object
            verify: Whether to verify URLs
            request_timeout: HTTP request timeout in seconds
            max_redirects: Maximum number of redirects to follow

        Returns:
            Tuple of (url, reason)
        """
        journal_name = standardize_journal_name(pma.journal)
        handler = self.get_handler_for_journal(journal_name)

        if handler:
            return handler.get_pdf_url(pma, verify=verify, request_timeout=request_timeout,
                                     max_redirects=max_redirects)
        else:
            return None, f"NOFORMAT: No handler found for journal '{journal_name}'. Report with sample PMID at https://github.com/metapub/metapub/issues"
