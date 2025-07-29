API Overview
============

Metapub provides a comprehensive Python API for accessing biomedical literature and databases. The library is organized into several core modules, each serving specific functionality.

Core Modules
------------

Data Retrieval Classes
~~~~~~~~~~~~~~~~~~~~~~

These are the primary classes for fetching data from various NCBI databases:

.. currentmodule:: metapub

.. autosummary::
   :toctree: _autosummary
   :template: class.rst

   PubMedFetcher
   MedGenFetcher
   ClinVarFetcher
   CrossRefFetcher

**PubMedFetcher**
   Primary interface for PubMed/NCBI literature searches. Supports article retrieval by PMID, DOI, PMC ID, and complex query searches.

**MedGenFetcher** 
   Access to NCBI's MedGen database for medical genetics concepts, disease-gene relationships, and clinical phenotypes.

**ClinVarFetcher**
   Interface to ClinVar database for clinical significance of genetic variants and variant-literature associations.

**CrossRefFetcher**
   CrossRef API integration for DOI resolution and publication metadata when PubMed data is incomplete.

Data Model Classes
~~~~~~~~~~~~~~~~~

These classes represent structured data returned by the fetcher classes:

.. autosummary::
   :toctree: _autosummary
   :template: class.rst

   PubMedArticle
   MedGenConcept
   ClinVarVariant
   PubMedAuthor

**PubMedArticle**
   Rich representation of a scientific article with automatic parsing of titles, authors, abstracts, MeSH terms, and bibliographic details.

**MedGenConcept**
   Medical genetics concept with CUI identifiers, definitions, synonyms, and related literature.

**ClinVarVariant**
   Clinical variant with HGVS notation, clinical significance, molecular consequences, and supporting evidence.

Full-Text Discovery
~~~~~~~~~~~~~~~~~~

.. autosummary::
   :toctree: _autosummary
   :template: class.rst

   findit.FindIt

**FindIt**
   Sophisticated system for locating full-text PDFs using publisher-specific strategies. Supports 15+ major publishers with embargo detection and legal access verification.

Utility Functions
~~~~~~~~~~~~~~~~

Text Mining and Validation
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. currentmodule:: metapub.text_mining

.. autosummary::
   :toctree: _autosummary

   find_doi_in_string
   find_pmid_in_string
   
.. currentmodule:: metapub.validate

.. autosummary::
   :toctree: _autosummary
   
   is_valid_pmid

Conversion and Citation
^^^^^^^^^^^^^^^^^^^^^^

.. currentmodule:: metapub.convert

.. autosummary::
   :toctree: _autosummary

   pmid2doi
   doi2pmid

.. currentmodule:: metapub.cite

.. autosummary::
   :toctree: _autosummary

   format_citation

Error Handling
~~~~~~~~~~~~~

.. currentmodule:: metapub.exceptions

.. autosummary::
   :toctree: _autosummary
   :template: exception.rst

   MetaPubError
   InvalidPMID
   NCBIServiceError

Common Usage Patterns
--------------------

Basic Article Retrieval
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from metapub import PubMedFetcher
   
   # Initialize fetcher (singleton pattern)
   fetch = PubMedFetcher()
   
   # Get article by PMID
   article = fetch.article_by_pmid('12345678')
   print(f"{article.title} - {article.journal} ({article.year})")

Literature Search
~~~~~~~~~~~~~~~~

.. code-block:: python

   # Search for articles
   pmids = fetch.pmids_for_query('machine learning genomics', retmax=50)
   
   # Process results
   for pmid in pmids:
       article = fetch.article_by_pmid(pmid)
       print(f"PMID {pmid}: {article.title}")

Full-Text Discovery
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from metapub import FindIt
   
   # Find PDF for an article
   src = FindIt('12345678')  # PMID
   
   if src.url:
       print(f"PDF available: {src.url}")
   else:
       print(f"No access: {src.reason}")

Medical Genetics Research
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from metapub import MedGenFetcher, ClinVarFetcher
   
   # Research genetic condition
   mg = MedGenFetcher()
   concepts = mg.concepts_for_term('cystic fibrosis')
   
   # Find clinical variants
   cv = ClinVarFetcher()
   variants = cv.variants_for_gene('CFTR')

Architecture Notes
-----------------

Singleton Pattern
~~~~~~~~~~~~~~~~

Most fetcher classes use the Borg singleton pattern, meaning all instances share the same state and cache. This ensures efficient resource usage and consistent caching across your application.

Caching Strategy
~~~~~~~~~~~~~~~

- **SQLite-based caching** for all API responses
- **Configurable cache directories** via environment variables
- **TTL-based cache expiration** to ensure data freshness
- **Cache warming** capabilities for batch processing

Error Handling
~~~~~~~~~~~~~

- **Intelligent error diagnosis** distinguishes between service outages and code issues
- **Automatic retry logic** for transient network failures  
- **Comprehensive exception hierarchy** for specific error handling
- **Graceful degradation** when services are unavailable

API Keys and Rate Limiting
~~~~~~~~~~~~~~~~~~~~~~~~~

- **NCBI API key support** via environment variables for higher rate limits
- **Built-in rate limiting** respects NCBI guidelines
- **Request batching** for efficient bulk operations

See Also
--------

- :doc:`quickstart` - Getting started with basic usage
- :doc:`advanced` - Advanced patterns and publisher-specific features  
- :doc:`tutorials` - Complete workflows for research tasks
- :doc:`examples` - Practical code examples and patterns