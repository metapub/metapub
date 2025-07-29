Advanced Usage
==============

This section covers advanced patterns and sophisticated features demonstrated in the demo scripts.

FindIt: Publisher-Specific PDF Access
-------------------------------------

FindIt provides sophisticated publisher-specific URL resolution for academic papers:

Basic FindIt Usage
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from metapub import FindIt
   
   # Basic usage
   src = FindIt('25575644')  # PMID
   
   if src.url:
       print(f"PDF available: {src.url}")
       print(f"Journal: {src.pma.journal}")
   else:
       print(f"No access: {src.reason}")
       if src.backup_url:
           print(f"Backup URL: {src.backup_url}")

Advanced FindIt Options
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # With error retry
   src = FindIt(pmid='12345678', retry_errors=True)
   
   # NIH access mode
   src = FindIt(pmid='12345678', use_nih=True)
   
   # Debug mode for troubleshooting
   src = FindIt(pmid='12345678', debug=True)
   
   # Skip verification for speed
   src = FindIt(pmid='12345678', verify=False)

Embargo Detection
~~~~~~~~~~~~~~~~

.. code-block:: python

   from metapub import FindIt
   
   src = FindIt('25575644')
   
   # Check embargo status
   embargo_date = src.pma.history.get('pmc-release', None)
   is_embargoed = False
   
   if src.reason.startswith("PAYWALL") and "embargo" in src.reason:
       is_embargoed = True
       print(f"Article is embargoed until: {embargo_date}")

Publisher Coverage Examples
~~~~~~~~~~~~~~~~~~~~~~~~~~

FindIt handles many publisher-specific patterns:

.. code-block:: python

   # Test PMIDs for different publishers
   test_pmids = {
       'Nature': ['16419642', '18830250', '12187393'],
       'BMC': ['25943194', '20170543', '25927199'], 
       'ScienceDirect': ['20000000', '25735572', '24565554'],
       'Wiley': ['14981756', '10474162', '10470409'],
       'JAMA': ['25742465', '23754022', '25739104']
   }
   
   for publisher, pmids in test_pmids.items():
       print(f"\n{publisher} results:")
       for pmid in pmids:
           src = FindIt(pmid)
           status = "✓" if src.url else "✗"
           print(f"  {status} {pmid}: {src.pma.journal}")

Clinical and Medical Genetics Queries
-------------------------------------

Specialized Search Types
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from metapub import PubMedFetcher
   
   fetch = PubMedFetcher()
   
   # Clinical queries with categories
   pmids = fetch.pmids_for_clinical_query(
       'Global developmental delay', 
       'etiology', 
       'broad'  # or 'narrow'
   )
   
   # Medical genetics queries
   pmids = fetch.pmids_for_medical_genetics_query(
       'Brugada Syndrome',
       'diagnosis'  # or 'genetic_counseling', 'prognosis'
   )

Advanced Citation Lookup
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Find article by detailed citation
   params = {
       'jtitle': 'Genetics in Medicine',
       'year': 2017,
       'volume': 19, 
       'first_page': 1105,
       'aulast': 'Nykamp'
   }
   
   pmids = fetch.pmids_for_citation(**params)
   
   # Alternative parameter names
   params2 = {
       'journal': 'Nature',
       'year': 2023,
       'volume': 615,
       'spage': 123,  # start page
       'authors': 'Smith; Jones; Brown'
   }

MedGen and ClinVar Integration
-----------------------------

Disease-Gene Mapping
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from metapub import MedGenFetcher
   
   mg = MedGenFetcher()
   
   # Disease to gene mapping
   term = "diabetes"
   uids = mg.uids_by_term(term)
   
   for uid in uids[:5]:  # First 5 results
       concept = mg.concept_by_uid(uid)
       print(f"CUI: {concept.cui}")
       print(f"Name: {concept.name}")
       print(f"Definition: {concept.definition}")
       
       # Get related PMIDs
       pmids = mg.pubmeds_for_cui(concept.cui)
       print(f"Related articles: {len(pmids)}")

Gene-Condition Mapping
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Gene to condition mapping
   gene = "CFTR"
   uids = mg.uids_by_term(f"{gene}[gene]")
   
   for uid in uids:
       concept = mg.concept_by_uid(uid)
       if concept.cui:
           print(f"Gene {gene} associated with: {concept.name}")

ClinVar Variant Analysis
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from metapub import ClinVarFetcher
   
   cv = ClinVarFetcher()
   
   # Get variant by ID
   variant = cv.variant('123456')
   
   print(f"Variation name: {variant.variation_name}")
   print(f"HGVS notation: {variant.hgvs_c}")
   print(f"Clinical significance: {variant.clinical_significance}")
   print(f"Molecular consequences: {variant.molecular_consequences}")

CrossRef Integration
-------------------

DOI Resolution with Fallbacks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from metapub import PubMedFetcher, CrossRefFetcher
   
   fetch = PubMedFetcher()
   CR = CrossRefFetcher()
   
   def get_doi_with_fallback(pmid):
       # Try PubMed first
       pma = fetch.article_by_pmid(pmid)
       if pma.doi:
           return pma.doi
       
       # Fallback to CrossRef
       work = CR.article_by_pma(pma)
       if work and work.score > 80:  # High confidence match
           return work.doi
       
       return None

Batch Processing with CrossRef
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import csv
   from metapub.exceptions import InvalidPMID
   
   pmids = ['12345678', '23456789', '34567890']
   
   with open('pmid_doi_mapping.csv', 'w', newline='') as csvfile:
       writer = csv.writer(csvfile)
       writer.writerow(['PMID', 'DOI', 'Title', 'Status'])
       
       for pmid in pmids:
           try:
               pma = fetch.article_by_pmid(pmid)
               doi = get_doi_with_fallback(pmid)
               writer.writerow([pmid, doi or '', pma.title, 'SUCCESS'])
           except InvalidPMID:
               writer.writerow([pmid, '', '', 'INVALID_PMID'])
           except Exception as e:
               writer.writerow([pmid, '', '', f'ERROR: {e}'])

Error Handling Patterns
-----------------------

Robust Error Handling
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from metapub.exceptions import MetaPubError, InvalidPMID
   import logging
   
   # Configure logging for debugging
   logging.getLogger('metapub').setLevel(logging.DEBUG)
   logging.getLogger('requests').setLevel(logging.WARNING)
   
   def safe_article_fetch(pmid):
       try:
           article = fetch.article_by_pmid(pmid)
           return article
       except InvalidPMID:
           print(f"Invalid PMID: {pmid}")
           return None
       except MetaPubError as e:
           print(f"MetaPub error for {pmid}: {e}")
           return None
       except Exception as e:
           print(f"Unexpected error for {pmid}: {e}")
           return None

Network Error Recovery
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import time
   from requests.exceptions import RequestException
   
   def fetch_with_retry(pmid, max_retries=3):
       for attempt in range(max_retries):
           try:
               return fetch.article_by_pmid(pmid)
           except RequestException as e:
               if attempt < max_retries - 1:
                   print(f"Network error, retrying in 5 seconds... ({attempt + 1}/{max_retries})")
                   time.sleep(5)
               else:
                   raise e

Performance Optimization
------------------------

Caching System Overview
~~~~~~~~~~~~~~~~~~~~~~

Metapub includes a sophisticated caching system designed to minimize API requests and improve performance. The system has evolved to use SQLite-based persistent storage with thread-safe operations.

**Key Features:**

- **Persistent Storage**: SQLite database for responses that survive process restarts
- **Thread Safety**: All cache operations are thread-safe using locks
- **NCBI Compliance**: Automatic rate limiting respects NCBI guidelines (3 req/sec without API key, 10 req/sec with)
- **Response Validation**: Only valid XML responses are cached; HTML error pages are rejected
- **Legacy Compatibility**: Works with existing cache files from previous versions

Cache Configuration
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import os
   from metapub import PubMedFetcher
   from metapub.ncbi_client import NCBIClient
   
   # Method 1: Environment variables (traditional)
   os.environ['METAPUB_CACHE_DIR'] = '/path/to/large/cache'
   os.environ['NCBI_API_KEY'] = 'your_api_key_here'
   
   fetch = PubMedFetcher()
   
   # Method 2: Direct NCBIClient usage (new system)
   client = NCBIClient(
       api_key='your_api_key_here',
       cache_path='/path/to/cache/ncbi_cache.db',
       requests_per_second=10,  # Will be capped to NCBI limits
       tool='my_research_tool',
       email='researcher@university.edu'
   )

Understanding Cache Behavior
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from metapub.ncbi_client import SimpleCache
   
   # Direct cache manipulation
   cache = SimpleCache('/path/to/cache.db')
   
   # Cache uses URL + parameters as keys
   url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
   params = {'db': 'pubmed', 'id': '12345678', 'retmode': 'xml'}
   
   # Check if response is cached
   cached_response = cache.get(url, params)
   if cached_response:
       print("Response found in cache")
   else:
       print("Fresh API request needed")
   
   # Manual cache storage (normally done automatically)
   cache.set(url, params, xml_response_string)

Rate Limiting and Performance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from metapub.ncbi_client import RateLimiter
   import time
   
   # Understanding rate limits
   rate_limiter = RateLimiter(requests_per_second=3)  # Without API key
   
   start_time = time.time()
   for i in range(5):
       rate_limiter.wait_if_needed()
       print(f"Request {i+1} at {time.time() - start_time:.2f}s")
       # Your API request here
   
   # Output shows requests spaced by ~0.33 seconds (3 per second)

Cache Database Schema
~~~~~~~~~~~~~~~~~~~~

The cache uses a simple SQLite schema compatible with existing cache files:

.. code-block:: sql
   
   CREATE TABLE cache (
       key BLOB PRIMARY KEY,      -- URL + sorted parameters
       value BLOB,                -- Cached response data
       created INTEGER,           -- Unix timestamp
       value_compressed BOOL DEFAULT 0  -- Legacy compression flag
   );

Advanced Cache Management
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import sqlite3
   import os
   from metapub.cache_utils import get_cache_path, cleanup_dir
   
   # Inspect cache contents
   cache_path = get_cache_path()
   if cache_path and os.path.exists(cache_path):
       with sqlite3.connect(cache_path) as conn:
           # Count cached entries
           count = conn.execute("SELECT COUNT(*) FROM cache").fetchone()[0]
           print(f"Cache contains {count} entries")
           
           # Find oldest entries
           oldest = conn.execute(
               "SELECT created FROM cache ORDER BY created LIMIT 1"
           ).fetchone()
           if oldest:
               import datetime
               oldest_date = datetime.datetime.fromtimestamp(oldest[0])
               print(f"Oldest entry: {oldest_date}")
   
   # Clear entire cache directory
   if cache_path:
       cache_dir = os.path.dirname(cache_path)
       cleanup_dir(cache_dir)
       print("Cache cleared")

Traditional vs Modern Caching System
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Traditional System:**
- Dictionary-style access with pickle serialization
- Backward compatible with existing cache files
- Used by PubMedFetcher and other high-level classes

**Modern System (NCBIClient):**
- URL-based caching with parameter normalization
- JSON serialization for complex objects
- Better thread safety and error handling
- Validation prevents caching of error responses

.. code-block:: python

   # Traditional style (still supported)
   from metapub import PubMedFetcher
   fetch = PubMedFetcher()  # Uses traditional caching
   
   # Modern style (recommended for new code)
   from metapub.ncbi_client import NCBIClient
   client = NCBIClient(cache_path='/path/to/cache.db')
   response = client.efetch(db='pubmed', id='12345678')

Caching Strategies

Batch Processing Optimization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Process PMIDs in batches
   def process_pmids_batch(pmids, batch_size=100):
       results = []
       
       for i in range(0, len(pmids), batch_size):
           batch = pmids[i:i + batch_size]
           print(f"Processing batch {i//batch_size + 1}...")
           
           for pmid in batch:
               try:
                   article = fetch.article_by_pmid(pmid)
                   results.append((pmid, article))
               except Exception as e:
                   print(f"Error with {pmid}: {e}")
           
           # Rate limiting between batches
           time.sleep(1)
       
       return results

Preloading and Cache Warming
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Preload FindIt cache for a list of PMIDs
   def preload_findit_cache(pmid_file):
       with open(pmid_file, 'r') as f:
           pmids = [line.strip() for line in f if line.strip()]
       
       print(f"Preloading FindIt cache for {len(pmids)} PMIDs...")
       
       for i, pmid in enumerate(pmids):
           if i % 100 == 0:
               print(f"Progress: {i}/{len(pmids)}")
           
           try:
               src = FindIt(pmid)
               # Just accessing it loads into cache
           except Exception as e:
               print(f"Error preloading {pmid}: {e}")

URL Reverse Engineering
----------------------

Extract Identifiers from URLs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from metapub.urlreverse import UrlReverse
   
   # Extract DOI and PMID from URLs
   urls = [
       'https://doi.org/10.1038/nature12373',
       'https://pubmed.ncbi.nlm.nih.gov/12345678/',
       'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3458974/'
   ]
   
   for url in urls:
       urlrev = UrlReverse(url)
       print(f"URL: {url}")
       print(f"DOI: {urlrev.doi}")
       print(f"PMID: {urlrev.pmid}")
       print(f"PMC: {urlrev.pmcid}")
       print("Steps taken:")
       for step in urlrev.steps:
           print(f"  * {step}")
       print()

Troubleshooting and Debugging
----------------------------

Common Issues and Solutions
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Enable detailed logging
   import logging
   logging.basicConfig(level=logging.DEBUG)
   
   # Check NCBI service health
   from metapub.ncbi_health_check import main as health_check
   health_check()  # Run health check
   
   # Validate PMIDs before processing
   import re
   pmid_pattern = re.compile(r'^\d+$')
   
   def is_valid_pmid(pmid):
       return pmid_pattern.match(str(pmid)) is not None
   
   # Clear cache if having issues
   import shutil
   from metapub.cache_utils import get_cache_path
   
   cache_dir = get_cache_path()
   if os.path.exists(cache_dir):
       shutil.rmtree(cache_dir)
       print(f"Cleared cache directory: {cache_dir}")