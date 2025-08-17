#!/usr/bin/env python3
"""
Database utilities for FindIt coverage testing.

This module provides PostgreSQL database connection management and common
database operations for the PMID tracking system.
"""

import os
import sys
import logging
import json
import psycopg2
import psycopg2.extras
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

# Add parent directory to sys.path for metapub imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class DatabaseConfig:
    """Database configuration management."""
    
    def __init__(self):
        # Use Unix socket by default (like psql), fallback to localhost if specified
        self.host = os.getenv('FINDIT_DB_HOST', '/var/run/postgresql')
        self.port = int(os.getenv('FINDIT_DB_PORT', '5432'))
        self.database = os.getenv('FINDIT_DB_NAME', 'findit_coverage')
        self.user = os.getenv('FINDIT_DB_USER', os.getenv('USER', 'nthmost'))
        self.password = os.getenv('FINDIT_DB_PASSWORD', '')
        
        # Connection pool settings
        self.min_connections = int(os.getenv('FINDIT_DB_MIN_CONN', '1'))
        self.max_connections = int(os.getenv('FINDIT_DB_MAX_CONN', '10'))
    
    def get_connection_string(self) -> str:
        """Get PostgreSQL connection string."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    def get_connection_params(self) -> Dict[str, Any]:
        """Get connection parameters as dictionary."""
        return {
            'host': self.host,
            'port': self.port,
            'database': self.database,
            'user': self.user,
            'password': self.password
        }


class DatabaseManager:
    """PostgreSQL database manager for FindIt coverage testing."""
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        self.config = config or DatabaseConfig()
        self.logger = logging.getLogger(__name__)
        self._connection = None
    
    def connect(self) -> psycopg2.extensions.connection:
        """Establish database connection."""
        try:
            connection = psycopg2.connect(**self.config.get_connection_params())
            connection.autocommit = False
            self.logger.debug(f"Connected to database: {self.config.database}")
            return connection
        except psycopg2.Error as e:
            self.logger.error(f"Database connection failed: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = None
        try:
            conn = self.connect()
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
    @contextmanager
    def get_cursor(self, connection=None):
        """Context manager for database cursors."""
        if connection:
            cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            try:
                yield cursor
            finally:
                cursor.close()
        else:
            with self.get_connection() as conn:
                cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                try:
                    yield cursor
                    conn.commit()
                except Exception:
                    conn.rollback()
                    raise
                finally:
                    cursor.close()
    
    def execute_sql_file(self, sql_file_path: str) -> None:
        """Execute SQL commands from a file."""
        sql_path = Path(sql_file_path)
        if not sql_path.exists():
            raise FileNotFoundError(f"SQL file not found: {sql_file_path}")
        
        with open(sql_path, 'r') as f:
            sql_content = f.read()
        
        with self.get_connection() as conn:
            with self.get_cursor(conn) as cursor:
                cursor.execute(sql_content)
                conn.commit()
        
        self.logger.info(f"Executed SQL file: {sql_file_path}")
    
    def initialize_database(self) -> None:
        """Initialize database schema."""
        schema_path = Path(__file__).parent.parent / "sql" / "schema.sql"
        self.execute_sql_file(str(schema_path))
        self.logger.info("Database schema initialized")
    
    def test_connection(self) -> bool:
        """Test database connection."""
        try:
            with self.get_connection() as conn:
                with self.get_cursor(conn) as cursor:
                    cursor.execute("SELECT 1")
                    return cursor.fetchone() is not None
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False


class PMIDResultsManager:
    """Manager for PMID results operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.logger = logging.getLogger(__name__)
    
    def upsert_pmid_result(self, pmid: str, **kwargs) -> None:
        """Insert or update a PMID result."""
        # Build the UPDATE SET clause dynamically
        update_fields = []
        values = [pmid]
        placeholder_idx = 2
        
        for field, value in kwargs.items():
            if value is not None:
                # Handle CURRENT_TIMESTAMP specially
                if value == 'CURRENT_TIMESTAMP':
                    update_fields.append(f"{field} = CURRENT_TIMESTAMP")
                # Handle JSONB fields
                elif field == 'other_identifiers' and isinstance(value, dict):
                    update_fields.append(f"{field} = %s")
                    values.append(json.dumps(value))
                    placeholder_idx += 1
                else:
                    update_fields.append(f"{field} = %s")
                    values.append(value)
                    placeholder_idx += 1
        
        if not update_fields:
            return  # Nothing to update
        
        sql = f"""
        INSERT INTO pmid_results (pmid) VALUES (%s)
        ON CONFLICT (pmid) DO UPDATE SET
        {', '.join(update_fields)},
        updated_at = CURRENT_TIMESTAMP
        """
        
        with self.db.get_cursor() as cursor:
            cursor.execute(sql, values)
    
    def get_pmid_result(self, pmid: str) -> Optional[Dict[str, Any]]:
        """Get PMID result by PMID."""
        sql = "SELECT * FROM pmid_results WHERE pmid = %s"
        
        with self.db.get_cursor() as cursor:
            cursor.execute(sql, (pmid,))
            result = cursor.fetchone()
            return dict(result) if result else None
    
    def get_pmids_by_status(self, status_field: str, status_value: str) -> List[str]:
        """Get PMIDs with specific status."""
        sql = f"SELECT pmid FROM pmid_results WHERE {status_field} = %s"
        
        with self.db.get_cursor() as cursor:
            cursor.execute(sql, (status_value,))
            return [row['pmid'] for row in cursor.fetchall()]
    
    def get_processable_pmids_for_pass2(self, list_id: int) -> List[str]:
        """Get PMIDs from a specific list that are ready for pass2 processing.
        
        This is much faster than the old approach of loading all PMIDs and checking each one.
        """
        sql = """
        SELECT plm.pmid 
        FROM pmid_list_members plm
        JOIN pmid_results pr ON plm.pmid = pr.pmid
        WHERE plm.list_id = %s 
        AND pr.pass1_status = 'success'
        AND (pr.pass2_status IS NULL OR pr.pass2_status NOT IN ('pdf_url_found', 'no_pdf_url', 'no_pdf_link', 'findit_error', 'no_article'))
        ORDER BY plm.position
        """
        
        with self.db.get_cursor() as cursor:
            cursor.execute(sql, (list_id,))
            return [row['pmid'] for row in cursor.fetchall()]
    
    def get_processable_pmids_for_pass3(self, list_id: int) -> List[str]:
        """Get PMIDs from a specific list that are ready for pass3 processing."""
        sql = """
        SELECT plm.pmid 
        FROM pmid_list_members plm
        JOIN pmid_results pr ON plm.pmid = pr.pmid
        WHERE plm.list_id = %s 
        AND pr.pass2_status = 'pdf_url_found'
        AND pr.pdf_url IS NOT NULL
        AND (pr.pass3_status IS NULL OR pr.pass3_status NOT IN ('verified', 'failed', 'error'))
        ORDER BY plm.position
        """
        
        with self.db.get_cursor() as cursor:
            cursor.execute(sql, (list_id,))
            return [row['pmid'] for row in cursor.fetchall()]
    
    def update_pass_status(self, pmid: str, pass_num: int, status: str, 
                          completed_at: Optional[str] = None, error: Optional[str] = None) -> None:
        """Update pass status for a PMID."""
        updates = {
            f'pass{pass_num}_status': status,
            f'pass{pass_num}_completed_at': completed_at or 'CURRENT_TIMESTAMP'
        }
        
        if error:
            updates[f'pass{pass_num}_error'] = error
        
        self.upsert_pmid_result(pmid, **updates)
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Get overall processing statistics."""
        with self.db.get_cursor() as cursor:
            cursor.execute("SELECT * FROM pmid_summary")
            return dict(cursor.fetchone())
    
    def get_publisher_statistics(self) -> List[Dict[str, Any]]:
        """Get publisher-specific statistics."""
        with self.db.get_cursor() as cursor:
            cursor.execute("SELECT * FROM publisher_stats ORDER BY total_articles DESC")
            return [dict(row) for row in cursor.fetchall()]


class PMIDListManager:
    """Manager for PMID list operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.logger = logging.getLogger(__name__)
    
    def create_pmid_list(self, name: str, description: str = None, 
                        file_path: str = None) -> int:
        """Create a new PMID list and return its ID."""
        sql = """
        INSERT INTO pmid_lists (name, description, file_path, total_pmids)
        VALUES (%s, %s, %s, 0)
        RETURNING id
        """
        
        with self.db.get_cursor() as cursor:
            cursor.execute(sql, (name, description, file_path))
            return cursor.fetchone()['id']
    
    def load_pmid_list_from_file(self, list_id: int, file_path: str) -> int:
        """Load PMIDs from file into database and return count."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PMID file not found: {file_path}")
        
        pmids = []
        with open(file_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line and not line.startswith('#'):
                    pmids.append((list_id, line, line_num))
        
        if not pmids:
            raise ValueError("No PMIDs found in file")
        
        # Insert PMIDs into results table if they don't exist
        pmid_values = [(pmid,) for _, pmid, _ in pmids]
        with self.db.get_cursor() as cursor:
            # Insert PMIDs into pmid_results (will be ignored if already exist)
            cursor.executemany(
                "INSERT INTO pmid_results (pmid) VALUES (%s) ON CONFLICT (pmid) DO NOTHING",
                pmid_values
            )
            
            # Insert into pmid_list_members
            cursor.executemany(
                "INSERT INTO pmid_list_members (list_id, pmid, position) VALUES (%s, %s, %s)",
                pmids
            )
            
            # Update total count
            cursor.execute(
                "UPDATE pmid_lists SET total_pmids = %s WHERE id = %s",
                (len(pmids), list_id)
            )
        
        self.logger.info(f"Loaded {len(pmids)} PMIDs from {file_path}")
        return len(pmids)
    
    def get_pmid_list(self, list_id: int) -> List[str]:
        """Get PMIDs for a list in order."""
        sql = """
        SELECT pmid FROM pmid_list_members 
        WHERE list_id = %s 
        ORDER BY position
        """
        
        with self.db.get_cursor() as cursor:
            cursor.execute(sql, (list_id,))
            return [row['pmid'] for row in cursor.fetchall()]
    
    def get_pmid_list_info(self, list_id: int) -> Optional[Dict[str, Any]]:
        """Get PMID list metadata."""
        sql = "SELECT * FROM pmid_lists WHERE id = %s"
        
        with self.db.get_cursor() as cursor:
            cursor.execute(sql, (list_id,))
            result = cursor.fetchone()
            return dict(result) if result else None
    
    def list_pmid_lists(self) -> List[Dict[str, Any]]:
        """List all PMID lists."""
        sql = "SELECT * FROM pmid_lists ORDER BY created_at DESC"
        
        with self.db.get_cursor() as cursor:
            cursor.execute(sql)
            return [dict(row) for row in cursor.fetchall()]
    
    def delete_pmid_list(self, list_id: int) -> bool:
        """
        Delete a PMID list and all associated data.
        
        Args:
            list_id: ID of the list to delete
            
        Returns:
            True if list was deleted, False if list didn't exist
        """
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                # Check if list exists
                cursor.execute("SELECT id FROM pmid_lists WHERE id = %s", (list_id,))
                if not cursor.fetchone():
                    return False
                
                # Delete in reverse dependency order
                # 1. Delete from processing_runs
                cursor.execute("DELETE FROM processing_runs WHERE list_id = %s", (list_id,))
                
                # 2. Delete from pmid_list_members
                cursor.execute("DELETE FROM pmid_list_members WHERE list_id = %s", (list_id,))
                
                # 3. Delete the list itself
                cursor.execute("DELETE FROM pmid_lists WHERE id = %s", (list_id,))
                
                conn.commit()
                self.logger.info(f"Deleted PMID list {list_id} and all associated data")
                return True
    
    def delete_pmid_list_by_name(self, name: str) -> bool:
        """
        Delete a PMID list by name.
        
        Args:
            name: Name of the list to delete
            
        Returns:
            True if list was deleted, False if list didn't exist
        """
        with self.db.get_cursor() as cursor:
            cursor.execute("SELECT id FROM pmid_lists WHERE name = %s", (name,))
            result = cursor.fetchone()
            if not result:
                return False
            
            return self.delete_pmid_list(result['id'])


class MeshTermManager:
    """Manager for MeSH term operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.logger = logging.getLogger(__name__)
    
    def store_mesh_terms(self, pmid: str, mesh_terms: List[Dict[str, Any]]) -> None:
        """Store MeSH terms for a PMID."""
        if not mesh_terms:
            return
        
        # Insert mesh terms
        mesh_values = []
        for term in mesh_terms:
            mesh_values.append((
                pmid,
                term['mesh_id'],
                term['mesh_term'],
                term['is_major_topic'],
                term['qualifier'],
                term['qualifier_major_topic']
            ))
        
        with self.db.get_cursor() as cursor:
            # Clear existing mesh terms for this PMID
            cursor.execute("DELETE FROM mesh_terms WHERE pmid = %s", (pmid,))
            
            # Insert new mesh terms
            cursor.executemany("""
                INSERT INTO mesh_terms (pmid, mesh_id, mesh_term, is_major_topic, qualifier, qualifier_major_topic)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (pmid, mesh_id, qualifier) DO UPDATE SET
                mesh_term = EXCLUDED.mesh_term,
                is_major_topic = EXCLUDED.is_major_topic,
                qualifier_major_topic = EXCLUDED.qualifier_major_topic
            """, mesh_values)
    
    def get_mesh_terms(self, pmid: str) -> List[Dict[str, Any]]:
        """Get MeSH terms for a PMID."""
        sql = """
        SELECT mesh_id, mesh_term, is_major_topic, qualifier, qualifier_major_topic
        FROM mesh_terms 
        WHERE pmid = %s
        ORDER BY mesh_term, qualifier
        """
        
        with self.db.get_cursor() as cursor:
            cursor.execute(sql, (pmid,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_mesh_statistics(self) -> Dict[str, Any]:
        """Get overall MeSH statistics."""
        with self.db.get_cursor() as cursor:
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT pmid) as articles_with_mesh,
                    COUNT(*) as total_mesh_assignments,
                    COUNT(DISTINCT mesh_term) as unique_mesh_terms,
                    COUNT(CASE WHEN is_major_topic THEN 1 END) as major_topic_assignments,
                    COUNT(CASE WHEN qualifier IS NOT NULL THEN 1 END) as qualified_assignments
                FROM mesh_terms
            """)
            return dict(cursor.fetchone())


class ProcessingRunManager:
    """Manager for processing run tracking."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.logger = logging.getLogger(__name__)
    
    def start_processing_run(self, list_id: int, pass_type: str, 
                           start_index: int = 0, end_index: int = None) -> int:
        """Start a new processing run and return its ID."""
        sql = """
        INSERT INTO processing_runs 
        (list_id, pass_type, start_index, end_index, status)
        VALUES (%s, %s, %s, %s, 'running')
        RETURNING id
        """
        
        with self.db.get_cursor() as cursor:
            cursor.execute(sql, (list_id, pass_type, start_index, end_index))
            return cursor.fetchone()['id']
    
    def update_processing_run(self, run_id: int, **kwargs) -> None:
        """Update processing run status."""
        update_fields = []
        values = []
        
        for field, value in kwargs.items():
            update_fields.append(f"{field} = %s")
            values.append(value)
        
        if not update_fields:
            return
        
        values.append(run_id)
        sql = f"""
        UPDATE processing_runs 
        SET {', '.join(update_fields)}
        WHERE id = %s
        """
        
        with self.db.get_cursor() as cursor:
            cursor.execute(sql, values)
    
    def complete_processing_run(self, run_id: int, status: str = 'completed') -> None:
        """Mark processing run as completed."""
        sql = """
        UPDATE processing_runs 
        SET status = %s, completed_at = CURRENT_TIMESTAMP
        WHERE id = %s
        """
        
        with self.db.get_cursor() as cursor:
            cursor.execute(sql, (status, run_id))


def setup_logger(name: str, log_file: str, level: int = logging.INFO) -> logging.Logger:
    """Set up logger for database operations."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # File handler
    log_path = Path(__file__).parent.parent / "log" / log_file
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


if __name__ == "__main__":
    # Test database connection
    import argparse
    
    parser = argparse.ArgumentParser(description="Database utilities for FindIt coverage")
    parser.add_argument("--init", action="store_true", help="Initialize database schema")
    parser.add_argument("--test", action="store_true", help="Test database connection")
    args = parser.parse_args()
    
    logger = setup_logger("database", "database.log")
    db_manager = DatabaseManager()
    
    if args.init:
        print("Initializing database schema...")
        try:
            db_manager.initialize_database()
            print("Database schema initialized successfully!")
        except Exception as e:
            print(f"Failed to initialize database: {e}")
            sys.exit(1)
    
    if args.test:
        print("Testing database connection...")
        if db_manager.test_connection():
            print("Database connection successful!")
        else:
            print("Database connection failed!")
            sys.exit(1)
    
    if not args.init and not args.test:
        parser.print_help()