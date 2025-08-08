# Dance Function Guidelines

Guidelines for writing proper dance functions in metapub FindIt system.

## Core Principles

Publisher Dance Development Process

  Phase 1: Evidence Collection

  1. Create Investigation Script ({publisher}_investigator.py)
    - Fetch real HTML pages from 3-5 recent PMIDs
    - Save raw HTML to files for analysis
    - Look for consistent patterns (PDF links, embed codes, etc.)
    - Document SSL/certificate issues encountered
  2. Pattern Discovery
    - Identify the most reliable PDF extraction method
    - Look for patterns in the URLs that would allow us to build links without ever loading a remote page.
    - Examples of patterns:  volume-issue-page + journal code.  DOI insert.  PMID insert.
    - Note any protocol quirks (protocol-relative URLs, etc.)
    - Document error conditions and edge cases
    - Test pattern consistency across different articles

 End of Phase 1: STOP AND ASK USER: Does this pattern make sense?

  Phase 2: Infrastructure Assessment

  3. Evaluate Generic Functions
    - Would it work to use the_vip_shake or the_doi_slide instead of a whole new dance function?
    - Does verify_pdf_url handle this publisher's SSL setup?
    - IF we have to scrape an HTML page to get information, does unified_uri_get work with their servers?
    - Any new generic utilities needed?
  4. Fix Foundation First
    - Enhance generic functions if needed
    - Add publisher-specific handling to shared utilities
    - Ensure robust error handling at the infrastructure level following CLAUDE.md principles.

  Phase 3: Dance Implementation

  5. Write Focused Dance Function
    - No big try/except blocks
    - No giant if-then tree
    - Primary method to find PDF link should be the one that requires zero remote page loads, i.e. loading PubMedArticle info into a template string.
    - Secondary method to find PDF link could involve loading a page and finding information in the page.
    - Having 2 methods to find a PDF link is fine.  3 is too much.
    - Let specific errors bubble up (no generic Exception catching)
    - Use discovered patterns, not complex parsing
    - Require what's actually needed (DOI vs PMID vs journal name)
    - If dance function exists don't create a new one -- rewrite the old one. don't rename it!
    - TRUST THE REGISTRY: PMID -> journal -> publisher wiring is consistent. no need to verify DOI.
  6. Adhere to the FindIt contract: input PMID, get PDF link or a reason it couldn't be found.
    - Function must return PDF link, nothing else (e.g. no article page as a runner-up!)
    - Clear error messages with prefixes (MISSING:, TXERROR:, DENIED:)
    - Use verify=True parameter for optional verification

  Phase 4: Test Development

  7. Create Focused Tests
    - Test the happy path with real pattern examples
    - Test each error condition separately
    - Remove any tests that don't match actual function behavior
    - Don't test for wrong DOI, wrong journal, or wrong PMID.  FindIt wiring is consistent: PMID -> journal -> publisher handler. 
  8. Registry Integration Test
    - Verify journal recognition works
    - Confirm dance function mapping

  Decision Framework

  - Simple pattern found → Use regex extraction
  - Complex DOM needed → Use minimal BeautifulSoup, avoid XPath
  - SSL issues discovered → Document for verify_pdf_url enhancement
  - Authentication required → Comment in code and move on 
  - Paywall detected → Implement detection, fail gracefully

  Quality Gates

  - Function under 50 lines
  - No generic Exception catching
  - Clear error messages with prefixes
  - Tests cover actual function behavior
  - Works with real PMIDs found in output/verified_pmids
  - Evidence from output/article_html


Core principle: use evidence, understand, then implement simply.



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
- COULD be brought in with a template in the registry to use the_doi_slide or the_vip_shake (in which case don't write a whole new dance)
- if the_doi_slide or the_vip_shake don't work for this publisher, THEN write a standalone dance.

Example:

```python
def the_mdpi_moonwalk(pma, verify=True):
    """MDPI dance - direct PDF URL construction from DOI.

    MDPI uses a consistent URL pattern where DOI 10.3390/journal[volume][issue][article]
    maps to PDF URL /{journal_id}/{volume}/{issue}/{article}/pdf

    Pattern discovered from evidence:
    - DOI: 10.3390/cardiogenetics11030017
    - URL: /2035-8148/11/3/17/pdf
    - DOI: 10.3390/metabo14040228
    - URL: /2218-1989/14/4/228/pdf

    The challenge is mapping journal names to their numeric IDs.
    Since direct DOI resolution works well for MDPI, this function
    uses enhanced DOI resolution with '/pdf' appended.

    :param: pma (PubMedArticle object)
    :param: verify (bool) [default: True]
    :return: url (str) - Direct PDF URL
    :raises: NoPDFLink
    """
    if not pma.doi:
        raise NoPDFLink('MISSING: DOI required for MDPI PDF access')

    # MDPI strategy: resolve DOI and append /pdf
    # This works because MDPI DOIs resolve to their article pages
    # and the PDF pattern is consistent
    resolved_url = the_doi_2step(pma.doi)
    pdf_url = f"{resolved_url}/pdf"

    if verify:
        verify_pdf_url(pdf_url, 'MDPI')

    return pdf_url
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


## Specific Guidelines

### Data Requirements
1. **Validate required data first** - fail fast if missing
2. **Don't try to work around missing data** with guesses
3. **Use the data PubMed actually provides** (DOI, volume, issue, etc.)
4. **Don't invalidate an article based on its DOI base.** -- Trust the registry; some oddball DOIs belong to publishers due to acquisitions.

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
