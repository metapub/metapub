PubMedArticle Properties Reference
=================================

The PubMedArticle class provides access to a comprehensive set of properties extracted from NCBI PubMed XML data. This document details all available properties, organized by category and type.

Overview
--------

PubMedArticle objects automatically detect whether they represent a journal article or book chapter and populate properties accordingly. The ``pubmed_type`` attribute indicates the type ('article' or 'book').

Publication Date Access
-----------------------

**New in this version:** The ``pubdate`` property provides normalized access to publication dates.

**pubdate**
    Normalized publication date as a datetime object. Returns the best available date from:
    
    1. Article PubDate (Year/Month/Day or MedlineDate) 
    2. Book contribution date
    3. History dates (pubmed, entrez, received, accepted)
    
    Example::
    
        article = fetch.article_by_pmid('12345')
        if article.pubdate:
            print(f"Published: {article.pubdate.strftime('%Y-%m-%d')}")
            print(f"Year: {article.pubdate.year}")

Shared Properties (Articles & Books)
-----------------------------------

These properties are available for both journal articles and book chapters:

**Core Identifiers**

* **pmid** - PubMed ID (string)
* **url** - NCBI PubMed URL for the article

**Author Information**

* **authors** - List of author names in "LastName FirstInitials" format  
* **author_list** - List of PubMedAuthor objects with detailed author data
* **authors_str** - Semicolon-separated string of all authors 
* **author1_last_fm** - First author in "LastName FirstInitials" format
* **author1_lastfm** - First author in "LastNameFirstInitials" format (no space)

**Content**

* **title** - Article or chapter title
* **abstract** - Full text abstract (structured abstracts are concatenated)
* **keywords** - List of author-supplied keywords
* **year** - Publication year (string)

**Journal/Publication**

* **journal** - Journal name or book title
* **history** - Dictionary of publication history dates (pubmed, entrez, received, etc.)

Article-Only Properties
-----------------------

These properties are only available for journal articles (``pubmed_type='article'``):

**Publication Details**

* **volume** - Journal volume number
* **issue** - Journal issue number  
* **volume_issue** - Combined volume(issue) format, e.g. "123(4)"
* **pages** - Page range, e.g. "45-67"
* **first_page** - First page number
* **last_page** - Last page number (computed from page range)

**Identifiers**

* **doi** - Digital Object Identifier
* **pii** - Publisher Item Identifier  
* **pmc** - PubMed Central ID (without "PMC" prefix)
* **issn** - International Standard Serial Number

**Indexing & Classification**

* **mesh** - Dictionary of MeSH (Medical Subject Headings) terms with:
  
  - descriptor_name: Main MeSH term
  - descriptor_major_topic: Boolean indicating major topic
  - qualifiers: List of qualifier terms with names and major topic flags

* **chemicals** - Dictionary of chemical substances mentioned, keyed by substance ID:
  
  - substance_name: Chemical name
  - registry_number: CAS registry number or "0" if none

* **publication_types** - Dictionary of publication types (e.g., "Journal Article", "Review") keyed by type ID

* **grants** - List of grant information dictionaries with:
  
  - agency: Funding agency name
  - country: Country of funding agency

Book-Only Properties  
-------------------

These properties are only available for book chapters (``pubmed_type='book'``):

**Book Metadata**

* **book_accession_id** - NCBI Book ID (e.g. "NBK1403")
* **book_title** - Full book title
* **book_publisher** - Publisher name
* **book_language** - Language code (e.g. "eng")
* **book_medium** - Publication medium (e.g. "Internet")

**Book Content**

* **book_abstracts** - Dictionary of abstract sections keyed by label
* **book_sections** - Dictionary of book sections 
* **book_copyright** - Copyright information
* **book_synonyms** - List of disease/concept synonyms (for reference works)

**Book Authors & Editors**

* **book_editors** - List of book editors in "LastName FirstInitials" format

**Book Dates**

* **book_contribution_date** - Chapter contribution date as datetime object
* **book_date_revised** - Last revision date as datetime object  
* **book_history** - Dictionary of book publication history dates
* **book_publication_status** - Publication status (e.g. "ppublish")

Citation Properties
------------------

These properties provide formatted citations in different styles:

**citation**
    Standard academic citation format::
    
        McNally EM, et al. Genetic mutations and mechanisms in dilated cardiomyopathy. 
        Journal of Clinical Investigation. 2013; 123:19-26. doi: 10.1172/JCI62862.

**citation_html**  
    HTML-formatted citation with italics for journal names and bold for volume::
    
        McNally EM, <i>et al</i>. Genetic mutations and mechanisms in dilated cardiomyopathy. 
        <i>Journal of Clinical Investigation</i>. 2013; <b>123</b>:19-26. doi: 10.1172/JCI62862.

**citation_bibtex**
    BibTeX-formatted citation for reference managers::
    
        @article{McNally2013,
        author = {McNally, EM and et al},
        title = {Genetic mutations and mechanisms in dilated cardiomyopathy},
        journal = {Journal of Clinical Investigation},
        year = {2013},
        volume = {123},
        pages = {19-26},
        doi = {10.1172/JCI62862},
        }

Property Availability by Type
----------------------------

==================== ======== ====
Property             Article  Book  
==================== ======== ====
pmid                 ✓        ✓
url                  ✓        ✓  
authors              ✓        ✓
title                ✓        ✓
abstract             ✓        ✓
year                 ✓        ✓
journal              ✓        ✓
pubdate              ✓        ✓
volume               ✓        ✗
issue                ✓        ✗
pages                ✓        ✗
doi                  ✓        ✗
mesh                 ✓        ✗
chemicals            ✓        ✗
grants               ✓        ✗
book_title           ✗        ✓
book_editors         ✗        ✓
book_accession_id    ✗        ✓
==================== ======== ====

Usage Examples
--------------

**Basic Article Information**::

    from metapub import PubMedFetcher
    
    fetch = PubMedFetcher()
    article = fetch.article_by_pmid('23435529')
    
    print(f"Title: {article.title}")
    print(f"Journal: {article.journal} ({article.year})")
    print(f"Authors: {article.authors_str}")
    print(f"DOI: {article.doi}")
    
    # New normalized date access
    if article.pubdate:
        print(f"Published: {article.pubdate.strftime('%B %d, %Y')}")

**Working with MeSH Terms**::

    if article.mesh:
        print("\\nMeSH Terms:")
        for ui, mesh_data in article.mesh.items():
            term = mesh_data['descriptor_name']
            major = mesh_data['descriptor_major_topic']
            marker = "*" if major else " "
            print(f"  {marker} {term}")

**Book Chapter Information**::

    book_article = fetch.article_by_pmid('20301546')  # GeneReviews example
    
    if book_article.pubmed_type == 'book':
        print(f"Chapter: {book_article.title}")
        print(f"Book: {book_article.book_title}")
        print(f"Editors: {'; '.join(book_article.book_editors)}")
        print(f"Book ID: {book_article.book_accession_id}")

**Citation Generation**::

    # Different citation formats
    print("Standard:", article.citation)
    print("HTML:", article.citation_html)  
    print("BibTeX:", article.citation_bibtex)

Error Handling
--------------

Properties gracefully handle missing data:

* Missing optional fields return ``None`` 
* Missing list fields return empty lists ``[]``
* Missing dictionary fields return empty dictionaries ``{}``
* Invalid dates return ``None`` from date-related properties

Always check for ``None`` values before using date operations::

    if article.pubdate:
        days_old = (datetime.now() - article.pubdate).days
        print(f"Article is {days_old} days old")

See Also
--------

* :doc:`citation_formatting` - Detailed citation formatting guide
* :doc:`api_models` - Complete API reference for PubMedArticle
* :doc:`examples` - More usage examples and patterns