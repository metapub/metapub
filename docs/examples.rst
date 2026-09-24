Examples
========

Advanced Search Patterns
-----------------------

Complex PubMed Queries
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from metapub import PubMedFetcher
   
   fetch = PubMedFetcher()
   
   # Search with date range (searches publication date by default)
   pmids = fetch.pmids_for_query(
       query='cancer treatment',
       since='2020/01/01',
       until='2023/12/31',
       retmax=100
   )

   # Search a different date field: 'pdat' (publication date, the default),
   # 'edat' (entered PubMed), 'crdt' (record created), 'mdat' (last revised).
   # A record's creation date can be years from its publication date, so this
   # materially changes what comes back.
   pmids = fetch.pmids_for_query(
       query='cancer treatment',
       since='2020/01/01',
       until='2023/12/31',
       datetype='crdt',
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

Knowing when a result was truncated
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``pmids_for_query`` returns at most ``retmax`` pmids (250 by default), however
many records matched. The returned list carries the real total on
``total_count``, and a truncated result also logs a warning::

   pmids = fetch.pmids_for_query(author='Smith JA')
   len(pmids)           # 250 -- one page
   pmids.total_count    # 3922 -- the whole result set

This matters most for batch harvesting, where one prolific author or a loose
search term quietly caps at 250 and the gap looks like a metapub-vs-PubMed
discrepancy rather than a paging limit.

To collect everything, raise ``retmax`` past ``total_count`` and make a single
request::

   pmids = fetch.pmids_for_query(author='Smith JA')
   if pmids.total_count > len(pmids):
       pmids = fetch.pmids_for_query(author='Smith JA', retmax=pmids.total_count)

Prefer this over paging with ``retstart``. Results are currently sorted by
relevance, and that ordering is not stable between requests, so paging the same
query can return a record on two pages and omit another entirely (see issue
#183). A single large request has no such problem.

Date ranges are fuzzier than they look
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A date-range search will sometimes hand back articles whose printed date sits
outside the window you asked for. This is usually not a bug in metapub or in your
query -- it is how PubMed matches dates. Three separate effects are at work, and
it is worth knowing which one you are looking at before you go hunting.

**1. Imprecise publication dates are normalized to the start of their period.**

Plenty of records carry only a month ("2025 Jul"), only a year ("2025"), or even a
span ("2025 Jul-Dec"). PubMed resolves these to the first day of the period, so a
record dated "2025 Jul" behaves as though it were published on 2025/07/01. The
practical effect is that the first of any month acts as a magnet::

   ("2025/07/01"[DP] : "2025/07/01"[DP])     ->  74,332 records   (one day)
   ("2025/07/14"[DP] : "2025/07/15"[DP])     ->  12,523 records   (two days)

A single day at the start of a month outranks a two-day window mid-month roughly
six to one, because every month-precision record in July piles onto July 1st. If
your range begins on the 1st -- ``since='2026/04/01'`` -- you are pulling in every
record dated merely "2026 Apr", whatever day it actually appeared.

**2. Publication date means electronic or print, whichever matches.**

``[DP]`` indexes both. A paper published online in May and appearing in the
September print issue matches a May window, but reports ``PubDate`` as September::

   PMID 42298374   PubDate=2026 Sep    EPubDate=2026 Jun 15
   PMID 42136365   PubDate=2026 Aug 1  EPubDate=2026 May 15

Both are legitimately inside an April-June window. Reading ``article.year`` back
and comparing it to your range will make them look wrong when they are not.

**3. The other date fields drift much further.**

``datetype='crdt'`` and ``'edat'`` search record-keeping dates, not bibliographic
ones. A back-catalog deposit can be created in PubMed decades after publication,
so a single quarter of ``crdt`` routinely contains papers from the 1990s. Use
these only when you specifically want "what did PubMed ingest recently".

If you need the window enforced exactly, filter after the fact on the article's own
dates rather than trusting the search to do it::

   pmids = fetch.pmids_for_query(author='Smith JA',
                                 since='2026/04/01', until='2026/06/30')
   articles = [fetch.article_by_pmid(p) for p in pmids]
   # then apply your own date predicate to article.history / article.year

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
