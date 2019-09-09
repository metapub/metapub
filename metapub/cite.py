__doc__ = "Common functions for the formatting of academic reference citations."

article_cit_fmt = '{author}. {title}. {journal}. {year}; {volume}:{pages}.{doi}'
book_cit_fmt = '{author}. {book.title}. {cdate} (Update {mdate}). In: {editors}, editors. {book.journal} (Internet). {book.book_publisher}'


def author_str(author_list_or_string, as_html=False):
    """ Helper function for constructing article citations.

    :param author_list_or_string:
    :return: author(s) str suitable for printed citation
    """
    if type(author_list_or_string) == list:
        authors = author_list_or_string
    else:
        authors = author_list_or_string.split(';')

    if len(authors) > 2:
        auth = authors[0].strip()
        if as_html:
            auth += ', <i>et al</i>'
        else:
            auth += ', et al'
    elif len(authors) == 2:
        auth = ' and '.join([aut.strip() for aut in authors])
    else:
        auth = authors[0]

    return auth


def citation(**kwargs):
    """ Returns a formatted citation string built from this article's author(s), title,
    journal, year, volume, pages, and doi.

    see cite.article and cite.book for more specific use cases.

    Note that "authors" (as list) will be used preferentially over "author" (as str).

    Keywords:
        as_html: (bool) returns citation with light HTML formatting.
        author: (str) -- prints author as-is without modification
        authors: (list) -- prints as author1 (first in list) as "Lastname_FirstInitials, et al"
        title: (str)
        journal: (str)
        year: (str or int)
        volume: (str or int)
        pages: (str) should be formatted "nn-mm", e.g. "55-58"
        doi: (str)
        
    Returns:
        citation (str)
    """
    #Author(s)
    if kwargs.get('authors', None):
        author = author_str(kwargs['authors'], as_html=kwargs.get('as_html', False))
    else:
        author = kwargs.get('author', '(None)')

    #DOI
    doi_str = '' if not kwargs.get('doi', None) else ' doi: %s' % kwargs['doi']

    #Title
    title = '(None)' if not kwargs.get('title', None) else kwargs['title'].strip('.')
    #Journal
    journal = '(None)' if not kwargs.get('journal', None) else kwargs['title'].strip('.')
    # Year
    year = '(unknown year)' if not kwargs.get('year', None) else kwargs['year']

    # Volume
    volume = '(unknown volume)' if not kwargs.get('volume', None) else str(kwargs['volume'])
    # Pages
    pages = '(unknown pages)' if not kwargs.get('pages', None) else kwargs['pages']

    #TODO: how many articles DON'T have a volume, or are missing pages? (not that important for now.)
    # article_cit_fmt = '{author}. {title}. {journal}. {year}; {volume}:{pages}.{doi}'
    return article_cit_fmt.format(author=author, volume=volume, pages=pages, year=year,
                                  title=title, journal=journal, doi=doi_str)


def article(**kwargs):
    """ Returns a formatted citation string built from this article's author(s), title,
        journal, year, volume, pages, and doi.

        This function uses the Article format citation template. For example:

        McNally EM, et al. Genetic mutations and mechanisms in dilated cardiomyopathy. Journal of Clinical Investigation. 2013; 123:19-26. doi: 10.1172/JCI62862.

        Keywords:
            journal
            title
            doi
            authors (str or list) -- if str, prints authors without modification.

        Return:
            citation (str)
    """
    return citation(**kwargs)


def book(book, **kwargs):
    """ Takes a PubMedArticle "book" and formats a citation string.  This is a special type of citation
        built mostly for NCBI GeneReviews and not currently generalizable to other academic books (yet).

        Returns a formatted citation string for a book.  A "book" needs to contain the following attributes:

            author
            title
            book_date_revised
            book_contribution_date
            editors             
            journal
            book_publisher      (may be a URL)

        This function uses the Book format citation template: 

        book_cit_fmt = '{author}. {title}. {cdate} (Update {mdate}). In: {editors}, editors. {journal} (Internet). {book_publisher}'

        For example:

        Tranebjarg L, et al. Jervell and Lange-Nielsen syndrome. 2002 Jul 29 (Updated 2014 Nov 20). In: Pagon RA, et al., editors. GeneReviews (Internet). Seattle (WA): University of Washington, Seattle; 1993-2015. Available from: https://www.ncbi.nlm.nih.gov/books/NBK1405/.

        :param book: PubMedArticle of type "book"
        :param use_html: (bool) whether to return with light HTML formatting
        :return: formatted citation string
        :rtype: str
    """
    author = author_str(book.authors_str, as_html=kwargs.get('as_html', False))

    # Special handling for GeneReviews and other books:
    if book.book_accession_id:
        mdate = book.book_date_revised.strftime('%Y %b %d')
        cdate = book.book_contribution_date.strftime('%Y %b %d')
        editors = author_str(book.book_editors, as_html=kwargs.get('as_html', False))
        if editors.endswith(', et al'):
            editors += '.'
        return book_cit_fmt.format(editors=editors, author=author, book=book,
                                   mdate=mdate, cdate=cdate)

