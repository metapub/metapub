Examples
========

Advanced Search Patterns
-----------------------

Complex PubMed Queries
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from metapub import PubMedFetcher
   
   fetch = PubMedFetcher()
   
   # Search with date range
   pmids = fetch.pmids_for_query(
       query='cancer treatment',
       since='2020/01/01',
       until='2023/12/31',
       retmax=100
   )
   
   # Search specific journal
   pmids = fetch.pmids_for_query(
       journal='Nature',
       year=2023,
       retmax=50
   )
   
   # PMC-only articles
   pmids = fetch.pmids_for_query(
       query='open access',
       pmc_only=True,
       retmax=25
   )

Citation Lookup
~~~~~~~~~~~~~~

.. code-block:: python

   from metapub import PubMedFetcher
   
   fetch = PubMedFetcher()
   
   # Find article by citation details
   pmids = fetch.pmids_for_citation(
       jtitle='Nature',
       year=2023,
       volume=615,
       first_page=123,
       aulast='Smith'
   )

Working with Related Articles
----------------------------

.. code-block:: python

   from metapub import PubMedFetcher
   
   fetch = PubMedFetcher()
   
   # Get related articles
   related_pmids = fetch.related_pmids('12345678')
   
   print(f"Found {len(related_pmids)} related articles")
   
   for pmid in related_pmids[:5]:  # First 5
       article = fetch.article_by_pmid(pmid)
       print(f"{pmid}: {article.title}")

ClinVar Integration
------------------

.. code-block:: python

   from metapub import ClinVarFetcher
   
   cv = ClinVarFetcher()
   
   # Search for variants in a gene
   variants = cv.variants_for_gene('BRCA1')
   
   for variant in variants:
       print(f"Accession: {variant.accession}")
       print(f"Clinical Significance: {variant.clinical_significance}")
       print(f"Gene: {variant.gene_symbol}")

Batch Processing
---------------

Processing Multiple PMIDs
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from metapub import PubMedFetcher
   import csv
   
   fetch = PubMedFetcher()
   pmids = ['12345678', '23456789', '34567890']
   
   # Export to CSV
   with open('articles.csv', 'w', newline='') as csvfile:
       writer = csv.writer(csvfile)
       writer.writerow(['PMID', 'Title', 'Journal', 'Year', 'DOI'])
       
       for pmid in pmids:
           try:
               article = fetch.article_by_pmid(pmid)
               writer.writerow([
                   pmid,
                   article.title,
                   article.journal,
                   article.year,
                   article.doi
               ])
           except Exception as e:
               print(f"Error processing {pmid}: {e}")

Text Mining
----------

Extracting DOIs from Text
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from metapub.text_mining import find_doi_in_string
   
   text = """The study (doi:10.1038/nature12373) shows that...
   Another reference is https://doi.org/10.1126/science.1234567"""
   
   dois = find_doi_in_string(text)
   print(f"Found DOIs: {dois}")

Finding PMIDs in Text
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from metapub.text_mining import find_pmid_in_string
   
   text = "See PMID: 12345678 and also PMID 23456789 for details."
   
   pmids = find_pmid_in_string(text)
   print(f"Found PMIDs: {pmids}")

Caching and Performance
----------------------

Custom Cache Directory
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from metapub import PubMedFetcher
   import os
   
   # Set custom cache directory
   os.environ['METAPUB_CACHE_DIR'] = '/path/to/my/cache'
   
   fetch = PubMedFetcher()
   # Subsequent requests will use the custom cache

API Key Configuration
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import os
   from metapub import PubMedFetcher
   
   # Set API key for higher rate limits
   os.environ['NCBI_API_KEY'] = 'your_api_key_here'
   
   fetch = PubMedFetcher()
   # Now you can make more requests per second

Error Handling
-------------

Handling Network Issues
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from metapub import PubMedFetcher
   from metapub.exceptions import MetaPubError
   
   fetch = PubMedFetcher()
   
   try:
       article = fetch.article_by_pmid('12345678')
       print(article.title)
   except MetaPubError as e:
       print(f"Metapub error: {e}")
   except Exception as e:
       print(f"Unexpected error: {e}")

Validating PMIDs
~~~~~~~~~~~~~~~

.. code-block:: python

   from metapub.validate import is_valid_pmid
   
   pmids = ['12345678', 'invalid', '23456789']
   
   valid_pmids = [pmid for pmid in pmids if is_valid_pmid(pmid)]
   print(f"Valid PMIDs: {valid_pmids}")
