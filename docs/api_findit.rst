FindIt: Full-Text PDF Discovery
=================================

.. currentmodule:: metapub.findit

The FindIt module provides sophisticated capabilities for locating full-text PDFs of academic papers using publisher-specific strategies and legal access verification.

FindIt Class
-----------

.. autoclass:: findit.FindIt
   :members:
   :show-inheritance:

The FindIt class is the primary interface for PDF discovery. It employs publisher-specific "dances" (custom algorithms) to locate downloadable PDFs while respecting publisher policies and embargo restrictions.

Key Features
~~~~~~~~~~~

**Publisher Coverage**
   - 15+ major academic publishers supported
   - Publisher-specific URL patterns and access methods
   - Dynamic strategy selection based on journal/publisher
   
**Access Verification**
   - HTTP verification of PDF availability
   - Embargo detection and date checking
   - Legal access validation

**Caching System**
   - SQLite-based result caching
   - Configurable cache directories
   - Smart cache invalidation for error cases

**Intelligent Error Reporting**
   - Structured error categories with actionable information
   - Always includes attempted URLs for debugging
   - Distinguishes between paywall, technical, and data issues
   - Developer-friendly reason codes for automated handling

Core Methods
~~~~~~~~~~~

.. automethod:: findit.FindIt.__init__

.. automethod:: findit.FindIt.load

.. automethod:: findit.FindIt.load_from_cache

Result Attributes
~~~~~~~~~~~~~~~

After initialization, FindIt objects provide these key attributes:

**url** (str or None)
   Direct link to downloadable PDF if found

**reason** (str or None)  
   Detailed explanation when PDF is not available, always includes attempted URL:
   
   - ``"MISSING: ..."`` - Required data not available (DOI, volume/issue, etc.)
   - ``"PAYWALL: ..."`` - Requires subscription/payment  
   - ``"DENIED: ..."`` - Access forbidden or login required
   - ``"TXERROR: ..."`` - Technical/network/server error
   - ``"NOFORMAT: ..."`` - Publisher doesn't provide expected format
   - ``"NOTFOUND: ..."`` - Content not found at expected location
   
   All reason messages include ``- attempted: {URL}`` for debugging.

**backup_url** (str or None)
   Alternative URL when primary fails

**pma** (PubMedArticle)
   Associated article metadata

**doi_score** (int)
   Confidence score for DOI match (0-100)

FindIt Error Handling Philosophy
--------------------------------

FindIt employs a sophisticated error reporting system that provides meaningful, actionable information to developers about why a PDF link could not be obtained. This system distinguishes between different types of failures and always includes the attempted URL for debugging purposes.

Error Categories and Usage
~~~~~~~~~~~~~~~~~~~~~~~~~~

FindIt uses three main error classification approaches:

**NoPDFLink Exception - Expected Operational Failures**

Used when the system cannot produce a PDF link due to expected operational conditions:

.. code-block:: python

   from metapub import FindIt
   from metapub.exceptions import NoPDFLink
   
   try:
       src = FindIt('12345678')  # Article without DOI
   except NoPDFLink as e:
       print(str(e))
       # "MISSING: DOI required for SAGE journals - attempted: none"

**AccessDenied Exception - Publisher Restrictions**  

Used when publishers explicitly deny access due to paywall or subscription requirements:

.. code-block:: python

   from metapub.exceptions import AccessDenied
   
   try:
       src = FindIt('16419642')  # Nature paywall article
   except AccessDenied as e:
       print(str(e))
       # "PAYWALL: Nature requires subscription - attempted: https://nature.com/articles/..."

**TXERROR Prefix - Technical Failures**

Used within NoPDFLink messages when technical issues prevent accessing content:

.. code-block:: python

   try:
       src = FindIt('12345678')  # Server timeout
   except NoPDFLink as e:
       print(str(e))
       # "TXERROR: Connection timeout after 30s - attempted: https://publisher.com/..."

Error Message Format
~~~~~~~~~~~~~~~~~~~

All error messages follow a consistent structure:

.. code-block:: text

   {ERROR_TYPE}: {Description} - attempted: {URL}

**Error Type Prefixes:**

- ``MISSING:`` - Required data not available (DOI, volume/issue, etc.)
- ``NOFORMAT:`` - Publisher doesn't provide expected format
- ``PAYWALL:`` - Subscription or payment required  
- ``DENIED:`` - Access forbidden or login required
- ``TXERROR:`` - Technical, network, or server error
- ``NOTFOUND:`` - Content not found at expected location

**Always Includes Attempted URL:**

Every error message includes the URL(s) that were attempted, allowing developers to:

- Debug access issues manually
- Understand what URLs the system tried  
- Implement alternative access methods
- Report publisher-specific problems

Developer Usage Patterns
~~~~~~~~~~~~~~~~~~~~~~~~

The structured error information enables sophisticated error handling:

**Basic Error Categorization**

.. code-block:: python

   from metapub import FindIt
   from metapub.exceptions import NoPDFLink, AccessDenied
   
   def handle_findit_result(pmid):
       try:
           src = FindIt(pmid)
           if src.url:
               return {'status': 'success', 'url': src.url}
           else:
               return {'status': 'no_pdf', 'reason': src.reason}
               
       except AccessDenied as e:
           # Publisher paywall/subscription required
           return {
               'status': 'paywall', 
               'reason': str(e),
               'action': 'purchase_required'
           }
           
       except NoPDFLink as e:
           error_msg = str(e)
           if 'TXERROR' in error_msg:
               # Technical issue - retry later
               return {
                   'status': 'technical_error',
                   'reason': error_msg,
                   'action': 'retry_later'
               }
           elif 'MISSING' in error_msg:
               # Data issue - try alternative approach
               return {
                   'status': 'data_missing',
                   'reason': error_msg,
                   'action': 'try_alternative'
               }
           else:
               return {'status': 'unknown_error', 'reason': error_msg}

**Automated Response to Error Types**

.. code-block:: python

   import time
   from collections import defaultdict
   
   def batch_findit_with_smart_retry(pmids, max_retries=3):
       """Process PMIDs with intelligent error handling and retry logic."""
       results = []
       retry_queue = defaultdict(list)  # Group by error type for batch retry
       
       for pmid in pmids:
           try:
               src = FindIt(pmid)
               if src.url:
                   results.append({'pmid': pmid, 'url': src.url, 'status': 'success'})
               elif src.reason:
                   # Store reason for analysis
                   results.append({'pmid': pmid, 'reason': src.reason, 'status': 'failed'})
               
           except AccessDenied as e:
               # Paywall - annotate for purchase consideration
               results.append({
                   'pmid': pmid, 
                   'status': 'paywall',
                   'reason': str(e),
                   'needs_purchase': True
               })
               
           except NoPDFLink as e:
               error_msg = str(e)
               if 'TXERROR' in error_msg:
                   # Technical errors - queue for retry
                   retry_queue['technical'].append(pmid)
                   results.append({
                       'pmid': pmid,
                       'status': 'technical_error', 
                       'reason': error_msg,
                       'will_retry': True
                   })
               else:
                   # Data/format errors - unlikely to succeed on retry
                   results.append({
                       'pmid': pmid,
                       'status': 'permanent_failure',
                       'reason': error_msg
                   })
       
       # Retry technical errors after delay
       if retry_queue['technical'] and max_retries > 0:
           print(f"Retrying {len(retry_queue['technical'])} technical failures...")
           time.sleep(5)  # Wait for transient issues to resolve
           
           retry_results = batch_findit_with_smart_retry(
               retry_queue['technical'], 
               max_retries - 1
           )
           
           # Update original results with retry outcomes
           for retry_result in retry_results:
               # Find and update the original failed result
               for i, result in enumerate(results):
                   if result['pmid'] == retry_result['pmid']:
                       results[i] = retry_result
                       break
       
       return results

**Error Analysis and Reporting**

.. code-block:: python

   def analyze_findit_errors(results):
       """Analyze FindIt results to identify patterns and actionable insights."""
       error_stats = defaultdict(int)
       paywall_publishers = defaultdict(int)
       technical_issues = []
       
       for result in results:
           if result['status'] == 'paywall':
               # Extract publisher from error message for purchase planning
               reason = result['reason']
               if 'Nature' in reason:
                   paywall_publishers['Nature Publishing'] += 1
               elif 'Elsevier' in reason:
                   paywall_publishers['Elsevier/ScienceDirect'] += 1
               # Add more publisher patterns as needed
               
           elif result['status'] == 'technical_error':
               technical_issues.append(result['reason'])
               
           error_stats[result['status']] += 1
       
       print("=== FindIt Error Analysis ===")  
       print(f"Success rate: {error_stats['success']}/{len(results)} ({error_stats['success']/len(results)*100:.1f}%)")
       print(f"Paywall articles: {error_stats['paywall']}")
       print(f"Technical errors: {error_stats['technical_error']}")
       
       if paywall_publishers:
           print("\n=== Publishers Requiring Subscription ===")
           for publisher, count in paywall_publishers.items():
               print(f"  {publisher}: {count} articles")
               
       if technical_issues:
           print(f"\n=== Technical Issues (consider retrying) ===")
           for issue in set(technical_issues):  # Unique issues only
               count = technical_issues.count(issue)
               print(f"  {issue} (×{count})")
       
       return {
           'error_stats': dict(error_stats),
           'paywall_publishers': dict(paywall_publishers),
           'technical_issues': technical_issues
       }

Error Message Examples
~~~~~~~~~~~~~~~~~~~~~

**Missing Data Errors:**

.. code-block:: text

   MISSING: DOI required for SAGE journals - attempted: none
   MISSING: pii needed for ScienceDirect lookup - attempted: https://sciencedirect.com/...
   MISSING: volume/issue/pii data - cannot construct Nature URL - attempted: none

**Access Denied Errors:**

.. code-block:: text

   PAYWALL: Nature requires subscription - attempted: https://nature.com/articles/s41586-020-2936-y.pdf
   DENIED: JAMA requires login - attempted: https://jamanetwork.com/journals/jama/fullarticle/...
   PAYWALL: Elsevier paywall detected - attempted: https://sciencedirect.com/science/article/pii/...

**Technical Errors:**

.. code-block:: text

   TXERROR: Server returned 503 Service Unavailable - attempted: https://publisher.com/...
   TXERROR: Connection timeout after 30s - attempted: https://journals.sagepub.com/...
   TXERROR: dx.doi.org lookup failed (Network error) - attempted: http://dx.doi.org/10.1038/...

**Publisher Format Issues:**

.. code-block:: text

   NOFORMAT: BMC article has no PDF version - attempted: https://bmcgenomics.biomedcentral.com/...
   NOTFOUND: Article not found on Nature platform - attempted: https://nature.com/..., traditional URL

Benefits for Developers
~~~~~~~~~~~~~~~~~~~~~~

This comprehensive error handling system provides:

1. **Clear Action Path** - Developers know exactly what went wrong and why
2. **Debugging Information** - Attempted URLs allow manual verification  
3. **Automated Categorization** - Error types enable programmatic responses
4. **Publisher Intelligence** - Identify which publishers require subscriptions
5. **Technical Issue Detection** - Distinguish between transient and permanent failures
6. **Batch Processing Optimization** - Group similar errors for efficient handling

The goal is to make FindIt failures informative and actionable rather than opaque, enabling developers to build robust applications that handle PDF access gracefully.

Usage Patterns
-------------

Basic PDF Discovery
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from metapub import FindIt
   
   # Find PDF by PMID
   src = FindIt('33157158')
   
   if src.url:
       print(f"✓ PDF available: {src.url}")
       print(f"Journal: {src.pma.journal}")
   else:
       print(f"✗ No access: {src.reason}")
       if src.backup_url:
           print(f"Backup URL: {src.backup_url}")

Advanced Configuration
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Advanced options
   src = FindIt(
       pmid='12345678',
       use_nih=True,           # Use NIH access when available
       verify=False,           # Skip URL verification for speed
       retry_errors=True,      # Retry cached error results
       debug=True,             # Enable debug logging
       cachedir='/custom/cache' # Custom cache location
   )

DOI-Based Discovery
~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Find PDF by DOI instead of PMID
   src = FindIt(doi='10.1038/nature12373')
   
   if src.url:
       print(f"Found via DOI: {src.url}")
   else:
       print(f"DOI lookup failed: {src.reason}")

Publisher-Specific Examples
--------------------------

Nature Publishing Group
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Nature articles - often available through institutional access
   nature_pmids = ['16419642', '18830250', '12187393']
   
   for pmid in nature_pmids:
       src = FindIt(pmid)
       print(f"PMID {pmid}: {src.pma.journal}")
       if src.url:
           print(f"  ✓ Available: {src.url}")
       else:
           print(f"  ✗ {src.reason}")

BMC and Open Access
~~~~~~~~~~~~~~~~~

.. code-block:: python

   # BMC journals - typically open access
   bmc_pmids = ['25943194', '20170543', '25927199']
   
   for pmid in bmc_pmids:
       src = FindIt(pmid)
       print(f"PMID {pmid}: {src.pma.journal}")
       if src.url:
           print(f"  ✓ Open access: {src.url}")
       else:
           print(f"  ✗ Unexpected: {src.reason}")

Embargo Detection
~~~~~~~~~~~~~~~~

.. code-block:: python

   # Check for embargoed content
   src = FindIt('25575644')  # Example embargoed article
   
   embargo_date = src.pma.history.get('pmc-release', None)
   
   if src.reason and 'embargo' in src.reason.lower():
       print(f"Article is embargoed")
       if embargo_date:
           print(f"Available after: {embargo_date}")
   elif src.url:
       print(f"Immediate access: {src.url}")

Batch Processing
--------------

Processing Multiple Articles
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import csv
   import time
   from metapub import FindIt
   
   def batch_findit_analysis(pmids, output_file='findit_results.csv'):
       """Analyze PDF availability for a list of PMIDs."""
       results = []
       
       with open(output_file, 'w', newline='') as csvfile:
           fieldnames = ['pmid', 'journal', 'title', 'url_available', 
                        'url', 'reason', 'embargo_status']
           writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
           writer.writeheader()
           
           for i, pmid in enumerate(pmids):
               print(f"Processing {pmid} ({i+1}/{len(pmids)})")
               
               try:
                   src = FindIt(pmid, retry_errors=True)
                   
                   # Check embargo status
                   embargo_date = src.pma.history.get('pmc-release', None)
                   is_embargoed = (
                       src.reason and 
                       src.reason.startswith("PAYWALL") and 
                       "embargo" in src.reason
                   )
                   
                   result = {
                       'pmid': pmid,
                       'journal': src.pma.journal,
                       'title': src.pma.title,
                       'url_available': bool(src.url),
                       'url': src.url or '',
                       'reason': src.reason or '',
                       'embargo_status': 'embargoed' if is_embargoed else 'not_embargoed'
                   }
                   
                   writer.writerow(result)
                   results.append(result)
                   
               except Exception as e:
                   print(f"Error processing {pmid}: {e}")
               
               # Rate limiting
               time.sleep(0.5)
       
       return results

   # Usage
   pmids = ['12345678', '23456789', '34567890']
   results = batch_findit_analysis(pmids)

Result Analysis
~~~~~~~~~~~~~

.. code-block:: python

   import pandas as pd
   
   def analyze_findit_results(results):
       """Analyze FindIt batch processing results."""
       df = pd.DataFrame(results)
       
       print("=== PDF Access Analysis ===")
       print(f"Total articles: {len(df)}")
       print(f"PDFs available: {df['url_available'].sum()} ({df['url_available'].mean()*100:.1f}%)")
       print(f"Embargoed: {(df['embargo_status'] == 'embargoed').sum()}")
       
       print("\n=== Access by Journal ===")
       journal_stats = df.groupby('journal').agg({
           'url_available': ['count', 'sum', 'mean']
       }).round(3)
       journal_stats.columns = ['total', 'available', 'access_rate']
       print(journal_stats.sort_values('access_rate', ascending=False))
       
       print("\n=== Failure Reasons ===")
       failed = df[~df['url_available']]
       if len(failed) > 0:
           reason_counts = failed['reason'].value_counts()
           print(reason_counts)
   
   # Analyze results
   analyze_findit_results(results)

Advanced Features
----------------

Cache Management
~~~~~~~~~~~~~~

.. code-block:: python

   # Custom cache configuration
   import os
   from metapub.cache_utils import get_cache_path
   
   # Set global cache directory
   os.environ['METAPUB_CACHE_DIR'] = '/large/cache/partition'
   
   # Or disable caching entirely
   src = FindIt('12345678', cachedir=None)
   
   # Clear cache for fresh results
   import shutil
   cache_dir = get_cache_path('default', 'findit.db')
   if os.path.exists(cache_dir):
       os.remove(cache_dir)
       print("FindIt cache cleared")

Error Recovery
~~~~~~~~~~~~

.. code-block:: python

   from requests.exceptions import ConnectionError, Timeout
   
   def robust_findit(pmid, max_retries=3):
       """FindIt with automatic retry on network errors."""
       for attempt in range(max_retries):
           try:
               src = FindIt(pmid)
               return src
           except (ConnectionError, Timeout) as e:
               if attempt < max_retries - 1:
                   print(f"Network error, retrying... ({attempt + 1}/{max_retries})")
                   time.sleep(2 ** attempt)  # Exponential backoff
               else:
                   print(f"Failed after {max_retries} attempts: {e}")
                   return None
   
   # Usage
   src = robust_findit('12345678')
   if src and src.url:
       print(f"Success: {src.url}")

Publisher Strategy Information
----------------------------

Supported Publishers
~~~~~~~~~~~~~~~~~~

The FindIt system includes specialized strategies for:

**Open Access Publishers**
   - BMC (BioMed Central)
   - PLOS (Public Library of Science)
   - PMC (PubMed Central)

**Commercial Publishers**
   - Nature Publishing Group
   - Elsevier (ScienceDirect)
   - Wiley
   - Springer
   - American Chemical Society

**Society Publishers**
   - American Association for the Advancement of Science (AAAS)
   - JAMA Network
   - Biochemical Society

**Regional Publishers**
   - J-STAGE (Japan)
   - Karger (Switzerland)
   - Dustri (Germany)

Strategy Selection
~~~~~~~~~~~~~~~~

.. code-block:: python

   # The system automatically selects strategies based on:
   # 1. Journal title patterns
   # 2. Publisher information
   # 3. DOI prefixes
   # 4. URL patterns in metadata
   
   src = FindIt('12345678', debug=True)
   # Debug mode shows strategy selection process

Integration with Other Modules
-----------------------------

Combined Workflows
~~~~~~~~~~~~~~~~

.. code-block:: python

   from metapub import PubMedFetcher, FindIt
   
   # Literature review with full-text access checking
   fetch = PubMedFetcher()
   
   # Search for articles
   pmids = fetch.pmids_for_query('CRISPR therapeutics', retmax=50)
   
   accessible_articles = []
   
   for pmid in pmids:
       # Get article metadata
       article = fetch.article_by_pmid(pmid)
       
       # Check PDF availability
       src = FindIt(pmid)
       
       if src.url:
           accessible_articles.append({
               'pmid': pmid,
               'title': article.title,
               'journal': article.journal,
               'year': article.year,
               'pdf_url': src.url
           })
   
   print(f"Found {len(accessible_articles)} articles with PDFs out of {len(pmids)} total")

See Also
--------

- :doc:`advanced` - Advanced FindIt patterns and publisher-specific examples
- :doc:`tutorials` - Complete workflows using FindIt for batch processing
- :doc:`api_fetchers` - Integration with other fetcher classes
- :doc:`examples` - Practical FindIt usage examples