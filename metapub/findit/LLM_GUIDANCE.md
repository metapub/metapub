# LLM Guidance for FindIt Development

This document provides guidance for AI assistants working on the FindIt system, based on project requirements and user preferences established during development.

## Core Philosophy

### Trust the Registry System
- **DO**: Trust that journal registry mappings are correct
- **DON'T**: Add artificial restrictions in dance functions that second-guess the registry
- **WHY**: The journal registry is the authoritative source for which dance function should handle which journal

### DOI Prefix Restrictions
- **DO**: Remove or avoid DOI prefix restrictions in dance functions
- **DON'T**: Validate DOI prefixes against expected publisher patterns
- **WHY**: Publishers acquire other publishers and inherit their DOI prefixes. Cambridge might publish journals with `10.1192/`, `10.1353/`, or other prefixes due to acquisitions.

### Error Handling Philosophy
- **DO**: Use structured error messages with attempted URLs
- **DO**: Follow the pattern: `"ERROR_TYPE: Description - attempted: {url}"`
- **Examples**:
  - `"MISSING: DOI required for Cambridge University Press journals - attempted: none"`
  - `"PAYWALL: Cambridge article requires subscription - attempted: {pdf_url}"`
  - `"TXERROR: Network error accessing publisher - attempted: {pdf_url}"`

### Configuration Trust Philosophy
- **DO**: Trust that registry configuration is complete and correct
- **DO**: Let code fail fast with clear errors when configuration is missing
- **DON'T**: Use defensive programming to "handle" missing configuration
- **WHY**: If a dance function exists, the configuration MUST exist. Missing config is a bug to fix, not a runtime condition to handle gracefully.

### Dance Function Design
- **DO**: Keep dance functions focused on URL construction and verification
- **DO**: Provide fallback mechanisms when possible (e.g., PMC for paywalled content)
- **DO**: Use a unique dance name for each publisher every time we're inventing a new dance.
- **DO**: Access registry data directly without defensive checks (e.g., `templates['primary'][0]['template']`)
- **DO**: Let KeyError/IndexError exceptions surface when configuration is incomplete
- **DON'T**: Make assumptions about what DOI prefixes a publisher "should" use
- **DON'T**: Reject articles based on DOI format unless absolutely required for URL construction
- **DON'T**: Use `if not config:` or similar defensive patterns for configuration that MUST exist

## Testing Guidelines

### Test Coverage
- **DO**: Test PMIDs from different eras (1990s, 2010s, 2020s) to ensure historical compatibility
- **DO**: Test edge cases like missing DOIs, network errors, paywalls
- **DO**: Include tests for different DOI prefixes within the same publisher
- **DON'T**: Assume all articles from a publisher will have the same DOI prefix

### Test Organization
- **DO**: Consolidate related tests in `tests/findit/`
- **DO**: Remove redundant test files after consolidating functionality
- **DO**: Use descriptive test names that indicate what publisher/scenario is being tested

## Code Organization

### File Structure
- **DO**: Keep publisher-specific journal lists in `metapub/findit/journals/{publisher}.yaml`
- **DO**: Document URL patterns and dance function mappings in journal files

### CLEANUP Directory
- **DO**: Remove scripts from CLEANUP/ once functionality is integrated into main codebase
- **DON'T**: Leave development/analysis scripts in CLEANUP indefinitely
- **DO**: Clean up after completing major integrations

## Publisher Integration Process

### Adding New Publishers
1. Analyze URL patterns across multiple articles
2. Create dance function with proper error handling
3. Create journal list in appropriate format
4. Add comprehensive tests across different time periods
5. Integrate with registry system
6. Clean up development scripts
7. Create 3 tests for each publisher "dance" using 3 PMIDs with different outcomes (if possible).

### Registry Integration
- **DO**: Add publishers with `add_publisher()` first, then add journals
- **DO**: Use the returned publisher_id when adding journals
- **DO**: Handle existing publisher/journal cases gracefully
- **DON'T**: Assume publishers or journals don't already exist in registry

## Documentation

### Reports and Analysis
- **DO**: Place any *.md reports in the `update_reports/` directory
- **DO**: Document findings, decisions, and integration steps
- **DO**: Keep python function and class docstrings updated per actual behavior.
- **DON'T**: Create documentation files unless explicitly requested

### Code Comments
- **DO**: Update docstrings to reflect actual behavior (e.g., "various DOI prefixes due to acquisitions")
- **DON'T**: Add unnecessary code comments unless asked
- **DO**: Keep function documentation accurate and helpful

## Network and Verification

### URL Verification
- **DO**: Provide `verify=False` option for fast URL construction without network calls
- **DO**: Handle network timeouts and errors gracefully
- **DON'T**: Make network calls during unit tests unless necessary

### Fallback Mechanisms
- **DO**: Provide meaningful error messages when fallbacks aren't available
- **DO**: Log attempted URLs even when they fail

## Common Pitfalls to Avoid

1. **DOI Prefix Assumptions**: Don't assume publishers only use one DOI prefix
2. **Registry Overwrites**: Don't create publisher entries without checking if they exist
3. **Test Data Accuracy**: Verify that test PMIDs actually belong to the expected publisher
4. **Overly Restrictive Validation**: Let the registry determine routing, not artificial restrictions
5. **Incomplete Error Messages**: Always include attempted URLs in error messages
6. **Defensive Programming**: Don't use `if not config:` checks for configuration that MUST exist
7. **False Robustness**: Don't hide configuration bugs behind graceful error handling

## Code Examples

### ❌ **Bad Pattern - Defensive Programming:**
```python
# DON'T DO THIS
publisher_config = registry.get_publisher_config('aha')
if not publisher_config:
    raise NoPDFLink('MISSING: AHA publisher not found in registry')

url_template = publisher_config.get('format_template')
if not url_template:
    # Try alternative approach...
    if not url_template:
        raise NoPDFLink('MISSING: No URL template found')

journal_params = registry.get_journal_params(jrnl)  
if not journal_params:
    raise NoPDFLink('MISSING: Journal not found')

host = journal_params.get('host')
if not host:
    raise NoPDFLink('MISSING: Host parameter not found')
```

### ✅ **Good Pattern - Trust and Fail Fast:**
```python
# DO THIS INSTEAD
# Get configuration - MUST exist or it's a config bug
registry = JournalRegistry()
templates = registry.get_url_templates('aha')
journal_params = registry.get_journal_parameters('aha', jrnl)

# Use primary template - MUST exist for this dance to be valid
url_template = templates['primary'][0]['template']
host = journal_params['host']  # Will fail fast with KeyError if missing

# Construct URL
url = url_template.format(host=host, volume=pma.volume, issue=pma.issue, first_page=pma.first_page)
```

### **Why This is Better:**
- **Fail Fast**: Real configuration problems surface immediately as clear KeyErrors
- **No False Robustness**: Stops pretending missing config is a runtime condition  
- **Cleaner Code**: Focus on logic, not defensive nonsense
- **Easier Debugging**: Clear tracebacks point to actual problems
- **Confidence**: If the dance exists, the config MUST exist

## Decision Making Framework

When faced with design decisions:

1. **Trust the Registry**: If the registry says a journal belongs to a publisher, trust it
2. **Err on the Side of Permissiveness**: Better to attempt URL construction than reject based on assumptions
3. **Provide Meaningful Errors**: Users need to understand why PDF retrieval failed
4. **Test Thoroughly**: Cover different eras, DOI formats, and edge cases
5. **Clean Up After Yourself**: Remove development artifacts once integration is complete
6. **Fail Fast on Config Issues**: Let missing configuration cause immediate, clear errors

