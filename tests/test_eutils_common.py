import os
import unittest

from metapub.eutils_common import get_eutils_client

CACHE_PATH = "test_cache_eutils_client.sqlite"

class TestGetEutilsClient(unittest.TestCase):

    def tearDown(self) -> None:
        if os.path.exists(CACHE_PATH):
            os.remove(CACHE_PATH)
        return super().tearDown()

    def test_get_eutils_client(self):
        client = get_eutils_client(CACHE_PATH)
        assert client._cache is not None

    def test_get_eutils_client_no_caching(self):
        client = get_eutils_client(None)
        assert client._cache is None
