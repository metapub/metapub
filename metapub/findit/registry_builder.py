"""Registry Builder - Populates journal registry from YAML configurations.

This module provides the core functionality for building and populating the
journal registry database from YAML configuration files. It's used by the
registry system for auto-population when the database is empty.
"""

import os
import yaml
import glob
import json
import logging
from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path

log = logging.getLogger(__name__)


def get_yaml_configs(journals_dir: Optional[str] = None) -> Dict[str, Dict]:
    """Load all YAML configuration files from the journals directory.
    
    Args:
        journals_dir: Path to journals directory. If None, uses default location.
        
    Returns:
        Dictionary mapping publisher_id -> config data
    """
    if journals_dir is None:
        journals_dir = os.path.join(os.path.dirname(__file__), 'journals')
    
    configs = {}
    yaml_pattern = os.path.join(journals_dir, '*.yaml')
    
    for yaml_file in glob.glob(yaml_pattern):
        publisher_id = Path(yaml_file).stem
        
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                
            if config and 'publisher' in config:
                configs[publisher_id] = config
                log.debug(f"Loaded config for {publisher_id}")
            else:
                log.warning(f"Invalid config format in {yaml_file}")
                
        except (yaml.YAMLError, IOError) as error:
            log.error(f"Error loading {yaml_file}: {error}")
    
    log.info(f"Loaded {len(configs)} YAML configurations")
    return configs


def extract_publisher_info(publisher_id: str, config: Dict) -> Dict[str, Any]:
    """Extract publisher information from YAML config.
    
    Args:
        publisher_id: Publisher identifier
        config: YAML configuration dictionary
        
    Returns:
        Dictionary with publisher data for registry
    """
    publisher_section = config.get('publisher', {})
    url_patterns = config.get('url_patterns', {})
    
    # Determine dance function - check both publisher section and top level
    dance_function = (publisher_section.get('dance_function') or 
                     config.get('dance_function'))
    if not dance_function:
        # Fallback based on publisher ID
        dance_function = f"the_{publisher_id}_dance"
    
    # Get primary template
    format_template = url_patterns.get('primary_template')
    
    # Store complex configuration as JSON
    config_data = {
        'url_patterns': url_patterns,
        'metadata': config.get('metadata', {}),
    }
    
    return {
        'name': publisher_section.get('name', publisher_id),
        'dance_function': dance_function,
        'format_template': format_template,
        'config_data': json.dumps(config_data),
        'notes': f"Auto-generated from {publisher_id}.yaml"
    }


def extract_journal_info(config: Dict) -> List[Tuple[str, Dict]]:
    """Extract journal information from YAML config.
    
    Args:
        config: YAML configuration dictionary
        
    Returns:
        List of (journal_name, format_params) tuples
    """
    journals = []
    journal_section = config.get('journals', {})
    
    # Handle parameterized journals
    if 'parameterized' in journal_section:
        for journal_name, params in journal_section['parameterized'].items():
            journals.append((journal_name, params))
    
    # Handle simple list journals
    if 'simple_list' in journal_section:
        for journal_name in journal_section['simple_list']:
            journals.append((journal_name, {}))
    
    return journals


def populate_registry(registry, journals_dir: Optional[str] = None) -> Tuple[int, int]:
    """Populate registry from YAML configurations.
    
    Args:
        registry: JournalRegistry instance to populate
        journals_dir: Path to journals directory
        
    Returns:
        Tuple of (publishers_added, journals_added)
    """
    configs = get_yaml_configs(journals_dir)
    
    publishers_added = 0
    journals_added = 0
    
    for publisher_id, config in configs.items():
        try:
            # Extract and add publisher
            publisher_info = extract_publisher_info(publisher_id, config)
            
            publisher_db_id = registry.add_publisher(
                name=publisher_info['name'],
                dance_function=publisher_info['dance_function'],
                format_template=publisher_info.get('format_template'),
                config_data=publisher_info.get('config_data'),
                notes=publisher_info.get('notes')
            )
            
            publishers_added += 1
            log.debug(f"Added publisher: {publisher_id} (ID: {publisher_db_id})")
            
            # Extract and add journals
            journal_list = extract_journal_info(config)
            
            for journal_name, format_params in journal_list:
                registry.add_journal(
                    name=journal_name,
                    publisher_id=publisher_db_id,
                    format_params=json.dumps(format_params) if format_params else None
                )
                journals_added += 1
                
            log.debug(f"Added {len(journal_list)} journals for {publisher_id}")
            
        except Exception as error:
            log.error(f"Error processing {publisher_id}: {error}")
            continue
    
    log.info(f"Registry population complete: {publishers_added} publishers, {journals_added} journals")
    return publishers_added, journals_added


# Legacy compatibility - provide the expected interface
PUBLISHER_CONFIGS = {}  # Will be populated dynamically from YAML

def extract_journal_info_legacy(publisher_name: str) -> List[Tuple[str, Dict]]:
    """Legacy interface for journal extraction."""
    configs = get_yaml_configs()
    if publisher_name in configs:
        return extract_journal_info(configs[publisher_name])
    return []