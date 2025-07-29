Data Model Classes
==================

Metapub provides rich data model classes that represent structured information from biomedical databases. These classes automatically parse complex XML responses into convenient Python objects.

PubMedArticle
------------

.. currentmodule:: metapub

.. autoclass:: PubMedArticle
   :members:
   :show-inheritance:

The PubMedArticle class is the core data model for representing scientific articles from PubMed. It automatically parses NCBI XML into structured attributes.

Key Attributes
~~~~~~~~~~~~~

**Identifiers**
   - ``pmid`` - PubMed ID
   - ``doi`` - Digital Object Identifier  
   - ``pmc`` - PubMed Central ID
   - ``pii`` - Publisher Item Identifier

**Bibliographic Information**
   - ``title`` - Article title
   - ``journal`` - Journal name
   - ``year`` - Publication year
   - ``volume`` - Journal volume
   - ``issue`` - Journal issue
   - ``pages`` - Page range
   - ``first_page`` - Starting page
   - ``last_page`` - Ending page

**Authors and Content**
   - ``authors`` - List of :class:`PubMedAuthor` objects
   - ``author_list`` - Simple list of author name strings
   - ``abstract`` - Article abstract text
   - ``keywords`` - Author-supplied keywords

**Classification**
   - ``mesh_headings`` - Medical Subject Headings (MeSH) terms
   - ``publication_types`` - Type classifications (e.g., "Clinical Trial")
   - ``chemicals`` - Chemical substances mentioned

**Dates and History**
   - ``history`` - Publication timeline with key dates
   - ``received_date`` - When manuscript was received
   - ``accepted_date`` - When manuscript was accepted

Key Methods
~~~~~~~~~~

.. automethod:: PubMedArticle.__init__

.. automethod:: PubMedArticle.to_dict

**Properties**

.. autoproperty:: PubMedArticle.citation

.. autoproperty:: PubMedArticle.citation_html

Example Usage
~~~~~~~~~~~~

.. code-block:: python

   from metapub import PubMedFetcher
   
   fetch = PubMedFetcher()
   article = fetch.article_by_pmid('33157158')
   
   # Basic information
   print(f"Title: {article.title}")
   print(f"Journal: {article.journal} ({article.year})")
   print(f"Volume {article.volume}, Issue {article.issue}, Pages {article.pages}")
   
   # Authors
   print(f"Authors: {len(article.authors)}")
   for author in article.authors:
       print(f"  {author.lastname}, {author.firstname}")
   
   # Content
   print(f"Abstract: {article.abstract[:200]}...")
   print(f"Keywords: {', '.join(article.keywords) if article.keywords else 'None'}")
   
   # Classification
   print(f"MeSH terms: {', '.join(article.mesh_headings[:5])}")  # First 5
   print(f"Publication types: {', '.join(article.publication_types)}")
   
   # Generate citation
   print(f"Citation: {article.citation}")
   
   # Export to dictionary
   data = article.to_dict()

Book Articles
~~~~~~~~~~~~

PubMedArticle also handles NCBI book chapters with additional attributes:

.. code-block:: python

   # When pubmed_type == 'book'
   if article.pubmed_type == 'book':
       print(f"Book ID: {article.book_id}")
       print(f"Book title: {article.book_title}")
       print(f"Publisher: {article.book_publisher}")
       print(f"Editors: {', '.join(article.book_editors)}")

PubMedAuthor
-----------

.. autoclass:: PubMedAuthor
   :members:
   :show-inheritance:

Represents individual authors with detailed name parsing and affiliation information.

Key Attributes
~~~~~~~~~~~~~

**Name Components**
   - ``lastname`` - Author's last name
   - ``firstname`` - Author's first name  
   - ``initials`` - First/middle initials
   - ``suffix`` - Name suffix (Jr., Sr., etc.)

**Affiliation**
   - ``affiliation`` - Institutional affiliation

Example Usage
~~~~~~~~~~~~

.. code-block:: python

   # Access authors from an article
   for author in article.authors:
       print(f"Name: {author.lastname}, {author.firstname}")
       print(f"Initials: {author.initials}")
       if author.affiliation:
           print(f"Affiliation: {author.affiliation}")
       print(f"Full name: {str(author)}")  # Uses __str__ method

MedGenConcept
------------

.. autoclass:: MedGenConcept
   :members:
   :show-inheritance:

Represents medical genetics concepts from NCBI's MedGen database.

Key Attributes
~~~~~~~~~~~~~

**Identifiers**
   - ``cui`` - Concept Unique Identifier
   - ``uid`` - MedGen UID
   - ``name`` - Primary concept name

**Content**
   - ``definition`` - Concept definition
   - ``synonyms`` - Alternative names
   - ``semantic_types`` - Semantic classifications

**Relationships**
   - ``related_concepts`` - Related MedGen concepts
   - ``sources`` - Source vocabularies

Example Usage
~~~~~~~~~~~~

.. code-block:: python

   from metapub import MedGenFetcher
   
   mg = MedGenFetcher()
   concepts = mg.concepts_for_term('cystic fibrosis')
   
   for concept in concepts[:3]:  # First 3 results
       print(f"Name: {concept.name}")
       print(f"CUI: {concept.cui}")
       print(f"Definition: {concept.definition}")
       
       if concept.synonyms:
           print(f"Synonyms: {', '.join(concept.synonyms[:3])}")  # First 3
           
       print(f"Semantic types: {', '.join(concept.semantic_types)}")

ClinVarVariant
-------------

.. autoclass:: ClinVarVariant
   :members:
   :show-inheritance:

Represents genetic variants from NCBI's ClinVar database with clinical significance information.

Key Attributes
~~~~~~~~~~~~~

**Identifiers**
   - ``accession`` - ClinVar accession number
   - ``variation_id`` - Variation ID
   - ``allele_id`` - Allele ID

**Genomic Information**
   - ``hgvs_c`` - HGVS coding sequence notation
   - ``hgvs_p`` - HGVS protein sequence notation
   - ``hgvs_g`` - HGVS genomic notation
   - ``gene_symbol`` - Associated gene symbol
   - ``molecular_consequences`` - Predicted effects

**Clinical Data**
   - ``clinical_significance`` - Clinical interpretation
   - ``review_status`` - Review/evidence level
   - ``last_evaluated`` - Date of last evaluation

**Supporting Data**
   - ``submitters`` - Contributing organizations
   - ``conditions`` - Associated conditions/diseases
   - ``citations`` - Supporting literature

Example Usage
~~~~~~~~~~~~

.. code-block:: python

   from metapub import ClinVarFetcher
   
   cv = ClinVarFetcher()
   variant = cv.variant('12345')  # ClinVar ID
   
   print(f"Accession: {variant.accession}")
   print(f"Gene: {variant.gene_symbol}")
   print(f"HGVS notation: {variant.hgvs_c}")
   print(f"Clinical significance: {variant.clinical_significance}")
   print(f"Review status: {variant.review_status}")
   
   if variant.molecular_consequences:
       print(f"Molecular consequences: {', '.join(variant.molecular_consequences)}")
   
   if variant.conditions:
       print(f"Associated conditions: {', '.join(variant.conditions[:3])}")  # First 3

Data Model Utilities
-------------------

Validation Functions
~~~~~~~~~~~~~~~~~~

.. currentmodule:: metapub.validate

.. autofunction:: is_valid_pmid

.. autofunction:: is_valid_doi

Example usage:

.. code-block:: python

   from metapub.validate import is_valid_pmid, is_valid_doi
   
   # Validate PMIDs before processing
   pmids = ['12345678', 'invalid', '23456789', '']
   valid_pmids = [pmid for pmid in pmids if is_valid_pmid(pmid)]
   
   # Validate DOIs
   dois = ['10.1038/nature12373', 'invalid-doi', '10.1126/science.1234567']
   valid_dois = [doi for doi in dois if is_valid_doi(doi)]

Conversion Functions
~~~~~~~~~~~~~~~~~~

.. currentmodule:: metapub.convert

.. autofunction:: pmid2doi

.. autofunction:: doi2pmid

Example usage:

.. code-block:: python

   from metapub.convert import pmid2doi, doi2pmid
   
   # Convert PMID to DOI
   doi = pmid2doi('33157158')
   if doi:
       print(f"DOI: {doi}")
   
   # Convert DOI to PMID  
   pmid = doi2pmid('10.1038/nature12373')
   if pmid:
       print(f"PMID: {pmid}")

Working with Multiple Data Types
-------------------------------

Integration Example
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from metapub import PubMedFetcher, MedGenFetcher, ClinVarFetcher
   
   # Initialize fetchers
   fetch = PubMedFetcher()
   mg = MedGenFetcher()
   cv = ClinVarFetcher()
   
   # Research workflow: gene -> variants -> literature
   gene = 'BRCA1'
   
   # 1. Find genetic variants
   variant_ids = cv.ids_by_gene(gene, single_gene=True)
   
   # 2. Get MedGen concepts for the gene
   concepts = mg.concepts_for_term(f"{gene}[gene]")
   
   # 3. Collect all related literature
   all_pmids = set()
   
   # From variants
   for var_id in variant_ids[:5]:  # Limit for demo
       pmids = cv.pmids_for_id(var_id)
       all_pmids.update(pmids)
   
   # From MedGen concepts  
   for concept in concepts[:3]:  # Limit for demo
       pmids = mg.pubmeds_for_cui(concept.cui)
       all_pmids.update(pmids)
   
   # 4. Analyze the literature
   print(f"Found {len(all_pmids)} unique articles for {gene}")
   
   # Sample the articles
   for pmid in list(all_pmids)[:10]:  # First 10
       try:
           article = fetch.article_by_pmid(pmid)
           print(f"PMID {pmid}: {article.title}")
           print(f"  Journal: {article.journal} ({article.year})")
       except Exception as e:
           print(f"  Error with PMID {pmid}: {e}")

Serialization and Export
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import json
   import csv
   
   # Export article data to JSON
   articles_data = []
   for pmid in pmids:
       article = fetch.article_by_pmid(pmid)
       articles_data.append(article.to_dict())
   
   with open('articles.json', 'w') as f:
       json.dump(articles_data, f, indent=2, default=str)
   
   # Export to CSV
   with open('articles.csv', 'w', newline='') as csvfile:
       writer = csv.writer(csvfile)
       writer.writerow(['PMID', 'Title', 'Journal', 'Year', 'DOI', 'Authors'])
       
       for article_data in articles_data:
           writer.writerow([
               article_data['pmid'],
               article_data['title'],
               article_data['journal'],
               article_data['year'],
               article_data['doi'],
               '; '.join([str(author) for author in article_data['authors']])
           ])