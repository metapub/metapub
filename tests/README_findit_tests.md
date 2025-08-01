# FindIt Test Suite Documentation

This document describes the comprehensive test suite for the FindIt system, including the new handler-based architecture implemented in issue #92.

## Test Files

### `test_findit.py`
Original FindIt tests with new comprehensive publisher testing:
- Basic FindIt functionality (caching, backup URLs, supported journals)
- Publisher-specific tests for Oxford, Nature, Springer, Science journals
- Handler system integration tests
- Publisher coverage verification

### `test_findit_handlers.py`
Dedicated tests for the new handler system:
- `PublisherHandler` base class functionality
- `PaywallHandler` specialized behavior
- `HandlerFactory` creation logic
- `RegistryBackedLookupSystem` core functionality
- Registry integration tests
- Live PMID testing with real network calls

### `test_findit_dances.py`
Existing dance function tests (legacy system compatibility)

## Running Tests

### Run All FindIt Tests
```bash
python -m pytest tests/test_findit*.py -v
```

### Run Tests Without Network Calls
```bash
export SKIP_NETWORK_TESTS=1
python -m pytest tests/test_findit*.py -v
```

### Run Only Handler System Tests
```bash
python -m pytest tests/test_findit_handlers.py -v
```

### Run Specific Test Categories
```bash
# Only unit tests (no network)
python -m pytest tests/test_findit_handlers.py::TestPublisherHandler tests/test_findit_handlers.py::TestPaywallHandler tests/test_findit_handlers.py::TestHandlerFactory -v

# Only integration tests (requires network)
python -m pytest tests/test_findit_handlers.py::TestRegistryIntegration -v

# Only live tests with real PMIDs (requires network)
python -m pytest tests/test_findit_handlers.py::TestLiveHandlerBehavior -v
```

## Skipping Network Tests

Network-dependent tests can be skipped by setting the `SKIP_NETWORK_TESTS` environment variable:

```bash
export SKIP_NETWORK_TESTS=1
```

This will skip:
- Tests that make actual HTTP requests to publishers
- Tests that require real PMID lookups
- Tests that verify URLs are accessible
- Registry integration tests that seed from remote sources

### Why Skip Network Tests?

1. **CI/CD Environments**: Avoid rate limiting and network dependency issues
2. **Offline Development**: Work on code without internet access
3. **Fast Test Runs**: Focus on core logic without network overhead
4. **Publisher Rate Limits**: Prevent excessive requests to journal websites

## Test Data Sources

### Sample PMIDs
Tests use real PMIDs from the `output/publishers_clean/` directory:

- **Oxford University Press**: 860 PMIDs from 507 journals
- **Nature Publishing Group**: 209 PMIDs from 109 journals  
- **Springer**: 3366 PMIDs from 1889 journals
- **Other Publishers**: Wiley, Science/AAAS, BMJ, etc.

### Test Coverage
The comprehensive test suite covers:

1. **Handler System Architecture**
   - Publisher handler creation and caching
   - Dance function dispatching
   - Registry-backed lookups
   - Paywall detection

2. **Publisher-Specific Logic**
   - Oxford Academic journals (VIP format)
   - Nature Publishing Group (nature.com format)
   - Springer journals (springer.com format)
   - Science/AAAS journals (sciencemag.org format)

3. **Error Handling**
   - Unknown journals
   - Network failures
   - Malformed URLs
   - Paywall responses

4. **Backwards Compatibility**
   - Legacy dance functions still work
   - Existing FindIt API unchanged
   - Cache behavior preserved

## Expected Test Results

### Without Network (Unit Tests Only)
```
tests/test_findit_handlers.py::TestPublisherHandler ✓ (3 tests)
tests/test_findit_handlers.py::TestPaywallHandler ✓ (2 tests)  
tests/test_findit_handlers.py::TestHandlerFactory ✓ (3 tests)
tests/test_findit_handlers.py::TestRegistryBackedLookupSystem ✓ (4 tests)
```

### With Network (Full Test Suite)
```
tests/test_findit.py ✓ (10+ tests including publisher-specific)
tests/test_findit_handlers.py ✓ (15+ tests including integration)
tests/test_findit_dances.py ✓ (existing dance function tests)
```

## Troubleshooting

### Common Issues

1. **Network Tests Failing**: Set `SKIP_NETWORK_TESTS=1` or check internet connection
2. **Registry Database Missing**: First run will seed SQLite database automatically
3. **Rate Limiting**: Reduce concurrent test runs or add delays between requests
4. **PMID Not Found**: Some test PMIDs may become unavailable over time

### Performance Considerations

- Handler system uses caching to minimize registry lookups
- Network tests are limited to 1-2 PMIDs per publisher to avoid overloading
- Registry seeding happens once and is cached in SQLite database

## Contributing Test Cases

When adding new publishers or dance functions:

1. Add sample PMIDs to appropriate test data
2. Create publisher-specific test methods
3. Test both success and failure cases
4. Ensure tests can be skipped with `SKIP_NETWORK_TESTS`
5. Document any special handling requirements

## Test Architecture Benefits

The new test architecture provides:

- **Comprehensive Coverage**: Tests both old and new systems
- **Network Flexibility**: Can run with or without internet
- **Publisher Validation**: Verifies real-world functionality
- **Regression Protection**: Ensures changes don't break existing functionality
- **Performance Testing**: Validates caching and lookup efficiency