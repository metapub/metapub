"""
Lightweight NCBI E-utilities client - replacement for eutils library.
Provides direct HTTP interface to NCBI APIs with caching and rate limiting.
"""

import time
import sqlite3
import hashlib
import json
import logging
from urllib.parse import urlencode
from typing import Dict, List, Optional, Union, Any
import requests
from threading import Lock

from .exceptions import MetaPubError
from .ncbi_errors import diagnose_ncbi_error, NCBIServiceError

try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree


log = logging.getLogger('metapub.ncbi_client')


class RateLimiter:
    """Simple rate limiter to respect NCBI API limits."""
    
    def __init__(self, requests_per_second: int = 10):
        self.requests_per_second = requests_per_second
        self.min_interval = 1.0 / requests_per_second
        self.last_request_time = 0
        self.lock = Lock()
    
    def wait_if_needed(self):
        with self.lock:
            now = time.time()
            time_since_last = now - self.last_request_time
            if time_since_last < self.min_interval:
                sleep_time = self.min_interval - time_since_last
                time.sleep(sleep_time)
            self.last_request_time = time.time()


class SQLiteCache:
    """SQLite-based cache for NCBI API responses."""
    
    def __init__(self, cache_path: str):
        self.cache_path = cache_path
        self.lock = Lock()
        self._init_db()
    
    def _init_db(self):
        with sqlite3.connect(self.cache_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    timestamp REAL,
                    expires_at REAL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_expires ON cache(expires_at)")
    
    def _make_key(self, url: str, params: Dict) -> str:
        """Generate cache key from URL and parameters."""
        sorted_params = sorted(params.items())
        key_string = f"{url}?{urlencode(sorted_params)}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, url: str, params: Dict, ttl: int = 3600) -> Optional[str]:
        """Get cached response if still valid."""
        with self.lock:
            key = self._make_key(url, params)
            now = time.time()
            
            with sqlite3.connect(self.cache_path) as conn:
                result = conn.execute(
                    "SELECT value FROM cache WHERE key = ? AND expires_at > ?",
                    (key, now)
                ).fetchone()
                
                if result:
                    log.debug(f"Cache hit for {key}")
                    return result[0]
                
                log.debug(f"Cache miss for {key}")
                return None
    
    def set(self, url: str, params: Dict, value: str, ttl: int = 3600):
        """Store response in cache."""
        with self.lock:
            key = self._make_key(url, params)
            now = time.time()
            expires_at = now + ttl
            
            with sqlite3.connect(self.cache_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO cache (key, value, timestamp, expires_at) VALUES (?, ?, ?, ?)",
                    (key, value, now, expires_at)
                )
    
    def cleanup_expired(self):
        """Remove expired entries from cache."""
        with self.lock:
            now = time.time()
            with sqlite3.connect(self.cache_path) as conn:
                conn.execute("DELETE FROM cache WHERE expires_at < ?", (now,))


class NCBIClient:
    """Lightweight NCBI E-utilities client."""
    
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    def __init__(self, api_key: Optional[str] = None, cache_path: Optional[str] = None, 
                 requests_per_second: int = 10, tool: str = "metapub", email: str = ""):
        self.api_key = api_key
        self.tool = tool
        self.email = email
        
        # Setup rate limiting
        rps = 10 if api_key else 3  # NCBI limits: 10/sec with key, 3/sec without
        self.rate_limiter = RateLimiter(min(requests_per_second, rps))
        
        # Setup caching
        self.cache = SQLiteCache(cache_path) if cache_path else None
        
        # Setup HTTP session
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': f'{tool}/metapub-ncbi-client'
        })
    
    def _build_params(self, **kwargs) -> Dict[str, str]:
        """Build standard parameters for NCBI requests."""
        params = {}
        
        # Add API key if available
        if self.api_key:
            params['api_key'] = self.api_key
        
        # Add tool and email for NCBI tracking
        if self.tool:
            params['tool'] = self.tool
        if self.email:
            params['email'] = self.email
        
        # Add custom parameters
        for key, value in kwargs.items():
            if value is not None:
                if isinstance(value, (list, tuple)):
                    params[key] = ','.join(str(v) for v in value)
                else:
                    params[key] = str(value)
        
        return params
    
    def _is_valid_xml_response(self, content: str, response: requests.Response) -> bool:
        """Validate that response content is actually XML, not HTML error pages."""
        # Check content type first
        content_type = response.headers.get('content-type', '').lower()
        if 'html' in content_type:
            return False
        
        # Check for obvious HTML markers
        content_lower = content.lower().strip()
        if (content_lower.startswith('<!doctype html') or 
            content_lower.startswith('<html') or
            'down_bethesda' in content_lower):
            return False
        
        # Try to parse as XML
        try:
            etree.fromstring(content.encode('utf-8'))
            return True
        except (etree.XMLSyntaxError, Exception):
            return False
    
    def _make_request(self, endpoint: str, **params) -> str:
        """Make HTTP request to NCBI with caching and rate limiting."""
        url = f"{self.BASE_URL}/{endpoint}.fcgi"
        request_params = self._build_params(**params)
        
        # Check cache first
        if self.cache:
            cached_response = self.cache.get(url, request_params)
            if cached_response:
                return cached_response
        
        # Rate limit
        self.rate_limiter.wait_if_needed()
        
        try:
            log.debug(f"Making request to {endpoint} with params: {request_params}")
            response = self.session.get(url, params=request_params, timeout=30)
            response.raise_for_status()
            
            content = response.text
            
            # Cache successful responses - but only if they contain valid XML
            if self.cache and response.status_code == 200:
                # Validate that response is actually XML before caching
                if self._is_valid_xml_response(content, response):
                    self.cache.set(url, request_params, content)
                else:
                    log.warning(f"Skipping cache for non-XML response from {endpoint}")
            
            return content
            
        except requests.exceptions.RequestException as e:
            diagnosis = diagnose_ncbi_error(e, url)
            if diagnosis['is_service_issue']:
                raise NCBIServiceError(
                    diagnosis['user_message'],
                    diagnosis['error_type'],
                    diagnosis['suggested_actions']
                ) from e
            else:
                raise MetaPubError(f"Request failed: {str(e)}") from e
    
    def efetch(self, db: str, id: Union[str, List[str]], rettype: str = 'xml', 
               retmode: str = 'text', **kwargs) -> str:
        """Fetch full records for given IDs."""
        return self._make_request(
            'efetch',
            db=db,
            id=id,
            rettype=rettype,
            retmode=retmode,
            **kwargs
        )
    
    def esearch(self, db: str, term: str, retmax: int = 20, retstart: int = 0,
                sort: str = None, **kwargs) -> str:
        """Search database and return UIDs."""
        return self._make_request(
            'esearch',
            db=db,
            term=term,
            retmax=retmax,
            retstart=retstart,
            sort=sort,
            **kwargs
        )
    
    def elink(self, dbfrom: str, id: Union[str, List[str]], db: str = None,
              cmd: str = 'neighbor', **kwargs) -> str:
        """Find related records."""
        return self._make_request(
            'elink',
            dbfrom=dbfrom,
            id=id,
            db=db,
            cmd=cmd,
            **kwargs
        )
    
    def esummary(self, db: str, id: Union[str, List[str]], retmode: str = 'xml',
                 **kwargs) -> str:
        """Get document summaries."""
        return self._make_request(
            'esummary',
            db=db,
            id=id,
            retmode=retmode,
            **kwargs
        )
    
    def einfo(self, db: str = None, **kwargs) -> str:
        """Get database information."""
        return self._make_request(
            'einfo',
            db=db,
            **kwargs
        )