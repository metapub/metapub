"""Demo: find articles in CrossRef by title.

Shows CrossRefFetcher.article_by_title() which searches CrossRef's
bibliographic database using a paper title and returns a CrossRefWork
object with DOI, authors, journal, score, and citation info.

Usage:
    python demo_crossref_article_by_title.py
    python demo_crossref_article_by_title.py "Tumor longest diameter"
"""

import sys

from metapub import CrossRefFetcher

CR = CrossRefFetcher()

SAMPLE_TITLES = [
    'The hallmarks of cancer',
    'Tumor longest diameter is not reliable for staging of rectal cancer',
    'A global reference for human genetic variation',
]


def show_crossref_result(title):
    print(f'Query: "{title}"')
    print('-' * 60)

    work = CR.article_by_title(title)
    if work is None:
        print('  No results found')
        print()
        return

    print(f'  Title:   {work.title[0]}')
    print(f'  DOI:     {work.doi}')
    print(f'  Score:   {work.score}')
    print(f'  Journal: {work.container_title[0] if work.container_title else "N/A"}')
    print(f'  Year:    {work.pubyear}')
    print(f'  Authors: {", ".join(work.author_list[:5])}')
    if len(work.author_list) > 5:
        print(f'           ... and {len(work.author_list) - 5} more')
    print(f'  Type:    {work.type}')
    print(f'  Pages:   {work.page}')
    print(f'  Citation: {work.citation}')
    print()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        titles = [' '.join(sys.argv[1:])]
    else:
        titles = SAMPLE_TITLES

    for title in titles:
        show_crossref_result(title)
