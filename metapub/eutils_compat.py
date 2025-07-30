"""
Compatibility layer that mimics the eutils library interface.
Provides drop-in replacement using NCBIClient with proper caching (no eutils dependency).
(This is a transitional step en route to metapub 1.0.)
"""

import logging
from .ncbi_client import NCBIClient
from .exceptions import MetaPubError

try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree

log = logging.getLogger('metapub.eutils_compat')


class EutilsRequestError(Exception):
    """Compatibility exception to match eutils library."""
    pass


class QueryService:
    """Drop-in replacement for eutils.QueryService."""

    def __init__(self, cache=None, api_key=None, email="", tool="metapub"):
        # Use NCBIClient with built-in caching
        self.client = NCBIClient(
            api_key=api_key,
            cache_path=cache,
            email=email,
            tool=tool
        )
        # Expose cache for compatibility with tests
        self._cache = self.client.cache

    def _is_valid_xml_response(self, content: str) -> bool:
        """Validate that response content is actually XML, not HTML error pages."""
        if not content or not content.strip():
            return False

        # Check for obvious HTML markers
        content_lower = content.lower().strip()
        if (content_lower.startswith('<!doctype html') or
            content_lower.startswith('<html') or
            'down_bethesda' in content_lower):
            log.warning("Detected HTML error page in response - not caching")
            return False

        # Try to parse as XML
        try:
            if content.strip().startswith('<?xml'):
                etree.fromstring(content.encode('utf-8'))
            else:
                etree.fromstring(content)
            return True
        except (etree.XMLSyntaxError, Exception) as e:
            log.warning(f"Invalid XML response: {e}")
            return False

    def efetch(self, params: dict) -> str:
        """Compatibility method for efetch."""
        try:
            db = params.get('db')
            id_param = params.get('id')
            rettype = params.get('rettype', 'xml')
            retmode = params.get('retmode', 'text')

            if not db or not id_param:
                raise EutilsRequestError("Missing required parameters: db and id")

            # NCBIClient handles caching and XML validation
            return self.client.efetch(
                db=db,
                id=id_param,
                rettype=rettype,
                retmode=retmode
            )
        except Exception as e:
            if isinstance(e, (MetaPubError, EutilsRequestError)):
                raise EutilsRequestError(str(e)) from e
            else:
                raise EutilsRequestError(f"Request failed: {str(e)}") from e

    def esearch(self, params: dict) -> str:
        """Compatibility method for esearch."""
        try:
            db = params.get('db')
            term = params.get('term')
            retmax = params.get('retmax', 20)
            retstart = params.get('retstart', 0)
            sort = params.get('sort')

            if not db or not term:
                raise EutilsRequestError("Missing required parameters: db and term")

            return self.client.esearch(
                db=db,
                term=term,
                retmax=retmax,
                retstart=retstart,
                sort=sort
            )
        except Exception as e:
            if isinstance(e, (MetaPubError, EutilsRequestError)):
                raise EutilsRequestError(str(e)) from e
            else:
                raise EutilsRequestError(f"Request failed: {str(e)}") from e

    def elink(self, params: dict) -> str:
        """Compatibility method for elink."""
        try:
            dbfrom = params.get('dbfrom')
            id_param = params.get('id')
            db = params.get('db')
            cmd = params.get('cmd', 'neighbor')

            if not dbfrom or not id_param:
                raise EutilsRequestError("Missing required parameters: dbfrom and id")

            return self.client.elink(
                dbfrom=dbfrom,
                id=id_param,
                db=db,
                cmd=cmd
            )
        except Exception as e:
            if isinstance(e, (MetaPubError, EutilsRequestError)):
                raise EutilsRequestError(str(e)) from e
            else:
                raise EutilsRequestError(f"Request failed: {str(e)}") from e

    def esummary(self, params: dict) -> str:
        """Compatibility method for esummary."""
        try:
            db = params.get('db')
            id_param = params.get('id')
            retmode = params.get('retmode', 'xml')

            if not db or not id_param:
                raise EutilsRequestError("Missing required parameters: db and id")

            return self.client.esummary(
                db=db,
                id=id_param,
                retmode=retmode
            )
        except Exception as e:
            if isinstance(e, (MetaPubError, EutilsRequestError)):
                raise EutilsRequestError(str(e)) from e
            else:
                raise EutilsRequestError(f"Request failed: {str(e)}") from e

    def einfo(self, params: dict = None) -> str:
        """Compatibility method for einfo."""
        try:
            if params is None:
                params = {}

            db = params.get('db')
            return self.client.einfo(db=db)
        except Exception as e:
            if isinstance(e, (MetaPubError, EutilsRequestError)):
                raise EutilsRequestError(str(e)) from e
            else:
                raise EutilsRequestError(f"Request failed: {str(e)}") from e
