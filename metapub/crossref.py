# -*- coding: utf-8 -*-

import datetime 
import logging

from habanero import Crossref as CREngine
import Levenshtein

from .base import Borg
from .config import DEFAULT_EMAIL
from . import cite

log = logging.getLogger('metapub.crossref')

# for use with Levenshtein distance string comparison of titles in CR results.
TITLE_SIMILARITY_IDEAL_SCORE = .95   # automatically accept results over .95 threshold.
TITLE_SIMILARITY_MIN_SCORE = .8     # throw out results that fall below .8 threshold.


def get_most_similar_work_from_crossref_results(qstring, qname, cr_results):
    """Uses Levanshtein distance on result title to rank CrossRef results. 
    Returns top candidate for a match from these items based on comparison title.

    :param qstring: (str) original query string for search
    :param qname: (str) name of query item (e.g. "title")
    :param cr_results: (dict) crossref results as returned by habanero
    :return: {'title_ld': <score>, 'work': <CrossRefWork or None>} 
    """
    bestcandidate = { qname+'_ld': 0, 'work': None, }

    if cr_results['message']['total-results'] > 0:
        for item in cr_results['message']['items']:
            this = item[qname][0].lower()
            this_ld = Levenshtein.ratio(qstring.lower(), this.lower())
            if this_ld > bestcandidate[qname+'_ld']:
                bestcandidate = { qname+'_ld': this_ld, 'work': item, }

    return bestcandidate


class CrossRefWork(object):
    "Represents one 'work' from CrossRef search results."

    def __init__(self, **kwargs):
        self.doi = kwargs.get('DOI', None)
        self.url = kwargs.get('URL', None)
        self.author = kwargs.get('author', None)
        self.indexed = kwargs.get('indexed', None)
        self.reference_count = kwargs.get('reference-count', None)
        self.publisher = kwargs.get('publisher', None)
        self.issue = kwargs.get('issue', None)
        self.funder = kwargs.get('funder', None)
        self.content_domain = kwargs.get('content-domain', None)
        self.published_print = kwargs.get('published-print', None)
        self.type = kwargs.get('type', None)
        self.created = kwargs.get('created', None)
        self.page = kwargs.get('page', None)
        self.source = kwargs.get('source', None)
        self.is_referenced_by_count = kwargs.get('is-referenced-by-count', None)
        self.title = kwargs.get('title', None)
        self.prefix = kwargs.get('prefix', None)
        self.volume = kwargs.get('volume', None)
        self.member = kwargs.get('member', None)
        self.published_online = kwargs.get('published-online', None)
        self.reference = kwargs.get('reference', None)
        self.container_title = kwargs.get('container-title', None)
        self.language = kwargs.get('language', None)
        self.link = kwargs.get('link', None)
        self.deposited = kwargs.get('deposited', None)
        self.score = kwargs.get('score', None)
        self.editor = kwargs.get('editor', None)
        self.issued = kwargs.get('issued', None)
        self.references_count = kwargs.get('references-count', None)
        self.journal_issue = kwargs.get('journal-issue', None)
        self.relation = kwargs.get('relation', None)
        self.ISSN = kwargs.get('ISSN', None)
        self.issn_type = kwargs.get('issn-type', None)

    @property
    def first_page(self):
        """Returns first page (number) of article as string, or None if self.page is empty."""
        if self.page:
            return self.page.split('-')[0]
        return None

    @property
    def citation(self):
        """Returns a formal citation string for this work."""
        return cite.article(**self.to_citation())

    @property
    def pubyear(self):
        if self.issued:
            return self.issued['date-parts'][0][0]
        return ''

    @property
    def pubmonth(self):
        if self.issued:
            return self.issued['date-parts'][0][1]

    @property
    def pubdate(self):
        if self.issued:
            return datetime.date(self.issued['date-parts'][0])

    @property
    def author1(self):
        for auth in self.author:
            if auth['sequence'] == 'first':
                return auth['given'] + ' ' + auth['family']
        return ''

    @property
    def author1_last_fm(self):
        for auth in self.author:
            if auth['sequence'] == 'first':
                return auth['family'] + ' ' + auth['given'][0].upper()
        return ''

    @property
    def authors_str_lastfirst(self):
        """Returns this work's authors as a semicolon-separated string -- LASTNAME FIRSTInitial."""
        out = self.author1_last_fm
        # assume already sorted by crossref with first author first in the list.
        if len(self.author) > 1:
            for auth in self.author[1:]:
                out += ';' + auth['family'] + ' ' + auth['given'][0].upper()
        return out

    @property
    def author_list(self):
        """Returns this work's authors as a flat list (Firstname Lastname), retaining order given by Crossref."""
        out = []
        for auth in self.author:
            out.append(auth['given'] + ' ' + auth['family'])
        return out

    @property
    def author_list_last_fm(self):
        """Returns this work's authors as a flat list (Lastname FirstInitial), retaining order given by Crossref."""
        out = []
        for auth in self.author:
            out.append(auth['family'] + ' ' + auth['given'][0].upper())
        return out

    def to_citation(self):
        """Describes this work as a dictionary suitable for citation lookups in PubMed."""
        return {'journal': self.container_title[0],
                'year': self.pubyear,
                'title': self.title[0],
                'authors': self.author_list_last_fm,
                'doi': self.doi,
                'volume': self.volume,
                'issue': self.issue,
                'pages': self.page,
                'first_page': self.first_page,
                'aulast': self.author1.split()[-1:][0],    #just the last name of first author.
                }

    def to_dict(self):
        "Describes this Work as a dictionary similar to the one returned by CrossRef."
        outd = self.__dict__.copy()
        outd['references-count'] = outd.pop('references_count')
        outd['issn-type'] = outd.pop('issn_type')
        outd['journal-issue'] = outd.pop('journal_issue')
        outd['container-title'] = outd.pop('container_title')
        outd['published-print'] = outd.pop('published_print')
        outd['is_referenced-by-count'] = outd.pop('is_referenced_by_count')
        outd['published-online'] = outd.pop('published_online')
        outd['content-domain'] = outd.pop('content_domain')
        return outd

    def __str__(self):
        return """<CrossRefWork {doi} Score: {score}> {aulast}. "{title}" {journal}. {year}. {volume}({issue}):{pages}\n\t""".format(score=self.score, **self.to_citation())

    def __repr__(self):
        return "<CrossRefWork DOI: {doi}>".format(doi=self.doi)



class CrossRefFetcher(Borg):

    """Valid field queries for this route are: affiliation, degree, event-acronym, bibliographic, container-title, publisher-name, author, event-theme, standards-body-acronym, chair, event-location, translator, funder-name, event-name, publisher-location, title, standards-body-name, contributor, editor, event-sponsor"""

    def __init__(self, **kwargs):
        self.cr = CREngine(mailto=kwargs.get('email', DEFAULT_EMAIL))
        self.log = logging.getLogger('metapub.crossref.CrossRefFetcher')

    def article_by_doi(self, doi):
        """Returns a CrossRefWork object loaded by querying the Crossref works/DOI REST endpoint.
        
        :param doi: (str)
        :rtype: CrossRefWork
        :raises: HTTPError (404) if DOI not found.
        """
        res = self.cr.works(doi)
        return CrossRefWork(**res['message'])

    def article_by_pma(self, pma, ideal_ld=TITLE_SIMILARITY_IDEAL_SCORE, 
                                  min_ld=TITLE_SIMILARITY_MIN_SCORE):
                
        """From a PubMedArticle object, use as much info as needed to get as precise 
        a match on CrossRef as is possible.

        1st attempt: Title + Journal.  Runs Levenshtein distance on results; if any results have
                     a better similarity ratio than ideal_ld, the top of these results will
                     be returned.  Otherwise, the first item with a score better than min_ld
                     will be kept and compared against 1nd attempt results.

        2nd attempt: Title + First Author.  Same process as 1st attempt but with any candidates
                     found in 1st attempt submitted for comparison.

        Finally: Return CrossRefWork from best candidate that exceeds min_ld requirement.

        :param pma: PubMedArticle object
        :param ideal_ld: (float) [default: set in global at top of crossref.py]
        :param min_ld: (float) [default: set in global at top of crossref.py]
        :rtype: CrossRefWork
        """
        # Try with Title and Journal only
        res = self.cr.works(query_title=pma.title, query_container_title=pma.journal, limit=5)
        self.log.debug('PMID %s: Crossref Title/Journal query got %i results', pma.pmid, res['message']['total-results'])

        bestcandidate = get_most_similar_work_from_crossref_results(pma.title, 'title', res)
    
        # if we have a real winner (exceeds ideal Lev. ratio), let's just take this one.
        if bestcandidate['title_ld'] > ideal_ld:
            self.log.debug('PMID %s: Best candidate had Levanshtein title similarity %f', pma.pmid, bestcandidate['title_ld'])
            return CrossRefWork(**bestcandidate['work'])

        self.log.debug('PMID %s: OK candidate with title_ld %f (title: %s)', pma.pmid, bestcandidate['title_ld'], bestcandidate['work']['title'][0])
        # No/insufficient results, try different combo of details.
        # Run our last candidate (if we got one) in the next pageont.

        # Try with Title and Author
        res = self.cr.works(query_title=pma.title, query_author=pma.author1_lastfm, limit=5)
        self.log.debug('PMID %s: Crossref Title/Author query got %i results', pma.pmid, res['message']['total-results'])

        if res['message']['total-results'] > 0:
            thiscandidate = get_most_similar_work_from_crossref_results(pma.title, 'title', res)
            if thiscandidate['title_ld'] > bestcandidate['title_ld']:
                self.log.debug('PMID %s: Better candidate with title_ld %f (title: %s)', pma.pmid, bestcandidate['title_ld'], bestcandidate['work']['title'][0])
                bestcandidate = thiscandidate

        if bestcandidate['title_ld'] > min_ld:
            self.log.debug('PMID %s: Best candidate with title_ld %f > %f (min_ld) (title: %s)', 
                            pma.pmid, bestcandidate['title_ld'], min_ld, bestcandidate['work']['title'][0])
            return CrossRefWork(**bestcandidate['work'])
            
        else:
            self.log.debug('PMID %s: No suitable CrossRefWork found.', pma.pmid)
            return None

    def article_by_title(self, title, **kwargs):
        """Use CrossRef to find a work by its title. Returns first item in the list.

        Keywords are passed unmodified to crossref.works() [habanero].
        
        :param title: str
        :rtype: CrossRefWork or None (if no results)
        """
        res = self.cr.works(query_title=title, limit=1)
        if res['message']['total-results'] > 0:
            item = res['message']['items'][0]
            return CrossRefWork(**item)
        return None

