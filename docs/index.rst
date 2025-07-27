Welcome to Metapub's documentation!
=====================================

.. image:: https://img.shields.io/pypi/dm/metapub
   :alt: PyPI - Monthly Downloads

Metapub is a Python library that provides python objects fetched via eutils 
that represent Pubmed papers and concepts found within the NCBI databases.

Metapub currently provides abstraction layers over Medgen, Pubmed, ClinVar, 
and CrossRef, and intends to encompass as many types of database lookups and 
summaries as can be provided via Eutils / Entrez.

Features
--------

* Build formatted citations easily from lists of PMIDs
* Generate valid LEGAL links to paper PDFs using FindIt, given a PMID or DOI
* Common text mining "batteries included" such as finding DOIs in text
* NCBI_API_KEY supported as environment variable
* PubMedArticle object is a privileged class across Metapub
* Widespread use of Logging so you can see what's going on under the hood
* Command line utilities for common tasks

Quick Start
-----------

Installation::

   pip install metapub

Basic usage::

   from metapub import PubMedFetcher
   
   fetch = PubMedFetcher()
   pmids = fetch.pmids_for_query('breast cancer', retmax=10)
   
   for pmid in pmids:
       article = fetch.article_by_pmid(pmid)
       print(f"{pmid}: {article.title}")

.. toctree::
   :maxdepth: 2
   :caption: User Guide:

   installation
   quickstart
   examples
   advanced
   tutorials

.. toctree::
   :maxdepth: 2
   :caption: API Reference:

   api_overview
   api_fetchers
   api_models
   api_findit
   api/modules

.. toctree::
   :maxdepth: 1
   :caption: Additional Information:

   changelog

