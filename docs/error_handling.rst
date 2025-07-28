Error Handling & Diagnostics
============================

Metapub provides intelligent error detection and user-friendly error messages when NCBI services are down or experiencing issues. Instead of cryptic XML parsing errors or connection timeouts, users get clear, actionable guidance.

NCBI Service Errors
-------------------

Enhanced Error Messages
~~~~~~~~~~~~~~~~~~~~~~~

**Before (Cryptic Errors)**

.. code-block:: python

   from metapub import PubMedFetcher
   
   fetch = PubMedFetcher()
   article = fetch.article_by_pmid(123456)  # When NCBI is down
   
   # Users would see:
   # XMLSyntaxError: Opening and ending tag mismatch
   # eutils.EutilsNCBIError: Document is empty, line 1, column 1
   # ConnectionError: HTTPSConnectionPool(host='eutils.ncbi.nlm.nih.gov'...)

**After (User-Friendly Messages)**

.. code-block:: python

   from metapub import PubMedFetcher
   from metapub.ncbi_errors import NCBIServiceError
   
   fetch = PubMedFetcher()
   
   try:
       article = fetch.article_by_pmid(123456)
   except NCBIServiceError as e:
       print(e)  # Shows helpful formatted message

**Example Output:**

.. code-block:: text

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

Error Types Detected
~~~~~~~~~~~~~~~~~~~

- **Server Errors** (HTTP 500, 502, 503)
- **Rate Limiting** (HTTP 429) 
- **Maintenance Mode** (HTML responses instead of XML)
- **Connection Issues** (timeouts, DNS failures)
- **XML Parsing Errors** (malformed responses)
- **Empty Responses** (service returning no data)

Exception Hierarchy
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   Exception
   └── NCBIServiceError  # New exception for service issues
       ├── error_type: str     # 'server_error', 'rate_limit', 'maintenance', etc.
       ├── suggestions: List   # Actionable suggestions for users
       └── user_message: str   # Human-readable error description

Enhanced Modules
----------------

The following modules include enhanced error handling:

**PubMedFetcher**
   - ``article_by_pmid()`` - Enhanced error detection for article fetching
   - ``pmids_for_query()`` - Better search error handling  
   - ``related_pmids()`` - Improved XML parsing error detection

**Convert Module**
   - ``pmid2doi()`` - Intelligent conversion error handling
   - ``doi2pmid()`` - Enhanced CrossRef/PubMed integration errors

Usage Examples
--------------

Basic Error Handling
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

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

Conversion with Error Handling  
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

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

Checking Service Status
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from metapub.ncbi_errors import check_ncbi_status
   
   status = check_ncbi_status()
   if status.is_available:
       # Proceed with NCBI operations
       fetch = PubMedFetcher()
       article = fetch.article_by_pmid(12345)
   else:
       print(f"NCBI unavailable: {status.error_message}")
       # Handle offline mode or show user-friendly message

Health Check Integration
-----------------------

The error handling integrates seamlessly with the ``ncbi_health_check`` utility:

.. code-block:: python

   # Errors suggest using the health check
   try:
       fetch = PubMedFetcher()
       article = fetch.article_by_pmid(123456)
   except NCBIServiceError as e:
       if e.error_type == 'server_error':
           # Error message includes: "Check NCBI service status with: ncbi_health_check --quick"
           pass

**Command Line Health Check:**

.. code-block:: bash

   # Quick status check
   ncbi_health_check --quick
   
   # Detailed diagnostics
   ncbi_health_check --verbose
   
   # JSON output for automation
   ncbi_health_check --format json

Benefits
--------

1. **🎯 Clearer User Experience** - Users understand when issues are external vs. their code
2. **⚡ Actionable Guidance** - Specific suggestions for resolving issues  
3. **📞 Reduced Support Burden** - Users can self-diagnose service outages
4. **🔗 Better Integration** - Works with health check and test suite
5. **📋 Consistent Messaging** - Uniform error handling across all modules

Backward Compatibility
----------------------

- ✅ Existing code continues to work unchanged
- ✅ Original exceptions still raised for non-service issues
- ✅ ``NCBIServiceError`` inherits from base ``Exception``
- ✅ Optional enhanced error handling via try/except blocks

Best Practices
--------------

**Production Applications**

.. code-block:: python

   import time
   from metapub import PubMedFetcher
   from metapub.ncbi_errors import NCBIServiceError
   
   def robust_fetch_with_retry(pmid, max_retries=3):
       """Fetch article with automatic retry on service errors."""
       
       for attempt in range(max_retries):
           try:
               fetch = PubMedFetcher()
               return fetch.article_by_pmid(pmid)
               
           except NCBIServiceError as e:
               if e.error_type == 'rate_limit':
                   # Exponential backoff for rate limits
                   wait_time = 2 ** attempt
                   time.sleep(wait_time)
                   continue
               elif e.error_type == 'server_error' and attempt < max_retries - 1:
                   # Retry server errors with delay
                   time.sleep(5)
                   continue
               else:
                   # Re-raise if max retries exceeded or non-retryable error
                   raise
                   
           except Exception as e:
               # Non-service errors shouldn't be retried
               raise
       
       raise Exception(f"Failed to fetch PMID {pmid} after {max_retries} attempts")

**Batch Processing**

.. code-block:: python

   from metapub import PubMedFetcher
   from metapub.ncbi_errors import NCBIServiceError
   
   def process_pmid_list(pmids):
       """Process list of PMIDs with graceful error handling."""
       
       fetch = PubMedFetcher()
       results = []
       errors = []
       
       for pmid in pmids:
           try:
               article = fetch.article_by_pmid(pmid)
               results.append({
                   'pmid': pmid,
                   'title': article.title,
                   'status': 'success'
               })
               
           except NCBIServiceError as e:
               if e.error_type == 'server_error':
                   # Log service outage and stop processing
                   print(f"NCBI service down, stopping batch at PMID {pmid}")
                   break
               else:
                   # Individual item error, continue processing
                   errors.append({'pmid': pmid, 'error': str(e)})
                   
           except Exception as e:
               # Log other errors but continue
               errors.append({'pmid': pmid, 'error': str(e)})
       
       return {'results': results, 'errors': errors}