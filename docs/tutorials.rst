Tutorials
=========

Real-World Workflows and Use Cases
----------------------------------

This section provides step-by-step tutorials for common research workflows using Metapub.

Tutorial 1: Building a Literature Review Dataset
-----------------------------------------------

This tutorial shows how to systematically collect and analyze papers for a literature review.

Step 1: Define Your Search Strategy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from metapub import PubMedFetcher
   import pandas as pd
   from datetime import datetime
   
   fetch = PubMedFetcher()
   
   # Define search parameters
   search_terms = [
       'machine learning AND genomics',
       'artificial intelligence AND genetics', 
       'deep learning AND biomarker'
   ]
   
   date_range = {
       'since': '2020/01/01',
       'until': '2024/12/31'
   }

Step 2: Collect PMIDs
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   all_pmids = set()  # Use set to avoid duplicates
   
   for term in search_terms:
       print(f"Searching for: {term}")
       pmids = fetch.pmids_for_query(
           query=term,
           retmax=500,  # Adjust based on needs
           **date_range
       )
       all_pmids.update(pmids)
       print(f"Found {len(pmids)} papers")
   
   print(f"Total unique papers: {len(all_pmids)}")

Step 3: Extract Article Metadata
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from metapub.exceptions import InvalidPMID
   
   articles_data = []
   
   for i, pmid in enumerate(all_pmids):
       if i % 50 == 0:
           print(f"Processed {i}/{len(all_pmids)} articles")
       
       try:
           article = fetch.article_by_pmid(pmid)
           
           # Extract key information
           data = {
               'pmid': pmid,
               'title': article.title,
               'journal': article.journal,
               'year': article.year,
               'doi': article.doi,
               'authors': '; '.join([str(author) for author in article.authors]),
               'abstract': article.abstract,
               'mesh_terms': '; '.join(article.mesh_headings) if article.mesh_headings else '',
               'publication_types': '; '.join(article.publication_types) if article.publication_types else ''
           }
           articles_data.append(data)
           
       except InvalidPMID:
           print(f"Invalid PMID: {pmid}")
       except Exception as e:
           print(f"Error processing {pmid}: {e}")

Step 4: Analyze and Export
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Create DataFrame
   df = pd.DataFrame(articles_data)
   
   # Basic analysis
   print(f"Total articles collected: {len(df)}")
   print(f"Year range: {df['year'].min()} - {df['year'].max()}")
   print(f"Top 10 journals:")
   print(df['journal'].value_counts().head(10))
   
   # Export results
   df.to_csv(f'literature_review_{datetime.now().strftime("%Y%m%d")}.csv', index=False)
   print("Results exported to CSV")

Tutorial 2: FindIt Batch Processing for Full-Text Access
--------------------------------------------------------

This tutorial demonstrates how to systematically check full-text availability for a collection of papers.

Step 1: Prepare PMID List
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from metapub import FindIt
   import csv
   import time
   
   # Load PMIDs from various sources
   def load_pmids_from_file(filename):
       pmids = []
       with open(filename, 'r') as f:
           for line in f:
               pmid = line.strip()
               if pmid.isdigit():
                   pmids.append(pmid)
       return pmids
   
   # Or from previous search
   pmids = ['25575644', '25700512', '25554792']  # Example PMIDs

Step 2: Batch FindIt Processing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def process_findit_batch(pmids, output_file='findit_results.csv'):
       results = []
       
       with open(output_file, 'w', newline='') as csvfile:
           fieldnames = ['pmid', 'journal', 'title', 'url_available', 'url', 'reason', 'backup_url', 'embargo_status']
           writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
           writer.writeheader()
           
           for i, pmid in enumerate(pmids):
               print(f"Processing {pmid} ({i+1}/{len(pmids)})")
               
               try:
                   src = FindIt(pmid, retry_errors=True)
                   
                   # Check embargo status
                   embargo_date = src.pma.history.get('pmc-release', None)
                   embargo_status = 'embargoed' if (
                       src.reason.startswith("PAYWALL") and "embargo" in src.reason
                   ) else 'not_embargoed'
                   
                   result = {
                       'pmid': pmid,
                       'journal': src.pma.journal,
                       'title': src.pma.title,
                       'url_available': bool(src.url),
                       'url': src.url or '',
                       'reason': src.reason,
                       'backup_url': src.backup_url or '',
                       'embargo_status': embargo_status
                   }
                   
                   writer.writerow(result)
                   results.append(result)
                   
               except Exception as e:
                   print(f"Error processing {pmid}: {e}")
                   
               # Rate limiting
               time.sleep(0.5)
       
       return results

Step 3: Analyze Access Patterns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def analyze_access_results(results):
       df = pd.DataFrame(results)
       
       print("=== Full-Text Access Analysis ===")
       print(f"Total articles: {len(df)}")
       print(f"URL available: {df['url_available'].sum()} ({df['url_available'].mean()*100:.1f}%)")
       print(f"Embargoed articles: {(df['embargo_status'] == 'embargoed').sum()}")
       
       print("\n=== Access by Journal ===")
       journal_access = df.groupby('journal')['url_available'].agg(['count', 'sum', 'mean'])
       journal_access.columns = ['total', 'available', 'access_rate']
       journal_access['access_rate'] = journal_access['access_rate'] * 100
       print(journal_access.sort_values('access_rate', ascending=False))
       
       print("\n=== Common Failure Reasons ===")
       failed = df[~df['url_available']]
       print(failed['reason'].value_counts().head(10))

Tutorial 3: Clinical Genetics Research Workflow
----------------------------------------------

This tutorial shows how to research genetic conditions using MedGen and ClinVar integration.

Step 1: Condition to Gene Discovery
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from metapub import MedGenFetcher, ClinVarFetcher, PubMedFetcher
   
   mg = MedGenFetcher()
   cv = ClinVarFetcher()
   fetch = PubMedFetcher()
   
   def research_condition(condition_name):
       print(f"=== Researching: {condition_name} ===")
       
       # Step 1: Find MedGen concepts
       concepts = mg.concepts_for_term(condition_name)
       
       if not concepts:
           print("No MedGen concepts found")
           return
       
       main_concept = concepts[0]  # Use primary concept
       print(f"Main concept: {main_concept.name} (CUI: {main_concept.cui})")
       print(f"Definition: {main_concept.definition}")
       
       return main_concept

Step 2: Find Associated Genes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def find_associated_genes(concept):
       # Get related PMIDs from MedGen
       pmids = mg.pubmeds_for_cui(concept.cui)
       
       print(f"Found {len(pmids)} related articles")
       
       # Analyze abstracts for gene mentions
       gene_mentions = {}
       
       for pmid in pmids[:20]:  # Limit for demo
           try:
               article = fetch.article_by_pmid(pmid)
               if article.abstract:
                   # Simple gene pattern matching (improve as needed)
                   import re
                   gene_pattern = r'\b[A-Z][A-Z0-9]{2,}\b'  # Basic gene pattern
                   genes = re.findall(gene_pattern, article.abstract)
                   
                   for gene in genes:
                       if gene not in gene_mentions:
                           gene_mentions[gene] = 0
                       gene_mentions[gene] += 1
                       
           except Exception as e:
               continue
       
       # Sort by frequency
       top_genes = sorted(gene_mentions.items(), key=lambda x: x[1], reverse=True)
       print(f"Top mentioned genes: {top_genes[:10]}")
       
       return top_genes

Step 3: ClinVar Variant Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def analyze_clinvar_variants(gene_list):
       for gene, count in gene_list[:5]:  # Top 5 genes
           print(f"\n=== ClinVar variants for {gene} ===")
           
           try:
               # Search for variants in this gene
               variants = cv.variants_for_gene(gene)
               
               if variants:
                   print(f"Found {len(variants)} variants")
                   
                   # Analyze clinical significance
                   significance_counts = {}
                   for variant in variants[:10]:  # Limit for demo
                       sig = variant.clinical_significance
                       if sig:
                           significance_counts[sig] = significance_counts.get(sig, 0) + 1
                   
                   print("Clinical significance distribution:")
                   for sig, count in significance_counts.items():
                       print(f"  {sig}: {count}")
               
           except Exception as e:
               print(f"Error analyzing {gene}: {e}")

Step 4: Generate Research Summary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def generate_research_summary(condition_name):
       # Run the full workflow
       concept = research_condition(condition_name)
       if not concept:
           return
       
       genes = find_associated_genes(concept)
       analyze_clinvar_variants(genes)
       
       # Generate bibliography
       pmids = mg.pubmeds_for_cui(concept.cui)
       
       print(f"\n=== Key References for {condition_name} ===")
       for pmid in pmids[:5]:  # Top 5 references
           try:
               article = fetch.article_by_pmid(pmid)
               print(f"PMID {pmid}: {article.title}")
               print(f"  {article.journal} ({article.year})")
               print(f"  DOI: {article.doi}")
               print()
           except Exception:
               continue
   
   # Run the analysis
   generate_research_summary("Brugada syndrome")

Tutorial 4: Journal Analysis and Metrics
---------------------------------------

This tutorial shows how to analyze publication patterns and journal metrics.

Step 1: Collect Journal Data
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def analyze_journal_publication_patterns(journal_name, years_back=5):
       from datetime import datetime, timedelta
       
       current_year = datetime.now().year
       start_year = current_year - years_back
       
       yearly_data = []
       
       for year in range(start_year, current_year + 1):
           print(f"Analyzing {journal_name} for {year}")
           
           pmids = fetch.pmids_for_query(
               journal=journal_name,
               year=year,
               retmax=1000  # Adjust as needed
           )
           
           # Sample articles for analysis
           sample_size = min(50, len(pmids))
           sample_pmids = pmids[:sample_size]
           
           articles = []
           for pmid in sample_pmids:
               try:
                   article = fetch.article_by_pmid(pmid)
                   articles.append(article)
               except Exception:
                   continue
           
           yearly_data.append({
               'year': year,
               'total_articles': len(pmids),
               'analyzed_articles': articles
           })
       
       return yearly_data

Step 2: Analyze Publication Trends
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def analyze_publication_trends(yearly_data):
       import matplotlib.pyplot as plt
       
       years = [data['year'] for data in yearly_data]
       counts = [data['total_articles'] for data in yearly_data]
       
       # Publication volume trend
       plt.figure(figsize=(10, 6))
       plt.plot(years, counts, marker='o')
       plt.title('Publication Volume Over Time')
       plt.xlabel('Year')
       plt.ylabel('Number of Articles')
       plt.grid(True)
       plt.show()
       
       # Analyze author patterns
       all_authors = []
       for data in yearly_data:
           for article in data['analyzed_articles']:
               if article.authors:
                   all_authors.extend([str(author) for author in article.authors])
       
       from collections import Counter
       author_counts = Counter(all_authors)
       print("Most prolific authors:")
       for author, count in author_counts.most_common(10):
           print(f"  {author}: {count} papers")

Tutorial 5: Cross-Database Literature Mining
-------------------------------------------

This tutorial demonstrates mining literature across PubMed, CrossRef, and other databases.

Step 1: Multi-Database Search
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from metapub import CrossRefFetcher
   
   def comprehensive_literature_search(topic, max_results=100):
       CR = CrossRefFetcher()
       
       # Search PubMed
       pubmed_pmids = fetch.pmids_for_query(topic, retmax=max_results)
       print(f"PubMed results: {len(pubmed_pmids)}")
       
       # Search CrossRef
       crossref_works = CR.works_by_query(topic, max_results=max_results)
       print(f"CrossRef results: {len(crossref_works)}")
       
       # Combine and deduplicate
       all_works = []
       
       # Process PubMed results
       for pmid in pubmed_pmids:
           try:
               article = fetch.article_by_pmid(pmid)
               all_works.append({
                   'source': 'PubMed',
                   'pmid': pmid,
                   'doi': article.doi,
                   'title': article.title,
                   'journal': article.journal,
                   'year': article.year
               })
           except Exception:
               continue
       
       # Process CrossRef results
       for work in crossref_works:
           all_works.append({
               'source': 'CrossRef',
               'pmid': None,
               'doi': work.doi,
               'title': work.title[0] if work.title else '',
               'journal': work.container_title[0] if work.container_title else '',
               'year': work.published_print_date_parts[0][0] if work.published_print_date_parts else None
           })
       
       return all_works

Step 2: Deduplicate and Merge
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def deduplicate_works(works):
       # Simple deduplication by DOI and title similarity
       from difflib import SequenceMatcher
       
       unique_works = []
       seen_dois = set()
       
       for work in works:
           if work['doi'] and work['doi'] in seen_dois:
               continue
           
           # Check for title similarity
           is_duplicate = False
           for existing in unique_works:
               if work['title'] and existing['title']:
                   similarity = SequenceMatcher(None, 
                       work['title'].lower(), 
                       existing['title'].lower()
                   ).ratio()
                   
                   if similarity > 0.9:  # 90% similarity threshold
                       is_duplicate = True
                       break
           
           if not is_duplicate:
               unique_works.append(work)
               if work['doi']:
                   seen_dois.add(work['doi'])
       
       print(f"After deduplication: {len(unique_works)} unique works")
       return unique_works

This comprehensive documentation update includes real-world workflows, advanced patterns, and practical tutorials that researchers would actually use. The examples are based on the sophisticated functionality demonstrated in the demo scripts.