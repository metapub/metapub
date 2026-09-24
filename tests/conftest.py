import socket
import requests
import pytest
import sys
from lxml import etree


# ---------------------------------------------------------------------------
# Network guardrail: keep publisher/external HTTP out of the offline (CI) suite.
#
# CI runs `pytest -m "not live_network"`. Any test that reaches a publisher site
# (or any external host other than NCBI eutils) is either a live drift-detector
# that must be marked @pytest.mark.live_network, or an offline test with a
# broken mock. Both are bugs when they run in CI: they flake and they turn a
# drift sensor into a dead one. Per-test marking alone is not enough -- a leak
# only shows up if the publisher happens to be reachable during the run, so a
# scan can miss it. This guard makes leaks fail loudly and deterministically.
#
# Tests explicitly marked live_network are exempt (they are run by hand, never
# in CI). NCBI eutils is allowlisted because the project deliberately allows
# live eutils calls in the offline suite (see CLAUDE.md); localhost is allowed
# for any local-service tests.
# ---------------------------------------------------------------------------

_ALLOWED_HOST_SUBSTRINGS = ('ncbi.nlm.nih.gov',)
_ALLOWED_HOST_EXACT = {'localhost', '127.0.0.1', '::1', '0.0.0.0'}

_real_getaddrinfo = socket.getaddrinfo
_network_guard = {'active': False, 'nodeid': None}


class BlockedNetworkError(Exception):
    """Raised when an offline test tries to reach a non-allowlisted host."""


def _host_is_allowed(host):
    name = str(host)
    if name in _ALLOWED_HOST_EXACT:
        return True
    return any(substr in name for substr in _ALLOWED_HOST_SUBSTRINGS)


def _guarded_getaddrinfo(host, *args, **kwargs):
    if _network_guard['active'] and not _host_is_allowed(host):
        raise BlockedNetworkError(
            "Blocked live network call to %r from offline test %s.\n"
            "Tests that reach publisher/external sites must be marked "
            "@pytest.mark.live_network -- they are run manually for drift "
            "detection and never in CI. If this test is meant to be offline, "
            "fix its mock target so it does not hit the network." % (
                host, _network_guard['nodeid'])
        )
    return _real_getaddrinfo(host, *args, **kwargs)


socket.getaddrinfo = _guarded_getaddrinfo


@pytest.fixture(autouse=True)
def _block_publisher_network(request):
    """Block non-allowlisted network access unless the test is live_network."""
    if request.node.get_closest_marker('live_network'):
        yield
        return
    _network_guard['active'] = True
    _network_guard['nodeid'] = request.node.nodeid
    try:
        yield
    finally:
        _network_guard['active'] = False


def check_ncbi_service():
    """Check if NCBI eutils service is responding with valid XML."""
    try:
        # Test a simple eutils call
        response = requests.get(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
            params={
                "db": "pubmed",
                "id": "123456",  # Known invalid PMID for quick test
                "retmode": "xml"
            },
            timeout=10
        )

        # Check for rate limiting (429 status code)
        if response.status_code == 429:
            return False

        # Check for server errors (5xx status codes)
        if response.status_code >= 500:
            return False

        # Check if we get HTML error page instead of XML
        content_type = response.headers.get('content-type', '').lower()
        if 'html' in content_type:
            return False

        # Check for empty response (which shouldn't happen for valid service)
        if len(response.content) == 0:
            return False

        # Check for JSON error responses (rate limiting)
        if 'json' in content_type or response.content.strip().startswith(b'{'):
            try:
                import json
                error_data = json.loads(response.content)
                if 'error' in error_data and 'rate limit' in error_data.get('error', '').lower():
                    return False
            except (json.JSONDecodeError, AttributeError):
                pass

        # Try to parse as XML
        try:
            etree.XML(response.content)
            return True
        except etree.XMLSyntaxError:
            # Check if we got the "down_bethesda.html" page
            if b'down_bethesda' in response.content or b'<html' in response.content.lower():
                return False
            # Check if response looks like a JSON error
            if response.content.strip().startswith(b'{') and b'error' in response.content:
                return False
            # Other XML errors might be OK (like invalid PMID response)
            return True

    except (requests.RequestException, Exception):
        return False


def print_ncbi_down_warning():
    """Print ASCII art warning that NCBI service is down."""
    warning = """
╔════════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                        ║
║  ███╗   ██╗ ██████╗██████╗ ██╗    ███████╗███████╗██████╗ ██╗   ██╗██╗ ██████╗███████╗ ║
║  ████╗  ██║██╔════╝██╔══██╗██║    ██╔════╝██╔════╝██╔══██╗██║   ██║██║██╔════╝██╔════╝ ║
║  ██╔██╗ ██║██║     ██████╔╝██║    ███████╗█████╗  ██████╔╝██║   ██║██║██║     █████╗   ║
║  ██║╚██╗██║██║     ██╔══██╗██║    ╚════██║██╔══╝  ██╔══██╗╚██╗ ██╔╝██║██║     ██╔══╝   ║
║  ██║ ╚████║╚██████╗██████╔╝██║    ███████║███████╗██║  ██║ ╚████╔╝ ██║╚██████╗███████╗ ║
║  ╚═╝  ╚═══╝ ╚═════╝╚═════╝ ╚═╝    ╚══════╝╚══════╝╚═╝  ╚═╝  ╚═══╝  ╚═╝ ╚═════╝╚══════╝ ║
║                                                                                        ║
║                            ██████╗  ██████╗ ██╗    ██╗███╗   ██╗                       ║
║                            ██╔══██╗██╔═══██╗██║    ██║████╗  ██║                       ║
║                            ██║  ██║██║   ██║██║ █╗ ██║██╔██╗ ██║                       ║
║                            ██║  ██║██║   ██║██║███╗██║██║╚██╗██║                       ║
║                            ██████╔╝╚██████╔╝╚███╔███╔╝██║ ╚████║                       ║
║                            ╚═════╝  ╚═════╝  ╚══╝╚══╝ ╚═╝  ╚═══╝                       ║
║                                                                                        ║
║  WARNING: NCBI eutils service appears to be down or returning HTML errors!             ║
║                                                                                        ║
║  Many tests will fail because they depend on external NCBI API calls.                  ║
║  This is likely temporary - please try again later.                                    ║
║                                                                                        ║
║  Service status: https://www.ncbi.nlm.nih.gov/                                         ║
║                                                                                        ║
╚════════════════════════════════════════════════════════════════════════════════════════╝
"""
    print(warning)


@pytest.fixture(scope="session", autouse=True)
def check_ncbi_before_tests():
    """Check NCBI service health before running any tests."""
    ncbi_available = check_ncbi_service()
    if not ncbi_available:
        # Force output to show regardless of pytest capture settings
        import sys
        import os

        # Write to stderr which pytest doesn't capture by default
        original_stdout = sys.stdout
        sys.stdout = sys.stderr
        print_ncbi_down_warning()
        print("\nSkipping network-dependent tests due to NCBI service issues...\n")
        sys.stdout = original_stdout
        sys.stderr.flush()
    yield

# Global variable to store NCBI service status
_ncbi_service_available = None

def get_ncbi_service_status():
    """Get cached NCBI service status."""
    global _ncbi_service_available
    if _ncbi_service_available is None:
        _ncbi_service_available = check_ncbi_service()
    return _ncbi_service_available

# NOTE: there used to be a `network` marker here, auto-applied to any test whose
# nodeid contained 'findit'/'doi'/'pmid'/'fetch'/etc., plus a coordinate_network_tests
# fixture that slept 0.5s before and 0.1s after every such test to avoid NCBI rate
# limits. That was both wrong and expensive: it marked by filename, so ~600 offline
# tests that make zero network calls (URL construction, registry lookups, this file's
# journal-resolution guard) each paid ~0.6s of pure sleep. It was also redundant --
# get_eutils_client() is an lru_cache(maxsize=1) singleton, so the whole suite shares
# one NCBIClient whose RateLimiter already paces every eutils call to NCBI's limit,
# and the client's Retry adapter absorbs transient 429s. NCBI pacing is the client's
# job; publisher hygiene is the guardrail's (above). The apparatus is gone.
