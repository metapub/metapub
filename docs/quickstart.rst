Quick Start Guide
=================

This guide will help you get started with Metapub quickly.

Basic PubMed Search
------------------

.. code-block:: python

   from metapub import PubMedFetcher
   
   # Create a fetcher instance
   fetch = PubMedFetcher()
   
   # Search for papers on a topic
   pmids = fetch.pmids_for_query('machine learning', retmax=10)
   
   # Get article details
   for pmid in pmids:
       article = fetch.article_by_pmid(pmid)
       print(f"PMID {pmid}: {article.title}")
       print(f"Authors: {', '.join([str(a) for a in article.authors])}")
       print(f"Journal: {article.journal}")
       print("---")

Retrieving Article by PMID
-------------------------

.. code-block:: python

   from metapub import PubMedFetcher
   
   fetch = PubMedFetcher()
   article = fetch.article_by_pmid('12345678')
   
   print(f"Title: {article.title}")
   print(f"Abstract: {article.abstract}")
   print(f"DOI: {article.doi}")
   print(f"Publication Date: {article.year}")

Finding Full Text with FindIt
----------------------------

.. code-block:: python

   from metapub import FindIt
   
   # Try to find full text for a paper
   src = FindIt('12345678')  # PMID
   
   if src.url:
       print(f"Full text available at: {src.url}")
   else:
       print(f"Could not find full text: {src.reason}")

Working with MedGen
------------------

.. code-block:: python

   from metapub import MedGenFetcher
   
   mg = MedGenFetcher()
   
   # Search for a condition
   concepts = mg.concepts_for_term('diabetes')
   
   for concept in concepts:
       print(f"CUI: {concept.cui}")
       print(f"Name: {concept.name}")
       print(f"Definition: {concept.definition}")

Command Line Tools
-----------------

Metapub includes several command line utilities:

.. code-block:: bash

   # Convert between IDs
   convert pmid2doi 12345678
   convert doi2pmid 10.1038/nature12373
   
   # Get article information
   pubmed_article 12345678
   
   # Check NCBI health
   ncbi_health_check

Next Steps
----------

* Check out the :doc:`api/modules` for detailed API documentation
* See :doc:`examples` for more advanced usage patterns
* Read about specific modules like :doc:`api/metapub.findit` for FindIt functionality
