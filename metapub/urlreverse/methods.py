from __future__ import absolute_import, print_function, unicode_literals

import re

from ..dx_doi import DxDOI
from ..exceptions import DxDOIError, BadDOI
from ..text_mining import find_doi_in_string, scrape_doi_from_article_page
from ..utils import hostname_of, rootdomain_of

from .hostname2jrnl import HOSTNAME_TO_JOURNAL_MAP
from .hostname2doiprefix import HOSTNAME_TO_DOI_PREFIX_MAP


# string templates
OFFICIAL_PII_FORMAT = '{pt1}-{pt2}({pt3}){pt4}-{pt5}'


# VIP (volume-issue-page)
re_vip = re.compile('(?P<hostname>.*?)\/content(\/\w+)?\/(?P<volume>\d+)\/(?P<issue>\w+)\/(?P<first_page>\w+)', re.I)

# PMID in url
re_pmidlookup = re.compile('.*?(\?|&)pmid=(?P<pmid>\d+)', re.I)
re_pubmed_pmid = re.compile('.*?ncbi.nlm.nih.gov\/pubmed\/(?P<pmid>\d+)')

# PMCID in url
re_pmcid = re.compile('.*?(?P<hostname>ncbi.nlm.nih.gov|europepmc.org)\/.*?(?P<pmcid>PMC\d+)', re.I)

# PII -- see http://en.wikipedia.org/wiki/Publisher_Item_Identifier
pii_official = '(?P<pii>S\d{4}-\d{4}\(\d{2}\)\d{5}-\w{1})'
re_sciencedirect_pii_simple = re.compile('.*?(?P<hostname>sciencedirect\.com)\/science\/article\/pii\/(?P<pii>S\d+\w?)', re.I)
re_sciencedirect_pii_official = re.compile('.*?(?P<hostname>sciencedirect\.com)\/science\/article\/pii\/' + pii_official, re.I)
re_cell_pii_simple = re.compile('.*?(?P<hostname>cell\.com)\/(?P<journal_abbrev>.*?)\/(pdf|abstract|fulltext|pdfExtended)\/(?P<pii>S\d+)', re.I)
re_cell_pii_official = re.compile('.*?cell.com\/((?P<journal_abbrev>.*?)\/)?(pdf|abstract|fulltext|pdfExtended)\/' + pii_official, re.I)
re_cell_old_style = re.compile('.*?(?P<hostname>cell\.com)\/(pdf|abstract|fulltext)\/(?P<pii>\d+)', re.I)

# Unique
re_jstage = re.compile('.*?(?P<hostname>jstage\.jst\.go\.jp)\/article\/(?P<journal_abbrev>.*?)\/(?P<volume>\d+)\/(?P<issue>.*?)\/(?P<info>).*?\/', re.I)
re_jci = re.compile('.*?jci\.org\/articles\/view\/(?P<jci_id>\d+)', re.I)
re_karger = re.compile('.*?(?P<hostname>karger\.com)\/Article\/(Abstract|Pdf)\/(?P<kid>\d+)', re.I)
#re_ahajournals = re.compile('\/(?P<doi_suffix>\w+\.\d+\.\d+\.\w+)', re.I)
re_ahajournals = re.compile('\/(?P<doi_suffix>[a-z0-9]+\.\d+\.\d+\.[a-z0-9]+)', re.I)
re_elifesciences = re.compile('(^|http?:\/\/)elifesciences.org\/content\/(?P<volume>\d+)\/e(?P<ident>\d+)', re.I)
re_elifesciences_figures = re.compile('elifesciences\.org\/elife-articles\/(?P<ident>\d+)\/figures-pdf\/', re.I)

re_bmj = re.compile('(^|http?:\/\/)(?P<subdomain>\w+)\.bmj.com\/content\/(?P<volume>\d+)\/(?P<doi_suffix>bmj.\w+)', re.I)
re_bmj_vip_to_doi = re.compile('(^|http?:\/\/)(?P<subdomain>\w+).bmj.com\/content\/(?P<volume>\d+)\/(?P<issue>\d+)\/(?P<first_page>\w+)', re.I)

# Early release formats
re_early_release = re.compile('(^|(http?):\/\/)(?P<hostname>.*?)\/content(\/\w+)?\/early\/(?P<year>\d+)\/(?P<month>\d+)\/(?P<day>\d+)\/(?P<doi_suffix>.*?)(\.full|\.pdf|\.abstract|$)')


# TODO: Common supplement URL format
#re_supplement_common = re.compile()
# http://jmg.bmj.com/content/suppl/2012/05/09/jmedgenet-2012-100892.DC1/Otocephaly_Supplementary_Table_3.pdf
# http://www.pnas.org/content/suppl/2013/07/08/1305207110.DCSupplemental/sapp.pdf
# http://jmg.bmj.com/content/suppl/2015/07/17/jmedgenet-2015-103132.DC1/jmedgenet-2015-103132supp.pdf

re_pnas_supplement = re.compile('.*?pnas.org\/content\/suppl\/(?P<year>\d+)\/(?P<month>\d+)\/(?P<day>\d+)\/(?P<ident>.*?)\/', re.I)

# dx.doi.org self-cacheing lookup engine.
DXDOI_INSTANCE = None

def DXDOI():
    global DXDOI_INSTANCE
    if not DXDOI_INSTANCE:
        DXDOI_INSTANCE = DxDOI()
    return DXDOI_INSTANCE


def get_journal_name_from_url(url):
    if not url.lower().startswith('http'):
        url = 'http://' + url

    hostname = hostname_of(url)

    if hostname in HOSTNAME_TO_JOURNAL_MAP.keys():
        return HOSTNAME_TO_JOURNAL_MAP[hostname]
    else:
        return None


def get_pnas_doi_from_link(url):
    """ PNAS (proceedings of the national academy of sciences of the USA)

    Examples:
        http://www.pnas.org/content/suppl/2013/07/08/1305207110.DCSupplemental/sapp.pdf --> 10.1073/pnas.1305207110

    :param url: (str)
    :return: doi (str) or None
    """
    out = '10.1073/pnas.'
    match = re_pnas_supplement.match(url)
    if match:
        doi_suffix = match.groupdict()['ident'].split('.')[0]
        return out + doi_suffix
    return None


def get_elifesciences_doi_from_link(url):
    """ eLIFE / http://elifesciences.org

    Examples:
        * http://elifesciences.org/content/5/e12203 --> 10.7554/eLife.12203
        * http://elifesciences.org/content/4/e11205 --> 10.7554/eLife.11205
        * http://elifesciences.org/content/4/e11205-download.pdf
        * http://cdn.elifesciences.org/elife-articles/11205/figures-pdf/elife11205-figures.pdf?xxxx

    :param url: (str)
    :return: doi (str) or None
    """
    if 'elifesciences.org' not in url:
        return None

    out = '10.7554/eLife.'
    patterns = [re_elifesciences,
                re_elifesciences_figures]

    for pattern in patterns:
        match = pattern.match(url)
        if match:
            doi_suffix = match.groupdict()['ident']
            return out + doi_suffix

    return None


def get_bmj_doi_from_link(url):
    """ BMJ and subsidiaries use a VIP-ish format that can *sometimes* be mapped to their real
    DOIs. In the case that this process fails, use of the VIP->citation routines should work.

    List of BMJ Journals: http://journals.bmj.com/

    Examples:
        http://jmg.bmj.com/content/39/6/e31.full --> 10.1136/jmg.39.6.e31
        http://www.bmj.com/content/353/bmj.i2195 --> 10.1136/bmj.i2195
        http://www.bmj.com/content/353/bmj.i2139 --> 10.1136/bmj.i2139

    Returns None (should be caught by find_doi_in_string):
        http://bmjopengastro.bmj.com/doi/full/10.1136/bmjgast-2015-000075 --> 10.1136/bmjgast-2015-000075

    Returns None (must use VIP->citation routines):
        http://gut.bmj.com/content/65/5/767.abstract --> 10.1136/gutjnl-2015-311246

    :param url: (str)
    :return: doi (str) or None
    """
    
    if 'bmj.com' not in url:
        return None

    out = '10.1136/'
    doi = None

    BMJ_VIP_TO_DOI_DOMAINS = ['jmg']
    match = re_bmj_vip_to_doi.match(url)
    if match:
        parts = match.groupdict()
        if parts['subdomain'] in BMJ_VIP_TO_DOI_DOMAINS:
            doi = out + '{subdomain}.{volume}.{issue}.{first_page}'.format(**parts)

    else:
        match = re_bmj.match(url)
        if match:
            parts = match.groupdict()
            doi = out + parts['doi_suffix']

    # gotta test that doi. it might be a dud.
    if doi:
        try:
            DXDOI().resolve(doi)
            return doi
        except (BadDOI, DxDOIError):
            return None
    return None


def get_spandidos_doi_from_link(url):
    """ Spandidos urls follow several different conventions and their website seems to be undergoing
    some changes recently. For now, let's just scrape the page for the first available DOI.

    Examples:
        http://www.spandidos-publications.com/or/30/2/553 --> 10.3892/or.2013.2535
        http://www.spandidos-publications.com/10.3892/or.2016.4700 --> 10.3892/or.2013.2535
        http://www.spandidos-publications.com/10.3892/or.2013.2535/abstract --> 10.3892/or.2013.2535

    :param url: (str)
    :return: doi (str) or None
    """
    if 'spandidos-publications.com' not in url:
        return None

    url = url.replace('download', 'abstract')
    return scrape_doi_from_article_page(url)


def get_karger_doi_from_link(url):
    """ Karger IDs can be found in the URL after the "PDF" or "Abstract" piece, and used to
    compose a DOI by prepending enough zeroes to make a 9-digit number. The Karger publisher
    ID is 10.1159

    e.g.
       http://www.karger.com/Article/Abstract/329047 --> 10.1159/000329047
       http://www.karger.com/Article/Abstract/83388 --> 10.1159/000083388

    :param url: (str)
    :return: doi (str) or None
    """
    out = '10.1159/'
    match = re_karger.match(url)
    if match:
        kid = match.groupdict()['kid']
        num_zeroes_needed = 9 - len(kid)
        return out + '0'*num_zeroes_needed + kid
    else:
        return None


def get_jstage_doi_from_link(url):
    """ Since the jstage urls are composed with some degree of unpredictability with respect to
    what's found in segment that ought to contain the first_page element, we have to load the _article
    page (if we can) and try to extract the DOI.

    :param url: (str)
    :return: doi or None
    """
    match = re_jstage.match(url)
    if match:
        if url.find('_pdf') > -1:
            url = url.replace('_pdf', '_article')
        return scrape_doi_from_article_page(url)


def get_sciencedirect_doi_from_link(url):
    """ We can extract the PII from most sciencedirect links. To get a DOI, we may be able to
    simply append the PII to the publisher code "10.1016/", or we may have to inject the special
    character separaters into the PII numbers.

    Example:
        http://www.sciencedirect.com/science/article/pii/S0094576599000673

        PII = S0094576599000673
        DOI = 10.1016/S0094-5765(99)00067-3

    :param url: (str)
    :return: doi or None
    """
    if 'sciencedirect.com' not in url:
        return None

    out = '10.1016/'

    try:
        pii = re_sciencedirect_pii_simple.match(url).groupdict()['pii']
        pii = OFFICIAL_PII_FORMAT.format(pt1=pii[:5], pt2=pii[5:9], pt3=pii[9:11], pt4=pii[11:16], pt5=pii[16])
    except AttributeError:
        try:
            pii = re_sciencedirect_pii_official.match(url).groupdict()['pii']
        except AttributeError:
            return None
    doi = out + pii
    try:
        DXDOI().resolve(doi)
        return doi
    except DxDOIError:
        # some
        pass

    # use URL scrape
    return scrape_doi_from_article_page('http://www.sciencedirect.com/science/article/pii/%s' % pii)


def get_cell_doi_from_link(url):
    """ Cell and ScienceDirect links have similar properties, but there are several different url
    types for Cell abstracts and PDFs (much like biomedcentral).

    Examples:
        http://www.cell.com/pdf/0092867480906212.pdf --> 10.1016/0092-8674(80)90621-2
        http://www.cell.com/cancer-cell/pdf/S1535610806002844.pdf --> 10.1016/j.ccr.2006.09.010
        http://www.cell.com/molecular-cell/abstract/S1097-2765(00)80321-4 --> 10.1016/S1097-2765(00)80321-4
        http://www.cell.com/current-biology/fulltext/S0960-9822%2816%2930170-1 --> 10.1016/j.cub.2016.03.002
        http://www.cell.com/cell-reports/pdfExtended/S2211-1247(15)01030-X --> 10.1016/j.celrep.2015.09.019
        http://www.cell.com/ajhg/pdfExtended/S0002-9297(16)30051-9 --> 10.1016/j.ajhg.2016.03.016
        http://www.cell.com/ajhg/pdf/S0002-9297(16)00050-1.pdf --> 10.1016/j.ajhg.2016.03.016

    Unsolved cases:
        http://www.cell.com/cms/attachment/2020150130/2039963519/mmc1.pdf --> 10.1016/j.neuron.2014.09.027
        http://www.cell.com/cms/attachment/2024895080/2044576473/mmc1.pdf --> 10.1016/j.ajhg.2009.01.009
        http://www.cell.com/cms/attachment/2030360419/2047969851/mmc1.xlsx --> ?
        http://www.cell.com/cms/attachment/2030360419/2047969852/mmc2.xlsx --> ?

    :param url: (str)
    :return: doi or None
    """
    if 'cell.com' not in url:
        return None

    out = '10.1016/'
    pii = ''

    # Try "official" pii format first
    match = re_cell_pii_official.match(url)
    if match:
        pii = match.groupdict()['pii']

    else:
        # Try "simple" (no punctuation) pii formats.
        match = re_cell_pii_simple.match(url)
        if match:
            pii = match.groupdict()['pii']
            pii = OFFICIAL_PII_FORMAT.format(pt1=pii[:5], pt2=pii[5:9], pt3=pii[9:11], pt4=pii[11:16], pt5=pii[16])

        else:
            # Try "old style" (has no "S" in front).
            match = re_cell_old_style.match(url)
            if match:
                pii = match.groupdict()['pii']
                pii = OFFICIAL_PII_FORMAT.format(pt1=pii[:4], pt2=pii[4:8], pt3=pii[8:10], pt4=pii[10:15], pt5=pii[15])

    if match:
        journal_abbrev = match.groupdict().get('journal_abbrev', None)
        if journal_abbrev and journal_abbrev in ['cancer-cell', 'current-biology', 'cell-reports', 'ajhg']:
            url = url.replace('pdfExtended', 'abstract')
            url = url.replace('/pdf/', '/abstract/')
            url = url.replace('.pdf', '')
            return scrape_doi_from_article_page(url)

        return out + pii

    return None


# TODO: nature function needs improvement (Older articles, mostly).
def get_nature_doi_from_link(link):
    """ Custom method to get a DOI from a nature.com URL

    Examples:
        http://www.nature.com/modpathol/journal/vaop/ncurrent/extref/modpathol2014160x3.xlsx -->
        http://www.nature.com/onc/journal/v26/n57/full/1210594a.html --> 10.1038/sj.onc.1210594
        http://www.nature.com/pr/journal/v79/n5/full/pr201635a.html --> 10.1038/pr.2016.35

    Older articles may have very different DOIs, so at the tail end of this process we do a lookup
    in dx.doi.org.  If the DOI is invalid, we should use scrape_doi_from_article_page and return
    that instead.

    Example of older-style DOI from Pediatric Research journal ('pr'):
        http://www.nature.com/pr/journal/v49/n1/full/pr20018a.html --> 10.1203/00006450-200101000-00008

    :param link: the URL
    :return: a string containing a DOI, if one was resolved, or None
    """
    # TODO: check validity of DOI before returning.
    # Some older articles need to have their pages loaded and doi scraped.
    # example: http://www.nature.com/pr/journal/v49/n1/full/pr20018a.html --> 10.1203/00006450-200101000-00008

    if 'nature.com' not in link:
        return None

    # this is a non-comprehensive list of nature journals
    style1journals = ['gimo', 'nature', 'nbt', 'ncb', 'nchembio', 'ncomms', 'ng', 'nm', 'nn',
                      'nrc', 'nrm', 'nsmb', 'srep']

    # example: link:http://www.nature.com/modpathol/journal/vaop/ncurrent/extref/modpathol2014160x3.xlsx
    #          doi:10.1038/modpathol.2014.160
    style2journals = ['aps', 'bjc', 'cddis', 'cr', 'ejhg', 'gim', 'jcbfm', 'jhg', 'jid', 'labinvest', 'leu',
                      'modpathol', 'mp', 'onc', 'oncsis', 'pr']


    match = re.search(r'nature.com/[a-zA-z]+/', link)

    if match:
        try:
            journal_abbrev = match.group(0).split('/')[1]
        except:
            print('Warning: Unable to extract journal abbrev from link {}'.format(link))
            journal_abbrev = None

    # Example: http://www.nature.com/neuro/journal/v13/n11/abs/nn.2662.html
    if journal_abbrev == 'neuro':
        journal_abbrev = 'nn'

    match = re.search(r'%s\.{0,1}\d+' % journal_abbrev, link)
    if match:
        doi_suffix = match.group(0)
        if doi_suffix.endswith('.'):  # strip off a trailing period
            doi_suffix = doi_suffix[:-1]

        # the DOI suffix can be taken directly for these journals
        if journal_abbrev in style1journals:
            return '10.1038/{}'.format(doi_suffix)

        # style2journals are the default
        else:
            year = doi_suffix[len(journal_abbrev):len(journal_abbrev)+4]
            num = doi_suffix[len(journal_abbrev)+4:]
            return '10.1038/{}.{}.{}'.format(journal_abbrev, year, num)

    # http://www.nature.com/articles/cr2009141 :
    # http://www.nature.com/articles/cddis201475
    # http://www.nature.com/articles/nature03404
    # http://www.nature.com/articles/ng.2223
    # http://www.nature.com/articles/nsmb.2666
    match = re.search(r'articles/(([a-z]+)\.{0,1}(\d+))', link)
    if match:
        full_match = match.group(0)
        suffix = match.group(1)
        journal_abbrev = match.group(2)
        num = match.group(3)
        if journal_abbrev in style1journals:
            return '10.1038/{}'.format(suffix)
        else:
            return '10.1038/{}.{}.{}'.format(journal_abbrev, num[:4], num[4:])

    # http://www.nature.com/leu/journal/v19/n11/abs/2403943a.html : 10.1038/sj.leu.2403943
    # http://www.nature.com/onc/journal/v26/n57/full/1210594a.html :  doi:10.1038/sj.onc.1210594
    match = re.search(r'full/\d+|abs/\d+', link)
    if match:
        num = match.group(0).split('/')[1]
        return '10.1038/sj.{}.{}'.format(journal_abbrev, num)

    # nothing? try scraping the page.

    link = link.replace('.pdf', '.html')
    return scrape_doi_from_article_page(link)


def get_biomedcentral_doi_from_link(link):
    """ Custom method to get a DOI from a biomedcentral.com URL

    :param link: (str) the URL
    :return: doi (str) or None
    """
    # style 1:
    # http://www.biomedcentral.com/content/pdf/bcr1282.pdf : doi:10.1186/bcr1282
    # http://www.biomedcentral.com/content/pdf/1465-9921-12-49.pdf : doi:10.1186/1465-9921-12-49
    # http://www.biomedcentral.com/content/pdf/1471-2164-16-S1-S3.pdf : doi:10.1186/1471-2164-16-S1-S3
    # http://www.biomedcentral.com/content/pdf/1753-6561-4-s2-o22.pdf : doi:10.1186/1753-6561-4-S2-O22
    # http://genomebiology.com/content/pdf/gb-2013-14-10-r108.pdf : doi:10.1186/gb-2013-14-10-r108
    # for supplementary, must remove the last 'S' part
    # http://www.biomedcentral.com/content/supplementary/bcr1865-S3.doc : doi:10.1186/bcr1865
    # http://www.biomedcentral.com/content/supplementary/bcr3584-S1.pdf : doi:10.1186/bcr3584
    # http://www.biomedcentral.com/content/supplementary/1471-2105-11-300-S1.PDF : doi:10.1186/1471-2105-11-300
    # http://www.biomedcentral.com/content/supplementary/1471-2164-12-343-S3.XLS : doi:10.1186/1471-2164-12-343
    # http://www.biomedcentral.com/content/supplementary/1471-2164-14-S3-S7-S1.xlsx : doi:10.1186/1471-2164-14-S3-S7
    # http://www.biomedcentral.com/content/supplementary/gb-2013-14-10-r108-S8.xlsx : doi:10.1186/gb-2013-14-10-r108
    # style 2:
    # http://www.biomedcentral.com/1471-2148/12/114 : doi:10.1186/1471-2164-12-114
    # http://www.biomedcentral.com/1471-2164/15/707/table/T2 : doi:10.1186/1471-2164-15-707
    # http://www.biomedcentral.com/1471-2164/14/S1/S11 doi:10.1186/1471-2164-14-S1-S11
    # http://www.biomedcentral.com/1471-230X/11/31 doi:10.1186/1471-230X-11-31

    if 'biomedcentral.com' not in link:
        return None

    # first, try to use the filename
    if '/content/' in link:
        filename = link.split('/')[-1]
        if '.' in filename:
            base = filename.split('.')[0]
            if '/pdf/' in link:
                return '10.1186/' + base
            elif '/supplementary/' in link:
                i1 = base.rfind('S')
                i2 = base.rfind('s')
                i = max(i1, i2)
                return '10.1186/' + base[:i-1]
    else:
        parse_result = urlparse(link)
        path = parse_result.path
        keywords = ['abstract', 'figure', 'table']
        for kw in keywords:
            if kw in path:
                i = path.find(kw)
                path = path[:i-1]
                break
        if path[-1] == '/':
            path = path[:-1]
        if path[0] == '/':
            path = path[1:]
        return '10.1186/' + path.replace('/', '-')


def get_jci_doi_from_link(url):
    """ Journal of Clinical Investigation (JCI) links have a numerical ID that can be used to
    reconstruct the article's DOI.

    Example:
        http://www.jci.org/articles/view/32496 --> 10.1172/JCI32496
        http://www.jci.org/articles/view/8154/version/1/pdf/render --> 10.1172/JCI8154

    :param url: (str)
    :return: doi or None
    """
    out = '10.1172/JCI'
    match = re_jci.match(url)
    if match:
        return out + match.groupdict()['jci_id']
    else:
        return None


def get_ahajournals_doi_from_link(url):
    """ If this is an ahajournals.org journal, we might be able to compose a DOI using the publisher base
    of 10.1161 and pieces of the URL identifying the article.

    Example:
        http://circimaging.ahajournals.org/content/suppl/2013/04/02/CIRCIMAGING.112.000333.DC1/000333_Supplemental_Material.pdf
                --> 10.1161/CIRCIMAGING.112.000333
        http://jaha.ahajournals.org/content/4/12/e002395.full.pdf --> 10.1161/JAHA.115.002395 

    :param url: (str)
    :return: doi or None
    """
    if 'ahajournals.org' not in url:
        return None

    out = '10.1161/'
    match = re_ahajournals.match(url)
    if match:
        return out + match.groupdict()['doi_suffix']

    url = url.replace('.pdf', '')
    return scrape_doi_from_article_page(url)


def get_early_release_doi_from_link(url):
    """
    Examples:
        http://cancerres.aacrjournals.org/content/early/2015/12/30/0008-5472.CAN-15-0295.full.pdf --> 10.1158/0008-5472.CAN-15-0295
        http://ajcn.nutrition.org/content/early/2016/04/20/ajcn.115.123752.abstract --> 10.3945/ajcn.115.123752
        http://www.mcponline.org/content/early/2016/04/25/mcp.O115.055467.full.pdf+html --> 10.1074/mcp.O115.055467
        http://nar.oxfordjournals.org/content/early/2013/11/21/nar.gkt1163.full.pdf --> 10.1093/nar/gkt1163
        http://jmg.bmj.com/content/early/2008/07/08/jmg.2008.058297 --> 10.1136/jmg.2008.058297

    :param url: (str)
    :return: doi or None
    """

    match = re_early_release.match(url)
    if match:
        resd = match.groupdict()
        hostname = hostname_of(resd['hostname'])
        root_domain = rootdomain_of(hostname)

        # special treatment for oxfordjournals.org
        if root_domain in 'oxfordjournals.org':
            doi_pt1, doi_pt2 = resd['doi_suffix'].split('.', 2)
            doi_suffix = '%s/%s' % (doi_pt1, doi_pt2)
            return HOSTNAME_TO_DOI_PREFIX_MAP['*.oxfordjournals.org'] + '/' + doi_suffix

        if hostname in HOSTNAME_TO_DOI_PREFIX_MAP.keys():
            return HOSTNAME_TO_DOI_PREFIX_MAP[hostname] + '/' + resd['doi_suffix']

        elif '*.%s' % root_domain in HOSTNAME_TO_DOI_PREFIX_MAP.keys():
            # create a "wildcard" subdomain lookup in case that's an option in the hostname-doi map.
            return HOSTNAME_TO_DOI_PREFIX_MAP['*.%s' % root_domain] + '/' + resd['doi_suffix']


def get_generic_doi_from_link(url):
    """ Covers many publisher URLs such as wiley and springer.

    Examples:
        http://onlinelibrary.wiley.com/doi/10.1111/j.1582-4934.2011.01476.x/full --> 10.1111/j.1582-4934.2011.01476.x
        link.springer.com/article/10.1186/1471-2164-7-243 --> 10.1186/1471-2164-7-243
        http://link.springer.com/article/10.1007/s004399900122 --> 10.1007/s004399900122

    :param url: (str)
    :return: doi or None
    """
    doi = find_doi_in_string(url)
    if doi:
        # remove common addenda that may have come from the regular expression.
        for addendum in ['/full', '/asset', '/pdf', '.pdf']:
            place = doi.find(addendum)
            if place > -1:
               doi = doi[:place]

    # we had better check ourselves before we wreck ourselves.
    try:
        DXDOI().resolve(doi)
        return doi
    except (BadDOI, DxDOIError):
        return None


def get_plos_doi_from_link(url):
    """ PLOS one (almost?) always has the DOI in the link, with a twist -- some of 
    the links we run across are DOIs pointing straight to article supplements.

    For example:

        Supplement doi: 10.1371/journal.pone.0094554.s002
        Article doi: 10.1371/journal.pone.0094554

    Since we always want the article DOI for PMID gathering purposes, the DOI 
    returned from this function should be the one pointing to the parent article.

    Examples:
        http://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0154075 --> 10.1371/journal.pone.0154075
        http://journals.plos.org/plosone/article?id=info%3Adoi%2F10.1371%2Fjournal.pone.0153994 --> 10.1371/journal.pone.0153994
        http://journals.plos.org/plosone/article?id=10.1371/journal.pone.0152441#pone-0152441-t002 --> 10.1371/journal.pone.0152441
        http://journals.plos.org/plosone/article/asset?unique&id=info:doi/10.1371/journal.pone.0094554.s002 --> 10.1371/journal.pone.0094554

    :param url: (str)
    :return: doi (str) or None
    """
    if 'plos.org' not in url:
        return None

    doi = find_doi_in_string(url)
    if doi:
        if '#' in doi:
            doi = doi[:doi.find('#')]

        parts = doi.split('.')
        return '.'.join(parts[:4])
    return None


# == DOI search method registry... order matters! don't screw around with it unless you know what you're doing. :) == #
#
# Comments to the right of each method denote which "expensive" operations they use:
#       * "scrape": loading the page to read text off it (usually to get the DOI)
#       * "DxDOI": loading the DOI in dx.doi.org to verify that it is a real DOI.
#
# Some URLs can be reversed to DOIs using 2 or 3 different methods. We're trying to use the least "expensive"
# method that gets the job done, while making sure to avoid false positives.

DOI_METHODS = [get_elifesciences_doi_from_link,
               get_plos_doi_from_link,
               get_early_release_doi_from_link,
               get_cell_doi_from_link,
               get_jci_doi_from_link,
               get_jstage_doi_from_link,            # uses scrape (1st)
               get_pnas_doi_from_link,
               get_bmj_doi_from_link,
               get_ahajournals_doi_from_link,       # uses scrape (2nd)
               get_biomedcentral_doi_from_link,
               get_nature_doi_from_link,
               get_sciencedirect_doi_from_link,     # uses scrape (last) and DxDOI
               get_karger_doi_from_link,
               get_spandidos_doi_from_link,         # uses scrape (1st)
               get_generic_doi_from_link,           # uses DxDOI 
               ]


def try_doi_methods(url):
    """ Tries every "get_*_doi_from_link" method registered in DOI_METHODS and returns a doi
    when/if it finds one. As a last resort, uses find_doi_in_string(url), which may work in cases
    where the DOI can be parsed directly out of the URL.

    :param url: (str)
    :return: {'doi': <doi>, 'method': <method>} or None
    """
    for method in DOI_METHODS:
        doi = method(url)
        if doi:
            return {'doi': doi, 'method': method}
    return None


def try_vip_methods(url):
    """ Many URLs follow the "volume-issue-page" format. If this URL is one of them, this function will return
    a dictionary containing at least the volume, issue, and first_page aspects of this article. The 'jtitle'
    key may or may not be filled in depending on whether metapub is aware of this journal's domain name.

    See metapub/urlreverse/hostname2journal.py for the list of supported journals (and please consider
    contributing to the list if you can).

    :param url: (str)
    :return: dict or None
    """
    match = re_vip.match(url)

    if match:
        jrnl = get_journal_name_from_url(url)
        vipdict = match.groupdict()
        vipdict.update({'format': 'vip', 'jtitle': jrnl})
        return vipdict

    return None


def try_pmid_methods(url):
    """ Attempts to get the PMID directly out of the URL.

    Examples:
        https://www.ncbi.nlm.nih.gov/pubmed/22253870 --> 22253870
        http://aac.asm.org/cgi/pmidlookup?view=long&pmid=7689822 --> 7689822

    :param url: (str)
    :return: pmid or None
    """
    match = re_pmidlookup.match(url)
    if match:
        return match.groupdict()['pmid']

    match = re_pubmed_pmid.match(url)
    if match:
        return match.groupdict()['pmid']

