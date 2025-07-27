Data Fetcher Classes
===================

The core of Metapub consists of several fetcher classes that provide access to different biomedical databases. All fetchers use the Borg singleton pattern and include comprehensive caching.

**🔄 Borg Singleton Pattern**

Metapub fetchers use the Borg pattern, which means all instances of the same fetcher class share the same state (cache, configuration, etc.). This provides several benefits:

- **Shared cache:** Multiple ``PubMedFetcher()`` instances automatically share cached data
- **Consistent configuration:** API keys and settings apply across all instances  
- **Memory efficiency:** No duplicate caches or redundant API calls
- **Consistency:** Safe to use across different parts of your application

.. code-block:: python

   # These two fetchers share the same cache and configuration
   fetch1 = PubMedFetcher()
   fetch2 = PubMedFetcher()
   
   # Article cached by fetch1 is immediately available to fetch2
   article = fetch1.article_by_pmid('12345678')
   same_article = fetch2.article_by_pmid('12345678')  # Uses cache, no API call

PubMedFetcher
------------

.. currentmodule:: metapub

.. autoclass:: PubMedFetcher
   :members:
   :show-inheritance:

The PubMedFetcher is the primary interface for accessing PubMed literature via NCBI's E-utilities API. It provides methods for:

* **Article retrieval** by PMID, DOI, or PMC ID
* **Literature searches** with complex query support
* **Citation-based lookups** for bibliographic matching
* **Related article discovery** using NCBI's eLink service

**NCBI E-utilities Documentation:** `PubMed E-utilities <https://www.ncbi.nlm.nih.gov/books/NBK25501/>`_ | `PubMed Search Field Descriptions <https://pubmed.ncbi.nlm.nih.gov/help/>`_

Key Methods
~~~~~~~~~~

.. automethod:: PubMedFetcher.__init__

.. automethod:: PubMedFetcher.article_by_pmid

.. automethod:: PubMedFetcher.article_by_doi

.. automethod:: PubMedFetcher.article_by_pmcid

.. automethod:: PubMedFetcher.pmids_for_query

.. automethod:: PubMedFetcher.pmids_for_citation

.. automethod:: PubMedFetcher.related_pmids

Example Usage
~~~~~~~~~~~~

.. code-block:: python

   from metapub import PubMedFetcher
   
   # Initialize fetcher
   fetch = PubMedFetcher()
   
   # Get specific article
   article = fetch.article_by_pmid('33157158')
   print(f"Title: {article.title}")
   print(f"Journal: {article.journal}")
   print(f"DOI: {article.doi}")
   
   # Search for articles
   pmids = fetch.pmids_for_query(
       query='CRISPR gene editing',
       since='2020/01/01',
       retmax=100
   )
   
   # Citation-based lookup
   citation_pmids = fetch.pmids_for_citation(
       journal='Nature',
       year=2023,
       volume=615,
       first_page=123,
       aulast='Smith'
   )

MedGenFetcher  
------------

.. autoclass:: MedGenFetcher
   :members:
   :show-inheritance:

The MedGenFetcher provides access to NCBI's MedGen database for medical genetics concepts and disease-gene relationships.

**NCBI MedGen Documentation:** `MedGen Database <https://www.ncbi.nlm.nih.gov/medgen/>`_ | `MedGen Help <https://www.ncbi.nlm.nih.gov/books/NBK159970/>`_

Key Methods
~~~~~~~~~~

.. automethod:: MedGenFetcher.__init__

.. automethod:: MedGenFetcher.uids_by_term

.. automethod:: MedGenFetcher.concept_by_uid

.. automethod:: MedGenFetcher.concept_by_cui

.. automethod:: MedGenFetcher.uid_for_cui

.. automethod:: MedGenFetcher.pubmeds_for_cui

Example Usage
~~~~~~~~~~~~

.. code-block:: python

   from metapub import MedGenFetcher
   
   # Initialize fetcher
   mg = MedGenFetcher()
   
   # Search for genetic condition
   uids = mg.uids_by_term('Brugada syndrome')
   
   # Get detailed concept information
   for uid in uids[:3]:  # First 3 results
       concept = mg.concept_by_uid(uid)
       print(f"Name: {concept.name}")
       print(f"CUI: {concept.cui}")
       print(f"Definition: {concept.definition}")
       
       # Get related literature
       pmids = mg.pubmeds_for_cui(concept.cui)
       print(f"Related papers: {len(pmids)}")

ClinVarFetcher
-------------

.. autoclass:: ClinVarFetcher
   :members:
   :show-inheritance:

The ClinVarFetcher provides access to NCBI's ClinVar database for clinical significance of genetic variants.

**NCBI ClinVar Documentation:** `ClinVar Database <https://www.ncbi.nlm.nih.gov/clinvar/>`_ | `ClinVar API Guide <https://www.ncbi.nlm.nih.gov/clinvar/docs/api/>`_

Key Methods
~~~~~~~~~~

.. automethod:: ClinVarFetcher.__init__

.. automethod:: ClinVarFetcher.ids_by_gene

.. automethod:: ClinVarFetcher.variant

.. automethod:: ClinVarFetcher.pmids_for_id

.. automethod:: ClinVarFetcher.pmids_for_hgvs

Example Usage
~~~~~~~~~~~~

.. code-block:: python

   from metapub import ClinVarFetcher
   
   # Initialize fetcher
   cv = ClinVarFetcher()
   
   # Find variants for a gene
   variant_ids = cv.ids_by_gene('BRCA1', single_gene=True)
   
   # Get detailed variant information
   for var_id in variant_ids[:5]:  # First 5 variants
       variant = cv.variant(var_id)
       print(f"Accession: {variant.accession}")
       print(f"HGVS: {variant.hgvs_c}")
       print(f"Clinical significance: {variant.clinical_significance}")
       print(f"Molecular consequences: {variant.molecular_consequences}")
       
       # Get supporting literature
       pmids = cv.pmids_for_id(var_id)
       print(f"Supporting papers: {len(pmids)}")

CrossRefFetcher
--------------

.. autoclass:: CrossRefFetcher
   :members:
   :show-inheritance:

The CrossRefFetcher provides access to CrossRef's API for DOI resolution and publication metadata when PubMed data is incomplete.

**CrossRef API Documentation:** `CrossRef REST API <https://github.com/CrossRef/rest-api-doc>`_ | `Works API Reference <https://api.crossref.org/swagger-ui/index.html>`_

Example Usage
~~~~~~~~~~~~

.. code-block:: python

   from metapub import CrossRefFetcher, PubMedFetcher
   
   # Initialize fetchers
   fetch = PubMedFetcher()
   cr = CrossRefFetcher()
   
   # Get article that might be missing DOI in PubMed
   article = fetch.article_by_pmid('12345678')
   
   if not article.doi:
       # Try CrossRef as fallback
       work = cr.article_by_pma(article)
       if work and work.score > 80:  # High confidence match
           print(f"Found DOI via CrossRef: {work.doi}")
           print(f"Match score: {work.score}")

Advanced Configuration
---------------------

Custom Cache Directory
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import os
   
   # Set custom cache directory
   os.environ['METAPUB_CACHE_DIR'] = '/path/to/large/cache'
   
   # Or specify per-fetcher
   fetch = PubMedFetcher(cachedir='/custom/cache/path')

NCBI API Key Setup
~~~~~~~~~~~~~~~~~

**📈 Why Use an API Key?**

NCBI provides free API keys that increase your rate limits from 3 to 10 requests per second, essential for production applications and large-scale data collection.

**🔑 Getting Your API Key**

1. **Apply for a key:** `NCBI API Key Registration <https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/>`_
2. **No approval needed** - keys are issued immediately
3. **Free for academic and commercial use**

**⚙️ Configuration Options**

.. code-block:: python

   import os
   
   # Method 1: Environment variable (recommended)
   os.environ['NCBI_API_KEY'] = 'your_api_key_here'
   
   # Method 2: Direct parameter
   fetch = PubMedFetcher(api_key='your_api_key_here')
   
   # Method 3: Config file
   # Create ~/.metapub/config with:
   # [DEFAULT]
   # ncbi_api_key = your_api_key_here

**🚀 Rate Limit Benefits**

- **Without API key:** 3 requests/second
- **With API key:** 10 requests/second
- **Large datasets:** 3x faster processing
- **Production reliability:** Reduced throttling errors

Error Handling Patterns
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from metapub.exceptions import MetaPubError, InvalidPMID, NCBIServiceError
   
   try:
       article = fetch.article_by_pmid('12345678')
   except InvalidPMID:
       print("Invalid PMID provided")
   except NCBIServiceError as e:
       print(f"NCBI service issue: {e.user_message}")
       print(f"Suggested actions: {e.suggested_actions}")
   except MetaPubError as e:
       print(f"General MetaPub error: {e}")

Performance Considerations
-------------------------

Batch Processing
~~~~~~~~~~~~~~~

.. code-block:: python

   # Process large lists efficiently
   pmids = ['12345678', '23456789', '34567890']  # ... many more
   
   for i, pmid in enumerate(pmids):
       if i % 100 == 0:
           print(f"Progress: {i}/{len(pmids)}")
           
       try:
           article = fetch.article_by_pmid(pmid)
           # Process article...
       except Exception as e:
           print(f"Error with {pmid}: {e}")
           continue

Cache Warming
~~~~~~~~~~~~

.. code-block:: python

   # Pre-warm cache for known PMIDs
   def warm_cache(pmid_list):
       for pmid in pmid_list:
           try:
               # Just accessing loads into cache
               article = fetch.article_by_pmid(pmid)
           except Exception:
               continue