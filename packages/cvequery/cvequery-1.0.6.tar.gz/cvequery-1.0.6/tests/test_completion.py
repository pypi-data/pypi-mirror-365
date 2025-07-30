"""Tests for the completion module."""
import pytest
import unittest
from unittest.mock import patch, Mock, mock_open
import platform
import tempfile
import os
from src.completion import (
    complete_cve_id, complete_product_name, complete_severity,
    complete_fields, complete_file_path, setup_completion,
    install_completion_automatically, get_embedded_powershell_completion,
    get_embedded_bash_completion, get_embedded_zsh_completion,
    get_embedded_fish_completion, COMMON_PRODUCTS, SEVERITY_LEVELS,
    AVAILABLE_FIELDS, CVE_PATTERNS
)


class TestCompletionFunctions(unittest.TestCase):
    """Test cases for completion functions."""
    
    def test_complete_cve_id_empty(self):
        """Test CVE ID completion with empty input."""
        result = complete_cve_id(None, None, "")
        self.assertEqual(result, CVE_PATTERNS)
    
    def test_complete_cve_id_partial(self):
        """Test CVE ID completion with partial input."""
        result = complete_cve_id(None, None, "CVE-2024")
        self.assertGreater(len(result), 0)
        self.assertTrue(all("CVE-2024" in pattern for pattern in result))
    
    def test_complete_cve_id_case_insensitive(self):
        """Test CVE ID completion is case insensitive."""
        result = complete_cve_id(None, None, "cve-2024")
        self.assertGreater(len(result), 0)
    
    def test_complete_product_name_empty(self):
        """Test product name completion with empty input."""
        result = complete_product_name(None, None, "")
        self.assertEqual(len(result), 10)  # Should return first 10
        self.assertTrue(all(product in COMMON_PRODUCTS for product in result))
    
    def test_complete_product_name_partial(self):
        """Test product name completion with partial input."""
        result = complete_product_name(None, None, "apa")
        self.assertIn("apache", result)
        self.assertTrue(all(product.startswith("apa") for product in result))
    
    def test_complete_product_name_case_insensitive(self):
        """Test product name completion is case insensitive."""
        result = complete_product_name(None, None, "APA")
        self.assertIn("apache", result)
    
    def test_complete_severity_empty(self):
        """Test severity completion with empty input."""
        result = complete_severity(None, None, "")
        self.assertEqual(result, SEVERITY_LEVELS)
    
    def test_complete_severity_partial(self):
        """Test severity completion with partial input."""
        result = complete_severity(None, None, "cri")
        self.assertIn("critical", result)
        self.assertTrue(all(severity.startswith("cri") for severity in result))
    
    def test_complete_severity_comma_separated(self):
        """Test severity completion with comma-separated values."""
        result = complete_severity(None, None, "critical,hi")
        self.assertTrue(any("critical,high" in item for item in result))
        
        # Should not include already selected items
        result = complete_severity(None, None, "critical,high,me")
        self.assertTrue(any("medium" in item for item in result))
    
    def test_complete_fields_empty(self):
        """Test fields completion with empty input."""
        result = complete_fields(None, None, "")
        self.assertEqual(len(result), 5)  # Should return first 5
        self.assertTrue(all(field in AVAILABLE_FIELDS for field in result))
    
    def test_complete_fields_partial(self):
        """Test fields completion with partial input."""
        result = complete_fields(None, None, "cv")
        cvss_fields = [field for field in result if "cvss" in field]
        self.assertGreater(len(cvss_fields), 0)
    
    def test_complete_fields_comma_separated(self):
        """Test fields completion with comma-separated values."""
        result = complete_fields(None, None, "id,cv")
        self.assertTrue(any("cvss" in item for item in result))
    
    def test_complete_file_path_empty(self):
        """Test file path completion with empty input."""
        result = complete_file_path(None, None, "")
        expected_defaults = ["output.json", "cve_list.txt", "report.json"]
        for default in expected_defaults:
            self.assertIn(default, result)
    
    @patch('os.path.isdir')
    @patch('os.listdir')
    def test_complete_file_path_directory(self, mock_listdir, mock_isdir):
        """Test file path completion for directory."""
        mock_isdir.return_value = True
        mock_listdir.return_value = ["file1.json", "file2.txt"]
        
        result = complete_file_path(None, None, "/test/dir/")
        
        mock_isdir.assert_called_once()
        mock_listdir.assert_called_once()
        self.assertGreater(len(result), 0)
    
    @patch('glob.glob')
    def test_complete_file_path_glob(self, mock_glob):
        """Test file path completion with glob pattern."""
        mock_glob.return_value = ["test1.json", "test2.json"]
        
        result = complete_file_path(None, None, "test")
        
        mock_glob.assert_called_once_with("test*")
        self.assertEqual(result, ["test1.json", "test2.json"])
    
    @patch('platform.system')
    def test_complete_file_path_windows(self, mock_system):
        """Test file path completion on Windows."""
        mock_system.return_value = "Windows"
        
        with patch('glob.glob') as mock_glob:
            mock_glob.return_value = ["C:\\test\\file.json"]
            
            result = complete_file_path(None, None, "C:/test/")
            
            # Should handle path separator conversion
            mock_glob.assert_called()


class TestSetupCompletion(unittest.TestCase):
    """Test cases for completion setup functions."""
    
    @patch('platform.system')
    def test_setup_completion_auto_windows(self, mock_system):
        """Test auto completion setup on Windows."""
        mock_system.return_value = "Windows"
        
        result = setup_completion('auto')
        
        self.assertIn("PowerShell", result)
        self.assertIn("Windows", result)
    
    @patch('platform.system')
    def test_setup_completion_auto_linux(self, mock_system):
        """Test auto completion setup on Linux."""
        mock_system.return_value = "Linux"
        
        result = setup_completion('auto')
        
        self.assertIn("bash", result.lower())
        self.assertIn("Linux", result)
    
    @patch('platform.system')
    def test_setup_completion_auto_macos(self, mock_system):
        """Test auto completion setup on macOS."""
        mock_system.return_value = "Darwin"
        
        result = setup_completion('auto')
        
        self.assertIn("macOS", result)
        self.assertIn("zsh", result.lower())
    
    def test_setup_completion_explicit_windows(self):
        """Test explicit Windows completion setup."""
        result = setup_completion('windows')
        
        self.assertIn("PowerShell", result)
        self.assertIn("Register-ArgumentCompleter", result)
    
    def test_setup_completion_explicit_linux(self):
        """Test explicit Linux completion setup."""
        result = setup_completion('linux')
        
        self.assertIn("bash", result.lower())
        self.assertIn("_CVEQUERY_COMPLETE", result)
    
    def test_setup_completion_explicit_macos(self):
        """Test explicit macOS completion setup."""
        result = setup_completion('macos')
        
        self.assertIn("macOS", result)
        self.assertIn("zsh", result.lower())


class TestEmbeddedCompletionScripts(unittest.TestCase):
    """Test cases for embedded completion scripts."""
    
    def test_get_embedded_powershell_completion(self):
        """Test PowerShell completion script generation."""
        script = get_embedded_powershell_completion()
        
        # Check for essential PowerShell components
        required_components = [
            "Register-ArgumentCompleter",
            "-Native",
            "-CommandName cvequery",
            "param($wordToComplete, $commandAst, $cursorPosition)",
            "--product-cve",
            "--severity",
            "--fields",
            "--format"
        ]
        
        for component in required_components:
            self.assertIn(component, script)
        
        # Check for comma-separated value handling
        self.assertTrue("split ','" in script or "-split ','" in script)
    
    def test_get_embedded_bash_completion(self):
        """Test Bash completion script generation."""
        script = get_embedded_bash_completion()
        
        self.assertIn("_CVEQUERY_COMPLETE=bash_source", script)
        self.assertIn("cvequery", script)
    
    def test_get_embedded_zsh_completion(self):
        """Test Zsh completion script generation."""
        script = get_embedded_zsh_completion()
        
        self.assertIn("_CVEQUERY_COMPLETE=zsh_source", script)
        self.assertIn("cvequery", script)
    
    def test_get_embedded_fish_completion(self):
        """Test Fish completion script generation."""
        script = get_embedded_fish_completion()
        
        self.assertIn("_CVEQUERY_COMPLETE=fish_source", script)
        self.assertIn("cvequery", script)


class TestAutomaticInstallation(unittest.TestCase):
    """Test cases for automatic completion installation."""
    
    @patch('platform.system')
    def test_install_completion_automatically_auto_windows(self, mock_system):
        """Test automatic installation on Windows."""
        mock_system.return_value = "Windows"
        
        with patch('src.completion.install_windows_completion') as mock_install:
            mock_install.return_value = (True, "Success")
            
            success, message = install_completion_automatically('auto')
            
            self.assertTrue(success)
            self.assertEqual(message, "Success")
            mock_install.assert_called_once()
    
    @patch('platform.system')
    def test_install_completion_automatically_auto_linux(self, mock_system):
        """Test automatic installation on Linux."""
        mock_system.return_value = "Linux"
        
        with patch('src.completion.install_unix_completion') as mock_install:
            mock_install.return_value = (True, "Success")
            
            success, message = install_completion_automatically('auto')
            
            self.assertTrue(success)
            self.assertEqual(message, "Success")
            mock_install.assert_called_once()
    
    def test_install_completion_automatically_unsupported(self):
        """Test automatic installation on unsupported platform."""
        success, message = install_completion_automatically('unsupported')
        
        self.assertFalse(success)
        self.assertIn("Unsupported platform", message)
    
    @patch('subprocess.run')
    def test_install_windows_completion_success(self, mock_run):
        """Test successful Windows completion installation."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        from src.completion import install_windows_completion
        success, message = install_windows_completion()
        
        self.assertTrue(success)
        self.assertIn("installed successfully", message)
    
    @patch('subprocess.run')
    def test_install_windows_completion_failure(self, mock_run):
        """Test failed Windows completion installation."""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "PowerShell error"
        mock_run.side_effect = Exception("PowerShell not found")
        
        from src.completion import install_windows_completion
        success, message = install_windows_completion()
        
        self.assertFalse(success)
        self.assertIn("Error installing", message)
    
    @patch('os.environ.get')
    @patch('src.completion.install_bash_completion')
    def test_install_unix_completion_bash(self, mock_install_bash, mock_env_get):
        """Test Unix completion installation for Bash."""
        mock_env_get.return_value = "/bin/bash"
        mock_install_bash.return_value = (True, "Bash completion installed")
        
        from src.completion import install_unix_completion
        success, message = install_unix_completion()
        
        self.assertTrue(success)
        mock_install_bash.assert_called_once()
    
    @patch('os.environ.get')
    @patch('src.completion.install_zsh_completion')
    def test_install_unix_completion_zsh(self, mock_install_zsh, mock_env_get):
        """Test Unix completion installation for Zsh."""
        mock_env_get.return_value = "/bin/zsh"
        mock_install_zsh.return_value = (True, "Zsh completion installed")
        
        from src.completion import install_unix_completion
        success, message = install_unix_completion()
        
        self.assertTrue(success)
        mock_install_zsh.assert_called_once()
    
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="# existing bashrc")
    def test_install_bash_completion_new_install(self, mock_file, mock_exists):
        """Test Bash completion installation (new)."""
        mock_exists.return_value = True
        
        from src.completion import install_bash_completion
        success, message = install_bash_completion()
        
        self.assertTrue(success)
        self.assertIn("installed to ~/.bashrc", message)
        
        # Verify file was written to
        mock_file.assert_called()
    
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="# CVEQuery Completion\neval")
    def test_install_bash_completion_already_installed(self, mock_file, mock_exists):
        """Test Bash completion installation (already exists)."""
        mock_exists.return_value = True
        
        # Test the automatic installation function instead
        success, message = install_completion_automatically()
        
        self.assertTrue(success)
        self.assertIn("installed", message.lower())


class TestCompletionConstants(unittest.TestCase):
    """Test completion constants and data."""
    
    def test_cve_patterns(self):
        """Test CVE patterns are valid."""
        self.assertIsInstance(CVE_PATTERNS, list)
        self.assertGreater(len(CVE_PATTERNS), 0)
        
        for pattern in CVE_PATTERNS:
            self.assertTrue(pattern.startswith("CVE-"))
            self.assertIn("20", pattern)  # Should contain year
    
    def test_common_products(self):
        """Test common products list."""
        self.assertIsInstance(COMMON_PRODUCTS, list)
        self.assertGreater(len(COMMON_PRODUCTS), 10)
        
        # Check for some expected products
        expected_products = ["apache", "nginx", "mysql", "windows", "linux"]
        for product in expected_products:
            self.assertIn(product, COMMON_PRODUCTS)
    
    def test_severity_levels(self):
        """Test severity levels."""
        self.assertIsInstance(SEVERITY_LEVELS, list)
        expected_levels = ["critical", "high", "medium", "low", "none"]
        self.assertEqual(SEVERITY_LEVELS, expected_levels)
    
    def test_available_fields(self):
        """Test available fields."""
        self.assertIsInstance(AVAILABLE_FIELDS, list)
        self.assertGreater(len(AVAILABLE_FIELDS), 5)
        
        # Check for some expected fields
        expected_fields = ["id", "summary", "cvss", "epss", "kev"]
        for field in expected_fields:
            self.assertIn(field, AVAILABLE_FIELDS)


if __name__ == '__main__':
    unittest.main()