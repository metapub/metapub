__doc__ = "Common functions for the formatting of academic reference citations."

article_cit_fmt = '{author}. {title}. {journal}. {year}; {volume}:{pages}.{doi}'
book_cit_fmt = '{author}. {book.title}. {cdate} (Update {mdate}). In: {editors}, editors. {book.journal} (Internet). {book.book_publisher}'
bibtex_fmt = '@{entrytype}{{{citeID},\n{author}{doi}{title}{abstract}{journal}{year}{volume}{pages}{url}}}'

# HTML format strings for citation_html functionality
article_cit_fmt_html = '{author}. {title}. <i>{journal}</i>. {year}; <b>{volume}</b>:{pages}.{doi}'
book_cit_fmt_html = '{author}. <i>{book.title}</i>. {cdate} (Update {mdate}). In: {editors}, editors. <i>{book.journal}</i> (Internet). {book.book_publisher}'


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
    journal = '(None)' if not kwargs.get('journal', None) else kwargs['journal'].strip('.')
    # Year
    year = '(unknown year)' if not kwargs.get('year', None) else kwargs['year']

    # Volume
    volume = '(unknown volume)' if not kwargs.get('volume', None) else str(kwargs['volume'])
    # Pages
    pages = '(unknown pages)' if not kwargs.get('pages', None) else kwargs['pages']

    #TODO: how many articles DON'T have a volume, or are missing pages? (not that important for now.)
    # Choose format string based on HTML preference
    fmt = article_cit_fmt_html if kwargs.get('as_html', False) else article_cit_fmt
    return fmt.format(author=author, volume=volume, pages=pages, year=year,
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
        # Choose format string based on HTML preference
        fmt = book_cit_fmt_html if kwargs.get('as_html', False) else book_cit_fmt
        return fmt.format(editors=editors, author=author, book=book,
                          mdate=mdate, cdate=cdate)


def bibtex(**kwargs):
    """ Returns a BibTeX formatted citation string built from the book or article author(s), title,
    journal, year, volume, pages, and doi if the fields exist

    see cite.article and cite.book for more specific use cases.

    see https://ctan.org/tex-archive/biblio/bibtex/contrib/doc/ for more on the BibTeX format

    Note that "authors" (as list) will be used preferentially over "author" (as str).

    Keywords:
        isbook: (bool) returns citation with standard entry type as 'book'
        author: (str) -- prints author as-is without modification
        authors: (list) -- prints as author1 (first in list) as "Lastname_FirstInitials, et al"
        title: (str)
        journal: (str)
        year: (str or int)
        volume: (str or int)
        pages: (str) should be formatted "nn-mm", e.g. "55-58"
        doi: (str)
        
    Returns:
        bibtex citation (str)
    """

    entrytype = 'article' if not kwargs.get('isbook', False) else 'book'

    # Citation ID - create from first author last name and year
    year_str = str(kwargs.get('year', ''))
    if kwargs.get('authors', None) and len(kwargs['authors']) > 0 and year_str:
        # Extract last name from first author
        first_author = kwargs['authors'][0]
        # Handle formats like "Smith J" or "Smith, John"
        if ',' in first_author:
            last_name = first_author.split(',')[0].strip()
        else:
            # Handle "LastName Initial" or "Multi Word LastName Initial" formats
            parts = first_author.strip().split(' ')
            if len(parts) >= 2:
                # Take all but the last part (which should be initials)
                last_name = ''.join(parts[:-1])  # Join without spaces for citation ID
            else:
                last_name = parts[0].strip()
        citeID = last_name + year_str
    else:
        # Fallback to PMID if available
        citeID = kwargs.get('pmid', 'UnknownCitation') 

    # Author(s)
    if kwargs.get('authors', None):
        # Convert author list to BibTeX format: "Last, First and Last, First"
        authorlist = []
        for a in kwargs['authors']:
            if ',' in a:
                # Already in "Last, First" format
                authorlist.append(a.strip())
            else:
                # Convert "LastName Initial" to "LastName, Initial"
                parts = a.strip().split(' ')
                if len(parts) >= 2:
                    # For PubMed format "Smith J" -> "Smith, J"
                    last_name = ' '.join(parts[:-1])
                    initials = parts[-1]
                    authorlist.append(f"{last_name}, {initials}")
                else:
                    authorlist.append(a.strip())
        author = 'author = {%s},\n' % ' and '.join(authorlist)
    else:
        author = '' if not kwargs.get('author', None) else 'author = {%s},\n' % kwargs['author']

    # DOI
    doi_str = '' if not kwargs.get('doi', None) else 'doi = {%s},\n' % kwargs['doi']

    # Title
    title = '' if not kwargs.get('title', None) else 'title = {%s},\n' % kwargs['title'].strip('.')

    # Abstract (optional for BibTeX, often excluded for brevity)
    if kwargs.get('abstract', None):
        abs_text = kwargs['abstract'].strip('.')
        if len(abs_text) > 500:
            abs_text = abs_text[:500] + '...'
        abstract = 'abstract = {%s},\n' % abs_text
    else:
        abstract = ''

    # Journal
    journal = '' if not kwargs.get('journal', None) else 'journal = {%s},\n' % kwargs['journal'].strip('.')
    
    # Year
    year = '' if not kwargs.get('year', None) else 'year = {%s},\n' % kwargs['year']

    # Volume
    volume = '' if not kwargs.get('volume', None) else 'volume = {%s},\n' % str(kwargs['volume'])
    
    # Pages
    pages = '' if not kwargs.get('pages', None) else 'pages = {%s},\n' % kwargs['pages']

    # URL
    url = '' if not kwargs.get('url', None) else 'url = {%s},\n' % kwargs['url'].strip('.')


    # bibtex_fmt = '@{entrytype}{{{citeID},\n{author}{doi_str}{title}{abstract}{journal}{year}{volume}{pages}{url}}}'
    return bibtex_fmt.format(author=author, volume=volume, pages=pages, year=year, abstract=abstract, citeID=citeID,
                                  entrytype=entrytype, title=title, journal=journal, doi=doi_str, url=url)


 

