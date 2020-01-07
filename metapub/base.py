from lxml import etree
from lxml.html.clean import Cleaner

from .exceptions import MetaPubError, BaseXMLError


def parse_elink_response(xmlstr):
    """ return all Ids from an elink XML response

    :param xmlstr:
    :return: list of IDs, or None if XML response empty
    """
    dom = etree.fromstring(xmlstr)
    ids = []

    linkname_elem = dom.find('LinkSet/LinkSetDb/LinkName')
    if linkname_elem is not None:
        if linkname_elem.text:
            linkset = dom.find('LinkSet/LinkSetDb')
            for link in linkset.getchildren():
                if link.find('Id') is not None:
                    ids.append(link.find('Id').text)
            return ids

    # Medgen->Pubmed elink result with "0" in IDList
    """ <eLinkResult><LinkSet><DbFrom>medgen</DbFrom><IdList><Id>0</Id></IdList></LinkSet></eLinkResult> """
    idlist_elem = dom.find('LinkSet/IdList')
    if idlist_elem is not None and len(idlist_elem.getchildren()) > 0:
        for item in idlist_elem.getchildren():
            if item.find('Id') is not None:
                ids.append(link.find('Id').text)
        if len(ids)==1 and ids[0]=='0':
            return []
        else:
            return ids
    return None


class MetaPubObject(object):
    """ Base class for XML parsing objects (e.g. PubMedArticle)
    """

    def __init__(self, xml, root=None, *args, **kwargs):
        '''Instantiate with "xml" as string or bytes containing valid XML.

        Supply name of root element (string) to set virtual top level. (optional).''' 
 
        if not xml:
            if xml == '':
                xml = 'empty'
            raise MetaPubError('Cannot build MetaPubObject; xml string was %s' % xml)
        self.xml = xml
        self.content = self.parse_xml(xml, root)

    @staticmethod
    def parse_xml(xml, root=None):
        '''Takes xml (str or bytes) and (optionally) a root element definition string.

        If root element defined, DOM object returned is rebased with this element as
        root.

        Args:
            xml (str or bytes)
            root (str): (optional) name of root element

        Returns:
            lxml document object.
        '''
        if isinstance(xml, str) or isinstance(xml, bytes):
            dom = etree.XML(xml)
        else:
            dom = etree.XML(xml)

        if root:
            return dom.find(root)
        else:
            return dom

    def _get(self, tag):
        '''Returns content of named XML element, or None if not found.'''
        elem = self.content.find(tag)
        if elem is not None:
            if len(elem.getchildren()):
                return self.__clean_html(elem)
            return elem.text
        return None

    def __clean_html(self, elem):
        '''Removes HTML elements like i, b, and a'''
        cleaner = Cleaner(remove_tags = ['a', 'i', 'b', 'em'])
        return cleaner.clean_html(etree.tostring(elem).decode("utf-8"))\
            .replace("<div>", "").replace("</div>", "").strip() # This part seems hacky to me

# singleton class used by the fetchers.
class Borg(object):
    """ singleton class backing cache engine objects. """
    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state

