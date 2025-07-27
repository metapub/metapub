# Enhanced NCBI Error Handling

## Overview

Metapub now provides intelligent error detection and user-friendly error messages when NCBI services are down or experiencing issues. Instead of cryptic XML parsing errors or connection timeouts, users get clear, actionable guidance.

## What Changed

### Before (Cryptic Errors)
```python
from metapub import PubMedFetcher

fetch = PubMedFetcher()
article = fetch.article_by_pmid(123456)  # When NCBI is down

# Users would see:
# XMLSyntaxError: Opening and ending tag mismatch
# eutils.EutilsNCBIError: Document is empty, line 1, column 1
# ConnectionError: HTTPSConnectionPool(host='eutils.ncbi.nlm.nih.gov'...)
```

### After (User-Friendly Messages)
```python
from metapub import PubMedFetcher
from metapub.ncbi_errors import NCBIServiceError

fetch = PubMedFetcher()

try:
    article = fetch.article_by_pmid(123456)
except NCBIServiceError as e:
    print(e)  # Shows helpful formatted message
```

Output:
```
╔══════════════════════════════════════════════════════════════════════════════╗
║                            NCBI SERVICE ISSUE                               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  NCBI servers are experiencing issues.                                      ║
║                                                                              ║
║  Suggested actions:                                                          ║
║  • NCBI servers are temporarily unavailable                                 ║
║  • This is not an issue with your code or data                              ║
║  • Try again in a few minutes                                               ║
║  • Check NCBI status: https://www.ncbi.nlm.nih.gov/                         ║
║                                                                              ║
║  This is likely a temporary issue with NCBI's servers, not your code.       ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## Enhanced Modules

### PubMedFetcher
- `article_by_pmid()` - Enhanced error detection for article fetching
- `pmids_for_query()` - Better search error handling
- `related_pmids()` - Improved XML parsing error detection

### Convert Module
- `pmid2doi()` - Intelligent conversion error handling
- `doi2pmid()` - Enhanced CrossRef/PubMed integration errors

### Error Types Detected
- **Server Errors** (HTTP 500, 502, 503)
- **Rate Limiting** (HTTP 429)
- **Maintenance Mode** (HTML responses instead of XML)
- **Connection Issues** (timeouts, DNS failures)
- **XML Parsing Errors** (malformed responses)
- **Empty Responses** (service returning no data)

## Integration with Health Check

The error handling integrates seamlessly with the health check utility:

```python
# Errors suggest using the health check
try:
    fetch = PubMedFetcher()
    article = fetch.article_by_pmid(123456)
except NCBIServiceError as e:
    if e.error_type == 'server_error':
        # Error message includes: "Check NCBI service status with: ncbi_health_check --quick"
        pass
```

## Exception Hierarchy

```python
Exception
└── NCBIServiceError  # New exception for service issues
    ├── error_type: str     # 'server_error', 'rate_limit', 'maintenance', etc.
    ├── suggestions: List   # Actionable suggestions for users
    └── user_message: str   # Human-readable error description
```

## Usage Examples

### Basic Error Handling
```python
from metapub import PubMedFetcher
from metapub.ncbi_errors import NCBIServiceError

try:
    fetch = PubMedFetcher()
    article = fetch.article_by_pmid(12345)
    
except NCBIServiceError as e:
    if e.error_type == 'server_error':
        print("NCBI is down, try again later")
    elif e.error_type == 'rate_limit':
        print("Slow down your requests")
    else:
        print(f"Service issue: {e.user_message}")
        
except Exception as e:
    print(f"Other error: {e}")
```

### Conversion with Error Handling
```python
from metapub.convert import pmid2doi
from metapub.ncbi_errors import NCBIServiceError

try:
    doi = pmid2doi(12345)
    print(f"DOI: {doi}")
    
except NCBIServiceError as e:
    print("NCBI service issue detected:")
    for suggestion in e.suggestions:
        print(f"  • {suggestion}")
        
except Exception as e:
    print(f"Other error: {e}")
```

### Checking Service Status Programmatically
```python
from metapub.ncbi_errors import check_ncbi_status

status = check_ncbi_status()
if status.is_available:
    # Proceed with NCBI operations
    fetch = PubMedFetcher()
    article = fetch.article_by_pmid(12345)
else:
    print(f"NCBI unavailable: {status.error_message}")
    # Handle offline mode or show user-friendly message
```

## Benefits

1. **Clearer User Experience** - Users understand when issues are external vs. their code
2. **Actionable Guidance** - Specific suggestions for resolving issues
3. **Reduced Support Burden** - Users can self-diagnose service outages
4. **Better Integration** - Works with health check and test suite
5. **Consistent Messaging** - Uniform error handling across all modules

## Backward Compatibility

- Existing code continues to work unchanged
- Original exceptions still raised for non-service issues
- NCBIServiceError inherits from base Exception
- Optional enhanced error handling via try/except blocks