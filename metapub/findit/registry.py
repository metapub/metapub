"""Journal Registry - Database-backed journal and publisher management for FindIt.

This module replaces the static journal lists with a SQLite-backed registry system
that can efficiently handle thousands of journals with lazy loading and caching.
"""

import sqlite3
import logging
import os
from typing import Optional, Dict, Tuple, List
from ..config import DEFAULT_CACHE_DIR
from ..cache_utils import get_cache_path

log = logging.getLogger('metapub.findit.registry')

REGISTRY_DB_FILENAME = 'journal_registry.db'

class JournalRegistry:
    """Database-backed journal registry with lazy loading and caching."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize the journal registry.
        
        Args:
            db_path: Path to the SQLite database. If None, uses shipped database.
        """
        if db_path is None:
            # Use shipped registry database by default
            shipped_db_path = os.path.join(os.path.dirname(__file__), 'data', 'registry.db')
            if os.path.exists(shipped_db_path):
                db_path = shipped_db_path
                log.debug(f"Using shipped registry database: {db_path}")
            else:
                # Fallback to cache directory for development/migration
                db_path = get_cache_path(DEFAULT_CACHE_DIR, REGISTRY_DB_FILENAME)
                log.warning(f"Shipped registry not found, using cache: {db_path}")
        
        self.db_path = db_path
        self._conn = None
        self._ensure_database()
        
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection, creating if needed."""
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
        return self._conn
    
    def _ensure_database(self):
        """Create database tables if they don't exist and auto-populate if empty."""
        conn = self._get_connection()
        
        # Publishers table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS publishers (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                dance_function TEXT NOT NULL,
                format_template TEXT,
                base_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Journals table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS journals (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                publisher_id INTEGER NOT NULL,
                format_params TEXT,  -- JSON string for format parameters
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (publisher_id) REFERENCES publishers (id)
            )
        ''')
        
        # Journal aliases for alternate names/abbreviations
        conn.execute('''
            CREATE TABLE IF NOT EXISTS journal_aliases (
                id INTEGER PRIMARY KEY,
                journal_id INTEGER NOT NULL,
                alias_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (journal_id) REFERENCES journals (id),
                UNIQUE(alias_name)
            )
        ''')
        
        # Create indexes for fast lookups
        conn.execute('CREATE INDEX IF NOT EXISTS idx_journals_name ON journals (name)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_journal_aliases_name ON journal_aliases (alias_name)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_publishers_name ON publishers (name)')
        
        conn.commit()
        log.debug('Journal registry database initialized at %s', self.db_path)
        
        # Auto-populate if database is empty and not using shipped database
        if not self._is_using_shipped_database():
            self._auto_populate_if_empty()
    
    def _is_using_shipped_database(self) -> bool:
        """Check if we're using the shipped registry database."""
        shipped_db_path = os.path.join(os.path.dirname(__file__), 'data', 'registry.db')
        return os.path.abspath(self.db_path) == os.path.abspath(shipped_db_path)
    
    def _auto_populate_if_empty(self):
        """Auto-populate database from embedded journal modules if empty.
        
        This ensures that PyPI-installed packages work out of the box without
        requiring users to manually run migration scripts.
        """
        conn = self._get_connection()
        
        # Check if database is empty
        publisher_count = conn.execute('SELECT COUNT(*) FROM publishers').fetchone()[0]
        
        if publisher_count == 0:
            log.info('Empty journal registry detected - auto-populating from embedded data')
            try:
                self._populate_from_embedded_modules()
                log.info('Auto-population completed successfully')
            except Exception as error:
                log.error('Auto-population failed: %s', error)
                # Don't raise - allow system to continue with empty database
                # Users can still manually run migration if needed
    
    def _populate_from_embedded_modules(self):
        """Populate database from the embedded journal module data.
        
        This is a simplified version of the migration script that runs
        automatically when the database is empty.
        """
        # Import the migration logic
        try:
            from .migrate_journals import PUBLISHER_CONFIGS, SPECIAL_JOURNALS, PAYWALL_PUBLISHERS
            from .migrate_journals import extract_journal_info
            
            total_publishers = 0
            total_journals = 0
            
            # Migrate main publishers
            for config in PUBLISHER_CONFIGS:
                publisher_id = self.add_publisher(
                    name=config['name'],
                    dance_function=config['dance_function'],
                    format_template=config.get('format_template'),
                )
                total_publishers += 1
                
                # Extract and add journals
                journals = extract_journal_info(config['journals'])
                for journal_name, format_params in journals:
                    self.add_journal(
                        name=journal_name,
                        publisher_id=publisher_id,
                        format_params=format_params
                    )
                    total_journals += 1
            
            # Migrate special single journals
            for config in SPECIAL_JOURNALS:
                publisher_id = self.add_publisher(
                    name=config['name'],
                    dance_function=config['dance_function'],
                )
                total_publishers += 1
                
                journals = extract_journal_info(config['journals'])
                for journal_name, format_params in journals:
                    self.add_journal(
                        name=journal_name,
                        publisher_id=publisher_id,
                        format_params=format_params
                    )
                    total_journals += 1
            
            # Migrate paywalled publishers
            for config in PAYWALL_PUBLISHERS:
                publisher_id = self.add_publisher(
                    name=config['name'],
                    dance_function=config['dance_function'],
                )
                total_publishers += 1
                
                journals = extract_journal_info(config['journals'])
                for journal_name, format_params in journals:
                    self.add_journal(
                        name=journal_name,
                        publisher_id=publisher_id,
                        format_params=format_params
                    )
                    total_journals += 1
            
            log.debug('Auto-populated %d publishers and %d journals', 
                     total_publishers, total_journals)
                     
        except ImportError as error:
            log.warning('Could not import migration data for auto-population: %s', error)
            raise
        except Exception as error:
            log.error('Error during auto-population: %s', error)
            raise
    
    def get_publisher_for_journal(self, journal_name: str) -> Optional[Dict]:
        """Get publisher information for a journal name.
        
        Args:
            journal_name: The journal name or abbreviation to look up.
            
        Returns:
            Dictionary with publisher info (name, dance_function, format_template) or None.
        """
        conn = self._get_connection()
        
        # First try direct journal name match
        cursor = conn.execute('''
            SELECT p.name, p.dance_function, p.format_template, p.base_url, j.format_params
            FROM journals j
            JOIN publishers p ON j.publisher_id = p.id
            WHERE j.name = ?
        ''', (journal_name,))
        
        result = cursor.fetchone()
        if result:
            return dict(result)
        
        # Try alias match
        cursor = conn.execute('''
            SELECT p.name, p.dance_function, p.format_template, p.base_url, j.format_params
            FROM journal_aliases ja
            JOIN journals j ON ja.journal_id = j.id
            JOIN publishers p ON j.publisher_id = p.id
            WHERE ja.alias_name = ?
        ''', (journal_name,))
        
        result = cursor.fetchone()
        if result:
            return dict(result)
        
        return None
    
    def add_publisher(self, name: str, dance_function: str, 
                     format_template: str = None, base_url: str = None) -> int:
        """Add a new publisher to the registry.
        
        Args:
            name: Publisher name
            dance_function: Name of the dance function to call
            format_template: URL format template (optional)
            base_url: Base URL for the publisher (optional)
            
        Returns:
            Publisher ID
        """
        conn = self._get_connection()
        cursor = conn.execute('''
            INSERT OR REPLACE INTO publishers (name, dance_function, format_template, base_url)
            VALUES (?, ?, ?, ?)
        ''', (name, dance_function, format_template, base_url))
        conn.commit()
        return cursor.lastrowid
    
    def add_journal(self, name: str, publisher_id: int, 
                   format_params: str = None, aliases: List[str] = None) -> int:
        """Add a new journal to the registry.
        
        Args:
            name: Journal name/abbreviation
            publisher_id: ID of the publisher
            format_params: JSON string of format parameters (optional)
            aliases: List of alternate names for this journal (optional)
            
        Returns:
            Journal ID
        """
        conn = self._get_connection()
        
        # Insert journal
        cursor = conn.execute('''
            INSERT OR REPLACE INTO journals (name, publisher_id, format_params)
            VALUES (?, ?, ?)
        ''', (name, publisher_id, format_params))
        journal_id = cursor.lastrowid
        
        # Insert aliases if provided
        if aliases:
            for alias in aliases:
                conn.execute('''
                    INSERT OR REPLACE INTO journal_aliases (journal_id, alias_name)
                    VALUES (?, ?)
                ''', (journal_id, alias))
        
        conn.commit()
        return journal_id
    
    def get_all_journals(self) -> List[str]:
        """Get all journal names in the registry."""
        conn = self._get_connection()
        cursor = conn.execute('SELECT name FROM journals ORDER BY name')
        return [row[0] for row in cursor.fetchall()]
    
    def get_stats(self) -> Dict[str, int]:
        """Get registry statistics."""
        conn = self._get_connection()
        
        publishers_count = conn.execute('SELECT COUNT(*) FROM publishers').fetchone()[0]
        journals_count = conn.execute('SELECT COUNT(*) FROM journals').fetchone()[0]
        aliases_count = conn.execute('SELECT COUNT(*) FROM journal_aliases').fetchone()[0]
        
        return {
            'publishers': publishers_count,
            'journals': journals_count,
            'aliases': aliases_count
        }
    
    def close(self):
        """Close database connection."""
        if hasattr(self, '_conn') and self._conn:
            self._conn.close()
            self._conn = None
    
    def __del__(self):
        """Cleanup database connection."""
        if hasattr(self, '_conn'):
            self.close()


def standardize_journal_name(journal_name: str) -> str:
    """Standardize journal name for consistent lookups.
    
    This function normalizes journal names by:
    - Stripping whitespace
    - Converting common abbreviations
    - Handling special cases
    
    Args:
        journal_name: Raw journal name from PubMed
        
    Returns:
        Standardized journal name
    """
    if not journal_name:
        return journal_name
    
    # Basic cleanup
    name = journal_name.strip()
    
    # Handle common PubMed variations
    # Add more normalizations as needed
    replacements = {
        'J.': 'J',
        'Am.': 'Am',
        'Br.': 'Br',
        'Int.': 'Int',
    }
    
    for old, new in replacements.items():
        name = name.replace(old, new)
    
    return name