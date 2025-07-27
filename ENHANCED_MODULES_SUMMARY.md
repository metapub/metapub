# Enhanced Error Handling - Complete Module Coverage

## Overview

All major metapub classes now have intelligent error detection and user-friendly error messages when NCBI services are down or experiencing issues.

## Enhanced Modules ✅

### 1. **PubMedFetcher** (`metapub/pubmedfetcher.py`)
- **Methods Enhanced**: `article_by_pmid()`, `pmids_for_query()`, `get_uids_from_esearch_result()`, `parse_related_pmids_result()`
- **Error Types**: Server errors, XML parsing, connection issues, rate limiting
- **Service URLs**: EFetch, ESearch, ELink, ESummary

### 2. **MedGenFetcher** (`metapub/medgenfetcher.py`) 
- **Methods Enhanced**: `uids_by_term()`, `uid_for_cui()`, `concept_by_uid()`
- **Error Types**: MedGen search failures, concept lookup errors
- **Service URLs**: MedGen ESearch, ESummary

### 3. **ClinVarFetcher** (`metapub/clinvarfetcher.py`)
- **Methods Enhanced**: `get_accession()` (more methods could be enhanced)
- **Error Types**: ClinVar database access issues
- **Service URLs**: ClinVar ESearch, ESummary, EFetch

### 4. **Convert Module** (`metapub/convert.py`)
- **Functions Enhanced**: `pmid2doi()`, `doi2pmid()`
- **Error Types**: Conversion failures, CrossRef integration issues
- **Integration**: Works with both NCBI and CrossRef services

### 5. **PubMed Central** (`metapub/pubmedcentral.py`)
- **Functions Enhanced**: `_pmc_id_conversion_api()` (base function for all ID conversions)
- **Error Types**: PMC ID conversion API failures
- **Service URLs**: PMC ID Conversion API

### 6. **CrossRef Fetcher** (`metapub/crossref.py`)
- **Methods Enhanced**: `article_by_doi()` (basic network error handling)
- **Error Types**: Network/connection issues (not NCBI-specific)
- **Service URLs**: CrossRef REST API

## Error Handling Features

### 🎯 **Intelligent Detection**
- **Server Errors**: HTTP 500, 502, 503, 504
- **Rate Limiting**: HTTP 429 responses  
- **Maintenance Mode**: HTML responses instead of XML
- **Connection Issues**: Timeouts, DNS failures
- **XML Parsing**: Malformed responses, empty documents
- **Service-Specific**: Down pages, API errors

### 📱 **User-Friendly Messages**
```
╔══════════════════════════════════════════════════════════════════════════════╗
║                            NCBI SERVICE ISSUE                                ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Unable to fetch PMID 123456: NCBI servers are experiencing issues.          ║
║                                                                              ║
║  Suggested actions:                                                          ║
║  • NCBI servers are temporarily unavailable                                  ║
║  • Try again in a few minutes                                                ║
║  • Check NCBI status: https://www.ncbi.nlm.nih.gov/                          ║
║  • Use ncbi_health_check --quick to diagnose issues                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

### 🔗 **Seamless Integration**
- **Health Check**: Errors suggest using `ncbi_health_check --quick`
- **Test Suite**: Works with automatic test skipping
- **Backward Compatibility**: Existing code continues to work
- **Consistent API**: Same error handling pattern across modules

## Exception Hierarchy

```python
Exception
├── NCBIServiceError           # New: Service-related issues
│   ├── error_type: str       # 'server_error', 'rate_limit', etc.
│   ├── suggestions: List     # Actionable user guidance
│   └── user_message: str     # Human-readable description
├── MetaPubError              # Existing: Logic/validation errors
├── InvalidPMID               # Existing: Invalid identifiers
└── BaseXMLError              # Existing: XML structure issues
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
    # Handle service issues gracefully
    print(f"Service issue: {e.error_type}")
    for suggestion in e.suggestions:
        print(f"  • {suggestion}")
        
except Exception as e:
    # Handle other errors (invalid PMID, etc.)
    print(f"Other error: {e}")
```

### Multi-Module Usage
```python
from metapub import PubMedFetcher
from metapub.medgenfetcher import MedGenFetcher
from metapub.convert import pmid2doi
from metapub.ncbi_errors import NCBIServiceError

def robust_literature_search(term):
    try:
        # All these calls now have enhanced error handling
        fetch = PubMedFetcher()
        pmids = fetch.pmids_for_query(term)
        
        mg = MedGenFetcher()
        concepts = mg.uids_by_term(term)
        
        dois = [pmid2doi(pmid) for pmid in pmids[:5]]
        
        return {'pmids': pmids, 'concepts': concepts, 'dois': dois}
        
    except NCBIServiceError as e:
        # Single exception type handles all NCBI service issues
        return {'error': f"NCBI services unavailable: {e.user_message}"}
```

### Error Type Handling
```python
try:
    # Any metapub operation
    result = some_metapub_function()
    
except NCBIServiceError as e:
    if e.error_type == 'server_error':
        # Server is down, try again later
        schedule_retry()
    elif e.error_type == 'rate_limit':
        # Slow down requests
        add_delay()
    elif e.error_type == 'maintenance':
        # Service in maintenance mode
        use_cached_data()
    else:
        # Other service issue
        log_error(e)
```

## Benefits

### 👥 **User Experience**
- **Clear Communication**: Users understand service vs. code issues
- **Actionable Guidance**: Specific steps to resolve problems
- **Reduced Confusion**: No more cryptic XML parsing errors
- **Professional Feel**: Enterprise-level error handling

### 🛠️ **Developer Experience** 
- **Easier Debugging**: Clear distinction between service and logic errors
- **Consistent API**: Same error handling pattern across modules
- **Better Logging**: Structured error information for monitoring
- **Graceful Degradation**: Applications can handle outages elegantly

### 🏢 **Operations**
- **Reduced Support**: Users can self-diagnose service issues
- **Better Monitoring**: Structured error data for analytics
- **Service Integration**: Works with health check and test utilities
- **Proactive Communication**: Users know when to check service status

## Files Modified

1. **`metapub/ncbi_errors.py`** - Core error detection system (new)
2. **`metapub/pubmedfetcher.py`** - Enhanced with intelligent errors
3. **`metapub/medgenfetcher.py`** - Enhanced with intelligent errors  
4. **`metapub/clinvarfetcher.py`** - Enhanced with intelligent errors
5. **`metapub/convert.py`** - Enhanced conversion functions
6. **`metapub/pubmedcentral.py`** - Enhanced ID conversion API
7. **`metapub/crossref.py`** - Basic network error improvements

## Future Enhancements

### Potential Additions
- **More ClinVarFetcher methods** - Additional methods could be enhanced
- **Advanced retry logic** - Automatic retries with backoff
- **Service-specific health checks** - Individual database monitoring
- **Error analytics** - Collect anonymized error patterns
- **Custom error handlers** - Allow applications to register custom handlers

### Integration Opportunities
- **Logging frameworks** - Structured logging integration
- **Monitoring systems** - Metrics collection for service issues
- **Caching strategies** - Fallback to cached data during outages
- **Async support** - Error handling for async/await patterns

This comprehensive error handling system transforms metapub from a library that breaks mysteriously during service outages into a robust, user-friendly toolkit that guides users through external service issues.
