# FindIt Dance Tests

This directory contains publisher-specific tests for FindIt dance functions, 
organized for better maintainability and testing granularity.

## Directory Structure

```
tests/findit/
├── README.md                           # This file
├── __init__.py                         # Package marker
├── common.py                           # Common test utilities and base classes
├── all_dances.py                       # Master import file (non-discoverable by pytest)
└── test_[publisher].py                 # Individual publisher test files
```

## Publisher Test Files

Each publisher has its own dedicated test file following the naming pattern `test_[publisher].py`:

- `test_aaas.py` - AAAS (Science) journals
- `test_bentham.py` - Bentham Science Publishers (EurekaSelect.com)
- `test_cambridge.py` - Cambridge University Press
- `test_jama.py` - JAMA network journals
- `test_jci.py` - Journal of Clinical Investigation
- `test_jstage.py` - J-STAGE (Japanese journals)
- `test_liebert.py` - Mary Ann Liebert Publishers
- `test_lww.py` - LWW platform (Lippincott Williams & Wilkins)
- `test_mdpi.py` - MDPI (Multidisciplinary Digital Publishing Institute)
- `test_nature.py` - Nature Publishing Group
- `test_pmc.py` - PMC (PubMed Central) access
- `test_sage.py` - SAGE Publications
- `test_scielo.py` - SciELO (Scientific Electronic Library Online)
- `test_thieme.py` - Thieme Medical Publishers
- `test_wolterskluwer.py` - Wolters Kluwer

## Running Tests

### All Dance Tests
```bash
# Run all FindIt dance tests
pytest tests/findit/

# Run with verbose output
pytest tests/findit/ -v
```

### Individual Publisher Tests
```bash
# Test specific publisher
pytest tests/findit/test_bentham.py -v

# Test multiple specific publishers
pytest tests/findit/test_bentham.py tests/findit/test_sage.py -v
```

### Test Categories
```bash
# Run tests for a specific test method pattern
pytest tests/findit/ -k "paywall" -v

# Run tests but skip known broken ones
pytest tests/findit/ -v --tb=short
```

## Common Test Infrastructure

The `common.py` file provides:

- `BaseDanceTest` - Base class for all dance tests with common utilities
- `assertUrlOrReason()` - Assert that FindIt source has either URL or reason
- `assertNoFormatError()` - Assert that source doesn't have NOFORMAT error
- Logging configuration for all tests

## Test Structure

Each publisher test file follows this structure:

```python
from .common import BaseDanceTest
from metapub import FindIt

class TestPublisherDance(BaseDanceTest):
    \"\"\"Test cases for Publisher Name.\"\"\"
    
    def test_publisher_function(self):
        \"\"\"Test publisher-specific functionality.\"\"\"
        pmid = 'example_pmid'
        source = FindIt(pmid=pmid)
        # Test assertions...
```

## Migration from Original Structure

The original `test_findit_dances.py` has been refactored into this publisher-specific structure for:

- **Better organization** - Each publisher's tests are isolated
- **Easier maintenance** - Changes to one publisher don't affect others
- **Parallel testing** - Individual publishers can be tested independently
- **Clearer debugging** - Test failures are easier to trace to specific publishers
- **Scalability** - New publishers can be added without modifying existing tests
- **No test duplication** - Individual test files run once (not duplicated via imports)

## Test Discovery

**Important**: The `all_dances.py` file was renamed from `test_all_dances.py` to prevent pytest from discovering and running the same tests twice. Pytest automatically discovers any file starting with `test_*`, which would cause imported test classes to run in addition to their individual files.

## Adding New Publishers

To add tests for a new publisher:

1. Create `test_[publisher].py`
2. Import `BaseDanceTest` from `common.py`
3. Create test class inheriting from `BaseDanceTest`
4. Add publisher import to `test_all_dances.py`
5. Update this README

Example:
```python
from .common import BaseDanceTest
from metapub import FindIt

class TestNewPublisherDance(BaseDanceTest):
    \"\"\"Test cases for New Publisher.\"\"\"
    
    def test_new_publisher_dance(self):
        \"\"\"Test new publisher dance function.\"\"\"
        # Test implementation
```
