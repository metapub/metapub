# FindIt Registry Database

This directory contains the pre-populated journal registry database that ships with metapub.

## Architecture

**Shipped Registry Database:**
- `registry.db` - SQLite database containing 68 publishers and 13,047+ journals
- Pre-populated and version-controlled for consistent deployments
- Works in all environments (containers, CI/CD, read-only systems)

## How It Works

1. **Default Behavior**: JournalRegistry automatically uses the shipped database
2. **Fallback**: If shipped DB missing, falls back to cache directory  
3. **Development**: Use `migrate_journals.py` to regenerate registry.db

## Database Contents

- **Publishers**: 68 publishers with dance functions
- **Journals**: 13,047 journal entries with publisher associations  
- **Coverage**: 97.1% of FindIt publishers have verified PMIDs for testing

## Benefits

✅ **Reliability**: Always works, no runtime setup required  
✅ **Consistency**: All users get identical registry data  
✅ **Deployment-Friendly**: Works in containers and restricted environments  
✅ **Performance**: No startup time for registry population  
✅ **Predictable**: No "registry not found" errors  

## Developer Notes

To update the shipped registry:
1. Run `metapub-registry rebuild` (builds directly to data/registry.db)
2. Commit the updated registry.db file

**CLI Commands:**
- `metapub-registry rebuild` - Rebuild registry from YAML configurations
- `metapub-registry stats` - Show registry statistics  
- `metapub-registry validate` - Validate YAML configurations

The shipped registry ensures metapub works out-of-the-box for all users.