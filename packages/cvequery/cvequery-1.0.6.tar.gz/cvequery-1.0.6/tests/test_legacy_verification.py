"""Legacy test verification - moved from root directory."""
import unittest
import sys
import os
import tempfile
import json
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestLegacyFunctionality(unittest.TestCase):
    """Tests for legacy functionality that was previously verified."""
    
    def test_completion_functions_with_click(self):
        """Test that completion functions work with Click's completion system."""
        try:
            from src.completion import (
                complete_cve_id, complete_product_name, complete_severity,
                complete_fields, complete_file_path
            )
            import click
            
            # Test CVE completion
            cve_completions = complete_cve_id(None, None, "CVE-2024")
            self.assertIsInstance(cve_completions, list)
            self.assertGreater(len(cve_completions), 0)
            
            # Test product completion
            product_completions = complete_product_name(None, None, "apa")
            self.assertGreater(len(product_completions), 0)
            self.assertTrue(any("apache" in comp for comp in product_completions))
            
            # Test severity completion
            severity_completions = complete_severity(None, None, "cri")
            self.assertGreater(len(severity_completions), 0)
            self.assertTrue(any("critical" in comp for comp in severity_completions))
            
            # Test comma-separated severity completion
            multi_sev = complete_severity(None, None, "critical,hi")
            self.assertGreater(len(multi_sev), 0)
            
            # Test fields completion
            field_completions = complete_fields(None, None, "cv")
            self.assertGreater(len(field_completions), 0)
            self.assertTrue(any("cvss" in comp for comp in field_completions))
            
            # Test file path completion
            file_completions = complete_file_path(None, None, "")
            self.assertGreater(len(file_completions), 0)
            
        except Exception as e:
            self.fail(f"Completion functions test failed: {e}")
    
    def test_api_performance_improvements(self):
        """Test that API performance improvements are working."""
        try:
            from src.api import rate_limiter
            
            # Check that rate limiter is set to faster rate
            self.assertGreaterEqual(rate_limiter.calls_per_second, 10)
            
            # Test rate limiter timing
            start_time = time.time()
            rate_limiter.wait()
            rate_limiter.wait()
            end_time = time.time()
            
            duration = end_time - start_time
            self.assertLess(duration, 1.0)  # Should be faster than 1 second for 2 calls
            
        except Exception as e:
            self.fail(f"API performance test failed: {e}")
    
    def test_sbom_parsing_functionality(self):
        """Test SBOM parsing functionality."""
        try:
            from src.sbom import SimpleSBOMParser
            
            # Create test package.json
            test_package_json = {
                "name": "test-project",
                "version": "1.0.0",
                "dependencies": {
                    "express": "^4.17.1",
                    "lodash": "^4.17.20"
                },
                "devDependencies": {
                    "jest": "^26.6.3"
                }
            }
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='package.json', delete=False) as f:
                json.dump(test_package_json, f)
                temp_file = f.name
            
            try:
                parser = SimpleSBOMParser()
                components = parser.parse_file(temp_file)
                
                self.assertGreaterEqual(len(components), 3)
                self.assertTrue(any(comp['name'] == 'express' for comp in components))
                self.assertTrue(any(comp['name'] == 'lodash' for comp in components))
                
            finally:
                os.unlink(temp_file)
                
        except Exception as e:
            self.fail(f"SBOM parsing test failed: {e}")
    
    def test_requirements_txt_parsing(self):
        """Test requirements.txt parsing."""
        try:
            from src.sbom import SimpleSBOMParser
            
            # Create test requirements.txt
            test_requirements = """
# Test requirements file
requests>=2.25.0
click==8.0.1
colorama~=0.4.4
pytest  # for testing
"""
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='requirements.txt', delete=False) as f:
                f.write(test_requirements)
                temp_file = f.name
            
            try:
                parser = SimpleSBOMParser()
                components = parser.parse_file(temp_file)
                
                self.assertGreaterEqual(len(components), 3)
                self.assertTrue(any(comp['name'] == 'requests' for comp in components))
                self.assertTrue(any(comp['name'] == 'click' for comp in components))
                
            finally:
                os.unlink(temp_file)
                
        except Exception as e:
            self.fail(f"Requirements.txt parsing test failed: {e}")
    
    def test_enhanced_formatting_modes(self):
        """Test enhanced formatting modes."""
        try:
            from src.formatting import OutputFormatter
            
            test_cve = {
                "cve_id": "CVE-2023-1234",
                "summary": "Test vulnerability for formatting",
                "cvss_v3": {"baseScore": 8.5, "baseSeverity": "High"},
                "published": "2023-01-01T00:00:00Z",
                "kev": True,
                "epss": 0.75
            }
            
            test_cves = [test_cve, {
                "cve_id": "CVE-2023-5678",
                "summary": "Another test vulnerability",
                "cvss_v3": {"baseScore": 6.2, "baseSeverity": "Medium"},
                "published": "2023-02-01T00:00:00Z",
                "kev": False,
                "epss": 0.25
            }]
            
            # Test all format types
            formats = ['default', 'table', 'compact', 'detailed', 'summary']
            
            for fmt in formats:
                formatter = OutputFormatter(fmt)
                # These should not raise exceptions
                try:
                    formatter.format_cve_data(test_cve)
                    formatter.format_cve_list(test_cves)
                except Exception as e:
                    self.fail(f"Formatting failed for {fmt}: {e}")
                    
        except Exception as e:
            self.fail(f"Enhanced formatting test failed: {e}")
    
    def test_interactive_mode_components(self):
        """Test interactive mode components."""
        try:
            from src.interactive import InteractiveSession
            
            # Test session creation
            session = InteractiveSession()
            self.assertTrue(hasattr(session, 'session_data'))
            self.assertTrue(hasattr(session, 'results_history'))
            self.assertEqual(len(session.results_history), 0)
            
            # Test that methods exist
            self.assertTrue(hasattr(session, 'show_help'))
            self.assertTrue(hasattr(session, 'welcome'))
            self.assertTrue(hasattr(session, 'guided_search_wizard'))
            
        except Exception as e:
            self.fail(f"Interactive mode test failed: {e}")
    
    def test_cli_integration_with_new_options(self):
        """Test CLI integration with new options."""
        try:
            from src.cli import cli
            from click.testing import CliRunner
            
            runner = CliRunner()
            
            # Test help shows new options
            result = runner.invoke(cli, ['--help'])
            self.assertEqual(result.exit_code, 0)
            
            new_options = ['--interactive', '--format', '--sbom', '--setup-completion']
            for option in new_options:
                self.assertIn(option, result.output)
            
            # Test fields list
            result = runner.invoke(cli, ['--fields-list'])
            self.assertIn('cvss', result.output)
            
            # Test setup completion
            result = runner.invoke(cli, ['--setup-completion'])
            self.assertIn('completion', result.output.lower())
            
        except Exception as e:
            self.fail(f"CLI integration test failed: {e}")


class TestWindowsSpecificFeatures(unittest.TestCase):
    """Test Windows-specific features that were previously implemented."""
    
    def test_powershell_completion_script_embedded(self):
        """Test that PowerShell completion script is embedded."""
        try:
            from src.completion import get_embedded_powershell_completion
            
            ps_script = get_embedded_powershell_completion()
            
            # Check for essential PowerShell completion components
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
                self.assertIn(component, ps_script)
            
            # Check that it handles comma-separated values
            self.assertTrue("split ','" in ps_script or "-split ','" in ps_script)
            
        except Exception as e:
            self.fail(f"PowerShell completion script test failed: {e}")
    
    def test_cross_platform_completion_setup(self):
        """Test cross-platform completion setup."""
        try:
            from src.completion import setup_completion
            
            # Test that all platforms return valid instructions
            platforms = ['windows', 'linux', 'macos', 'auto']
            
            for platform_name in platforms:
                instructions = setup_completion(platform_name)
                self.assertGreater(len(instructions), 50)
                self.assertIn("CVEQuery", instructions)
                
                # Platform-specific checks
                if platform_name == 'windows':
                    self.assertIn("PowerShell", instructions)
                elif platform_name in ['linux', 'macos']:
                    self.assertIn("bash", instructions.lower())
                    
        except Exception as e:
            self.fail(f"Cross-platform completion setup test failed: {e}")


class TestImprovedCompletionSystem(unittest.TestCase):
    """Test improved completion system features."""
    
    def test_platform_detection_and_setup(self):
        """Test platform detection and completion setup."""
        try:
            from src.completion import setup_completion
            
            # Test auto-detection
            auto_instructions = setup_completion('auto')
            self.assertGreater(len(auto_instructions), 100)
            
            # Test explicit platform selection
            windows_instructions = setup_completion('windows')
            self.assertIn("PowerShell", windows_instructions)
            self.assertIn("Register-ArgumentCompleter", windows_instructions)
            
            linux_instructions = setup_completion('linux')
            self.assertIn("bash", linux_instructions.lower())
            self.assertIn("_CVEQUERY_COMPLETE", linux_instructions)
            
            macos_instructions = setup_completion('macos')
            self.assertIn("zsh", macos_instructions.lower())
            self.assertIn("macOS", macos_instructions)
            
        except Exception as e:
            self.fail(f"Platform detection test failed: {e}")
    
    def test_embedded_completion_scripts(self):
        """Test that completion scripts are properly embedded."""
        try:
            from src.completion import (
                get_embedded_powershell_completion,
                get_embedded_bash_completion,
                get_embedded_zsh_completion,
                get_embedded_fish_completion
            )
            
            # Test PowerShell script
            ps_script = get_embedded_powershell_completion()
            self.assertIn("Register-ArgumentCompleter", ps_script)
            self.assertIn("cvequery", ps_script)
            
            # Test Bash script
            bash_script = get_embedded_bash_completion()
            self.assertIn("_CVEQUERY_COMPLETE=bash_source", bash_script)
            
            # Test Zsh script
            zsh_script = get_embedded_zsh_completion()
            self.assertIn("_CVEQUERY_COMPLETE=zsh_source", zsh_script)
            
            # Test Fish script
            fish_script = get_embedded_fish_completion()
            self.assertIn("_CVEQUERY_COMPLETE=fish_source", fish_script)
            
        except Exception as e:
            self.fail(f"Embedded completion scripts test failed: {e}")
    
    def test_automatic_installation_functionality(self):
        """Test automatic installation functionality."""
        try:
            from src.completion import install_completion_automatically
            
            # Test that the function exists and can be called
            success, message = install_completion_automatically('auto')
            
            # The function should return a boolean and a message
            self.assertIsInstance(success, bool)
            self.assertIsInstance(message, str)
            self.assertGreater(len(message), 0)
            
        except Exception as e:
            self.fail(f"Automatic installation test failed: {e}")


if __name__ == '__main__':
    unittest.main()