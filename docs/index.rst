Metapub Documentation
====================

.. image:: https://img.shields.io/pypi/dm/metapub
   :alt: PyPI - Monthly Downloads
   :target: https://pypi.org/project/metapub/

**Metapub** is a Python library for accessing biomedical literature and databases. It provides Python objects fetched via eutils that represent PubMed papers and concepts found within NCBI databases.

🌐 **Project Homepage:** `metapub.org <http://metapub.org>`_

**Created and maintained by** `Naomi Most <https://github.com/nthmost>`_

What Metapub Does
----------------

🔬 **Literature Access**
   Metapub handles the complexity of NCBI's E-utilities APIs, providing clean Python interfaces for literature searches and article retrieval.

📚 **Multi-Database Support**
   - **PubMed**: Biomedical literature citations and abstracts
   - **MedGen**: Medical genetics concepts and disease-gene relationships  
   - **ClinVar**: Clinical significance of genetic variants
   - **CrossRef**: DOI resolution and publication metadata

🔓 **PDF Discovery**
   The FindIt module locates downloadable PDFs using publisher-specific strategies for major academic publishers.

⚙️  **Research Tools**
   - Intelligent caching with SQLite backends
   - Comprehensive error handling and diagnostics
   - Rate limiting that respects NCBI guidelines
   - Batch processing capabilities for large datasets

Key Use Cases
------------

**Literature Analysis**
   Programmatically collect and analyze large sets of biomedical literature with comprehensive metadata extraction.

**Clinical Genetics Workflows** 
   Connect genetic variants from ClinVar with supporting literature for evidence-based analysis.

**Bioinformatics Integration**
   Integrate literature data into analysis pipelines for automatic annotation of genomic findings.

**Research Applications**
   Build biomedical research tools with standardized access to multiple literature databases.

What You Can Do in Minutes
--------------------------

**Find Full-Text PDFs Instantly**

.. code-block:: python

   from metapub import FindIt
   
   # Get downloadable PDF for any paper
   src = FindIt('33157158')  # PMID
   
   if src.url:
       print(f"📄 PDF available: {src.url}")
   else:
       print(f"❌ Access restricted: {src.reason}")

**Build Literature Datasets**

.. code-block:: python

   from metapub import PubMedFetcher
   
   fetch = PubMedFetcher()
   
   # Collect recent CRISPR research
   pmids = fetch.pmids_for_query(
       'CRISPR gene editing',
       since='2023/01/01',
       retmax=100
   )
   
   # Extract comprehensive metadata
   for pmid in pmids:
       article = fetch.article_by_pmid(pmid)
       print(f"{article.journal} ({article.year}): {article.title}")

**Research Genetic Conditions**

.. code-block:: python

   from metapub import MedGenFetcher, ClinVarFetcher
   
   # Investigate Brugada syndrome
   mg = MedGenFetcher()
   concepts = mg.concepts_for_term('Brugada syndrome')
   
   # Find clinical variants
   cv = ClinVarFetcher()
   variant_ids = cv.ids_by_gene('SCN5A')
   
   # Get supporting literature for each variant
   for var_id in variant_ids[:5]:
       pmids = cv.pmids_for_id(var_id)
       print(f"Variant {var_id}: {len(pmids)} supporting papers")

Core Features
------------

**🏢 Publisher Intelligence**
   FindIt includes strategies for major publishers with knowledge of their access patterns, embargo policies, and URL structures.

**🧬 Genomics Focus** 
   Built with genomics research in mind, providing native support for gene-disease relationships, variant annotations, and clinical significance data.

**⚡ Performance Features**
   - SQLite-based caching with TTL management
   - Singleton patterns to prevent duplicate API calls
   - Batch processing optimizations for large datasets
   - Memory-efficient XML parsing

**🛡️ Reliability**
   - Error handling that distinguishes service outages from code issues
   - Automatic retry logic for transient failures
   - Extensive logging for debugging and monitoring
   - NCBI API key support for higher rate limits

**🔄 Standards Support**
   - Follows NCBI E-utilities best practices
   - Respects publisher robots.txt and access policies
   - Generates properly formatted citations
   - Supports standard identifiers (PMID, DOI, PMC ID, HGVS)

Getting Started
--------------

**Installation**

.. code-block:: bash

   pip install metapub

**Quick Start**

.. code-block:: python

   from metapub import PubMedFetcher, FindIt
   
   # Search and analyze literature
   fetch = PubMedFetcher()
   pmids = fetch.pmids_for_query('machine learning genomics', retmax=10)
   
   # Check PDF availability
   accessible_papers = []
   for pmid in pmids:
       article = fetch.article_by_pmid(pmid)
       src = FindIt(pmid)
       
       if src.url:
           accessible_papers.append({
               'title': article.title,
               'journal': article.journal,
               'pdf_url': src.url
           })
   
   print(f"Found {len(accessible_papers)} papers with accessible PDFs")

**Next Steps**

Ready to transform your biomedical research workflow? Start with our comprehensive guides:

.. toctree::
   :maxdepth: 2
   :caption: User Guide:

   installation
   quickstart
   examples
   citation_formatting
   pubmedarticle_properties
   advanced
   tutorials
   command_line_tools
   error_handling

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
   :caption: Community & Support:

   showcase
   changelog

Who Uses Metapub
---------------

**🎯 Research Teams** building literature reviews, systematic analyses, and evidence synthesis workflows.

**🧬 Genomics Labs** connecting genetic variants with supporting literature for clinical decision-making.

**⚙️ Developers** creating biomedical applications, research tools, and automated analysis pipelines.

**📊 Institutions** including pharmaceutical companies, academic institutions, and government research agencies.

For peer-reviewed academic citations, see `metapub.org/citations <https://metapub.org/citations>`_.

**Documentation Navigation**

📚 **New to Metapub?** Start with :doc:`quickstart` for basic usage patterns.

🔧 **Building Applications?** See :doc:`api_overview` for architectural guidance.

💡 **Looking for Examples?** Check :doc:`examples` and :doc:`tutorials` for complete workflows.

🌐 **Project Updates:** Visit `metapub.org <http://metapub.org>`_ for news and community resources.

The documentation provides comprehensive coverage for both simple scripts and production applications.

