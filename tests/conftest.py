import requests
import pytest
import sys
from lxml import etree


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

# Pytest marker for network-dependent tests
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "network: mark test as requiring network/NCBI connectivity"
    )

def pytest_collection_modifyitems(config, items):
    """Skip network tests if NCBI service is down."""
    import os

    # Allow forcing network tests with environment variable
    force_network_tests = os.environ.get('FORCE_NETWORK_TESTS', '').lower() in ('1', 'true', 'yes')

    if not get_ncbi_service_status() and not force_network_tests:
        skip_network = pytest.mark.skip(reason="NCBI service unavailable - use FORCE_NETWORK_TESTS=1 to run anyway")
        skipped_count = 0
        for item in items:
            # Skip tests that contain network-related keywords
            # Note: ncbi_health_check tests are excluded because they use mocked responses
            if any(keyword in item.nodeid.lower() for keyword in [
                'pmid', 'doi', 'fetch', 'pubmed', 'medgen', 'citation',
                'advquery', 'findit', 'convert', 'mesh_heading', 'random_efetch'
            ]) and 'ncbi_health_check' not in item.nodeid.lower():
                item.add_marker(skip_network)
                skipped_count += 1

        if skipped_count > 0:
            print(f"\n🚫 Skipping {skipped_count} network-dependent tests due to NCBI service issues.")
            print("   Use FORCE_NETWORK_TESTS=1 to run them anyway (they will likely fail).\n")
