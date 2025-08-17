#!/usr/bin/env python3
"""
Test for registry and dance function consistency.

This test catches systematic mismatches between:
- Dance functions defined in metapub/findit/dances/ modules
- Dance function assignments in metapub/findit/journals/*.yaml files  
- Dance function assignments in the registry database

This test would have caught the YAML dance function mismatches that were
manually discovered and fixed in August 2025.
"""

import pytest
import sys
import os
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent.absolute()))

from metapub.findit.registry import JournalRegistry
import metapub.findit.dances as dance_module
import yaml

class TestRegistryDanceConsistency:
    """Test that registry configuration matches available dance functions."""
    
    def test_all_dance_functions_exist(self):
        """Test that all dance functions referenced in YAML files actually exist."""
        registry = JournalRegistry()
        
        # Get all available dance functions
        available_functions = set()
        for attr_name in dir(dance_module):
            if attr_name.startswith('the_') and callable(getattr(dance_module, attr_name)):
                available_functions.add(attr_name)
        
        # Check each publisher in the registry
        conn = registry._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT name, dance_function FROM publishers WHERE is_active = 1")
        publishers = cursor.fetchall()
        
        missing_functions = []
        for publisher_name, dance_function in publishers:
            if dance_function not in available_functions:
                missing_functions.append((publisher_name, dance_function))
        
        registry.close()
        
        if missing_functions:
            error_msg = "Publishers with non-existent dance functions:\\n"
            for publisher, func in missing_functions:
                error_msg += f"  - {publisher}: {func}\\n"
            pytest.fail(error_msg)
    
    def test_dedicated_functions_are_used(self):
        """Test that publishers with dedicated dance functions actually use them."""
        
        # Map of publisher names to their expected dedicated functions
        # This would be the authoritative list based on what functions exist
        expected_dedicated_functions = {
            'jama': 'the_jama_dance',
            'Wolterskluwer': 'the_wolterskluwer_volta', 
            'Cambridge': 'the_cambridge_foxtrot',
            'Jstage': 'the_jstage_dive',
            'acm': 'the_acm_reel',
            'Rsc': 'the_rsc_reaction',
            'Scirp': 'the_scirp_timewarp',
            'Asm': 'the_asm_shimmy',
            'Brill': 'the_brill_bridge',
            'Plos': 'the_plos_pogo',
            'Dustri': 'the_dustri_polka',
            'Oatext': 'the_oatext_orbit',
            'Aacr': 'the_aacr_jitterbug',
            'Wjgnet': 'the_wjgnet_wave',
            'Projectmuse': 'the_projectmuse_syrtos',
            'inderscience': 'the_inderscience_ula',
            'annualreviews': 'the_annualreviews_round',
            'Hilaris': 'the_hilaris_hop',
            'Oxford': 'the_oxford_academic_foxtrot',
            'Ingentaconnect': 'the_ingenta_flux',
            'Karger': 'the_karger_conga',
            'jci': 'the_jci_jig',
            'Allenpress': 'the_allenpress_advance',
            'asme': 'the_asme_animal',
            'bmj': 'the_bmj_bump',
            'Aha': 'the_aha_waltz',
            'nature': 'the_nature_ballet',
            'dovepress': 'the_dovepress_peacock',
            'Scielo': 'the_scielo_chula',
            'Walshmedia': 'the_walshmedia_bora',
            'Iop': 'the_iop_fusion',
            'sciencedirect': 'the_sciencedirect_disco',
            'Mdpi': 'the_mdpi_moonwalk',
            'Longdom': 'the_longdom_hustle',
            'aaas': 'the_aaas_twist',
            'Science Magazine': 'the_aaas_twist',
        }
        
        registry = JournalRegistry()
        
        mismatches = []
        for publisher_name, expected_function in expected_dedicated_functions.items():
            conn = registry._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT dance_function FROM publishers WHERE name = ?", (publisher_name,))
            result = cursor.fetchone()
            
            if result:
                actual_function = result[0]
                if actual_function != expected_function:
                    mismatches.append((publisher_name, expected_function, actual_function))
            else:
                mismatches.append((publisher_name, expected_function, "PUBLISHER NOT FOUND"))
        
        registry.close()
        
        if mismatches:
            error_msg = "Publishers not using their dedicated dance functions:\\n"
            for publisher, expected, actual in mismatches:
                error_msg += f"  - {publisher}: expected '{expected}', got '{actual}'\\n"
            pytest.fail(error_msg)
    
    def test_yaml_registry_consistency(self):
        """Test that YAML files and registry database are consistent."""
        
        yaml_dir = Path("metapub/findit/journals")
        registry = JournalRegistry()
        
        inconsistencies = []
        
        for yaml_file in yaml_dir.glob("*.yaml"):
            if yaml_file.name == "schema.yaml":
                continue
                
            try:
                with open(yaml_file, 'r') as f:
                    yaml_data = yaml.safe_load(f)
                
                if not yaml_data or 'dance_function' not in yaml_data:
                    continue
                    
                yaml_dance = yaml_data['dance_function']
                publisher_name = yaml_data.get('publisher', {}).get('name', yaml_file.stem)
                
                # Check registry database
                conn = registry._get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT dance_function FROM publishers WHERE name = ?", (publisher_name,))
                result = cursor.fetchone()
                
                if result:
                    db_dance = result[0]
                    if yaml_dance != db_dance:
                        inconsistencies.append((yaml_file.name, publisher_name, yaml_dance, db_dance))
                else:
                    inconsistencies.append((yaml_file.name, publisher_name, yaml_dance, "NOT IN DB"))
                    
            except Exception as e:
                inconsistencies.append((yaml_file.name, "ERROR", str(e), ""))
        
        registry.close()
        
        if inconsistencies:
            error_msg = "YAML and database inconsistencies:\\n"
            for yaml_file, publisher, yaml_dance, db_dance in inconsistencies:
                error_msg += f"  - {yaml_file} ({publisher}): YAML='{yaml_dance}', DB='{db_dance}'\\n"
            pytest.fail(error_msg)
    
    def test_registry_integration_end_to_end(self):
        """Test end-to-end registry integration for a sample of publishers."""
        
        # Test cases: (journal_name, expected_publisher, expected_dance)
        test_cases = [
            ('JAMA', 'jama', 'the_jama_dance'),
            ('Medicine (Baltimore)', 'Wolterskluwer', 'the_wolterskluwer_volta'),
            ('PLoS One', 'Plos', 'the_plos_pogo'),
            ('Nature', 'nature', 'the_nature_ballet'),
            ('BMJ Open', 'bmj', 'the_bmj_bump'),
        ]
        
        registry = JournalRegistry()
        
        failures = []
        for journal_name, expected_publisher, expected_dance in test_cases:
            try:
                publisher_info = registry.get_publisher_for_journal(journal_name)
                
                if not publisher_info:
                    failures.append(f"{journal_name}: NOT FOUND in registry")
                    continue
                
                actual_publisher = publisher_info['name']
                actual_dance = publisher_info['dance_function']
                
                if actual_publisher != expected_publisher:
                    failures.append(f"{journal_name}: expected publisher '{expected_publisher}', got '{actual_publisher}'")
                
                if actual_dance != expected_dance:
                    failures.append(f"{journal_name}: expected dance '{expected_dance}', got '{actual_dance}'")
                    
            except Exception as e:
                failures.append(f"{journal_name}: ERROR - {e}")
        
        registry.close()
        
        if failures:
            error_msg = "End-to-end registry integration failures:\\n" + "\\n".join(f"  - {f}" for f in failures)
            pytest.fail(error_msg)

if __name__ == "__main__":
    # Run the tests
    test_class = TestRegistryDanceConsistency()
    
    print("Running registry consistency tests...")
    
    try:
        test_class.test_all_dance_functions_exist()
        print("✓ All dance functions exist")
    except Exception as e:
        print(f"❌ Dance function existence test failed: {e}")
    
    try:
        test_class.test_dedicated_functions_are_used()
        print("✓ Dedicated functions are used correctly")
    except Exception as e:
        print(f"❌ Dedicated function usage test failed: {e}")
    
    try:
        test_class.test_yaml_registry_consistency()
        print("✓ YAML and registry are consistent")
    except Exception as e:
        print(f"❌ YAML/registry consistency test failed: {e}")
    
    try:
        test_class.test_registry_integration_end_to_end()
        print("✓ End-to-end integration works")
    except Exception as e:
        print(f"❌ End-to-end integration test failed: {e}")