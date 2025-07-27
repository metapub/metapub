Data Fetcher Classes
===================

The core of Metapub consists of several fetcher classes that provide access to different biomedical databases. All fetchers use the Borg singleton pattern and include comprehensive caching.

PubMedFetcher
------------

.. currentmodule:: metapub

.. autoclass:: PubMedFetcher
   :members:
   :show-inheritance:

The PubMedFetcher is the primary interface for accessing PubMed literature. It provides methods for:

* **Article retrieval** by PMID, DOI, or PMC ID
* **Literature searches** with complex query support
* **Citation-based lookups** for bibliographic matching
* **Related article discovery** using NCBI's eLink service

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

API Key Configuration
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import os
   
   # Set NCBI API key for higher rate limits
   os.environ['NCBI_API_KEY'] = 'your_api_key_here'
   
   # All fetchers will automatically use the API key
   fetch = PubMedFetcher()

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