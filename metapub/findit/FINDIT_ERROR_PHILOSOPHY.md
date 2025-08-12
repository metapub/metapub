# FindIt Error Handling Philosophy

## Overview

FindIt uses a structured error handling approach that provides meaningful information to developers about why a PDF link could not be obtained. The error handling system distinguishes between different types of failures and provides consistent messaging that includes the attempted URL for debugging purposes.

## Error Types and Usage

### 1. NoPDFLink - Expected Operational Failures

**Purpose**: Raised when the dance function cannot produce a PDF link due to expected operational conditions (missing data, unsupported formats, etc.).

**When to use**:
- Missing required data (DOI, PII, volume/issue/page)
- Publisher doesn't support the format we expected
- Article is not available in PDF format
- Lookup services return no results

**Message format**:
```python
raise NoPDFLink(f'MISSING: {required_field} required for {publisher} (PMID: {pmid}) - attempted: {attempted_url}')
```

**Examples**:
```python
raise NoPDFLink('MISSING: DOI required for SAGE journals (PMID: {pmid}) - attempted: https://journals.sagepub.com/...')
raise NoPDFLink('MISSING: pii needed for ScienceDirect lookup (PMID: {pmid}) - attempted: https://sciencedirect.com/...')
```

### 2. AccessDenied - Publisher Access Restrictions

**Purpose**: Raised when the publisher explicitly denies access due to paywall, subscription requirements, or login restrictions.

**When to use**:
- HTTP 401/403 responses from publisher
- Publisher paywall pages detected
- Subscription-required content
- Login-only access

**Message format**:
```python
raise AccessDenied(f'PAYWALL: {publisher} requires purchase (PMID: {pmid}) - attempted: {attempted_url}')
raise AccessDenied(f'DENIED: {publisher} prevented download (PMID: {pmid}) - attempted: {attempted_url}')
```

**Examples**:
```python
raise AccessDenied('PAYWALL: Nature requires subscription (PMID: 1233456) - attempted: https://nature.com/articles/...')
raise AccessDenied('DENIED: JAMA requires login (PMID: 12345666) - attempted: https://jamanetwork.com/...')
```

### 3. TXERROR - Technical/Network Failures

**Purpose**: Used within NoPDFLink messages when server errors, network issues, or technical problems prevent accessing content.

**When to use**:
- HTTP 5xx server errors
- Network timeouts or connection failures  
- Too many redirects
- Malformed responses that prevent processing
- Any technical issue that prevents reaching the content

**Message format**:
```python
raise NoPDFLink(f'TXERROR: {error_description} (PMID: {pmid}) - attempted: {attempted_url}')
```

**Examples**:
```python
raise NoPDFLink('TXERROR: Server returned 503 Service Unavailable - attempted: https://publisher.com/...')
raise NoPDFLink('TXERROR: Connection timeout after 30s - attempted: https://publisher.com/...')
raise NoPDFLink('TXERROR: Too many redirects (>10) - attempted: https://publisher.com/...')
```

### 4. POSTONLY - Architectural Incompatibility

**Purpose**: Used within NoPDFLink messages when a publisher requires POST requests or session-based downloads that are incompatible with FindIt's URL-based model.

**When to use**:
- Publisher requires POST requests with CSRF tokens
- Session-based downloads with encrypted parameters
- Complex authentication flows that can't be captured in a simple URL
- Any download mechanism that cannot be represented as a GET-able URL

**Message format**:
```python
raise NoPDFLink(f'POSTONLY: {publisher} PDF requires POST request with session data - cannot provide direct PDF URL. Visit article page and click "Download Article": {article_url}')
```

**Examples**:
```python
raise NoPDFLink('POSTONLY: EurekaSelect PDF requires POST request with session data - cannot provide direct PDF URL. Visit article page and click "Download Article": https://www.eurekaselect.com/article/12345')
raise NoPDFLink('POSTONLY: Dustri-Verlag PDFs require POST form submission - visit: https://www.dustri.com/nc/article-response-page.html?doi=10.5414/CN110175Intro')
```

**Key principles for POSTONLY errors**:
- Always provide the article page URL where users can manually download
- Explain the architectural limitation clearly
- Give specific instructions (e.g., "click Download Article button")
- Document the complete POST process in code comments for future enhancement
- Consider creating detailed notes for potential pdf_utils implementation

**Future considerations**:
When multiple publishers require POST-based downloads, consider enhancing FindIt architecture to support:
- `method="POST"` in results
- Session management utilities in pdf_utils
- Standardized POST download helpers

### 5. Code Errors - Let Them Bubble Up

**Purpose**: Programming errors, unexpected conditions, or bugs should NOT be caught and re-raised as NoPDFLink.

**When to let bubble up**:
- AttributeError, IndexError, KeyError during parsing
- Invalid method calls or programming mistakes
- Unexpected data structure problems
- Any error that indicates a bug in the code

**Examples of what NOT to do**:
```python
# ❌ DON'T DO THIS
try:
    title = article.title.strip()
except AttributeError as e:
    raise NoPDFLink(f'Error processing article: {e}')

# ✅ DO THIS - let it bubble up
title = article.title.strip()  # If this fails, it's a code bug
```

## URL Inclusion Requirements

**Every error message MUST include the attempted URL** using this format:
```
- attempted: {attempted_url}
```

This allows developers to:
- Debug access issues manually
- Understand what URLs the system tried
- Implement alternative access methods
- Report publisher-specific problems

## Developer Usage Patterns

The error reason goes into the FindIt object's `reason` field, allowing developers to:

```python
# Example developer usage
result = findit.get_pdf_url(pmid)
if result.reason:
    if 'PAYWALL' in result.reason:
        # Annotate paper as requiring purchase
        mark_paper_for_purchase(pmid, result.reason)
    elif 'TXERROR' in result.reason:
        # Technical issue - retry later
        schedule_retry(pmid, result.reason)
    elif 'MISSING' in result.reason:
        # Data issue - may need different approach
        try_alternative_lookup(pmid, result.reason)
    elif 'POSTONLY' in result.reason:
        # Architectural limitation - provide manual download option
        show_manual_download_option(pmid, result.reason)
```

## Code Quality and Refactoring Guidelines

### 1. Avoid Bad Code Patterns

Based on extensive refactoring of dance functions, avoid these anti-patterns:

**❌ Massive try-except blocks (60+ lines)**:
```python
# DON'T DO THIS - Single try block covering entire function
def bad_dance(pma, verify=True):
    try:
        # 60+ lines of complex logic
        # Multiple HTTP requests
        # HTML parsing
        # Paywall detection
        # URL construction
        # All in one giant try block
    except Exception as e:
        raise NoPDFLink(f'Something failed: {e}')
```

**✅ Focused error handling**:
```python
# DO THIS - Specific error handling for each operation
def good_dance(pma, verify=True):
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required')
    
    try:
        article_url = the_doi_2step(pma.doi)
    except NoPDFLink as e:
        raise NoPDFLink(f'TXERROR: DOI resolution failed: {e}')
    
    # Each operation has focused error handling
```

**❌ Trial-and-error URL approaches**:
```python
# DON'T DO THIS - Testing multiple random URLs
possible_urls = [url1, url2, url3, url4, url5]
for url in possible_urls:
    try:
        if test_url(url):
            return url
    except:
        continue
```

**✅ Primary + fallback pattern**:
```python
# DO THIS - One tested primary pattern with fallback
primary_url = f'https://publisher.com/pdf/{pma.doi}'
if verify and _test_url(primary_url):
    return primary_url

# Single tested fallback if primary fails
try:
    fallback_url = the_doi_2step(pma.doi)
    return fallback_url
except NoPDFLink:
    raise NoPDFLink(f'TXERROR: Both primary and fallback failed - attempted: {primary_url}')
```

### 2. Use Generic Functions Consistently

Replace custom implementations with proven generic functions:

**✅ Use `detect_paywall_from_html()` instead of custom paywall detection**:
```python
# DON'T DO THIS
paywall_terms = ['subscribe', 'sign in', 'purchase', 'login required']
if any(term in page_text.lower() for term in paywall_terms):
    raise AccessDenied('PAYWALL: ...')

# DO THIS  
if detect_paywall_from_html(response.text):
    raise AccessDenied('PAYWALL: ...')
```

**✅ Use `unified_uri_get()` for all HTTP requests**:
```python
# DO THIS - Consistent headers and behavior
response = unified_uri_get(url, timeout=10)
```

**✅ Use `the_doi_2step()` for DOI resolution**:
```python
# DO THIS - Proven DOI resolution with proper error handling
resolved_url = the_doi_2step(pma.doi)
```

### 3. Helper Function Best Practices

**❌ Over-engineered helper functions**:
```python
# DON'T DO THIS - Unnecessary try-except wrapping
def _helper_function(url):
    try:
        response = unified_uri_get(url)
        # ... processing logic ...
        return result
    except AccessDenied:
        raise  # Silly re-raising
    except Exception:
        return None  # Lazy blanket catching
```

**✅ Clean helper functions that let errors bubble up**:
```python
# DO THIS - Let programming errors bubble up naturally
def _helper_function(url):
    response = unified_uri_get(url)
    # ... processing logic ...
    return result  # Let AccessDenied and other errors bubble up
```

**Key principles for helper functions**:
- Don't catch exceptions you don't know how to handle
- Don't re-raise the same exception type 
- Let programming errors (AttributeError, KeyError, etc.) bubble up
- Only catch exceptions at the level that knows what to do with them

### 4. Verification Mode Logic

**❌ Incorrect verification behavior**:
```python
# DON'T DO THIS - Returning article URL when no PDF found in verify=True mode
if no_pdf_found_but_page_accessible:
    return article_url  # WRONG! This violates verify=True contract
```

**✅ Correct verification behavior**:
```python
# DO THIS - Fail when PDF not found in verify=True mode
if no_pdf_found:
    raise NoPDFLink(f'TXERROR: No PDF link found on publisher page - attempted: {article_url}')
```

**Verification mode contract**:
- `verify=True`: Must return actual PDF URL or raise appropriate exception
- `verify=False`: Can return constructed URL without testing
- Never return non-PDF URLs when verification is requested

## Implementation Guidelines

### 1. URL Construction and Tracking

Always track the attempted URL for error reporting:

```python
def the_example_dance(pma, verify=True):
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for Example Publisher - attempted: none')
    
    pdf_url = f'https://example.com/pdf/{pma.doi}'
    
    try:
        response = requests.get(pdf_url, timeout=30)
        if response.status_code == 401:
            raise AccessDenied(f'PAYWALL: Example Publisher requires subscription - attempted: {pdf_url}')
        elif not response.ok:
            raise NoPDFLink(f'TXERROR: Server returned {response.status_code} - attempted: {pdf_url}')
        
        # Process response...
        return pdf_url
        
    except requests.exceptions.Timeout:
        raise NoPDFLink(f'TXERROR: Connection timeout after 30s - attempted: {pdf_url}')
    except requests.exceptions.RequestException as e:
        raise NoPDFLink(f'TXERROR: Network error - {e} - attempted: {pdf_url}')
```

### 2. Error Message Prefixes

Use consistent prefixes for error categorization:

- `MISSING:` - Required data not available (use with NoPDFLink)
- `PAYWALL:` - Subscription/payment required (use with AccessDenied)
- `DENIED:` - Access forbidden/login required (use with AccessDenied)  
- `TXERROR:` - Technical/network/server error (use with NoPDFLink)
- `POSTONLY:` - Architectural incompatibility (POST-required downloads) (use with NoPDFLink)

### 3. Verification Function Integration

When using `verify_pdf_url()`, it will automatically add appropriate URLs to error messages. The dance function should focus on construction logic:

```python
def the_example_dance(pma, verify=True):
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for Example Publisher - attempted: none')
    
    pdf_url = f'https://example.com/pdf/{pma.doi}'
    
    if verify:
        # verify_pdf_url() will add the URL to any error messages it raises
        return verify_pdf_url(pdf_url, 'Example Publisher')
    
    return pdf_url
```
