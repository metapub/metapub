# Dance Function Guidelines

Guidelines for writing proper dance functions in metapub FindIt system.

## Core Principles

### ✅ GOOD PATTERNS (Acceptable)

#### 1. Primary + Fallback Pattern (Nature, Wolters Kluwer style)
- **One well-tested primary method** with **one well-tested fallback method**
- Each method has been validated to actually work for that publisher
- Fallback is used when primary method lacks required data (e.g., no DOI but has volume/issue)
- Clear, separate logic paths - not trial-and-error

```python
def the_publisher_dance(pma, verify=True):
    # Try primary method if we have required data
    if pma.doi:
        url = construct_doi_url(pma.doi)
        if verify and verify_pdf_url(url):
            return url
        elif not verify:
            return url
    
    # Fallback method if primary data missing
    if pma.volume and pma.issue and pma.first_page:
        url = construct_voliss_url(pma)
        if verify and verify_pdf_url(url):
            return url
        elif not verify:
            return url
    
    raise NoPDFLink("Missing required data for both approaches")
```

#### 2. Single Method Pattern (Recommended for new dances)
- **One consistent, tested URL pattern**
- Simple, reliable, clean code
- Publisher has been verified to work with this pattern

```python
def the_publisher_dance(pma, verify=True):
    if not pma.doi:
        raise NoPDFLink("DOI required for Publisher")
    
    url = f"https://publisher.com/pdf/{pma.doi}"
    
    if verify:
        if verify_pdf_url(url):
            return url
        else:
            raise AccessDenied(f"PAYWALL: Publisher requires subscription - {url}")
    
    return url
```

### ❌ BAD PATTERNS (Avoid These!)

#### 1. Trial-and-Error Multiple URLs 
**NEVER DO THIS:**
```python
# BAD: Trying multiple untested URL patterns
possible_urls = [
    f'https://publisher.com/pdf/{doi}',
    f'https://publisher.com/article/{doi}', 
    f'https://www.publisher.com/pdf/{doi}',
    f'https://publisher.com/download/{doi}'
]

for url in possible_urls:  # This will get us banned!
    try:
        if works(url):
            return url
    except:
        continue
```

**Why this is bad:**
- Makes multiple requests to publisher for same article
- Publishers will ban us for this behavior
- Indicates we don't actually know how the publisher works
- Huge try-except blocks are bad code structure

#### 2. Speculative Strategy Attempts 
**NEVER DO THIS:**
```python
# BAD: Trying different "strategies" we're not sure about
try:
    # Strategy 1: Maybe this works?
    url1 = f"{resolved_url}/pdf"
    if maybe_works(url1):
        return url1
except:
    pass

try:
    # Strategy 2: Perhaps this pattern?
    url2 = f"https://publisher.com/openurl.php?doi={doi}"
    if perhaps_works(url2):
        return url2
except:
    pass

try:  
    # Strategy 3: What about this format?
    url3 = construct_guess_url(pma)
    if might_work(url3):
        return url3
except:
    pass
```

**Why this is bad:**
- Multiple untested approaches
- Makes publishers think we're attacking them
- Huge nested try-except blocks
- Each "strategy" is a guess, not validated

#### 3. Excessive HTML Parsing for Guessing
**AVOID:**
```python
# BAD: Complex HTML parsing to guess at PDF links
response = requests.get(article_url)
soup = BeautifulSoup(response.text)
for link in soup.find_all('a'):
    if 'pdf' in link.get('href', ''):
        try:
            maybe_pdf = urljoin(base_url, link['href'])
            if test_if_pdf(maybe_pdf):  # More requests!
                return maybe_pdf
        except:
            continue
```

## Specific Guidelines

### Data Requirements
1. **Validate required data first** - fail fast if missing
2. **Don't try to work around missing data** with guesses
3. **Use the data PubMed actually provides** (DOI, volume, issue, etc.)

### URL Construction  
1. **Research the publisher first** - understand their actual URL patterns
2. **Test with real PMIDs** before implementing
3. **One pattern per method** - don't construct multiple variations

### Error Handling
1. **No huge try-except blocks** - catch specific exceptions
2. **No catching and continuing** - if something fails, understand why
3. **Meaningful error messages** - help debug what went wrong

### Request Behavior
1. **Minimize requests per article** - don't make multiple attempts
2. **Use proper timeouts** and error handling
3. **Respect rate limits** and publisher policies

### When to Use Fallback Methods
✅ **Good reasons for fallback:**
- Primary method requires DOI, fallback uses volume/issue/page
- Publisher changed URL structure but supports both old and new
- Different journals within publisher use different patterns

❌ **Bad reasons for fallback:**
- "Maybe this URL format will work better"
- "Let's try a few different approaches"
- "I'm not sure which pattern they use"

## Implementation Checklist

Before writing a dance function:
- [ ] Research publisher's actual URL patterns
- [ ] Test with at least 3 real PMIDs from that publisher  
- [ ] Verify the URL pattern actually returns PDFs
- [ ] Understand what data is required (DOI vs volume/issue)
- [ ] Check if publisher has paywall detection needs
- [ ] Use common functions from generic.py where possible

## Code Review Red Flags

If you see these patterns, the dance needs rewriting:
- Multiple URL patterns being tried in sequence
- Large lists of "possible_urls" 
- Nested try-except blocks catching generic exceptions
- Comments like "maybe this will work" or "try different strategies"
- More than 2 distinct approaches per dance function
- Complex HTML parsing to hunt for PDF links

## Testing Requirements

Every dance function must:
- Work with at least 3 different PMIDs from that publisher
- Return actual PDF URLs (not just any URL)
- Handle paywall detection appropriately  
- Fail cleanly when articles aren't accessible
- Not make excessive requests to the publisher

## Summary

The key distinction is:
- ✅ **Primary + Fallback** = Two tested methods for different data scenarios  
- ❌ **Trial-and-Error** = Multiple untested attempts hoping something works

Remember: **We want to be good citizens of the academic publishing ecosystem**. Publishers should see us as a legitimate user, not as a scraper trying multiple attack vectors.
