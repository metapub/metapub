#!/usr/bin/env python3
"""Build journal registry database from YAML publisher configuration files.

This script reads YAML publisher configuration files and builds the SQLite
registry database that FindIt uses for journal lookups.

Usage:
    python scripts/build_registry_from_yaml.py [--output-db PATH] [--yaml-dir PATH]
"""

import os
import sys
import yaml
import sqlite3
import argparse
from pathlib import Path

# When run as a package module, no need to modify path

def create_registry_tables(conn):
    """Create the registry database tables matching existing schema."""
    conn.execute('''
        CREATE TABLE IF NOT EXISTS publishers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            dance_function TEXT NOT NULL,
            format_template TEXT,
            base_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS journals (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            publisher_id INTEGER NOT NULL,
            format_params TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (publisher_id) REFERENCES publishers (id)
        )
    ''')
    
    conn.execute('''
        CREATE INDEX IF NOT EXISTS idx_journals_publisher ON journals (publisher_id)
    ''')
    
    conn.commit()

def load_yaml_config(yaml_path):
    """Load and validate a YAML publisher configuration."""
    with open(yaml_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Basic validation
    if not config.get('publisher', {}).get('id'):
        raise ValueError(f"Missing publisher.id in {yaml_path}")
    
    return config

def insert_publisher(conn, config):
    """Insert publisher data into the database."""
    pub = config['publisher']
    url_patterns = config.get('url_patterns', {})
    
    # Use primary_template or doi_template as format_template
    format_template = url_patterns.get('primary_template') or url_patterns.get('doi_template', '')
    
    cursor = conn.execute('''
        INSERT INTO publishers (name, dance_function, format_template, base_url)
        VALUES (?, ?, ?, ?)
    ''', (
        pub.get('name', pub['id']),
        config.get('dance_function', 'the_doi_slide'),
        format_template,
        ''  # base_url not used in YAML configs
    ))
    
    return cursor.lastrowid

def insert_journals(conn, publisher_rowid, config):
    """Insert journal data into the database."""
    journals_config = config.get('journals', {})
    
    # Handle simple journal lists
    simple_journals = journals_config.get('simple_list', [])
    for journal_name in simple_journals:
        conn.execute('''
            INSERT INTO journals (name, publisher_id, format_params)
            VALUES (?, ?, ?)
        ''', (journal_name, publisher_rowid, None))
    
    # Handle parameterized journals (like BMJ with host configs)
    parameterized = journals_config.get('parameterized', {})
    for journal_name, params in parameterized.items():
        # Convert params dict to JSON string for format_params
        import json
        format_params = json.dumps(params) if params else None
        
        conn.execute('''
            INSERT INTO journals (name, publisher_id, format_params)
            VALUES (?, ?, ?)
        ''', (journal_name, publisher_rowid, format_params))

def build_registry(yaml_dir, output_db):
    """Build the complete registry database from YAML files."""
    yaml_path = Path(yaml_dir)
    
    if not yaml_path.exists():
        raise FileNotFoundError(f"YAML directory not found: {yaml_dir}")
    
    # Create/connect to database
    conn = sqlite3.connect(output_db)
    
    try:
        # Create tables
        create_registry_tables(conn)
        
        # Process all YAML files
        yaml_files = list(yaml_path.glob('*.yaml'))
        if not yaml_files:
            raise ValueError(f"No YAML files found in {yaml_dir}")
        
        total_publishers = 0
        total_journals = 0
        
        for yaml_file in sorted(yaml_files):
            try:
                print(f"Processing {yaml_file.name}...")
                config = load_yaml_config(yaml_file)
                
                # Insert publisher
                publisher_rowid = insert_publisher(conn, config)
                total_publishers += 1
                
                # Insert journals
                before_count = conn.execute('SELECT COUNT(*) FROM journals').fetchone()[0]
                insert_journals(conn, publisher_rowid, config)
                after_count = conn.execute('SELECT COUNT(*) FROM journals').fetchone()[0]
                journals_added = after_count - before_count
                total_journals += journals_added
                
                print(f"  Added {journals_added} journals for {config['publisher']['name']}")
                
            except Exception as e:
                print(f"Error processing {yaml_file}: {e}")
                raise
        
        # Commit all changes
        conn.commit()
        
        print(f"\nRegistry build complete:")
        print(f"  Publishers: {total_publishers}")
        print(f"  Journals: {total_journals}")
        print(f"  Database: {output_db}")
        
        # Verify database integrity
        pub_count = conn.execute('SELECT COUNT(*) FROM publishers').fetchone()[0]
        journal_count = conn.execute('SELECT COUNT(*) FROM journals').fetchone()[0]
        
        print(f"  Verification - Publishers: {pub_count}, Journals: {journal_count}")
        
    finally:
        conn.close()

def main():
    parser = argparse.ArgumentParser(description="Build journal registry from YAML files")
    parser.add_argument('--output-db', 
                       default='metapub/findit/data/registry.db',
                       help='Output SQLite database path')
    parser.add_argument('--yaml-dir', 
                       default='metapub/findit/journals_yaml/publishers',
                       help='Directory containing YAML publisher files')
    
    args = parser.parse_args()
    
    # Ensure output directory exists
    output_dir = os.path.dirname(args.output_db)
    if output_dir:  # Only create directory if there's a directory component
        os.makedirs(output_dir, exist_ok=True)
    
    try:
        build_registry(args.yaml_dir, args.output_db)
        print("Success!")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()