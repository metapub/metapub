import os
import random
from metapub import PubMedFetcher

# Set your NCBI API key as an environment variable
os.environ['NCBI_API_KEY'] = '978065a796e22e30673a7be4660101103707'

fetcher = PubMedFetcher()

def get_random_pmids(n):
    """Generate a list of n random PMIDs"""
    return [str(random.randint(1, 30000000)) for _ in range(n)]

def check_articles(pmids):
    pubdate_pmids = []
    medline_pmids = []
    
    for pmid in pmids:
        try:
            article = fetcher.article_by_pmid(pmid)
            pub_date = article.content.get('PubDate', {})
            if 'MedlineDate' in pub_date:
                medline_pmids.append(pmid)
            else:
                pubdate_pmids.append(pmid)
        except Exception as e:
            print(f"Error fetching PMID {pmid}: {e}")
    
    return pubdate_pmids, medline_pmids

def main():
    pubdate_pmids_total = []
    medline_pmids_total = []
    
    for _ in range(10):  # 10 iterations to cover 100 articles
        pmids = get_random_pmids(10)
        pubdate_pmids, medline_pmids = check_articles(pmids)
        pubdate_pmids_total.extend(pubdate_pmids)
        medline_pmids_total.extend(medline_pmids)
    
    # Save the results
    with open('pubdate_pmids.txt', 'w') as f:
        for pmid in pubdate_pmids_total:
            f.write(f"{pmid}\n")
    
    with open('medline_pmids.txt', 'w') as f:
        for pmid in medline_pmids_total:
            f.write(f"{pmid}\n")
    
    print("Completed processing. Results saved in 'pubdate_pmids.txt' and 'medline_pmids.txt'.")

if __name__ == "__main__":
    main()

