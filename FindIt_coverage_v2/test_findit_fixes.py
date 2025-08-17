#!/usr/bin/env python3
"""
Quick test script to verify FindIt fixes.
"""

import sys
from pathlib import Path

# Add parent directory to sys.path for metapub imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_dance_imports():
    """Test that all dance functions can be imported without errors."""
    try:
        from metapub.findit.dances import (
            the_doi_slide, 
            the_vip_shake, 
            the_vip_shake_nonstandard,  # This should now work
            the_vip_nonstandard_shake
        )
        print("✅ All dance functions imported successfully")
        
        # Test that the alias works
        assert the_vip_shake_nonstandard == the_vip_nonstandard_shake
        print("✅ Backward compatibility alias working")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_registry_access():
    """Test that registry access works."""
    try:
        from metapub.findit.registry import JournalRegistry
        registry = JournalRegistry()
        
        # Try to get a common publisher
        info = registry.get_publisher_for_journal('nature')
        print(f"✅ Registry access working - found: {info.get('name') if info else 'None'}")
        
        registry.close()
        return True
    except Exception as e:
        print(f"❌ Registry error: {e}")
        return False

if __name__ == '__main__':
    print("Testing FindIt fixes...")
    
    success = True
    success &= test_dance_imports()
    success &= test_registry_access()
    
    if success:
        print("\n🎉 All tests passed! FindIt fixes look good.")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed.")
        sys.exit(1)