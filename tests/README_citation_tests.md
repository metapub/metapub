# Citation HTML Formatting Test Coverage

This directory contains comprehensive test coverage for the HTML citation formatting functionality that was restored in metapub. The testing is organized into three complementary test files that provide multiple layers of protection against regressions.

## Test Files Overview

### 1. `test_citation_formatting.py` (6 tests)
**Basic functionality tests** - Core testing of the citation formatting features
- Author formatting (HTML vs plain text)
- Article citation formatting (HTML vs plain text) 
- PubMedArticle.citation_html method integration
- Book citation formatting (basic)

### 2. `test_html_citation_protection.py` (14 tests)
**Comprehensive protection tests** - Deep testing of all edge cases and HTML functionality
- HTML format string validation
- Exact HTML tag placement verification
- Tag structure and balance validation
- Edge cases (empty values, None values, special characters)
- Format string injection protection
- Integration tests with real PubMed data
- Backwards compatibility verification
- Consistency across citation functions

### 3. `test_citation_html_regression.py` (8 tests)
**Regression prevention tests** - Specific tests based on the GitHub issue requirements
- Exact format requirements from the original GitHub issue
- MaveDB integration requirements testing
- PyPI installation compatibility verification
- "et al" HTML formatting protection
- Format string structure validation
- HTML escaping behavior verification

## Coverage Summary

**Total Tests: 28**
- ✅ All tests passing
- 🛡️ Full protection against HTML formatting regressions
- 🔧 Edge case handling verified
- 🌐 Integration with real PubMed data tested
- 📚 Both article and book citation formats covered

## Key Protected Requirements

The test suite specifically protects these critical requirements:

1. **Journal names** must be wrapped in `<i>` tags
2. **Volume numbers** must be wrapped in `<b>` tags  
3. **"et al"** must be wrapped in `<i>` tags
4. **Book titles** must be wrapped in `<i>` tags
5. **Plain citations** must never contain HTML tags
6. **HTML formatting** only applies when `as_html=True`
7. **Backwards compatibility** with existing code that doesn't use HTML
8. **Tag balance** ensuring properly formed HTML
9. **Special character handling** without breaking HTML structure
10. **Security** against format string injection attacks

## Running the Tests

```bash
# Run all citation tests
python -m pytest tests/test_citation*.py tests/test_html_citation*.py -v

# Run specific test files
python -m pytest tests/test_citation_formatting.py -v
python -m pytest tests/test_html_citation_protection.py -v  
python -m pytest tests/test_citation_html_regression.py -v

# Run with coverage
python -m pytest tests/test_citation*.py tests/test_html_citation*.py --cov=metapub.cite
```

## Test Philosophy

This test suite follows a **defense in depth** strategy:

- **Basic tests** ensure core functionality works
- **Protection tests** verify edge cases and comprehensive functionality  
- **Regression tests** ensure specific requirements from the GitHub issue are maintained

The tests are designed to catch regressions early and provide clear failure messages that indicate exactly what HTML formatting requirement was broken.

## Future Maintenance

When modifying citation functionality:

1. Run the full test suite to ensure no regressions
2. Add new tests to the appropriate file based on the type of change
3. Update this README if new test categories are added
4. Ensure any new HTML formatting features are thoroughly tested

The test suite provides a safety net that allows confident refactoring and enhancement of the citation system while maintaining the HTML formatting functionality that applications like MaveDB depend on.