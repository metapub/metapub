"""
NCBI Service Error Detection and User-Friendly Error Messages

This module provides intelligent error detection for NCBI service outages
and converts cryptic network/XML errors into clear, actionable user messages.
"""

import re
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass

import requests
from lxml import etree


@dataclass
class ServiceStatus:
    """Status information for NCBI services."""
    is_available: bool
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    response_time: Optional[float] = None
    status_code: Optional[int] = None


class NCBIErrorDetector:
    """Detects and categorizes NCBI service errors."""

    def __init__(self):
        self._status_cache = {}
        self._last_check = 0
        self._cache_duration = 300  # 5 minutes

    def check_service_status(self, url: str, timeout: int = 10) -> ServiceStatus:
        """Check if NCBI service is available and responding properly."""
        # Use cached result if recent
        cache_key = url
        now = time.time()

        if (cache_key in self._status_cache and
            now - self._last_check < self._cache_duration):
            return self._status_cache[cache_key]

        start_time = time.time()

        try:
            # Test with a simple query
            if 'efetch.fcgi' in url:
                params = {'db': 'pubmed', 'id': '123456', 'retmode': 'xml'}
            elif 'esearch.fcgi' in url:
                params = {'db': 'pubmed', 'term': 'test', 'retmax': '1'}
            else:
                params = {'db': 'pubmed'}

            response = requests.get(url, params=params, timeout=timeout)
            response_time = time.time() - start_time

            # Check for various failure modes
            if response.status_code >= 500:
                status = ServiceStatus(
                    is_available=False,
                    error_type='server_error',
                    error_message=f"NCBI server error: {response.status_code}",
                    response_time=response_time,
                    status_code=response.status_code
                )
            elif response.status_code == 429:
                status = ServiceStatus(
                    is_available=False,
                    error_type='rate_limit',
                    error_message="NCBI rate limit exceeded",
                    response_time=response_time,
                    status_code=response.status_code
                )
            elif 'html' in response.headers.get('content-type', '').lower():
                status = ServiceStatus(
                    is_available=False,
                    error_type='maintenance',
                    error_message="NCBI service in maintenance mode",
                    response_time=response_time,
                    status_code=response.status_code
                )
            elif len(response.content) == 0:
                status = ServiceStatus(
                    is_available=False,
                    error_type='empty_response',
                    error_message="NCBI service returned empty response",
                    response_time=response_time,
                    status_code=response.status_code
                )
            else:
                # Try to parse XML to ensure it's valid
                try:
                    root = etree.XML(response.content)
                    # Check for API errors in the XML
                    error_elem = root.find('.//ERROR')
                    if error_elem is not None:
                        status = ServiceStatus(
                            is_available=False,
                            error_type='api_error',
                            error_message=f"NCBI API error: {error_elem.text}",
                            response_time=response_time,
                            status_code=response.status_code
                        )
                    else:
                        status = ServiceStatus(
                            is_available=True,
                            response_time=response_time,
                            status_code=response.status_code
                        )
                except etree.XMLSyntaxError:
                    # Check for known maintenance pages
                    if b'down_bethesda' in response.content:
                        status = ServiceStatus(
                            is_available=False,
                            error_type='maintenance',
                            error_message="NCBI service temporarily unavailable",
                            response_time=response_time,
                            status_code=response.status_code
                        )
                    else:
                        status = ServiceStatus(
                            is_available=False,
                            error_type='xml_error',
                            error_message="NCBI service returned invalid XML",
                            response_time=response_time,
                            status_code=response.status_code
                        )

        except requests.exceptions.Timeout:
            status = ServiceStatus(
                is_available=False,
                error_type='timeout',
                error_message=f"NCBI service timeout (>{timeout}s)",
                response_time=timeout
            )
        except requests.exceptions.ConnectionError:
            status = ServiceStatus(
                is_available=False,
                error_type='connection_error',
                error_message="Cannot connect to NCBI service",
                response_time=time.time() - start_time
            )
        except Exception as e:
            status = ServiceStatus(
                is_available=False,
                error_type='unknown_error',
                error_message=f"Unexpected error: {str(e)}",
                response_time=time.time() - start_time
            )

        # Cache the result
        self._status_cache[cache_key] = status
        self._last_check = now

        return status

    def diagnose_error(self, exception: Exception, url: str = None) -> Dict[str, Any]:
        """Analyze an exception and provide user-friendly diagnosis."""
        error_info = {
            'is_service_issue': False,
            'user_message': str(exception),
            'suggested_actions': [],
            'error_type': 'unknown'
        }

        exception_str = str(exception).lower()
        exception_type = type(exception).__name__

        # Network-related errors
        if any(keyword in exception_str for keyword in [
            'connection', 'timeout', 'network', 'dns', 'resolve'
        ]):
            error_info.update({
                'is_service_issue': True,
                'error_type': 'network',
                'user_message': 'Unable to connect to NCBI services.',
                'suggested_actions': [
                    'Check your internet connection',
                    'Verify NCBI service status: https://www.ncbi.nlm.nih.gov/',
                    'Try again in a few minutes',
                    'Use ncbi_health_check --quick to diagnose service issues'
                ]
            })

        # XML parsing errors (common when NCBI returns HTML error pages)
        elif any(keyword in exception_str for keyword in [
            'xml', 'syntax', 'parse', 'opening and ending tag mismatch'
        ]):
            # Check if NCBI is actually down
            if url:
                status = self.check_service_status(url)
                if not status.is_available:
                    error_info.update({
                        'is_service_issue': True,
                        'error_type': 'service_outage',
                        'user_message': f'NCBI service is currently unavailable: {status.error_message}',
                        'suggested_actions': [
                            'NCBI services appear to be down or in maintenance',
                            'Check service status: https://www.ncbi.nlm.nih.gov/',
                            'Try again later',
                            'Use ncbi_health_check --quick for detailed status'
                        ]
                    })
                else:
                    error_info.update({
                        'error_type': 'xml_parsing',
                        'user_message': 'Received invalid data from NCBI (XML parsing error).',
                        'suggested_actions': [
                            'This may be a temporary issue with NCBI services',
                            'Try your request again',
                            'If the problem persists, check NCBI service status'
                        ]
                    })

        # HTTP errors
        elif any(keyword in exception_str for keyword in [
            '500', '502', '503', '504', 'internal server error', 'bad gateway'
        ]):
            error_info.update({
                'is_service_issue': True,
                'error_type': 'server_error',
                'user_message': 'NCBI servers are experiencing issues.',
                'suggested_actions': [
                    'NCBI servers are temporarily unavailable',
                    'This is not an issue with your code or data',
                    'Try again in a few minutes',
                    'Check NCBI status: https://www.ncbi.nlm.nih.gov/'
                ]
            })

        # Rate limiting
        elif any(keyword in exception_str for keyword in [
            '429', 'rate limit', 'too many requests'
        ]):
            error_info.update({
                'is_service_issue': True,
                'error_type': 'rate_limit',
                'user_message': 'NCBI rate limit exceeded.',
                'suggested_actions': [
                    'You are making requests too quickly',
                    'Add delays between requests (time.sleep(0.5))',
                    'Consider using an NCBI API key for higher limits',
                    'See: https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/'
                ]
            })

        # Empty response errors
        elif any(keyword in exception_str for keyword in [
            'empty', 'no content', 'document is empty'
        ]):
            error_info.update({
                'is_service_issue': True,
                'error_type': 'empty_response',
                'user_message': 'NCBI service returned no data.',
                'suggested_actions': [
                    'NCBI services may be experiencing issues',
                    'Check if your query parameters are correct',
                    'Try a simpler query to test connectivity',
                    'Use ncbi_health_check --quick to check service status'
                ]
            })

        return error_info


# Global instance for easy access
_detector = NCBIErrorDetector()


def check_ncbi_status(url: str = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi") -> ServiceStatus:
    """Quick function to check NCBI service status."""
    return _detector.check_service_status(url)


def diagnose_ncbi_error(exception: Exception, url: str = None) -> Dict[str, Any]:
    """Quick function to diagnose NCBI-related errors."""
    return _detector.diagnose_error(exception, url)


def format_user_error(exception: Exception, url: str = None) -> str:
    """Format a user-friendly error message with suggestions."""
    diagnosis = diagnose_ncbi_error(exception, url)

    if diagnosis['is_service_issue']:
        message = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                            NCBI SERVICE ISSUE                               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  {diagnosis['user_message']:<76} ║
║                                                                              ║
║  Suggested actions:                                                          ║"""

        for action in diagnosis['suggested_actions']:
            message += f"\n║  • {action:<74} ║"

        message += """
║                                                                              ║
║  This is likely a temporary issue with NCBI's servers, not your code.       ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝"""

        return message
    else:
        return f"Error: {diagnosis['user_message']}\n\nSuggested actions:\n" + \
               "\n".join(f"• {action}" for action in diagnosis['suggested_actions'])


class NCBIServiceError(Exception):
    """Custom exception for NCBI service issues."""

    def __init__(self, message: str, error_type: str = 'unknown', suggestions: list = None):
        super().__init__(message)
        self.error_type = error_type
        self.suggestions = suggestions or []
        self.user_message = message
        self._formatted_message = self._format_message()

    def _format_message(self):
        """Format a user-friendly error message with suggestions."""
        message = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                            NCBI SERVICE ISSUE                                ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  {self.user_message:<76}║
║                                                                              ║
║  Suggested actions:                                                          ║"""

        for action in self.suggestions:
            message += f"\n║ • {action:<74} ║"

        message += """
║                                                                              ║
║  This is likely a temporary issue with NCBI's servers, not your code.        ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝"""

        return message

    def __str__(self):
        return self._formatted_message


def handle_ncbi_request_error(func):
    """Decorator to wrap NCBI API calls with intelligent error handling."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Try to extract URL from function arguments for better diagnosis
            url = None
            if args and hasattr(args[0], 'url'):
                url = args[0].url
            elif 'url' in kwargs:
                url = kwargs['url']

            diagnosis = diagnose_ncbi_error(e, url)

            if diagnosis['is_service_issue']:
                raise NCBIServiceError(
                    diagnosis['user_message'],
                    diagnosis['error_type'],
                    diagnosis['suggested_actions']
                ) from e
            else:
                # Re-raise original exception if it's not a service issue
                raise

    return wrapper
