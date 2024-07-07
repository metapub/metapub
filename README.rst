=======
Metapub
=======

![PyPI - Monthly Downloads](https://img.shields.io/pypi/dm/metapub)

Metapub is a Python library that provides python objects fetched via eutils 
that represent Pubmed papers and concepts found within the NCBI databases.

Metapub currently provides abstraction layers over Medgen, Pubmed, ClinVar, 
and CrossRef, and intends to encompass as many types of database lookups and 
summaries as can be provided via Eutils / Entrez.

Metapub can also help build scholarly paper libraries through the use of the
FindIt class.

MetaPub features include:

* Build formatted citations easily from lists of PMIDs.
* Generate valid LEGAL links to paper PDFs using FindIt, given a PMID or DOI.
* Common text mining "batteries included" such as finding DOIs in text.
* NCBI_API_KEY supported as environment variable (see below).
* PubMedArticle object is a privileged class across Metapub -- use it to instantiate CrossRef lookups, for example.
* Widespread use of Logging so you can see what's going on under the hood.
* Command line utilities -- see Getting Started below.

Getting Started
===============

Metapub is most easily installed using pip. It relies entirely on the arcane magic of classic Python setuptools::

  pip install metapub

When the package is installed, you'll have a few command line utilities available to you::

  convert pmid2doi <pmid>
  convert doi2pmid <doi>
  convert bookid2pmid <ncbi_bookID>
  pubmed_article <pmid>

All of these utilities contain their own help screens, by which you will be able to see options and usage.

Here's an example::

  convert pmid2doi 1000 -a -w 

Output::

    PMID:  1000
    DOI:  10.1042/bj1490739

    <PubMedArticle 1000> Wootton JC; Taylor JG; Jackson AA; Chambers GK; Fincham JR. The amino acid sequence of Neurospora NADP-specific glutamate dehydrogenase. The tryptic peptides.. Biochem. J.. 1975. 149(3):739-48
    <CrossRefWork 10.1042/bj1490739 Score: 1.0> Wootton. "The amino acid sequence ofNeurosporaNADP-specific glutamate dehydrogenase. The tryptic peptides" Biochemical Journal. 1975. 149(3):739-748


Here's another example, converting an NCBI Book ID to its PMID (if it has one):

`convert bookid2pmid NBK201366`

Output::

  BookID:  NBK201366
  PMID:  24830047



PubMedArticle / PubMedFetcher
=============================

First, a note about the NCBI_API_KEY... You'll want to grab an API key if you're doing more than a few 
requests per minute over here on the NCBI website: https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/

To load the API_KEY, do the following on the command line, or set this environment variable
in your deployment script of choice:

`export NCBI_API_KEY="Your_key_here"`

You don't need to use an API Key, but without it you are limited to 3 queries per second.

Now, on to PubMedFetcher basic usage::

  fetch = PubMedFetcher()
  article = fetch.article_by_pmid('123456')
  print(article.title)
  print(article.journal, article.year, article.volume, article.issue)
  print(article.authors)
  print(article.citation)


PubMedFetcher uses an SQLite cacheing engine (provided through eutils), which by 
default places a file in your user directory.  E.g. the author's cache directory
path would be */home/nthmost/.cache/eutils-cache.db*

This cache file can grow quite large over time. Deleting the cache file is safe
and can also be regarded as the way to "reset" the cache.

The *cachedir* keyword argument can be supplied to PubMedFetcher as a way to specify
where the cache file will reside.  For example::

  fetch = PubMedFetcher(cachedir='/path/to/cachedir')

User directory expansion also works:

  fetch = PubMedFetcher(cachedir='~/.othercachedir')

The cachedir will be created for you if it doesn't already exist, assuming the user 
account you're running metapub under has permissions to do so.

PubMedArticle Lookup Methods
----------------------------

The following methods return a PubMedArticle object (or raise InvalidPMID if NCBI lookup fails).

*article_by_pmid*

      (Attempt to) fetch an article by supplying its pubmed ID (both integer and string accepted).

*article_by_doi* 

      (Attempt to) fetch an article by looking up the DOI first.

*article_by_pmcid* 
    
      Fetch an article by looking up the PMCID first. Both integer and string accepted.


Pubmed ID List Methods
----------------------

The following methods return a list of pubmed IDs (if found) or an empty list (if None).

*pmids_from_citation*

      Produces a list of possible PMIDs for the submitted
      citation, where the citation is submitted as a collection of keyword
      arguments.  At least 3 of the 5, preferably 4 or 5 for best results,
      must be included::

        aulast or author_last_fm1
        year
        volume
        first_page or spage
        journal or jtitle

      Use NLM Title Abbreviation (aka ISO Abbreviation) journal strings whenever possible.


*pmids_for_query*

      Returns list of pmids for given freeform query string plus keyword arguments.
            
      All Pubmed Advanced Query tokens are supported.  

      See [NCBI Search Field Descriptions and Tags](http://www.ncbi.nlm.nih.gov/books/NBK3827/)


*pmids_for_clinical_query*

      Composes a "Clinical Query" as on this page: (http://www.ncbi.nlm.nih.gov/pubmed/clinical/)

      Supply a "category" (required) and an optimization ("broad" or "narrow") for this function.
      Available categories:

      * therapy
      * diagnosis
      * etiology
      * prognosis
      * prediction


      All keyword arguments for PubMedFetcher.pmids_for_query available.


*pmids_for_medical_genetics_query*

      Composes a "Medical Genetics Query" as described here: (http://www.ncbi.nlm.nih.gov/books/NBK3827/#pubmedhelp.Medical_Genetics_Search_Filte)

      Supply a "category" (required) and an optimization ("broad" or "narrow") for this function.
      Available categories:

      * therapy
      * diagnosis
      * etiology
      * prognosis
      * prediction


      All keyword arguments for PubMedFetcher.pmids_for_query available.


metapub.pubmedcentral.* 
-----------------------

The PubMedCentral functions are a loose collection of conversion 
methods for academic publishing IDs, allowing conversion (where possible)
between the following ID types::

    doi (Digital object identifier)
    pmid (PubMed ID)
    pmcid (Pubmed Central ID (including versioned document ID)

The following methods are supplied, returning a string (if found) or None::

    get_pmid_for_otherid(string)
    get_doi_for_otherid(string)
    get_pmcid_for_otherid(string)

As implied by the function names, you can supply any valid ID type ("otherid")
to acquire the desired ID type.



MedGenConcept / MedGenFetcher
=============================

The MedGen (medical genetics) database is a clinical dictionary linking medical concepts across multiple medical
ontologies and dictionaries such as OMIM and SNOMED.

Basic usage::

  from metapub import MedGenFetcher

  fetch = MedGenFetcher()

  concept = fetch.concept_by_uid('336867')
  print(concept.name)
  print(concept.description)
  print(concept.associated_genes)
  print(concept.modes_of_inheritance)
  print(concept.OMIM)
  print(concept.synonyms)


ClinVarVariation / ClinVarFetcher
=================================

The ClinVar database contains information submitted by genetic researchers, labs, and testing companies around the world.

Information queryable using the ClinVarFetcher currently includes searching for the ID of a variant ("Variation") in the 
database using an HGVS string and retrieving the Variant Summmary using a variation ID or HGVS string.

Since Pubmed citations by Variation ID are also available by a cross-query between ClinVar and Pubmed, ClinVarFetcher
allows retrieving PMIDs for given HGVS string.

Basic usage::

    clinvar = ClinVarFetcher()
    cv = clinvar.variation_by_hgvs('NM_000249.3:c.1958T>G')
    print(cv.variation_id)
    print(cv.variation_name)
    print(cv.genes)
    print(cv.hgvs)
    print(cv.molecular_consequences)

    pubmed_citations = clinvar.pmids_for_hgvs('NM_000249.3:c.1958T>G')
    print(pubmed_citations)


CrossRefFetcher
===============

The CrossRefFetcher object provides an object layer into search.crossref.org's API.
See http://search.crossref.org

CrossRef is a service that excels at resolving DOIs into article citation details.  It can
also be used to resolve a DOI /from/ article citation details.

Our interface to Crossref comes through the neat and clean habenero library by @sckott.

In metapub, the CrossRefFetcher object contains convenience methods into the crossref.works()
query that allows us to abstract away a lot of the string-handshaking between PubMedArticles
and CrossRef and just get what we need as quickly and accurately as possible.


Basic usage::

  CR = CrossRefFetcher()       # starts the query cache engine
  work = CR.article_by_title("Some great academic work of pure genius no doubt.", params)

  if work:
    print(work)


In the above example, we just had a title.  Sometimes that's good enough to get a result, 
and sometimes it's not.  The above function will return the top result off the list without
a lot of introspection.

The next method, on the other hand, performs some fancy Levenshtein distance calculation and
re-querying with different combos of parameters in order to drill down to a really precise 
result.

Example starting from a known pubmed ID::

  pma = PubMedFetcher().article_by_pmid(known_pmid)
  work = CR.article_by_pma(pma)

IMPORTANT NOTE

In this minor version (0.5) of Metapub there is no CrossRefFetcher cache.  
This feature is coming back very ASAP.


FindIt
------

Looking for an article PDF? Trying to gather a large corpus of research? 

The FindIt object was designed to be able to locate the direct urls of as many different
articles from as many different publishers of PubMed content as possible.

Any article that is Open Access, whether it is in PubmedCentral or not, can potentially
be "FindIt-able".  Usage is simple::

  from metapub import FindIt
  src = FindIt('18381613')
  print(src.url)

You can start FindIt from a DOI instead of a PMID by instantiating with FindIt(doi='10.1234/some.doi').  

If FindIt couldn't get a URL, you can take a look at the "reason" attribute to find out why. 
For example::

  src = FindIt('1234567')
  if src.url is None: print(src.reason) 

The FindIt object is cached (keyed to PMID), so while initialization the first time around 
for a given PMID or DOI may take a few seconds, the second time this information is requested
it will take far less time.

If you see a FindIt "reason" that starts with NOFORMAT, this is a great place to contribute
some help to metapub!  Feel free to dive in and submit a pull request, or contact the author
(naomi@nthmost.com) for advice on how to fill in these gaps.


UrlReverse
----------

Starting with a URL pointing to the abstract, pdf, or online fulltext of an article, UrlReverse
can "reverse" the DOI and/or the PubMed ID (pmid) of the article (assuming it can be found in
PubMed).

The UrlReverse object provides an interface to the urlreverse logic, and it attributes hold 
state for all of the information gathered and steps used to gather that information. 

Usage is very similar to FindIt::

  from metapub import UrlReverse
  urlrev = UrlReverse('http://onlinelibrary.wiley.com/doi/10.1002/humu.20708/pdf')
  print(urlrev.pmid)
  print(urlrev.doi)
  print(urlrev.steps)

UrlReverse is cached (keyed to URL); by default its cache db can be found in 
~/.cache/urlreverse-cache.db

As of metapub 0.4.3, there is no mechanism to have an item in cache expire. This is considered
a deficiency and will be remedied in a future version.

This is the newest feature in metapub (as of 0.4.2a0) and there is still much work to be done.
The world of biomedical literature URLs is fraught with inconsistencies and very weird URL
formats.  UrlReverse could really benefit from being able to parse supplement URLs, for example.

Collaboration and contributions heartily encouraged.


Miscellaneous Utilities
-----------------------

Currently underdocumented utilities that you might find useful.

In metapub.utils:

  * *asciify* (nuke all the unicode from orbit; it's the only way to be sure)
  * *parameterize* (make strings suitable for submission to GET-based query service)
  * *deparameterize* (somewhat-undo parameterization in string)
  * *remove_html_markup* (remove html and xml tags from text. preserves HTML entities like &amp;)
  * *hostname_of* (returns hostname part of URL, e.g. http://blood.oxfordjournals.org/stuff ==> blood.oxfordjournals.org)
  * *rootdomain_of* (returns the root domain of hostname of supplied URL, e.g. oxfordjournals.org)


In metapub.text_mining:

  * *find_doi_in_string* (returns the first seen DOI in the input string)
  * *findall_dois_in_text* (returns all seen DOIs in input string)
  * *pick_pmid* (return longest numerical string from text (string) as the pmid)


In metapub.convert:

  * *PubMedArticle2doi* (uses CrossRef to find a DOI for given PubMedArticle object.)
  * *pmid2doi* (returns first found doi for pubmed ID "by any means necessary.)
  * *doi2pmid* (uses CrossRef and eutils to return a PMID for given DOI if possible.)


In metapub.cite:

  * *citation* (constructs a research reference grade citation string from keyword arguments.)
  * *article*  (interface to citation; formats as article.)
  * *book*     (interface to citation; formats as book, e.g. GeneReviews)




More Information
----------------

Digital Identifiers of Scientific Literature: what they are, when they're 
used, and what they look like.

http://www.biosciencewriters.com/Digital-identifiers-of-scientific-literature-PMID-PMCID-NIHMS-DOI-and-how-to-use-them.aspx


About
-----

Metapub relies on the very neat eutils package created by Reece
Hart, which you can check out here:

http://bitbucket.org/biocommons/eutils

Metapub has been in development since November 15, 2014, and has come quite a long
way since then. Metapub has been deployed in production at many bioinformatics 
facilities (please tell me your story if you are among them!).

As of version 0.5.5, Metapub follows reasonably-strict Semantic Versioning which you 
can read about at https://semver.org/

Metapub is developed and maintained by a small group of volunteers based out of 
San Francisco, CA.  You are warmly welcome to contribute.  Please read the 
Contributing section carefully, and feel free to contact the main author (Naomi Most, 
@nthmost) directly with questions, comments, suggestions, and swear words.

Contributing: Help Wanted!
--------------------------

The Metapub project consists of a small handful of committed volunteers (primarily the original author, @nthmost) tracking bugs and making contributions through GitHub.

We welcome all contributions big and small, from ambitious new features all the way down to a thumbs-up on a bug or improvement.  Metapub is a highly detailed-oriented project that thrives with critical feedback.

If you'd like to contribute a new feature or bug fix, we ask that you open an issue at https://github.com/metapub/metapub/issues and give it as much detail as you can.  

Please submit examples of the data that breaks your code and/or the new type of data or API that you wish Metapub would support.   Examples are often crucial for reproducing bugs and for creating tests in the wake of a bug fix.

Extra special help is requested with the following items:

* Logging more consistently -- if you have a logging "philosophy" I'd love to hear from you.
* Test coverage -- especially clever testing strategies to handle data that change all the time.

Email inquiries to the maintainer address in this package. Or just submit a pull request.


About Python 2 and Python 3 Support
-----------------------------------
*Alert*: Metapub supports Python 3.x only from version 0.5.x onwards.

The LAST version of metapub to support Python 2.7 was 0.4.3.6 (2017)
