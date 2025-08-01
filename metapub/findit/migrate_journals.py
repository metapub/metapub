#!/usr/bin/env python3
"""Migration script to populate journal registry database from existing journal modules.

This script extracts all journal data from the existing Python modules and populates
the new SQLite-based journal registry database.
"""

import sys
import os
import json
import logging
from pathlib import Path

# Add metapub to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from metapub.findit.registry import JournalRegistry

# Import all the existing journal data
from metapub.findit.journals.aaas import aaas_journals
from metapub.findit.journals.biochemsoc import biochemsoc_journals
from metapub.findit.journals.bmc import BMC_journals
from metapub.findit.journals.cell import cell_journals
from metapub.findit.journals.degruyter import degruyter_journals
from metapub.findit.journals.dustri import dustri_journals
from metapub.findit.journals.endo import endo_journals
from metapub.findit.journals.jama import jama_journals
from metapub.findit.journals.jstage import jstage_journals
from metapub.findit.journals.karger import karger_journals
from metapub.findit.journals.lancet import lancet_journals
from metapub.findit.journals.nature import nature_journals
from metapub.findit.journals.scielo import scielo_journals
from metapub.findit.journals.sciencedirect import sciencedirect_journals
from metapub.findit.journals.springer import springer_journals
from metapub.findit.journals.spandidos import spandidos_journals
from metapub.findit.journals.wiley import wiley_journals
from metapub.findit.journals.wolterskluwer import wolterskluwer_journals

# Import format templates
from metapub.findit.journals.aaas import aaas_format
from metapub.findit.journals.biochemsoc import biochemsoc_format
from metapub.findit.journals.bmc import BMC_format
from metapub.findit.journals.cell import cell_format
from metapub.findit.journals.karger import karger_format
from metapub.findit.journals.nature import nature_format
from metapub.findit.journals.scielo import scielo_format
from metapub.findit.journals.spandidos import spandidos_format

# Import paywalled journals
from metapub.findit.journals.paywalled import (
    schattauer_journals, RSC_journals, thieme_journals, weird_paywall_publishers
)

# Only configure logging if this is run as a script, not when imported
log = logging.getLogger(__name__)

# Track if we've already configured this module's logging to avoid duplicates
_logging_configured = False

# Publisher configurations with their journals and dance functions
PUBLISHER_CONFIGS = [
    {
        'name': 'aaas',
        'dance_function': 'the_aaas_tango',
        'format_template': aaas_format,
        'journals': aaas_journals,
    },
    {
        'name': 'biochemsoc',
        'dance_function': 'the_biochemsoc_saunter', 
        'format_template': biochemsoc_format,
        'journals': biochemsoc_journals,
    },
    {
        'name': 'bmc',
        'dance_function': 'the_bmc_boogie',
        'format_template': BMC_format,
        'journals': BMC_journals,
    },
    {
        'name': 'cell',
        'dance_function': 'the_cell_pogo',
        'format_template': cell_format,
        'journals': cell_journals,
    },
    {
        'name': 'degruyter',
        'dance_function': 'paywall_handler',  # TODO: Implement the_degruyter_dance
        'format_template': None,
        'journals': degruyter_journals,
    },
    {
        'name': 'dustri',
        'dance_function': 'paywall_handler',  # TODO: Implement the_dustri_dance
        'format_template': None,
        'journals': dustri_journals,
    },
    {
        'name': 'endo',
        'dance_function': 'the_endo_mambo',
        'format_template': None,
        'journals': endo_journals,
    },
    {
        'name': 'jama',
        'dance_function': 'the_jama_dance',
        'format_template': None,
        'journals': jama_journals,
    },
    {
        'name': 'jstage',
        'dance_function': 'the_jstage_dive',
        'format_template': None,
        'journals': jstage_journals,
    },
    {
        'name': 'karger',
        'dance_function': 'the_karger_conga',
        'format_template': karger_format,
        'journals': karger_journals,
    },
    {
        'name': 'lancet',
        'dance_function': 'the_lancet_tango',
        'format_template': None,
        'journals': lancet_journals,
    },
    {
        'name': 'nature',
        'dance_function': 'the_nature_ballet',
        'format_template': nature_format,
        'journals': nature_journals,
    },
    {
        'name': 'scielo',
        'dance_function': 'the_scielo_chula',
        'format_template': scielo_format,
        'journals': scielo_journals,
    },
    {
        'name': 'sciencedirect',
        'dance_function': 'the_sciencedirect_disco',
        'format_template': None,
        'journals': sciencedirect_journals,
    },
    {
        'name': 'springer',
        'dance_function': 'the_springer_shag',
        'format_template': None,
        'journals': springer_journals,
    },
    {
        'name': 'spandidos',
        'dance_function': 'the_spandidos_lambada',
        'format_template': spandidos_format,
        'journals': spandidos_journals,
    },
    {
        'name': 'wiley',
        'dance_function': 'the_wiley_shuffle',
        'format_template': None,
        'journals': wiley_journals,
    },
    {
        'name': 'wolterskluwer',
        'dance_function': 'the_wolterskluwer_volta',
        'format_template': None,
        'journals': wolterskluwer_journals,
    },
]

# Special single journals
SPECIAL_JOURNALS = [
    {
        'name': 'jci',
        'dance_function': 'the_jci_jig',
        'journals': ('J Clin Invest',),
    },
    {
        'name': 'najms',
        'dance_function': 'the_najms_mazurka',
        'journals': ('N Am J Med Sci',),
    },
]

# Paywalled publishers
PAYWALL_PUBLISHERS = [
    {
        'name': 'schattauer',
        'dance_function': 'paywall_handler',
        'journals': schattauer_journals,
    },
    {
        'name': 'rsc',
        'dance_function': 'paywall_handler',
        'journals': RSC_journals,
    },
    {
        'name': 'thieme',
        'dance_function': 'paywall_handler',
        'journals': thieme_journals,
    },
    {
        'name': 'weird_paywall',
        'dance_function': 'paywall_handler',
        'journals': weird_paywall_publishers,
    },
]

def extract_journal_info(journals_data):
    """Extract journal names and format parameters from various data structures."""
    journal_list = []
    
    if isinstance(journals_data, dict):
        # Dictionary format like nature_journals
        for journal_name, params in journals_data.items():
            format_params = json.dumps(params) if params else None
            journal_list.append((journal_name, format_params))
    elif isinstance(journals_data, (list, tuple)):
        # Simple list/tuple format
        for journal_name in journals_data:
            journal_list.append((journal_name, None))
    else:
        log.warning("Unknown journal data format: %s", type(journals_data))
    
    return journal_list

def migrate_journals(db_path=None):
    """Migrate all existing journal data to the new registry database."""
    registry = JournalRegistry(db_path)
    
    # Check if database already has data to avoid duplicate migration
    stats = registry.get_stats()
    if stats['publishers'] > 0:
        log.debug("Journal registry already populated (%d publishers, %d journals), skipping migration", 
                 stats['publishers'], stats['journals'])
        registry.close()
        return stats
    
    log.info("Starting journal migration...")
    
    total_publishers = 0
    total_journals = 0
    
    # Migrate main publishers
    for config in PUBLISHER_CONFIGS:
        log.info("Migrating publisher: %s", config['name'])
        
        publisher_id = registry.add_publisher(
            name=config['name'],
            dance_function=config['dance_function'],
            format_template=config.get('format_template'),
        )
        total_publishers += 1
        
        # Extract and add journals
        journals = extract_journal_info(config['journals'])
        for journal_name, format_params in journals:
            registry.add_journal(
                name=journal_name,
                publisher_id=publisher_id,
                format_params=format_params
            )
            total_journals += 1
    
    # Migrate special single journals
    for config in SPECIAL_JOURNALS:
        log.info("Migrating special publisher: %s", config['name'])
        
        publisher_id = registry.add_publisher(
            name=config['name'],
            dance_function=config['dance_function'],
        )
        total_publishers += 1
        
        journals = extract_journal_info(config['journals'])
        for journal_name, format_params in journals:
            registry.add_journal(
                name=journal_name,
                publisher_id=publisher_id,
                format_params=format_params
            )
            total_journals += 1
    
    # Migrate paywalled publishers
    for config in PAYWALL_PUBLISHERS:
        log.info("Migrating paywalled publisher: %s", config['name'])
        
        publisher_id = registry.add_publisher(
            name=config['name'],
            dance_function=config['dance_function'],
        )
        total_publishers += 1
        
        journals = extract_journal_info(config['journals'])
        for journal_name, format_params in journals:
            registry.add_journal(
                name=journal_name,
                publisher_id=publisher_id,
                format_params=format_params
            )
            total_journals += 1
    
    # Get final stats
    stats = registry.get_stats()
    log.info("Migration completed!")
    log.info("Migrated %d publishers, %d journals", total_publishers, total_journals)
    log.info("Database stats: %s", stats)
    
    registry.close()
    return stats

def main():
    """Main entry point for the migration console script."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrate journal data to registry database')
    parser.add_argument('--db-path', help='Path to database file (optional)')
    parser.add_argument('--force', action='store_true', help='Force recreation of database')
    
    args = parser.parse_args()
    
    if args.force and args.db_path and os.path.exists(args.db_path):
        os.remove(args.db_path)
        log.info("Removed existing database: %s", args.db_path)
    
    stats = migrate_journals(args.db_path)
    print(f"Migration completed: {stats}")

def _configure_logging():
    """Configure logging if not already configured."""
    global _logging_configured
    if not _logging_configured:
        logging.basicConfig(level=logging.INFO)
        _logging_configured = True

if __name__ == '__main__':
    # Configure logging only when run as a script
    _configure_logging()
    main()