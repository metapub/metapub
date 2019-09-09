from docopt import docopt

from .pubmedfetcher import PubMedFetcher

__author__ = 'nthmost'
__version__= '0.1'        # version of THIS cli program only, not metapub as a whole.
__doc__ = """pubmed_article: utility for fetching an article by PMID.

Usage:
    pubmed_article <pmid>

Options:

    -h, --help       Print this screen.
    -v, --version    Print the version of this program.
    -a, --abstract   Include the abstract.
    -f, --full       Print the full article, if possible. (experimental)
"""

def print_pma(pmid):
    "Takes a PMID and prints a stringified PubMedArticle to the command line."
    fetch = PubMedFetcher()
    pma = fetch.article_by_pmid(pmid)
    print(pma)

def main():
    args = docopt(__doc__, version=__version__)
    print_pma(args['<pmid>'])

