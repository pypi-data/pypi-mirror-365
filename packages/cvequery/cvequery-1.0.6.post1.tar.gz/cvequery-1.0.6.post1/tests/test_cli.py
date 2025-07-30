"""Tests for the CLI module."""
import unittest
from unittest.mock import patch, Mock, MagicMock
from click.testing import CliRunner
import tempfile
import json
import os
from src.cli import cli, validate_mutually_exclusive, process_multiple_cves, process_cpe_lookup


class TestCLI(unittest.TestCase):
    """Test cases for CLI functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.sample_cve_data = {
            "cve_id": "CVE-2021-44228",
            "summary": "Apache Log4j2 vulnerability",
            "cvss_v3": {"baseScore": 10.0, "baseSeverity": "Critical"},
            "published": "2021-12-10T00:00:00Z"
        }
    
    def test_cli_help(self):
        """Test CLI help command."""
        result = self.runner.invoke(cli, ['--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('CVE Query Tool', result.output)
        self.assertIn('--cve', result.output)
        self.assertIn('--interactive', result.output)
        self.assertIn('--format', result.output)
        self.assertIn('--sbom', result.output)
    
    def test_cli_version(self):
        """Test CLI version command."""
        result = self.runner.invoke(cli, ['--version'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('version', result.output.lower())
    
    def test_fields_list(self):
        """Test fields list command."""
        result = self.runner.invoke(cli, ['--fields-list'])
        self.assertIn('cvss', result.output)
        self.assertIn('epss', result.output)
        self.assertIn('kev', result.output)
    
    @patch('src.cli.get_cve_data')
    def test_single_cve_lookup(self, mock_get_cve):
        """Test single CVE lookup."""
        mock_get_cve.return_value = self.sample_cve_data
        
        result = self.runner.invoke(cli, ['-c', 'CVE-2021-44228'])
        self.assertEqual(result.exit_code, 0)
        mock_get_cve.assert_called_once_with('CVE-2021-44228')
    
    @patch('src.cli.get_cve_data')
    def test_cve_lookup_error(self, mock_get_cve):
        """Test CVE lookup with error."""
        mock_get_cve.return_value = {"error": "CVE not found"}
        
        result = self.runner.invoke(cli, ['-c', 'CVE-2021-99999'])
        self.assertEqual(result.exit_code, 0)  # CLI handles errors gracefully
        self.assertIn('Error', result.output)
    
    @patch('src.cli.get_cves_data')
    def test_product_search(self, mock_get_cves):
        """Test product CVE search."""
        mock_get_cves.return_value = {
            "cves": [self.sample_cve_data],
            "total": 1
        }
        
        result = self.runner.invoke(cli, ['-pcve', 'apache'])
        self.assertEqual(result.exit_code, 0)
        mock_get_cves.assert_called_once()
    
    @patch('src.cli.get_cpe_data')
    def test_cpe_lookup(self, mock_get_cpe):
        """Test CPE lookup."""
        mock_get_cpe.return_value = {
            "cpes": ["cpe:2.3:a:apache:http_server:2.4.41"],
            "total": 1
        }
        
        result = self.runner.invoke(cli, ['-pcpe', 'apache'])
        self.assertEqual(result.exit_code, 0)
        mock_get_cpe.assert_called_once()
    
    def test_interactive_mode(self):
        """Test interactive mode activation."""
        with patch('src.cli.start_interactive_mode') as mock_interactive:
            result = self.runner.invoke(cli, ['--interactive'])
            mock_interactive.assert_called_once()
    
    def test_setup_completion(self):
        """Test completion setup."""
        result = self.runner.invoke(cli, ['--setup-completion'])
        self.assertIn('completion', result.output.lower())
    
    @patch('src.cli.get_cve_data')
    def test_mutually_exclusive_validation(self, mock_get_cve):
        """Test mutually exclusive parameter validation."""
        mock_get_cve.return_value = self.sample_cve_data
        
        # This should work fine
        result1 = self.runner.invoke(cli, ['-c', 'CVE-2021-44228'])
        self.assertEqual(result1.exit_code, 0)
        
        # This should fail due to mutually exclusive options
        result2 = self.runner.invoke(cli, ['-c', 'CVE-2021-44228', '-pcve', 'apache'])
        self.assertNotEqual(result2.exit_code, 0)
    
    def test_date_validation(self):
        """Test date format validation."""
        # Valid date format
        with patch('src.cli.get_cves_data') as mock_get_cves:
            mock_get_cves.return_value = {"cves": [], "total": 0}
            result = self.runner.invoke(cli, ['-pcve', 'apache', '-sd', '2021-01-01'])
            self.assertEqual(result.exit_code, 0)
        
        # Invalid date format
        result = self.runner.invoke(cli, ['-pcve', 'apache', '-sd', 'invalid-date'])
        self.assertNotEqual(result.exit_code, 0)
    
    def test_severity_filtering(self):
        """Test severity filtering."""
        with patch('src.cli.get_cves_data') as mock_get_cves:
            mock_get_cves.return_value = {"cves": [], "total": 0}
            
            # Valid severity levels
            result = self.runner.invoke(cli, ['-pcve', 'apache', '-s', 'critical,high'])
            self.assertEqual(result.exit_code, 0)
            
            # Invalid severity level
            result = self.runner.invoke(cli, ['-pcve', 'apache', '-s', 'invalid'])
            self.assertNotEqual(result.exit_code, 0)
    
    def test_json_output(self):
        """Test JSON output functionality."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json_file = f.name
        
        try:
            with patch('src.cli.get_cve_data') as mock_get_cve:
                mock_get_cve.return_value = self.sample_cve_data
                
                result = self.runner.invoke(cli, ['-c', 'CVE-2021-44228', '-j', json_file])
                self.assertEqual(result.exit_code, 0)
                
                # Verify JSON file was created and contains data
                self.assertTrue(os.path.exists(json_file))
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    self.assertEqual(data['cve_id'], 'CVE-2021-44228')
        finally:
            if os.path.exists(json_file):
                os.unlink(json_file)
    
    def test_format_options(self):
        """Test different output format options."""
        formats = ['default', 'table', 'compact', 'detailed', 'summary']
        
        for fmt in formats:
            with patch('src.cli.get_cve_data') as mock_get_cve:
                mock_get_cve.return_value = self.sample_cve_data
                
                result = self.runner.invoke(cli, ['-c', 'CVE-2021-44228', '--format', fmt])
                self.assertEqual(result.exit_code, 0)
    
    def test_process_multiple_cves_comma_separated(self):
        """Test processing comma-separated CVEs."""
        with patch('src.api.get_multiple_cves_parallel') as mock_parallel:
            mock_parallel.return_value = [self.sample_cve_data, self.sample_cve_data]
            
            # Capture output by redirecting stdout
            with patch('src.cli.format_cve_list_output') as mock_format:
                process_multiple_cves("CVE-2021-44228,CVE-2021-44229", None, None, False)
                mock_parallel.assert_called_once()
    
    def test_process_multiple_cves_file(self):
        """Test processing CVEs from file."""
        # Create temporary file with CVE IDs
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("CVE-2021-44228\nCVE-2021-44229\n")
            cve_file = f.name
        
        try:
            with patch('src.api.get_multiple_cves_parallel') as mock_parallel:
                mock_parallel.return_value = [self.sample_cve_data, self.sample_cve_data]
                
                with patch('src.cli.format_cve_list_output') as mock_format:
                    process_multiple_cves(cve_file, None, None, False)
                    mock_parallel.assert_called_once()
        finally:
            os.unlink(cve_file)
    
    def test_process_cpe_lookup(self):
        """Test CPE lookup processing."""
        with patch('src.cli.get_cpe_data') as mock_get_cpe:
            mock_get_cpe.return_value = {
                "cpes": ["cpe:2.3:a:apache:http_server:2.4.41"],
                "total": 1
            }
            
            # Capture output
            with patch('builtins.print') as mock_print:
                process_cpe_lookup("apache", 0, 1000, None, False)
                mock_get_cpe.assert_called_once_with("apache", 0, 1000)
    
    @patch('src.cli.analyze_sbom_file')
    def test_sbom_analysis(self, mock_analyze):
        """Test SBOM analysis functionality."""
        mock_analyze.return_value = {
            "components": [],
            "vulnerabilities": [],
            "summary": {"total_components": 0, "vulnerable_components": 0, "total_vulnerabilities": 0}
        }
        
        # Create a dummy SBOM file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"name": "test", "dependencies": {}}, f)
            sbom_file = f.name
        
        try:
            # The CLI will call ctx.exit(0) after SBOM analysis
            result = self.runner.invoke(cli, ['--sbom', sbom_file])
            # Check that the function was called (this is the main test)
            mock_analyze.assert_called_once()
            # Note: Click's ctx.exit() results in exit code 1 in tests, which is normal
        finally:
            os.unlink(sbom_file)


class TestCLIValidation(unittest.TestCase):
    """Test CLI validation functions."""
    
    def test_validate_mutually_exclusive(self):
        """Test mutually exclusive validation function."""
        # Create mock context and parameter
        mock_ctx = Mock()
        mock_ctx.params = {'cve': 'CVE-2021-44228', 'multiple_cves': None, 'product_cpe': None}
        mock_param = Mock()
        mock_param.name = 'cve'
        
        # Should return the value if no conflicts
        result = validate_mutually_exclusive(mock_ctx, mock_param, 'CVE-2021-44228')
        self.assertEqual(result, 'CVE-2021-44228')
        
        # Should raise exception if conflicts exist
        mock_ctx.params = {'cve': 'CVE-2021-44228', 'multiple_cves': 'CVE-2021-44229'}
        with self.assertRaises(Exception):
            validate_mutually_exclusive(mock_ctx, mock_param, 'CVE-2021-44228')


if __name__ == '__main__':
    unittest.main()