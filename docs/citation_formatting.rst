Citation Formatting
==================

Metapub provides three different citation formatting styles to accommodate various academic and technical requirements. All citation formatting is built on the robust foundation of the ``metapub.cite`` module, which handles complex author name parsing, journal formatting, and publication metadata.

Overview of Citation Formats
----------------------------

Metapub supports three citation formats:

1. **Standard Academic Citation** (``citation`` property) - Plain-text citations following traditional academic formatting
2. **HTML-Enhanced Citation** (``citation_html`` property) - Same format with HTML styling for journals and volumes  
3. **BibTeX Citation** (``citation_bibtex`` property) - BibTeX format for LaTeX documents and reference managers

All three formats are automatically generated from the same underlying article metadata, ensuring consistency across different output requirements.

Standard Academic Citations
---------------------------

The standard citation format produces plain-text academic citations suitable for manuscripts, reports, and documentation.

**Article Citation Format:**

.. code-block:: none

   Author(s). Title. Journal. Year; Volume:Pages. doi: DOI

**Usage:**

.. code-block:: python

   from metapub import PubMedFetcher
   
   fetch = PubMedFetcher()
   article = fetch.article_by_pmid('23435529')
   
   print(article.citation)
   # Output: Ruvolo G, et al. Lower sperm DNA fragmentation after r-FSH 
   # administration in functional hypogonadotropic hypogonadism. J Assist 
   # Reprod Genet. 2013; 30:497-503. doi: 10.1007/s10815-013-9951-y

**Book Citation Format (GeneReviews):**

.. code-block:: none

   Author(s). Title. Date (Update Date). In: Editors, editors. Journal (Internet). Publisher

.. code-block:: python

   # GeneReviews book example
   book_article = fetch.article_by_pmid('20301546')
   print(book_article.citation)
   # Output: Tranebjærg L, et al. Jervell and Lange-Nielsen syndrome. 2002 Jul 29 
   # (Updated 2014 Nov 20). In: Pagon RA, et al., editors. GeneReviews (Internet). 
   # Seattle (WA): University of Washington, Seattle; 1993-2015.

HTML-Enhanced Citations
----------------------

HTML citations add visual emphasis to journal names (italics) and volume numbers (bold) while maintaining the same structural format as standard citations.

**Article Citation with HTML:**

.. code-block:: python

   from metapub import PubMedFetcher
   
   fetch = PubMedFetcher()
   article = fetch.article_by_pmid('23435529')
   
   print(article.citation_html)
   # Output: Ruvolo G, <i>et al</i>. Lower sperm DNA fragmentation after r-FSH 
   # administration in functional hypogonadotropic hypogonadism. <i>J Assist 
   # Reprod Genet</i>. 2013; <b>30</b>:497-503. doi: 10.1007/s10815-013-9951-y

**HTML Features:**

- Journal names wrapped in ``<i>`` tags for italics
- Volume numbers wrapped in ``<b>`` tags for bold emphasis  
- Author "et al" formatted as ``<i>et al</i>``
- All other elements remain as plain text

**Book Citation with HTML:**

.. code-block:: python

   # GeneReviews book with HTML formatting
   book_article = fetch.article_by_pmid('20301546')
   print(book_article.citation_html)
   # Output: Tranebjærg L, <i>et al</i>. <i>Jervell and Lange-Nielsen syndrome</i>. 
   # 2002 Jul 29 (Updated 2014 Nov 20). In: Pagon RA, <i>et al</i>., editors. 
   # <i>GeneReviews</i> (Internet). Seattle (WA): University of Washington, Seattle; 1993-2015.

BibTeX Citations
---------------

BibTeX format provides structured citations compatible with LaTeX documents and reference management software like Zotero, Mendeley, and EndNote.

**Article BibTeX Format:**

.. code-block:: bibtex

   @article{AuthorYear,
   author = {Last, First and Last, First},
   doi = {DOI},
   title = {Article Title},
   journal = {Journal Name},
   year = {Year},
   volume = {Volume},
   pages = {Start-End},
   }

**Usage Example:**

.. code-block:: python

   from metapub import PubMedFetcher
   
   fetch = PubMedFetcher()
   article = fetch.article_by_pmid('23435529')
   
   print(article.citation_bibtex)

**Output:**

.. code-block:: bibtex

   @article{Ruvolo2013,
   author = {Ruvolo, G and Roccheri, MC and Brucculeri, AM and Longobardi, S and Cittadini, E and Bosco, L},
   doi = {10.1007/s10815-013-9951-y},
   title = {Lower sperm DNA fragmentation after r-FSH administration in functional hypogonadotropic hypogonadism},
   journal = {J Assist Reprod Genet},
   year = {2013},
   volume = {30},
   pages = {497-503},
   }

**Book BibTeX Format:**

.. code-block:: python

   # GeneReviews book BibTeX
   book_article = fetch.article_by_pmid('20301546')
   print(book_article.citation_bibtex)

**Output:**

.. code-block:: bibtex

   @book{Tranebjærg2002,
   author = {Tranebjærg, L and Samson, RA and Green, GE},
   title = {Jervell and Lange-Nielsen syndrome},
   year = {2002},
   }

BibTeX Features and Handling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Citation ID Generation:**

- **Primary:** First author's last name + publication year (e.g., ``Smith2023``)
- **Multi-word names:** Concatenated without spaces (``VanDerBerg2023``)
- **Fallback:** PMID if author/year unavailable
- **Final fallback:** ``UnknownCitation`` if no identifiers available

**Author Name Formatting:**

- Converts PubMed format (``Smith J``) to BibTeX format (``Smith, J``)
- Handles multi-word last names: ``Van Der Berg JH`` → ``Van Der Berg, JH``
- Preserves special characters: ``O'Brien J``, ``García-López M``
- Multiple authors joined with ``and``

**Field Processing:**

- **Title/Journal/Abstract:** Strips trailing periods automatically
- **Abstract:** Truncated to 500 characters + "..." if longer
- **URL:** Strips trailing periods for clean links
- **Empty fields:** Automatically excluded from output
- **Volume:** Accepts both string and integer formats

**Special Characters:**

BibTeX output preserves special characters without escaping, allowing BibTeX processors to handle formatting:

.. code-block:: python

   # Special characters are preserved
   test_data = {
       'authors': ['O\'Brien J', 'García-López M'],
       'title': 'Test with "quotes" & special chars',
       'year': 2023
   }
   
   bibtex = cite.bibtex(**test_data)
   # Output preserves: O'Brien, García-López, "quotes", &

Direct Citation Module Usage
----------------------------

You can also use the citation functions directly without fetching articles:

**Standard Citations:**

.. code-block:: python

   from metapub import cite
   
   # Article citation
   citation = cite.article(
       authors=['Smith J', 'Jones K'],
       title='Research Article Title',
       journal='Nature',
       year=2023,
       volume=615,
       pages='123-130',
       doi='10.1038/example'
   )
   
   # HTML citation
   html_citation = cite.article(
       authors=['Smith J', 'Jones K'],
       title='Research Article Title',
       journal='Nature',
       year=2023,
       volume=615,
       pages='123-130',
       doi='10.1038/example',
       as_html=True
   )

**BibTeX Citations:**

.. code-block:: python

   from metapub import cite
   
   # Article BibTeX
   bibtex = cite.bibtex(
       authors=['Smith J', 'Jones K'],
       title='Research Article Title',
       journal='Nature',
       year=2023,
       volume=615,
       pages='123-130',
       doi='10.1038/example'
   )
   
   # Book BibTeX
   book_bibtex = cite.bibtex(
       authors=['Editor A', 'Editor B'],
       title='Book Title',
       year=2022,
       isbook=True
   )

Edge Cases and Error Handling
-----------------------------

**Missing Author Information:**

.. code-block:: python

   # Falls back to PMID for citation ID
   cite.bibtex(
       pmid='12345678',
       title='Anonymous Article',
       journal='Unknown Journal'
   )
   # Output: @article{12345678, ...

**No Identifiers Available:**

.. code-block:: python

   # Uses generic citation ID
   cite.bibtex(
       title='Completely Unknown Article',
       journal='Unknown Journal'
   )
   # Output: @article{UnknownCitation, ...

**Multi-word Last Names:**

.. code-block:: python

   # Properly handles complex names
   cite.bibtex(
       authors=['Van Der Berg JH', 'De La Cruz M'],
       title='Multi-word Name Test',
       year=2023
   )
   # Citation ID: VanDerBerg2023
   # Author format: Van Der Berg, JH and De La Cruz, M

**Author Format Variations:**

.. code-block:: python

   # Handles pre-formatted names
   cite.bibtex(
       authors=['Smith, John H', 'Jones, Kate M'],
       title='Pre-formatted Names',
       year=2023
   )
   # Preserves existing formatting: Smith, John H and Jones, Kate M

Integration with Reference Managers
----------------------------------

**Zotero Integration:**

.. code-block:: python

   # Export BibTeX for Zotero import
   pmids = ['23435529', '25633503', '20301546']
   
   with open('references.bib', 'w') as f:
       for pmid in pmids:
           article = fetch.article_by_pmid(pmid)
           f.write(article.citation_bibtex + '\n\n')

**LaTeX Documents:**

.. code-block:: latex

   % In your .tex file
   \bibliography{references}
   \bibliographystyle{plain}
   
   % Cite the articles
   \cite{Ruvolo2013}
   \cite{Hoban2021}

**Programmatic Bibliography Generation:**

.. code-block:: python

   # Generate bibliography from search results
   from metapub import PubMedFetcher
   
   fetch = PubMedFetcher()
   pmids = fetch.pmids_for_query('CRISPR gene editing', retmax=10)
   
   bibliography = []
   for pmid in pmids:
       try:
           article = fetch.article_by_pmid(pmid)
           bibliography.append({
               'pmid': pmid,
               'standard': article.citation,
               'html': article.citation_html,
               'bibtex': article.citation_bibtex
           })
       except Exception as e:
           print(f"Error processing {pmid}: {e}")
   
   # Now you have all three formats for each article

Best Practices
-------------

**Choosing the Right Format:**

- **Standard citations:** Manuscripts, reports, plain text documentation
- **HTML citations:** Web pages, online documentation, rich text applications  
- **BibTeX citations:** LaTeX documents, reference managers, academic databases

**Performance Considerations:**

- Citation formatting is lightweight and cached with article data
- No additional API calls required once article is fetched
- BibTeX generation handles large author lists efficiently

**Quality Assurance:**

- All citations automatically handle missing fields gracefully
- Special characters preserved for proper rendering
- Consistent formatting across all three output types
- Extensive test coverage ensures reliability

.. note::
   
   Citation formatting depends on the completeness of article metadata from PubMed. 
   Some older articles may have incomplete author information or missing DOIs, 
   which will be handled gracefully with appropriate fallbacks.

.. seealso::

   - :doc:`api_models` for ``PubMedArticle`` class details
   - :doc:`examples` for more citation usage examples  
   - :doc:`api_overview` for general API architecture