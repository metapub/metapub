import unittest
import json
import sys
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

# Ensure no real network calls are made in tests
import pytest

from metapub.ncbi_health_check import NCBIHealthChecker, ServiceResult, main, print_results


class TestNCBIHealthChecker(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures with mocked NCBI client."""
        with patch('metapub.ncbi_health_check.get_eutils_client') as mock_get_client:
            self.mock_eutils_client = Mock()
            mock_get_client.return_value = self.mock_eutils_client
            self.checker = NCBIHealthChecker()

    def test_service_configuration(self):
        """Test that services are configured correctly."""
        # Should have 7 services total
        self.assertEqual(len(self.checker.services), 7)
        
        # Check essential services for quick mode
        essential_services = [k for k, v in self.checker.services.items() if v['essential']]
        self.assertEqual(len(essential_services), 5)
        self.assertIn('efetch', essential_services)
        self.assertIn('esearch', essential_services)
        self.assertIn('elink', essential_services)
        self.assertIn('esummary', essential_services)
        self.assertIn('einfo', essential_services)
        
        # Check non-essential services
        non_essential = [k for k, v in self.checker.services.items() if not v['essential']]
        self.assertEqual(len(non_essential), 2)
        self.assertIn('ncbi_main', non_essential)
        self.assertIn('medgen_search', non_essential)

    @patch('requests.get')
    def test_check_service_http_success(self, mock_get):
        """Test HTTP service check with successful response."""
        # Mock successful HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.reason = 'OK'
        mock_get.return_value = mock_response
        
        config = {
            'name': 'NCBI Main Website',
            'method': 'http',
            'url': 'https://www.ncbi.nlm.nih.gov/'
        }
        
        result = self.checker.check_service('ncbi_main', config)
        
        self.assertEqual(result.name, 'NCBI Main Website')
        self.assertEqual(result.status, 'up')
        self.assertEqual(result.status_code, 200)
        self.assertIsNone(result.error_message)
        self.assertIn('Response time:', result.details)

    @patch('requests.get')
    def test_check_service_http_server_error(self, mock_get):
        """Test HTTP service check with server error."""
        mock_response = Mock()
        mock_response.status_code = 503
        mock_response.reason = 'Service Unavailable'
        mock_get.return_value = mock_response
        
        config = {
            'name': 'NCBI Main Website',
            'method': 'http',
            'url': 'https://www.ncbi.nlm.nih.gov/'
        }
        
        result = self.checker.check_service('ncbi_main', config)
        
        self.assertEqual(result.status, 'down')
        self.assertEqual(result.status_code, 503)
        self.assertIn('Server error: 503', result.error_message)

    @patch('requests.get')
    def test_check_service_http_client_error(self, mock_get):
        """Test HTTP service check with client error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.reason = 'Not Found'
        mock_get.return_value = mock_response
        
        config = {
            'name': 'NCBI Main Website',
            'method': 'http',
            'url': 'https://www.ncbi.nlm.nih.gov/'
        }
        
        result = self.checker.check_service('ncbi_main', config)
        
        self.assertEqual(result.status, 'error')
        self.assertEqual(result.status_code, 404)
        self.assertIn('Client error: 404', result.error_message)

    def test_check_service_eutils_success(self):
        """Test eutils service check with successful response."""
        # Mock successful XML response
        mock_xml = b'<?xml version="1.0"?><eSearchResult><Count>1</Count></eSearchResult>'
        self.mock_eutils_client.esearch.return_value = mock_xml
        
        config = {
            'name': 'ESearch (PubMed Search)',
            'method': 'eutils',
            'eutils_method': 'esearch',
            'params': {'db': 'pubmed', 'term': 'cancer[title]', 'retmax': '1'}
        }
        
        result = self.checker.check_service('esearch', config)
        
        self.assertEqual(result.name, 'ESearch (PubMed Search)')
        self.assertEqual(result.status, 'up')
        self.assertEqual(result.status_code, 200)
        self.assertIsNone(result.error_message)
        self.assertIn('Response time:', result.details)

    def test_check_service_eutils_api_error(self):
        """Test eutils service check with API error in XML."""
        # Mock XML response with error
        mock_xml = b'<?xml version="1.0"?><eSearchResult><ERROR>API rate limit exceeded</ERROR></eSearchResult>'
        self.mock_eutils_client.esearch.return_value = mock_xml
        
        config = {
            'name': 'ESearch (PubMed Search)',
            'method': 'eutils',
            'eutils_method': 'esearch',
            'params': {'db': 'pubmed', 'term': 'cancer[title]', 'retmax': '1'}
        }
        
        result = self.checker.check_service('esearch', config)
        
        self.assertEqual(result.status, 'error')
        self.assertIn('API error: API rate limit exceeded', result.error_message)

    def test_check_service_eutils_empty_response(self):
        """Test eutils service check with empty response."""
        self.mock_eutils_client.esearch.return_value = b''
        
        config = {
            'name': 'ESearch (PubMed Search)',
            'method': 'eutils',
            'eutils_method': 'esearch',
            'params': {'db': 'pubmed', 'term': 'cancer[title]', 'retmax': '1'}
        }
        
        result = self.checker.check_service('esearch', config)
        
        self.assertEqual(result.status, 'down')
        self.assertIn('Empty response from eutils', result.error_message)

    def test_check_service_eutils_invalid_xml(self):
        """Test eutils service check with invalid XML."""
        self.mock_eutils_client.esearch.return_value = b'<invalid xml'
        
        config = {
            'name': 'ESearch (PubMed Search)',
            'method': 'eutils',
            'eutils_method': 'esearch',
            'params': {'db': 'pubmed', 'term': 'cancer[title]', 'retmax': '1'}
        }
        
        result = self.checker.check_service('esearch', config)
        
        self.assertEqual(result.status, 'error')
        self.assertIn('Invalid XML response:', result.error_message)

    def test_check_service_eutils_exception(self):
        """Test eutils service check with exception."""
        self.mock_eutils_client.esearch.side_effect = Exception('Connection timeout')
        
        config = {
            'name': 'ESearch (PubMed Search)',
            'method': 'eutils',
            'eutils_method': 'esearch',
            'params': {'db': 'pubmed', 'term': 'cancer[title]', 'retmax': '1'}
        }
        
        result = self.checker.check_service('esearch', config)
        
        self.assertEqual(result.status, 'error')
        self.assertIn('Unexpected error: Connection timeout', result.error_message)

    @patch('metapub.ncbi_health_check.API_KEY', 'test_api_key')
    def test_check_service_with_api_key(self):
        """Test that API key status is shown in details."""
        mock_xml = b'<?xml version="1.0"?><eSearchResult><Count>1</Count></eSearchResult>'
        self.mock_eutils_client.esearch.return_value = mock_xml
        
        config = {
            'name': 'ESearch (PubMed Search)',
            'method': 'eutils',
            'eutils_method': 'esearch',
            'params': {'db': 'pubmed', 'term': 'cancer[title]', 'retmax': '1'}
        }
        
        result = self.checker.check_service('esearch', config)
        
        self.assertIn('(with API key)', result.details)

    @patch('metapub.ncbi_health_check.API_KEY', None)
    def test_check_service_without_api_key(self):
        """Test that no API key status is shown in details."""
        mock_xml = b'<?xml version="1.0"?><eSearchResult><Count>1</Count></eSearchResult>'
        self.mock_eutils_client.esearch.return_value = mock_xml
        
        config = {
            'name': 'ESearch (PubMed Search)',
            'method': 'eutils',
            'eutils_method': 'esearch',
            'params': {'db': 'pubmed', 'term': 'cancer[title]', 'retmax': '1'}
        }
        
        result = self.checker.check_service('esearch', config)
        
        self.assertIn('(no API key)', result.details)

    def test_check_service_slow_response(self):
        """Test that slow responses are marked as 'slow'."""
        # Mock slow response
        mock_xml = b'<?xml version="1.0"?><eSearchResult><Count>1</Count></eSearchResult>'
        self.mock_eutils_client.esearch.return_value = mock_xml
        
        config = {
            'name': 'ESearch (PubMed Search)',
            'method': 'eutils',
            'eutils_method': 'esearch',
            'params': {'db': 'pubmed', 'term': 'cancer[title]', 'retmax': '1'}
        }
        
        # Patch time.time to simulate slow response
        with patch('time.time', side_effect=[0, 6.0]):  # 6 second response
            result = self.checker.check_service('esearch', config)
        
        self.assertEqual(result.status, 'slow')
        self.assertEqual(result.response_time, 6.0)

    @patch('requests.get')
    def test_check_all_services_quick_mode(self, mock_get):
        """Test checking services in quick mode."""
        # Mock HTTP response for NCBI main (not essential, so not included in quick)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Mock eutils responses
        mock_xml = b'<?xml version="1.0"?><eSearchResult><Count>1</Count></eSearchResult>'
        self.mock_eutils_client.efetch.return_value = mock_xml
        self.mock_eutils_client.esearch.return_value = mock_xml
        self.mock_eutils_client.elink.return_value = mock_xml
        self.mock_eutils_client.esummary.return_value = mock_xml
        self.mock_eutils_client.einfo.return_value = mock_xml
        
        results = self.checker.check_all_services(quick=True)
        
        # Should only check essential services (5 total)
        self.assertEqual(len(results), 5)
        service_names = [r.name for r in results]
        self.assertIn('EFetch (PubMed Articles)', service_names)
        self.assertIn('ESearch (PubMed Search)', service_names)
        self.assertIn('ELink (Related Articles)', service_names)
        self.assertIn('ESummary (Article Summaries)', service_names)
        self.assertIn('EInfo (Database Info)', service_names)
        
        # Should not include non-essential services
        self.assertNotIn('NCBI Main Website', service_names)
        self.assertNotIn('MedGen Search', service_names)

    @patch('requests.get')
    def test_check_all_services_full_mode(self, mock_get):
        """Test checking all services in full mode."""
        # Mock HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Mock eutils responses
        mock_xml = b'<?xml version="1.0"?><eSearchResult><Count>1</Count></eSearchResult>'
        self.mock_eutils_client.efetch.return_value = mock_xml
        self.mock_eutils_client.esearch.return_value = mock_xml
        self.mock_eutils_client.elink.return_value = mock_xml
        self.mock_eutils_client.esummary.return_value = mock_xml
        self.mock_eutils_client.einfo.return_value = mock_xml
        
        results = self.checker.check_all_services(quick=False)
        
        # Should check all services (7 total)
        self.assertEqual(len(results), 7)
        service_names = [r.name for r in results]
        self.assertIn('NCBI Main Website', service_names)
        self.assertIn('MedGen Search', service_names)

    @patch('requests.get')
    def test_service_ordering(self, mock_get):
        """Test that services are ordered with NCBI Main Website first."""
        # Mock HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Mock eutils responses
        mock_xml = b'<?xml version="1.0"?><eSearchResult><Count>1</Count></eSearchResult>'
        self.mock_eutils_client.efetch.return_value = mock_xml
        self.mock_eutils_client.esearch.return_value = mock_xml
        self.mock_eutils_client.elink.return_value = mock_xml
        self.mock_eutils_client.esummary.return_value = mock_xml
        self.mock_eutils_client.einfo.return_value = mock_xml
        
        ordered_results = self.checker.check_all_services(quick=False)
        
        # NCBI Main Website should be first
        self.assertEqual(ordered_results[0].name, 'NCBI Main Website')


class TestHealthCheckOutput(unittest.TestCase):
    """Test output formatting and CLI functionality."""

    def test_print_results_all_up(self):
        """Test print_results with all services up."""
        results = [
            ServiceResult('ESearch (PubMed Search)', 'eutils:esearch', 'up', 0.5, 200, details='Response time: 0.50s'),
            ServiceResult('EFetch (PubMed Articles)', 'eutils:efetch', 'up', 0.3, 200, details='Response time: 0.30s'),
        ]
        
        # Capture stdout
        captured_output = StringIO()
        with patch('sys.stdout', captured_output):
            print_results(results)
        
        output = captured_output.getvalue()
        
        # Check for expected content
        self.assertIn('NCBI SERVICE HEALTH CHECK REPORT', output)
        self.assertIn('📊 SUMMARY: 2 services checked', output)
        self.assertIn('✅ UP: 2', output)
        self.assertIn('✅ ALL GOOD: All services are responding normally.', output)
        self.assertIn('ESearch (PubMed Search)', output)
        self.assertIn('EFetch (PubMed Articles)', output)

    def test_print_results_with_errors(self):
        """Test print_results with some services down."""
        results = [
            ServiceResult('ESearch (PubMed Search)', 'eutils:esearch', 'up', 0.5, 200, details='Response time: 0.50s'),
            ServiceResult('EFetch (PubMed Articles)', 'eutils:efetch', 'down', 10.0, None, error_message='Timeout after 10s'),
        ]
        
        captured_output = StringIO()
        with patch('sys.stdout', captured_output):
            print_results(results)
        
        output = captured_output.getvalue()
        
        self.assertIn('📊 SUMMARY: 2 services checked', output)
        self.assertIn('✅ UP: 1', output)
        self.assertIn('❌ DOWN: 1', output)
        self.assertIn('🚨 CRITICAL: Core PubMed services are down', output)
        self.assertIn('Timeout after 10s', output)

    def test_print_results_slow_services(self):
        """Test print_results with slow services."""
        results = [
            ServiceResult('ESearch (PubMed Search)', 'eutils:esearch', 'slow', 6.0, 200, details='Response time: 6.00s'),
        ]
        
        captured_output = StringIO()
        with patch('sys.stdout', captured_output):
            print_results(results)
        
        output = captured_output.getvalue()
        
        self.assertIn('🐌 SLOW: 1', output)
        self.assertIn('🐌 NOTICE: Some services are responding slowly', output)

    @patch('sys.argv', ['ncbi_health_check', '--json'])
    @patch('metapub.ncbi_health_check.get_eutils_client')
    @patch('requests.get')
    def test_main_json_output(self, mock_get, mock_get_client):
        """Test main function with JSON output."""
        # Mock eutils client
        mock_eutils_client = Mock()
        mock_get_client.return_value = mock_eutils_client
        
        # Mock successful responses
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        mock_xml = b'<?xml version="1.0"?><eSearchResult><Count>1</Count></eSearchResult>'
        mock_eutils_client.efetch.return_value = mock_xml
        mock_eutils_client.esearch.return_value = mock_xml
        mock_eutils_client.elink.return_value = mock_xml
        mock_eutils_client.esummary.return_value = mock_xml
        mock_eutils_client.einfo.return_value = mock_xml
        
        captured_output = StringIO()
        with patch('sys.stdout', captured_output):
            with patch('sys.exit') as mock_exit:
                main()
        
        output = captured_output.getvalue()
        
        # Should be valid JSON
        try:
            json_data = json.loads(output)
            self.assertIn('timestamp', json_data)
            self.assertIn('summary', json_data)
            self.assertIn('services', json_data)
            self.assertEqual(json_data['summary']['total'], 7)
        except json.JSONDecodeError:
            self.fail('Output is not valid JSON')
        
        # Should exit with code 0 (all good)
        mock_exit.assert_called_with(0)

    @patch('sys.argv', ['ncbi_health_check', '--quick'])
    @patch('metapub.ncbi_health_check.get_eutils_client')
    @patch('requests.get')
    def test_main_quick_mode(self, mock_get, mock_get_client):
        """Test main function in quick mode."""
        # Mock eutils client
        mock_eutils_client = Mock()
        mock_get_client.return_value = mock_eutils_client
        
        # Mock responses with one service down
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        mock_xml = b'<?xml version="1.0"?><eSearchResult><Count>1</Count></eSearchResult>'
        mock_eutils_client.efetch.side_effect = Exception('Service down')
        mock_eutils_client.esearch.return_value = mock_xml
        mock_eutils_client.elink.return_value = mock_xml
        mock_eutils_client.esummary.return_value = mock_xml
        mock_eutils_client.einfo.return_value = mock_xml
        
        captured_output = StringIO()
        with patch('sys.stdout', captured_output):
            with patch('sys.exit') as mock_exit:
                main()
        
        output = captured_output.getvalue()
        
        # Should show quick mode
        self.assertIn('(Quick mode: essential services only)', output)
        self.assertIn('📊 SUMMARY: 5 services checked', output)
        
        # Should exit with code 1 (services down)
        mock_exit.assert_called_with(1)

    @patch('sys.argv', ['ncbi_health_check'])
    @patch('metapub.ncbi_health_check.get_eutils_client')
    @patch('requests.get')
    def test_main_slow_services_exit_code(self, mock_get, mock_get_client):
        """Test main function exit code with slow services."""
        # Mock eutils client
        mock_eutils_client = Mock()
        mock_get_client.return_value = mock_eutils_client
        
        # Mock responses
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        mock_xml = b'<?xml version="1.0"?><eSearchResult><Count>1</Count></eSearchResult>'
        mock_eutils_client.efetch.return_value = mock_xml
        mock_eutils_client.esearch.return_value = mock_xml
        mock_eutils_client.elink.return_value = mock_xml
        mock_eutils_client.esummary.return_value = mock_xml
        mock_eutils_client.einfo.return_value = mock_xml
        
        # Patch time to simulate slow response
        with patch('time.time', side_effect=[0, 6.0, 0, 1.0, 0, 1.0, 0, 1.0, 0, 1.0, 0, 1.0, 0, 1.0]):
            captured_output = StringIO()
            with patch('sys.stdout', captured_output):
                with patch('sys.exit') as mock_exit:
                    main()
        
        # Should exit with code 2 (slow services)
        mock_exit.assert_called_with(2)


if __name__ == '__main__':
    unittest.main()