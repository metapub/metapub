"""
Compatibility layer that mimics the eutils library interface.
Provides drop-in replacement using the lightweight NCBIClient.
"""

from .ncbi_client import NCBIClient
from .exceptions import MetaPubError


class EutilsRequestError(Exception):
    """Compatibility exception to match eutils library."""
    pass


class QueryService:
    """Drop-in replacement for eutils.QueryService."""
    
    def __init__(self, cache=None, api_key=None, email="", tool="metapub"):
        self.client = NCBIClient(
            api_key=api_key,
            cache_path=cache,
            email=email,
            tool=tool
        )
    
    def efetch(self, params: dict) -> str:
        """Compatibility method for efetch."""
        try:
            db = params.get('db')
            id_param = params.get('id')
            rettype = params.get('rettype', 'xml')
            retmode = params.get('retmode', 'text')
            
            if not db or not id_param:
                raise EutilsRequestError("Missing required parameters: db and id")
            
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