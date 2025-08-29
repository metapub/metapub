# FindIt Network Timeout Implementation - Version 0.11

## Overview

The FindIt system now includes comprehensive network timeout controls to prevent infinite stalling during PDF discovery operations. This addresses a critical issue where the FindIt pass2 process could hang indefinitely when publisher servers become unresponsive.

## Key Changes

### Core FindIt Class

- **New Parameters**: Added `request_timeout` (default: 10 seconds) and `max_redirects` (default: 3) to FindIt constructor
- **Backward Compatibility**: All timeout parameters are optional with sensible defaults
- **Consistent Application**: Timeout controls apply to all network operations

### Publisher Dance Functions

- **Universal Coverage**: Updated all 40+ publisher-specific dance functions to support timeout parameters
- **Function Signatures**: All dance functions now accept `request_timeout` and `max_redirects` parameters
- **Network Requests**: All `unified_uri_get()` calls now use timeout and redirect controls

### HTTP Session Management

- **Redirect Limits**: Implemented HTTPAdapter-based redirect control using `max_redirects` parameter
- **Connection Pooling**: Enhanced session management with proper timeout configuration
- **Error Handling**: Clear error messages for timeout and redirect limit violations

## Technical Details

### Modified Files

**Core Infrastructure:**
- `metapub/findit/findit.py` - Added timeout parameters to FindIt class
- `metapub/findit/logic.py` - Updated dispatch logic to pass timeout parameters
- `metapub/findit/handlers.py` - Updated registry and handler systems
- `metapub/findit/dances/generic.py` - Updated all generic dance functions

**Publisher Dance Functions:** (31 files updated)
- All publisher-specific dance functions in `metapub/findit/dances/`
- Consistent timeout parameter integration across all publishers

### Error Messages

Network timeout issues are now clearly reported:

```
TXERROR: Connection timeout after 10s - attempted: https://publisher.com/article
TXERROR: Too many redirects (>3) - attempted: https://journals.example.com/...
```

## Usage Examples

### Default Behavior (Recommended)
```python
from metapub import FindIt

# Uses 10-second timeout, 3-redirect limit
src = FindIt('12345678')
```

### Custom Timeout Configuration
```python
# Conservative settings for unreliable networks
src = FindIt('12345678', request_timeout=20, max_redirects=5)

# Aggressive settings for fast batch processing  
src = FindIt('12345678', request_timeout=5, max_redirects=1)

# Disable redirects entirely
src = FindIt('12345678', max_redirects=0)
```

### Batch Processing with Timeouts
```python
def batch_with_timeouts(pmids):
    results = []
    for pmid in pmids:
        try:
            # Fast timeout for batch operations
            src = FindIt(pmid, request_timeout=5, max_redirects=1)
            results.append({'pmid': pmid, 'url': src.url, 'status': 'success'})
        except Exception as e:
            results.append({'pmid': pmid, 'error': str(e), 'status': 'failed'})
    return results
```

## Performance Impact

### Benefits

- **Faster Failure Detection**: Network issues detected within 10 seconds instead of hanging indefinitely
- **Predictable Batch Processing**: Timeout controls make large-scale operations reliable
- **Resource Management**: Prevents accumulation of hanging network connections
- **Better Error Reporting**: Clear timeout-related error messages for debugging

### Publisher-Specific Improvements

- **IOP Publishing**: Timeout controls apply to both direct access and CrossRef API fallbacks
- **JAMA Network**: Reliable timeout handling for articles with Cloudflare protection
- **All Publishers**: Consistent behavior across 68+ supported publishers

## Testing

- **Comprehensive Test Coverage**: Updated all test suites to expect timeout parameters
- **Mock Integration**: Fixed test mocking to properly simulate timeout scenarios
- **Error Handling Tests**: Verified proper timeout error reporting

## Migration Notes

### For Existing Code

No code changes required - all timeout parameters are optional with backward-compatible defaults.

### For Advanced Users

Consider configuring timeout parameters based on your use case:
- **Interactive Applications**: Use defaults (10s timeout, 3 redirects)
- **Batch Processing**: Use faster settings (5s timeout, 1 redirect)  
- **Unreliable Networks**: Use conservative settings (20s timeout, 5 redirects)

## Future Considerations

- **Adaptive Timeouts**: Could implement publisher-specific timeout values based on historical performance
- **Retry Logic**: Could add automatic retry with exponential backoff for timeout errors
- **Monitoring**: Could add metrics collection for timeout frequency analysis

## Version Compatibility

- **Minimum Version**: Python 3.6+
- **Dependencies**: No new dependencies added
- **API Compatibility**: Fully backward compatible with existing FindIt usage