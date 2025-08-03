"""Common utilities for FindIt dance tests."""

import unittest
import logging
from metapub import FindIt

# Set up logging for all dance tests
log = logging.getLogger()
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
log.addHandler(ch)


class BaseDanceTest(unittest.TestCase):
    """Base class for all FindIt dance tests."""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def assertUrlOrReason(self, source):
        """Assert that FindIt source has either a URL or a reason."""
        assert source.url is not None or source.reason is not None

    def assertNoFormatError(self, source):
        """Assert that source doesn't have NOFORMAT error."""
        if source.reason:
            assert 'NOFORMAT' not in source.reason