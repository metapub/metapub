"""Publisher handlers for the new FindIt system.

This module provides the interface between the registry and the dance functions,
replacing the static PUBMED_SWITCHBOARD with a dynamic handler system.
"""

import logging
from typing import Optional, Tuple, Dict, Any
from ..exceptions import MetaPubError

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
    
    def get_pdf_url(self, pma, verify: bool = True) -> Tuple[Optional[str], Optional[str]]:
        """Get PDF URL for the given PubMed article.
        
        Args:
            pma: PubMedArticle object
            verify: Whether to verify the URL
            
        Returns:
            Tuple of (url, reason)
        """
        return self._dispatch_dance_function(pma, verify)
    
    def _dispatch_dance_function(self, pma, verify: bool = True) -> Tuple[Optional[str], Optional[str]]:
        """Dispatch to the appropriate dance function.
        
        Args:
            pma: PubMedArticle object
            verify: Whether to verify the URL
            
        Returns:
            Tuple of (url, reason)
        """
        # Import dance functions dynamically
        try:
            from .dances import (
                the_aaas_tango, the_biochemsoc_saunter, the_biomed_calypso,
                the_cell_pogo, the_jama_dance, the_jstage_dive,
                the_karger_conga, the_lancet_tango, the_nature_ballet,
                the_scielo_chula, the_sciencedirect_disco, the_springer_shag,
                the_spandidos_lambada, the_wiley_shuffle, the_wolterskluwer_volta,
                the_jci_jig, the_najms_mazurka, the_endo_mambo
            )
            
            # Map dance function names to actual functions
            dance_functions = {
                'the_aaas_tango': the_aaas_tango,
                'the_biochemsoc_saunter': the_biochemsoc_saunter,
                'the_bmc_boogie': the_biomed_calypso,  # BMC uses biomed_calypso
                'the_cell_pogo': the_cell_pogo,
                'the_degruyter_dance': None,  # No dance function found
                'the_dustri_dance': None,     # No dance function found
                'the_endo_dance': the_endo_mambo,  # Endo uses endo_mambo
                'the_jama_dance': the_jama_dance,
                'the_jstage_dive': the_jstage_dive,
                'the_karger_conga': the_karger_conga,
                'the_lancet_tango': the_lancet_tango,
                'the_nature_ballet': the_nature_ballet,
                'the_scielo_chula': the_scielo_chula,
                'the_sciencedirect_disco': the_sciencedirect_disco,
                'the_springer_shag': the_springer_shag,
                'the_spandidos_lambada': the_spandidos_lambada,
                'the_wiley_shuffle': the_wiley_shuffle,
                'the_wolterskluwer_volta': the_wolterskluwer_volta,
                'the_jci_jig': the_jci_jig,
                'the_najms_mazurka': the_najms_mazurka,
            }
            
            dance_func = dance_functions.get(self.dance_function)
            if dance_func:
                log.debug("Calling dance function: %s for journal: %s", 
                         self.dance_function, pma.journal)
                return dance_func(pma, verify=verify)
            else:
                log.warning("Unknown dance function: %s", self.dance_function)
                return None, f"HANDLER_ERROR: Unknown dance function {self.dance_function}"
                
        except ImportError as e:
            log.error("Failed to import dance functions: %s", e)
            return None, f"HANDLER_ERROR: Import failed {e}"
        except Exception as e:
            log.error("Dance function %s failed: %s", self.dance_function, e)
            return None, f"HANDLER_ERROR: {e}"


class PaywallHandler(PublisherHandler):
    """Special handler for paywalled publishers."""
    
    def get_pdf_url(self, pma, verify: bool = True) -> Tuple[Optional[str], Optional[str]]:
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
        self._handler_cache = {}
    
    def get_handler_for_journal(self, journal_name: str) -> Optional[PublisherHandler]:
        """Get appropriate handler for a journal.
        
        Args:
            journal_name: Name of the journal to look up
            
        Returns:
            PublisherHandler instance or None if not found
        """
        # Check cache first
        if journal_name in self._handler_cache:
            return self._handler_cache[journal_name]
        
        # Look up in registry
        publisher_data = self.registry.get_publisher_for_journal(journal_name)
        if not publisher_data:
            return None
        
        # Create handler
        handler = HandlerFactory.create_handler(publisher_data)
        
        # Cache for future use
        self._handler_cache[journal_name] = handler
        
        return handler
    
    def find_pdf_url(self, pma, verify: bool = True) -> Tuple[Optional[str], Optional[str]]:
        """Find PDF URL for a PubMed article using the registry system.
        
        Args:
            pma: PubMedArticle object
            verify: Whether to verify URLs
            
        Returns:
            Tuple of (url, reason)
        """
        from .registry import standardize_journal_name
        
        journal_name = standardize_journal_name(pma.journal)
        handler = self.get_handler_for_journal(journal_name)
        
        if handler:
            return handler.get_pdf_url(pma, verify=verify)
        else:
            return None, f"NOFORMAT: No handler found for journal '{journal_name}'"