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

**Error Handling**
   - Comprehensive reason codes for failures
   - Network error detection and retry logic
   - Service outage diagnosis

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
   Explanation when PDF is not available:
   
   - ``"PAYWALL"`` - Requires subscription/payment
   - ``"EMBARGO"`` - Under publisher embargo period
   - ``"NOFORMAT"`` - Unsupported publisher format
   - ``"CANTDO"`` - No strategy available for this publisher
   - ``"TXERROR"`` - Network/connection error

**backup_url** (str or None)
   Alternative URL when primary fails

**pma** (PubMedArticle)
   Associated article metadata

**doi_score** (int)
   Confidence score for DOI match (0-100)

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