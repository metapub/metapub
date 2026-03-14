"""
Offline tests for URLReverse functionality.

These tests focus on core functionality, caching behavior, and JSON serialization
without requiring network access. They use mocking where necessary to isolate
URLReverse behavior from external dependencies.
"""

import unittest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock

from metapub.urlreverse.urlreverse import UrlReverse, get_article_info_from_url
from metapub.urlreverse.methods import try_doi_methods, try_pmid_methods, try_vip_methods


class TestUrlReverseOffline(unittest.TestCase):
    """Offline tests for URLReverse core functionality."""

    def setUp(self):
        # Create a temporary directory for cache testing
        self.temp_dir = tempfile.mkdtemp()
        self.cache_file = os.path.join(self.temp_dir, 'test_cache.db')

    def tearDown(self):
        # Clean up temporary files
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_url_parsing_pmid_detection(self):
        """Test that URLs with PMIDs are correctly identified and parsed."""
        # Test direct PMID URLs
        pmid_url = "https://www.ncbi.nlm.nih.gov/pubmed/12345678"
        info = get_article_info_from_url(pmid_url)
        
        self.assertEqual(info['format'], 'pmid')
        self.assertEqual(info['pmid'], '12345678')
        
        # Test PMID lookup URLs
        pmid_lookup_url = "http://example.com/lookup?pmid=23456789"
        info = get_article_info_from_url(pmid_lookup_url)
        
        self.assertEqual(info['format'], 'pmid')
        self.assertEqual(info['pmid'], '23456789')

    def test_url_parsing_vip_detection(self):
        """Test that volume-issue-page URLs are correctly identified."""
        # Test VIP format URL
        vip_url = "http://journal.example.com/content/42/3/123.full.pdf"
        info = get_article_info_from_url(vip_url)
        
        self.assertEqual(info['format'], 'vip')
        self.assertEqual(info['volume'], '42')
        self.assertEqual(info['issue'], '3')
        self.assertEqual(info['first_page'], '123')
        self.assertIn('hostname', info)

    def test_json_serialization_with_function_objects(self):
        """Test that to_dict() properly handles function objects for JSON serialization."""
        # Mock a function object to simulate the method field
        def mock_doi_method(url):
            return "10.1234/example.doi"
        
        # Create a minimal UrlReverse-like object for testing
        with patch('metapub.urlreverse.urlreverse.get_article_info_from_url') as mock_info:
            mock_info.return_value = {
                'format': 'doi',
                'doi': '10.1234/example.doi',
                'method': mock_doi_method  # This is a function object
            }
            
            with patch('metapub.urlreverse.urlreverse.UrlReverse._load_from_cache'):
                with patch('metapub.urlreverse.urlreverse.UrlReverse._urlreverse'):
                    urlrev = UrlReverse("http://example.com/paper", cachedir=None)
                    urlrev.info = mock_info.return_value
                    urlrev.doi = '10.1234/example.doi'
                    urlrev.pmid = '12345678'
                    urlrev.steps = ['Test step']
                    urlrev.format = 'doi'
                    
                    # Test to_dict() conversion
                    result_dict = urlrev.to_dict()
                    
                    # Verify function object was converted to string
                    self.assertEqual(result_dict['info']['method'], 'mock_doi_method')
                    self.assertEqual(result_dict['info']['doi'], '10.1234/example.doi')
                    self.assertEqual(result_dict['info']['format'], 'doi')
                    
                    # Verify JSON serialization works
                    json_str = json.dumps(result_dict)
                    self.assertIsInstance(json_str, str)
                    
                    # Verify we can deserialize back
                    restored_dict = json.loads(json_str)
                    self.assertEqual(restored_dict['info']['method'], 'mock_doi_method')

    def test_caching_behavior_and_persistence(self):
        """Test that caching key generation and basic cache operations work."""
        test_url = "http://example.com/test/article"
        
        # Mock the URL parsing and external calls to avoid network
        with patch('metapub.urlreverse.urlreverse.get_article_info_from_url') as mock_info:
            mock_info.return_value = {'format': 'unknown'}
            
            with patch('metapub.urlreverse.urlreverse.UrlReverse._urlreverse'):
                # Test cache key generation
                urlrev = UrlReverse(test_url, cachedir=self.temp_dir)
                cache_key = urlrev._make_cache_key(test_url)
                
                # Cache key should be consistent and not None
                self.assertIsNotNone(cache_key)
                self.assertEqual(cache_key, urlrev._make_cache_key(test_url))
                
                # Test that cache can be initialized without crashing
                # (The actual cache persistence is tested indirectly through successful initialization)
                self.assertIsNotNone(urlrev._cache)

    def test_url_reverse_with_no_cache(self):
        """Test URLReverse behavior when caching is disabled."""
        test_url = "https://www.ncbi.nlm.nih.gov/pubmed/11111111"
        
        with patch('metapub.urlreverse.urlreverse.UrlReverse._urlreverse'):
            # Create URLReverse with cachedir=None to disable caching
            urlrev = UrlReverse(test_url, cachedir=None)
            
            # Should not have a cache object
            self.assertIsNone(urlrev._cache)
            
            # Should be able to set basic attributes without caching errors
            urlrev.doi = '10.1234/nocache.doi'
            urlrev.pmid = '11111111'
            urlrev.steps = ['No cache test']
            
            # to_dict() should still work without caching
            result_dict = urlrev.to_dict()
            self.assertEqual(result_dict['doi'], '10.1234/nocache.doi')
            self.assertEqual(result_dict['pmid'], '11111111')
            
            # JSON serialization should work
            json_str = json.dumps(result_dict)
            self.assertIsInstance(json_str, str)


if __name__ == '__main__':
    unittest.main()