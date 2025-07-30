"""metapub.pubmedarticle -- PubMedArticle class instantiated by supplying ncbi XML string."""

import time
from datetime import datetime
from collections import OrderedDict

from .base import MetaPubObject
from .exceptions import MetaPubError
from .text_mining import re_numbers
from .pubmedauthor import PubMedAuthor

from . import cite


class PubMedArticle(MetaPubObject):
    """This PubMedArticle class receives an XML string as its required argument
    and parses it into its constituent parts, exposing them as attributes.

    Usage:
        paper = PubMedArticle(xml_string)

    To query services to return an article by pmid, use PubMedFetcher, which
    returns PubMedArticle objects.

    When xmlstr is parsed, the `pubmed_type` attribute will be set to one of 'article' or 'book',
    depending on whether PubmedBookArticle or PubmedArticle headings are found in the supplied
    xmlstr at instantiation.

    Since this class needs to work seamlessly in production whether it's a book
    or an article, the PubmedArticle attributes will always be available (set to None in many
    cases for PubmedBookArticle, e.g. volume, issue, journal), but PubmedBookArticle
    attributes will only be set when pubmed_type='book'.

    PubMedBook special handling of certain attributes:
        * abstract: a joined string from self.book_abstracts
        * title: comes from ArticleTitle

    Special attributes for PubmedBookArticle (pubmed_type='book'):
        * book_id (default: None) - string from IdType="bookaccession", e.g. "NBK1403"
        * book_title (default: None) - string with name of book (as differentiated from ArticleTitle)
        * book_publisher (default: None) - dict containing {'name': string, 'location': string}
        * book_sections (default: []) - dict with key->value pairs as section_name->SectionTitle
        * book_contribution_date (default: None) - python datetime date
        * book_date_revised (default: None) - python datetime date
        * book_history (default: [])  - dictionary with key->value pairs as PubStatus -> python datetime
        * book_language (default: None) - string (e.g. "eng")
        * book_editors (default: []) - list containing names from 'editors' AuthorList
        * book_abstracts (default: []) - dict with key->value pairs as Label->AbstractText.text)
        * book_medium (default: None) - string (e.g. "Internet")
        * book_synonyms (default: None) - list of disease synonyms (applicable to "gene" book)
        * book_publication_status (default: None) - string (e.g. "ppublish")
    """

    def __init__(self, xmlstr, *args, **kwargs):
        """Initialize PubMedArticle from NCBI XML data.
        
        Args:
            xmlstr (str): XML string from NCBI containing PubmedArticle or 
                PubmedBookArticle data.
            *args: Additional positional arguments passed to parent class.
            **kwargs: Additional keyword arguments passed to parent class.
        
        Note:
            The XML type is automatically detected to handle both regular articles
            and book chapters. The `pubmed_type` attribute will be set to 'article'
            or 'book' accordingly, and appropriate attributes will be populated.
        """
        self.pubmed_type = determine_pubmed_xml_type(xmlstr)

        if self.pubmed_type=='book':
            self._root = 'BookDocument'
            super(PubMedArticle, self).__init__(xmlstr, 'PubmedBookArticle', args, kwargs)
        elif self.pubmed_type=='article':
            self._root = 'MedlineCitation'
            super(PubMedArticle, self).__init__(xmlstr, 'PubmedArticle', args, kwargs)
        else:
            # assume we're here because of predownloaded Medline XML.
            self.pubmed_type = 'article'
            self._root = '.'
            super(PubMedArticle, self).__init__(xmlstr, None, args, kwargs)

        pmt = self.pubmed_type

        # shared between book and article types:
        self.pmid = self._get_pmid()
        self.url  = self._get_url()
        self.authors = self._get_authors() if pmt == 'article' else self._get_book_authors()
        self.author_list = self._get_author_list() if pmt == 'article' else self._get_book_author_list()
        self.title = self._get_title() if pmt == 'article' else self._get_book_articletitle()
        self.authors_str = self._get_authors_str()
        self.author1_last_fm = self._get_author1_last_fm()
        self.author1_lastfm = self._get_author1_lastfm()
        self.keywords = self._get_keywords()

        # 'article' only (not shared):
        self.pages = None if pmt == 'book' else self._get_pages()
        self.first_page = None if pmt == 'book' else self._get_first_page()
        self.last_page = None if pmt == 'book' else self._get_last_page()
        self.volume = None if pmt == 'book' else self._get_volume()
        self.issue = None if pmt == 'book' else self._get_issue()
        self.volume_issue = None if pmt == 'book' else self._get_volume_issue()
        self.doi = None if pmt == 'book' else self._get_doi()
        self.pii = None if pmt == 'book' else self._get_pii()
        self.pmc = None if pmt == 'book' else self._get_pmc()
        self.issn = None if pmt == 'book' else self._get_issn()

        # MeSH headings ('article' only)
        self.mesh = self._get_mesh_headings()

        # Chemical associations ('article' only)
        self.chemicals = self._get_chemicals()

        # Grant information (?? 'article' only ??)
        self.grants = self._get_grantlist()

        # Publication Types (?? 'article' only ??)
        self.publication_types = self._get_publication_types()

        # 'book' only:
        self.book_accession_id = None if pmt == 'article' else self._get_bookaccession_id()
        self.book_title = None if pmt == 'article' else self._get_book_title()
        self.book_publisher = None if pmt == 'article' else self._get_book_publisher()
        self.book_language = None if pmt == 'article' else self._get_book_language()
        self.book_editors = None if pmt == 'article' else self._get_book_editors()
        self.book_abstracts = None if pmt == 'article' else self._get_book_abstracts()
        self.book_sections = None if pmt == 'article' else self._get_book_sections()
        self.book_copyright = None if pmt == 'article' else self._get_book_copyright()
        self.book_medium = None if pmt == 'article' else self._get_book_medium()
        self.book_synonyms = None if pmt == 'article' else self._get_book_synonyms()
        self.book_publication_status = None if pmt == 'article' else self._get_book_publication_status()
        self.book_history = None if pmt == 'article' else self._get_book_history()
        self.book_contribution_date = None if pmt == 'article' else self._get_book_contribution_date()
        self.book_date_revised = None if pmt == 'article' else self._get_book_contribution_date()

        # the shared oddballs, must be done last.
        self.abstract = self._get_abstract() if pmt == 'article' else self._get_book_abstract()
        self.journal = self.book_title if pmt == 'book' else self._get_journal()
        self.year = self._get_book_year() if pmt == 'book' else self._get_year()

        self.history = self._get_article_history()

    def to_dict(self):
        """Convert PubMedArticle to dictionary representation.
        
        Returns:
            Dict[str, Any]: Dictionary containing all article attributes except
                internal XML content and processing attributes.
        
        Note:
            Excludes 'content', 'xml', and '_root' attributes from the output
            to provide a clean data representation suitable for serialization.
        """
        outd = self.__dict__.copy()
        outd.pop('content')
        outd.pop('xml')
        outd.pop('_root')
        return self.__dict__

    @property
    def citation(self):
        """ Returns a formatted citation string built from this article's author(s), title,
        journal, year, volume, pages, and doi.

        Article Example:

        McNally EM, et al. Genetic mutations and mechanisms in dilated cardiomyopathy. Journal of Clinical Investigation. 2013; 123:19-26. doi: 10.1172/JCI62862.

        Book Example (GeneReviews):

        Tranebjarg L, et al. Jervell and Lange-Nielsen syndrome. 2002 Jul 29 (Updated 2014 Nov 20). In: Pagon RA, et al., editors. GeneReviews (Internet). Seattle (WA): University of Washington, Seattle; 1993-2015. Available from: https://www.ncbi.nlm.nih.gov/books/NBK1405/.
        """
        #special handling for GeneReviews books
        if self.book_accession_id:
            return cite.book(self)
        return cite.article(**self.to_dict())

    @property
    def citation_html(self):
        """ Returns a formatted citation string built from this article's author(s), title,
        journal, year, volume, and pages.

        Article Example:

        McNally EM, <i>et al</i>. Genetic mutations and mechanisms in dilated cardiomyopathy. <i>Journal of Clinical Investigation</i>. 2013; <b>123</b>:19-26. doi: 10.1172/JCI62862.

        GeneReviews Example:
        Tranebjarg L, <i>et al</i>. <i>Jervell and Lange-Nielsen syndrome</i>. 2002 Jul 29 (Updated 2014 Nov 20). In: Pagon RA, <i>et al</i>., editors. GeneReviews (Internet). Seattle (WA): University of Washington, Seattle; 1993-2015. Available from: https://www.ncbi.nlm.nih.gov/books/NBK1405/.
        """
        #special handling for GeneReviews books
        if self.book_accession_id:
            return cite.book(self, as_html=True)
        return cite.article(as_html=True, **self.to_dict())

    @property
    def citation_bibtex(self):
        if self.book_accession_id:
            return cite.bibtex(isbook=True, **self.to_dict())
        return cite.bibtex(**self.to_dict())
    
    @property
    def pubdate(self):
        """Normalized publication date as datetime object.
        
        Returns the best available publication date from PubMed XML in order of preference:
        1. Article PubDate (Year/Month/Day or MedlineDate)
        2. Book contribution date  
        3. History dates (pubmed, entrez, etc.)
        
        Returns:
            datetime or None: Publication date as datetime object, or None if no date found
            
        Example:
            article = fetch.article_by_pmid('12345')
            if article.pubdate:
                print(f"Published: {article.pubdate.strftime('%Y-%m-%d')}")
        """
        if self.pubmed_type == 'book':
            # For books, use contribution date
            return self.book_contribution_date
        
        # For articles, try to construct from PubDate elements
        pubdate_element = self.content.find(self._root + '/Article/Journal/JournalIssue/PubDate')
        if pubdate_element is not None:
            constructed_date = self._construct_datetime(pubdate_element)
            if constructed_date:
                return constructed_date
        
        # Fallback to history dates if available
        if self.history:
            # Try common PubMed history statuses in order of preference
            for status in ['pubmed', 'entrez', 'received', 'accepted']:
                if status in self.history and self.history[status]:
                    return self.history[status]
        
        return None

    def _construct_datetime(self, d):
        names = ['Year', 'Month', 'Day']
        # if any part is missing, python will default to setting it to 1 anyway.
        parts = {'year': 1, 'month': 1, 'day': 1}
        
        # First try to parse structured date elements (Year, Month, Day)
        found_structured_date = False
        for name in names:
            if d.find(name) is not None:
                item = d.find(name).text
                found_structured_date = True
                try:
                    parts[name.lower()] = int(item)
                except ValueError:
                    if name.lower() == 'year':
                        # fixes spurious crap seen at least once: "2007 (details online)" (pmid 19659763)
                        parts['year'] = int(item[:4])
                    elif name.lower() == 'month':
                        # Force to 3-letter month name (months can look like "December", "Dec", "1")
                        parts['month'] = time.strptime(item[:3], '%b').tm_mon
                except TypeError:
                    # item is None
                    pass
        
        # If we found structured dates, use them
        if found_structured_date:
            try:
                return datetime(**parts)
            except ValueError:
                # one of the values didn't parse, or maybe it was like pmid 17924334
                # where the "accepted" year was "20007". at any rate, forget it.
                return None
        
        # If no structured date, try MedlineDate
        medline_elem = d.find('MedlineDate')
        if medline_elem is not None and medline_elem.text:
            return self._parse_medlinedate(medline_elem.text)
        
        # No date information found
        return None
    
    def _parse_medlinedate(self, medline_text):
        """Parse MedlineDate strings like '2007 Spring', '1999-2000', '2007 Mar-Apr'"""
        import re
        
        if not medline_text:
            return None
        
        # Clean the text
        text = medline_text.strip()
        
        # Extract 4-digit year - look for first occurrence
        year_match = re.search(r'\b(19|20)\d{2}\b', text)
        if not year_match:
            return None
        
        year = int(year_match.group())
        
        # Default to January 1st
        month = 1
        day = 1
        
        # Try to extract month information
        month_patterns = [
            # Full month names
            (r'\b(January|Jan)\b', 1), (r'\b(February|Feb)\b', 2), (r'\b(March|Mar)\b', 3),
            (r'\b(April|Apr)\b', 4), (r'\b(May)\b', 5), (r'\b(June|Jun)\b', 6),
            (r'\b(July|Jul)\b', 7), (r'\b(August|Aug)\b', 8), (r'\b(September|Sep)\b', 9),
            (r'\b(October|Oct)\b', 10), (r'\b(November|Nov)\b', 11), (r'\b(December|Dec)\b', 12),
            # Seasons (map to approximate months)
            (r'\b(Spring)\b', 3), (r'\b(Summer)\b', 6), (r'\b(Fall|Autumn)\b', 9), (r'\b(Winter)\b', 12),
        ]
        
        for pattern, month_num in month_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                month = month_num
                break
        
        # Try to extract day if present
        day_match = re.search(r'\b(\d{1,2})\b', text)
        if day_match:
            try:
                potential_day = int(day_match.group())
                if 1 <= potential_day <= 31:
                    day = potential_day
            except ValueError:
                pass
        
        try:
            return datetime(year=year, month=month, day=day)
        except ValueError:
            # Invalid date combination, fallback to year only
            return datetime(year=year, month=1, day=1)

    def _get_bookaccession_id(self):
        for item in self.content.findall('BookDocument/ArticleIdList/ArticleId'):
            if item.get('IdType') == 'bookaccession':
                return item.text

    def _get_book_title(self):
        return self._get('BookDocument/Book/BookTitle')

    def _get_book_articletitle(self):
        return self._get('BookDocument/ArticleTitle')

    def _get_book_authors(self):
        authors = [_xml_au_to_last_fm(au) for au in self.content.findall('BookDocument/AuthorList/Author')]
        return authors

    def _get_book_author_list(self):
        authors = [PubMedAuthor(au) for au in self.content.findall('BookDocument/AuthorList/Author')]
        return authors

    def _get_book_publisher(self):
        return self._get('BookDocument/Book/Publisher/PublisherName')

    def _get_book_publisher_location(self):
        return self._get('BookDocument/Book/Publisher/PublisherLocation')

    def _get_book_language(self):
        return self._get('BookDocument/Language')

    def _get_book_editors(self):
        return [_xml_au_to_last_fm(au) for au in self.content.findall('BookDocument/Book/AuthorList/Author')]

    def _get_book_abstracts(self):
        abd = OrderedDict()
        for item in self.content.findall('BookDocument/Abstract/AbstractText'):
            abd[item.get('Label')] = self._extract_text(item)
        return abd

    def _get_book_sections(self):
        sections = {}
        for item in self.content.findall('BookDocument/Sections/Section'):
            sec_title = item.find('SectionTitle')
            sections[sec_title.get('sec')] = sec_title.text
        return sections

    def _get_book_abstract(self):
        abstract_strs = ['%s: %s' % (key, val) for key, val in self.book_abstracts.items()]
        return '\n'.join(abstract_strs)

    def _get_book_copyright(self):
        return self._get('BookDocument/Abstract/CopyrightInformation')

    def _get_book_medium(self):
        return self._get('BookDocument/Book/Medium')

    def _get_book_contribution_date(self):
        contribution_date_element = self.content.find('BookDocument/ContributionDate')
        if contribution_date_element is not None:
            return self._construct_datetime(self.content.find('BookDocument/ContributionDate'))
        return None

    def _get_book_date_revised(self):
        return self._construct_datetime(self.content.find('BookDocument/DateRevised'))

    def _get_book_synonyms(self):
        syn_list = self.content.find('BookDocument/ItemList')
        if syn_list is not None and syn_list.get('ListType') == 'Synonyms':
            return [item.text for item in self.content.findall('BookDocument/ItemList/Item')]
        else:
            return []

    def _get_book_history(self):
        history = {}
        items = self.content.findall('PubmedBookData/History/PubMedPubDate')
        for item in items:
            history[item.get('PubStatus')] = self._construct_datetime(item)
        return history

    def _get_book_publication_status(self):
        return self._get('PubmedBookData/PublicationStatus')

    def _get_book_year(self):
        if self.book_contribution_date:
            return self.book_contribution_date.year
        return None

    def _get_pmid(self):
        return self._get(self._root+'/PMID')

    def _get_url(self):
        return 'https://ncbi.nlm.nih.gov/pubmed/'+str(self.pmid)

    def _get_abstract(self):
        abstracts = self.content.findall(self._root + '/Article/Abstract/AbstractText')
        if abstracts == []:
            return self._get(self._root+'/Article/Abstract/AbstractText')

        if len(abstracts) == 1:
            return self._extract_text(abstracts[0])

        # This is a type of PMA with several AbstractText listings
        # for a structured abstract, see https://www.nlm.nih.gov/bsd/policy/structured_abstracts.html 
        abd = OrderedDict()
        for ab in abstracts:
            abd[ab.get('Label')] = self._extract_text(ab)
        return '\n'.join(['%s: %s' % (key, val) for key, val in abd.items()])

    def _get_authors(self):
        # N.B. Citations may have 0 authors. e.g., pmid:7550356
        authors = [_xml_au_to_last_fm(au) for au in self.content.findall(self._root+'/Article/AuthorList/Author')]
        return authors

    def _get_author_list(self):
        authors = [PubMedAuthor(au) for au in self.content.findall(self._root+'/Article/AuthorList/Author')]
        return authors

    def _get_authors_str(self):
        return '; '.join(self.authors)

    def _get_author1_last_fm(self):
        """ return first author's name, in format Last INITS (space between surname and initials)"""
        # return _xml_au_to_last_fm(self.content.find(self._root+'/Article/AuthorList/Author'))
        if self.authors:
            return self.authors[0]
        else:
            return None

    def _get_author1_lastfm(self):
        """return first author's name, in format LastINITS (no space between surname and initials)"""
        if self.author1_last_fm is not None:
            return self.author1_last_fm.replace(' ', '')
        return None

    def _get_keywords(self):
        keyword_list = [kw.text for kw in self.content.findall(self._root+'/KeywordList/Keyword')]
        return keyword_list

    def _get_journal(self):
        j = self._get(self._root+'/Article/Journal/ISOAbbreviation')
        if j is None:
            # e.g., https://www.ncbi.nlm.nih.gov/pubmed?term=21242195
            j = self._get(self._root+'/Article/Journal/Title')
        return j

    def _get_pages(self):
        return self._get(self._root+'/Article/Pagination/MedlinePgn')

    def _get_first_page(self):
        try:
            return self.pages.split('-')[0]
        except AttributeError:
            return self.pages

    def _get_last_page(self):
        try:
            lastnum = self.pages.split('-')[1]
        except (IndexError, AttributeError):
            return None
        try:
            # Return true last page from pages attribute, i.e if self.pages is
            # "148-52", return "152".  If self.pages is "291-4", return "294".
            if int(lastnum) < int(self.first_page):
                return self.first_page[:-len(lastnum)] + lastnum

            # If lastpage for some reason was not a number, just return it as-is.
        except (ValueError, TypeError):
            return lastnum

    def _get_title(self):
        return self._get(self._root+'/Article/ArticleTitle')

    def _get_volume(self):
        try:
            return self.content.find(self._root+'/Article/Journal/JournalIssue/Volume').text
        except AttributeError:
            return None

    def _get_issue(self):
        try:
            return self.content.find(self._root+'/Article/Journal/JournalIssue/Issue').text
        except AttributeError:
            return None

    def _get_volume_issue(self):
        ji = self.content.find(self._root+'/Article/Journal/JournalIssue')
        try:
            return '%s(%s)' % (ji.find('Volume').text, ji.find('Issue').text)

        except AttributeError:
            pass
        try:
            return ji.find('Volume').text
        except AttributeError:
            pass
        # electronic pubs may not have volume or issue
        # e.g., https://www.ncbi.nlm.nih.gov/pubmed?term=20860988
        return None

    def _get_article_history(self):
        history = {}
        pubdates = self.content.find('PubmedData/History')
        if pubdates is not None:
            for pubdate in pubdates.getchildren():
                history[pubdate.get('PubStatus')] = self._construct_datetime(pubdate)
        return history

    def _get_year(self):
        y = self._get(self._root+'/Article/Journal/JournalIssue/PubDate/Year')
        if y is None:
            # case applicable for pmid:9887384 (at least)
            try:
                y = self._get(self._root+'/Article/Journal/JournalIssue/PubDate/MedlineDate')[0:4]
            except TypeError:
                pass
        return y

    def _get_doi(self):
        return self._get('PubmedData/ArticleIdList/ArticleId[@IdType="doi"]')

    def _get_pii(self):
        return self._get('PubmedData/ArticleIdList/ArticleId[@IdType="pii"]')

    def _get_pmc(self):
        try:
            return self._get('PubmedData/ArticleIdList/ArticleId[@IdType="pmc"]')[3:]
        except TypeError:
            return None

    def _get_issn(self):
        return self._get(self._root+'/Article/Journal/ISSN')

    def _get_mesh_headings(self):
        if self.pubmed_type == 'book':
            return None

        meshtags = self.content.findall('MedlineCitation/MeshHeadingList/MeshHeading')
        outd = {}
        for mesh in meshtags:
            descript = mesh.find('DescriptorName')  # should always be present
            dui = descript.get('UI')

            qualifiers_list = []
            for qual in mesh.findall('QualifierName'):
                qualifiers_list.append({
                    'qualifier_name': qual.text,
                    'qualifier_ui': qual.get('UI'),
                    'qualifier_major_topic': True if qual.get('MajorTopicYN') == 'Y' else False,
                })

            outd[dui] = {
                'descriptor_name': descript.text,
                'descriptor_major_topic': True if descript.get('MajorTopicYN') == 'Y' else False,
                'qualifiers': qualifiers_list,
            }
        return outd

    def _get_chemicals(self):
        if self.pubmed_type == 'book':
            return None

        outd = {}
        chemicals = self.content.findall('MedlineCitation/ChemicalList/Chemical')
        for chem in chemicals:
            substance = chem.find('NameOfSubstance')
            regnum = chem.find('RegistryNumber').text  # very often this is '0'
            outd[substance.get('UI')] = {
                    'substance_name': substance.text,
                    'registry_number': regnum
                }
        return outd

    def _get_publication_types(self):
        outd = {}
        pubtypes = self.content.findall('MedlineCitation/Article/PublicationTypeList/PublicationType')
        for pt in pubtypes:
            outd[pt.get('UI')] = pt.text
        return outd

    def _get_grantlist(self):
        outl = []
        grants = self.content.findall('MedlineCitation/GrantList')
        for gr in grants:
            outl.append({'agency': gr.get('Agency', None), 'country': gr.get('Country', None)})
        return outl

    def __str__(self):
        # [article example] 
        # Asensio C, Pérez-Díaz JC. A new family of low molecular weight antibiotics from enterobacteria. Biochem Biophys Res Commun. 1976 Mar 8;69(1):7-14. 
        if self.pubmed_type == 'article':
            return '<PubMedArticle {pmid}> {authors_str}. {title}. {journal}. {year}. {volume_issue}:{pages}'.format(**self.to_dict())
        else:
            return '<PubMedBook {pmid}> {title}. {authors_str}. {book_title}. {year}'.format(**self.to_dict())


############################################################################
## Utilities

def _xml_au_to_last_fm(au):
    "Medline XML specific conversion of author name to lastname-firstinitial format."

    if au is None:
        return
    try:
        return au.find('LastName').text + ' ' + au.find('Initials').text
    except AttributeError:
        pass
    try:
        return au.find('CollectiveName').text
    except AttributeError:
        pass
    try:
        return au.find('LastName').text
    except AttributeError:
        pass
    raise MetaPubError("Author structure not recognized")


def square_voliss_data_for_pma(pma):
    """ Takes a PubMedArticle object, returns same object with corrected volume/issue
    information (if needed)
    """
    if pma.volume != None and pma.issue is None:
        # try to get a number out of the parts that came after the first number.
        volparts = re_numbers.findall(pma.volume)
        if len(volparts) > 1:
            pma.volume = volparts[0]
            # take a guess. best we can do. this often works (e.g. Brain journal)
            pma.issue = volparts[1]
    if pma.issue and pma.volume:
        if pma.issue.find('Pt') > -1:
            pma.issue = re_numbers.findall(pma.issue)[0]
    return pma

def determine_pubmed_xml_type(xmlstr):
    """ Returns string "type" of pubmed article XML based on presence of expected strings.

    Possible returns:
        'article'
        'book'
        'unknown'

    :param xmlstr: xml in any data type (str, bytes, unicode...)
    :return typestring: (str)
    :rtype: str
    """
    if type(xmlstr)==bytes:
        xmlstr = xmlstr.decode()
    if '<PubmedBookArticle>' in xmlstr:
        return 'book'
    elif '<PubmedArticle>' in xmlstr:
        return 'article'

    return 'unknown'

