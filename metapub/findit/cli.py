#!/usr/bin/env python
"""CLI tool for managing the metapub journal registry.

This script provides commands for rebuilding, inspecting, and managing
the journal registry database from YAML configurations.

Generated 100% by Claude Code.
"""

import os
import sys
import argparse
import logging
from pathlib import Path

from .registry import JournalRegistry
from .registry_builder import populate_registry, get_yaml_configs


def setup_logging(verbose=False):
    """Configure logging based on verbosity level."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s %(name)s[%(process)d] %(levelname)s %(message)s'
    )


def cmd_rebuild(args):
    """Rebuild the registry from YAML configurations."""
    print("Rebuilding journal registry from YAML configurations...")

    # Remove existing database if it exists
    if args.db_path:
        db_path = args.db_path
    else:
        # Use shipped registry location by default
        db_path = os.path.join(os.path.dirname(__file__), 'data', 'registry.db')
        print(f"Building shipped registry at: {db_path}")

    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Removed existing database: {db_path}")

    # Create new registry and populate
    registry = JournalRegistry(db_path)

    try:
        publishers_added, journals_added = populate_registry(registry, args.journals_dir)
        print(f"✅ Registry rebuilt successfully!")
        print(f"   Publishers: {publishers_added}")
        print(f"   Journals: {journals_added}")
        print(f"   Database: {db_path}")

    except Exception as error:
        print(f"❌ Registry rebuild failed: {error}")
        sys.exit(1)
    finally:
        registry.close()


def cmd_stats(args):
    """Show registry statistics."""
    registry = JournalRegistry(args.db_path)

    try:
        stats = registry.get_stats()
        print("📊 Journal Registry Statistics")
        print(f"   Publishers: {stats['publishers']}")
        print(f"   Journals: {stats['journals']}")
        print(f"   Aliases: {stats['aliases']}")
        print(f"   Database: {registry.db_path}")

    except Exception as error:
        print(f"❌ Failed to get stats: {error}")
        sys.exit(1)
    finally:
        registry.close()


def cmd_lookup(args):
    """Look up a journal in the registry."""
    registry = JournalRegistry(args.db_path)

    try:
        result = registry.get_publisher_for_journal(args.journal)

        if result:
            print(f"🔍 Found journal: {args.journal}")
            print(f"   Publisher: {result['name']}")
            print(f"   Dance function: {result['dance_function']}")
            if result.get('format_template'):
                print(f"   Format template: {result['format_template']}")
            if result.get('format_params'):
                print(f"   Format params: {result['format_params']}")
        else:
            print(f"❌ Journal not found: {args.journal}")
            sys.exit(1)

    except Exception as error:
        print(f"❌ Lookup failed: {error}")
        sys.exit(1)
    finally:
        registry.close()


def cmd_list_publishers(args):
    """List all publishers in the registry."""
    registry = JournalRegistry(args.db_path)

    try:
        conn = registry._get_connection()
        cursor = conn.execute('SELECT name, dance_function FROM publishers ORDER BY name')

        print("📋 Publishers in registry:")
        for row in cursor.fetchall():
            print(f"   {row[0]} → {row[1]}")

    except Exception as error:
        print(f"❌ Failed to list publishers: {error}")
        sys.exit(1)
    finally:
        registry.close()


def cmd_validate_yaml(args):
    """Validate YAML configurations."""
    print("🔍 Validating YAML configurations...")

    try:
        configs = get_yaml_configs(args.journals_dir)

        errors = []
        warnings = []

        for publisher_id, config in configs.items():
            # Check required sections
            if 'publisher' not in config:
                errors.append(f"{publisher_id}: Missing 'publisher' section")

            if 'url_patterns' not in config:
                warnings.append(f"{publisher_id}: Missing 'url_patterns' section")

            # Check URL patterns structure
            url_patterns = config.get('url_patterns', {})
            if url_patterns and 'primary_template' not in url_patterns:
                warnings.append(f"{publisher_id}: Missing 'primary_template' in url_patterns")

        print(f"✅ Validated {len(configs)} YAML configurations")

        if warnings:
            print(f"⚠️  {len(warnings)} warnings:")
            for warning in warnings:
                print(f"   {warning}")

        if errors:
            print(f"❌ {len(errors)} errors:")
            for error in errors:
                print(f"   {error}")
            sys.exit(1)
        else:
            print("✅ All configurations valid!")

    except Exception as error:
        print(f"❌ Validation failed: {error}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Manage the metapub journal registry database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  metapub-registry rebuild                    # Rebuild registry from YAML
  metapub-registry stats                      # Show registry statistics
  metapub-registry lookup "Nature"            # Look up a journal
  metapub-registry list-publishers            # List all publishers
  metapub-registry validate                   # Validate YAML configs
        """
    )

    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--db-path', type=str,
                       help='Path to registry database (default: cache dir)')
    parser.add_argument('--journals-dir', type=str,
                       help='Path to journals YAML directory (default: embedded)')

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Rebuild command
    rebuild_parser = subparsers.add_parser('rebuild', help='Rebuild registry from YAML')
    rebuild_parser.set_defaults(func=cmd_rebuild)

    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show registry statistics')
    stats_parser.set_defaults(func=cmd_stats)

    # Lookup command
    lookup_parser = subparsers.add_parser('lookup', help='Look up a journal')
    lookup_parser.add_argument('journal', help='Journal name to look up')
    lookup_parser.set_defaults(func=cmd_lookup)

    # List publishers command
    list_parser = subparsers.add_parser('list-publishers', help='List all publishers')
    list_parser.set_defaults(func=cmd_list_publishers)

    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate YAML configurations')
    validate_parser.set_defaults(func=cmd_validate_yaml)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    setup_logging(args.verbose)
    args.func(args)


if __name__ == '__main__':
    main()
