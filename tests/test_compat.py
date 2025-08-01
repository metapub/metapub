"""
Test compatibility utilities.

Provides compatibility shims for pytest and other testing dependencies
to allow tests to run gracefully even when optional dependencies are missing.
"""

import os
import functools

# Pytest compatibility - provide skipif decorator even when pytest is not available
try:
    import pytest
    skipif = pytest.mark.skipif
    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False
    
    # Define a dummy skipif decorator if pytest is not available
    def skipif(condition, *, reason=""):
        """
        Compatibility skipif decorator that works without pytest.
        
        When pytest is not available, this decorator will skip tests by raising
        unittest.SkipTest if the condition is True.
        
        Usage:
            @skipif(condition, reason="Reason for skipping")
            def test_something(self):
                pass
        """
        def decorator(func):
            if condition:
                @functools.wraps(func)
                def skipped_test(*args, **kwargs):
                    import unittest
                    raise unittest.SkipTest(reason)
                return skipped_test
            return func
        return decorator

# Common test condition helpers
SKIP_NETWORK_TESTS = os.getenv('SKIP_NETWORK_TESTS', 'false').lower() == 'true'

# Commonly used skip decorators
skip_network_tests = skipif(SKIP_NETWORK_TESTS, reason="Network tests disabled")

def skip_if_no_pytest():
    """Skip test if pytest is not available"""
    return skipif(not HAS_PYTEST, reason="pytest not available")

def skip_if_env_var(env_var, reason=None):
    """Skip test if environment variable is set to 'true'"""
    condition = os.getenv(env_var, 'false').lower() == 'true'
    if reason is None:
        reason = f"Test skipped due to {env_var}=true"
    return skipif(condition, reason=reason)

# For backwards compatibility and convenience
def network_test(func):
    """
    Decorator to mark a test as requiring network access.
    Will be skipped if SKIP_NETWORK_TESTS=true.
    """
    return skip_network_tests(func)