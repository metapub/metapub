from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

from .aaas import aaas_format, aaas_journals
from .biochemsoc import biochemsoc_format, biochemsoc_journals
from .bmc import BMC_journals, BMC_format
from .cell import cell_format, cell_journals
from .degruyter import degruyter_journals
from .dustri import dustri_journals
from .endo import endo_journals
from .jama import jama_journals
from .jstage import jstage_journals
from .karger import karger_journals, karger_format
from .lancet import lancet_journals
from .nature import nature_journals, nature_format
from .misc_doi import doi_templates, simple_formats_doi
from .misc_pii import simple_formats_pii
from .misc_vip import vip_format, vip_journals, vip_journals_nonstandard
from .scielo import scielo_journals, scielo_format
from .sciencedirect import sciencedirect_journals, sciencedirect_url
from .springer import springer_journals
from .spandidos import spandidos_format, spandidos_journals
from .wiley import wiley_journals
from .wolterskluwer import wolterskluwer_journals

from .cantdo_list import JOURNAL_CANTDO_LIST

from .paywalled import (schattauer_journals, RSC_journals,
                       thieme_journals, weird_paywall_publishers)

# JCI == Journal of Clinical Investigation
jci_journals = ('J Clin Invest')

# NAJMS == North Am J Med Sci
najms_journals = ('N Am J Med Sci')

paywall_journals = schattauer_journals + thieme_journals + \
                   weird_paywall_publishers + RSC_journals

# TODO
# doiserbia (Library of Serbia) articles can be grabbed by doing the_doi_2step,
# then ...?
doiserbia_journals = ('Genetika')

# simple_formats_pmid: links to PDFs that can be constructed using the
# pubmed ID
simple_formats_pmid = {
    'Medicina (B Aires)': 'http://www.medicinabuenosaires.com/PMID/{pmid}.pdf',
}

# journals whose articles can best be accessed by loading up via dx.doi.org
#       and then doing some text replacement on the URL.
doi2step_journals = (
    # ex.
    # http://www.palgrave-journals.com/jphp/journal/v36/n2/pdf/jphp201453a.pdf
    'J Public Health Policy'
)

todo_journals = {
    'Pharmacol Rep': {'example': 'https://www.ncbi.nlm.nih.gov/pubmed/?term=23238479[uid] --> www.if-pan.krakow.pl/pjp/pdf/2012/5_1234.pdf'},
    'Med Sci Monit': {'example': 'http://www.medscimonit.com/download/index/idArt/869530'},
    'Asian Pac J Cancer Prev': {'example': 'http://www.apocpcontrol.org/paper_file/issue_abs/Volume12_No7/1771-1776%20c%206.9%20Lei%20Zhong.pdf'},
    'Rev Esp Cardiol': {'example': 'http://www.revespcardiol.org/en/linkresolver/articulo-resolver/13131646/'},
    'Ann Dermatol Venereol': {'example': 'http://www.em-consulte.com/article/152959/alertePM'},
    'Mol Cells': {'example': 'http://www.molcells.org/journal/view.html?year=2004&volume=18&number=2&spage=141 --> http://pdf.medrang.co.kr/KSMCB/2004/018/mac-18-2-141.pdf'},
    'Mol Vis': {'example': 'http://www.molvis.org/molvis/v10/a45/ --> http://www.molvis.org/bin/pdf.cgi?Zheng,10,45'},
    'Singapore Med J': {'example': 'http://www.sma.org.sg/smj/4708/4708cr4.pdf'},
    'Rev Port Cardiol': {'example': '16335287: http://www.spc.pt/DL/RPC/artigos/74.pdf'},
    'World J Gastroenterol': {'example': 'http://www.wjgnet.com/1007-9327/full/v11/i48/7690.htm --> http://www.wjgnet.com/1007-9327/pdf/v11/i48/7690.pdf'},
    'Genet Mol Res': {'example': '24668667: http://www.geneticsmr.com/articles/2992 --> http://www.geneticsmr.com//year2014/vol13-1/pdf/gmr2764.pdf'},
    'Arq Bras Cardiol': {'example': '20944894: http://www.scielo.br/pdf/abc/v95n5/en_aop13210.pdf'},
    'Arq Bras Endocrinol Metabol': {'example': '15611820: http://www.scielo.br/pdf/abem/v48n1/19521.pdf'},
    'Neoplasma': {'example': '17319787: http://www.elis.sk/download_file.php?product_id=1006&session_id=skl2f3grcd19ebnie17u15a571'},
    'Clinics (Sao Paulo)': {'example': '17823699: http://www.scielo.br/scielo.php?script=sci_arttext&pid=S1807-59322007000400003'},
    'Asian J Androl': {'example': '18097502: http://www.asiaandro.com/Abstract.asp?doi=10.1111/j.1745-7262.2008.00376.x'},
    'Anesthesiology': {'example': '18212565: http://dx.doi.org/10.1097/01.anes.0000299431.81267.3e --> html w/ <a id="pdfLink" data-article-url="THE_URL">'},
    'Nat Prod Commun': {'example': '19634325 (no direct link found yet) -- http://www.naturalproduct.us/'},
    'Oncotarget': {'example': '26008984 (pii = 3900) --> http://www.impactjournals.com/oncotarget/index.php?journal=oncotarget&page=article&op=view&path=3900'},
    'Clin Ter': {'example': '25756258 --> dx.doi.org/10.7417/CT.2015.1799 --> parse page to get PDF'},
    'J Pediatr (Rio J)': {'example': '17102902 --> dx.doi.org/10.2223/JPED.1550 --> http://www.jped.com.br/conteudo/06-82-06-437/port.pdf'},
    'Teach Learn Med': {'example': '17144842 --> dx.doi.org/10.1207/s15328015tlm1804_13 --> pdf link?'},
    'Med Clin (Barc)': {'example': '17145028 --> http://www.elsevier.es/es-revista-medicina-clinica-2-linkresolver-alopecia-androgenica-prematura-un-varon-13094419 --> http://apps.elsevier.es/watermark/ctl_servlet?_f=10&pident_articulo=13094419&pident_usuario=0&pcontactid=&pident_revista=2&ty=94&accion=L&origen=zonadelectura&web=www.elsevier.es&lan=es&fichero=2v127n16a13094419pdf001.pdf'},
    'J Periodontol': {'example': 'http://www.joponline.org/doi/10.1902/jop.2016.150733'},
}
