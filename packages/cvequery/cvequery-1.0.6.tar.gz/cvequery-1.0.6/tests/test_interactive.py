"""Tests for the interactive module."""
import pytest
import unittest
from unittest.mock import patch, Mock, MagicMock
from io import StringIO
import sys
from src.interactive import InteractiveSession


class TestInteractiveSession(unittest.TestCase):
    """Test cases for InteractiveSession class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.session = InteractiveSession()
        self.sample_cve_data = {
            "cve_id": "CVE-2021-44228",
            "summary": "Apache Log4j2 vulnerability",
            "cvss_v3": {"baseScore": 10.0, "baseSeverity": "Critical"},
            "published": "2021-12-10T00:00:00Z"
        }
        
        self.sample_cves_data = {
            "cves": [self.sample_cve_data],
            "total": 1
        }
    
    def test_session_initialization(self):
        """Test InteractiveSession initialization."""
        self.assertIsInstance(self.session.session_data, dict)
        self.assertIsInstance(self.session.results_history, list)
        self.assertEqual(len(self.session.results_history), 0)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_welcome_message(self, mock_stdout):
        """Test welcome message display."""
        self.session.welcome()
        
        output = mock_stdout.getvalue()
        self.assertIn("CVE Query Interactive Mode", output)
        self.assertIn("Welcome", output)
        self.assertIn("help", output)
        self.assertIn("quit", output)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_show_help(self, mock_stdout):
        """Test help message display."""
        self.session.show_help()
        
        output = mock_stdout.getvalue()
        self.assertIn("Available Commands", output)
        self.assertIn("search cve", output)
        self.assertIn("search product", output)
        self.assertIn("history", output)
        self.assertIn("export", output)
    
    @patch('src.interactive.get_cve_data')
    @patch('src.interactive.colorize_output')
    @patch('builtins.input')
    def test_wizard_cve_search(self, mock_input, mock_colorize, mock_get_cve):
        """Test CVE search wizard."""
        # Mock user inputs
        mock_input.side_effect = [
            "CVE-2021-44228",  # CVE ID
            "",                # No specific fields (use all)
            "n"                # Don't export
        ]
        
        mock_get_cve.return_value = self.sample_cve_data
        
        self.session._wizard_cve_search()
        
        # Verify CVE data was fetched
        mock_get_cve.assert_called_once_with("CVE-2021-44228")
        
        # Verify output was colorized
        mock_colorize.assert_called_once()
        
        # Verify result was added to history
        self.assertEqual(len(self.session.results_history), 1)
        self.assertEqual(self.session.results_history[0]["type"], "cve")
        self.assertEqual(self.session.results_history[0]["query"], "CVE-2021-44228")
    
    @patch('src.interactive.get_cves_data')
    @patch('src.interactive.colorize_output')
    @patch('builtins.input')
    def test_wizard_product_search(self, mock_input, mock_colorize, mock_get_cves):
        """Test product search wizard."""
        # Mock user inputs
        mock_input.side_effect = [
            "apache",          # Product name
            "",                # No severity filter
            "",                # No start date
            "",                # No end date
            "n",               # Not KEV only
            "",                # Default limit
            "n",               # Don't show all results
            "n"                # Don't export
        ]
        
        mock_get_cves.return_value = self.sample_cves_data
        
        self.session._wizard_product_search()
        
        # Verify CVEs data was fetched
        mock_get_cves.assert_called_once()
        
        # Verify result was added to history
        self.assertEqual(len(self.session.results_history), 1)
        self.assertEqual(self.session.results_history[0]["type"], "product")
        self.assertEqual(self.session.results_history[0]["query"], "apache")
    
    @patch('src.interactive.get_cves_data')
    @patch('builtins.input')
    def test_wizard_cpe_search(self, mock_input, mock_get_cves):
        """Test CPE search wizard."""
        mock_input.return_value = "cpe:2.3:a:apache:http_server:2.4.41"
        mock_get_cves.return_value = self.sample_cves_data
        
        self.session._wizard_cpe_search()
        
        # Verify CVEs data was fetched with CPE
        mock_get_cves.assert_called_once_with(cpe23="cpe:2.3:a:apache:http_server:2.4.41", limit=50)
        
        # Verify result was added to history
        self.assertEqual(len(self.session.results_history), 1)
        self.assertEqual(self.session.results_history[0]["type"], "cpe")
    
    @patch('src.interactive.get_cves_data')
    @patch('builtins.input')
    def test_wizard_advanced_search(self, mock_input, mock_get_cves):
        """Test advanced search wizard."""
        # Mock user inputs for advanced search
        mock_input.side_effect = [
            "apache",          # Product name
            "critical,high",   # Severity filter
            "2021-01-01",      # Start date
            "2021-12-31",      # End date
            "y",               # KEV only
            "y",               # Sort by EPSS
            "100"              # Limit
        ]
        
        mock_get_cves.return_value = self.sample_cves_data
        
        self.session._wizard_advanced_search()
        
        # Verify CVEs data was fetched with all parameters
        mock_get_cves.assert_called_once()
        call_args = mock_get_cves.call_args
        self.assertEqual(call_args[1]['product'], 'apache')
        self.assertEqual(call_args[1]['is_kev'], True)
        self.assertEqual(call_args[1]['sort_by_epss'], True)
        self.assertEqual(call_args[1]['start_date'], '2021-01-01')
        self.assertEqual(call_args[1]['end_date'], '2021-12-31')
        self.assertEqual(call_args[1]['limit'], 100)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_show_history_empty(self, mock_stdout):
        """Test showing empty history."""
        self.session.show_history()
        
        output = mock_stdout.getvalue()
        self.assertIn("No search history", output)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_show_history_with_results(self, mock_stdout):
        """Test showing history with results."""
        # Add some results to history
        self.session.results_history = [
            {
                "type": "cve",
                "query": "CVE-2021-44228",
                "data": self.sample_cve_data
            },
            {
                "type": "product",
                "query": "apache",
                "data": self.sample_cves_data
            }
        ]
        
        self.session.show_history()
        
        output = mock_stdout.getvalue()
        self.assertIn("Search History", output)
        self.assertIn("CVE: CVE-2021-44228", output)
        self.assertIn("PRODUCT: apache", output)
    
    @patch('src.interactive.save_to_json')
    @patch('sys.stdout', new_callable=StringIO)
    def test_export_last_results(self, mock_stdout, mock_save):
        """Test exporting last results."""
        # Add result to history
        self.session.results_history = [
            {
                "type": "cve",
                "query": "CVE-2021-44228",
                "data": self.sample_cve_data
            }
        ]
        
        self.session.export_last_results("test.json")
        
        # Verify save_to_json was called
        mock_save.assert_called_once_with(self.sample_cve_data, "test.json")
        
        output = mock_stdout.getvalue()
        self.assertIn("exported to test.json", output)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_export_no_results(self, mock_stdout):
        """Test exporting with no results."""
        self.session.export_last_results("test.json")
        
        output = mock_stdout.getvalue()
        self.assertIn("No results to export", output)
    
    @patch('os.system')
    def test_clear_screen(self, mock_system):
        """Test screen clearing."""
        self.session.clear_screen()
        
        # Should call os.system with appropriate command
        mock_system.assert_called_once()
    
    @patch('builtins.input')
    @patch('sys.stdout', new_callable=StringIO)
    def test_guided_search_wizard_menu(self, mock_stdout, mock_input):
        """Test guided search wizard menu."""
        # Mock user selecting CVE search (option 1)
        mock_input.side_effect = [
            "1",               # Select CVE search
            "CVE-2021-44228",  # CVE ID
            "",                # No specific fields
            "n"                # Don't export
        ]
        
        with patch('src.interactive.get_cve_data') as mock_get_cve:
            mock_get_cve.return_value = self.sample_cve_data
            
            self.session.guided_search_wizard()
            
            output = mock_stdout.getvalue()
            self.assertIn("Guided Search Wizard", output)
            self.assertIn("Select search type", output)
    
    @patch('builtins.input')
    def test_guided_search_wizard_invalid_choice(self, mock_input):
        """Test guided search wizard with invalid choice."""
        # Mock invalid choice followed by valid choice
        mock_input.side_effect = [
            "5",               # Invalid choice
            "1",               # Valid choice
            "CVE-2021-44228",  # CVE ID
            "",                # No specific fields
            "n"                # Don't export
        ]
        
        with patch('src.interactive.get_cve_data') as mock_get_cve:
            mock_get_cve.return_value = self.sample_cve_data
            
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                self.session.guided_search_wizard()
                
                output = mock_stdout.getvalue()
                self.assertIn("Invalid choice", output)


class TestInteractiveSessionRun(unittest.TestCase):
    """Test the main run loop of InteractiveSession."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.session = InteractiveSession()
    
    @patch('builtins.input')
    @patch('sys.stdout', new_callable=StringIO)
    def test_run_quit_command(self, mock_stdout, mock_input):
        """Test quitting the interactive session."""
        mock_input.return_value = "quit"
        
        self.session.run()
        
        output = mock_stdout.getvalue()
        self.assertIn("Goodbye", output)
    
    @patch('builtins.input')
    @patch('sys.stdout', new_callable=StringIO)
    def test_run_help_command(self, mock_stdout, mock_input):
        """Test help command in interactive session."""
        mock_input.side_effect = ["help", "quit"]
        
        self.session.run()
        
        output = mock_stdout.getvalue()
        self.assertIn("Available Commands", output)
    
    @patch('builtins.input')
    @patch('sys.stdout', new_callable=StringIO)
    def test_run_clear_command(self, mock_stdout, mock_input):
        """Test clear command in interactive session."""
        mock_input.side_effect = ["clear", "quit"]
        
        with patch.object(self.session, 'clear_screen') as mock_clear:
            self.session.run()
            mock_clear.assert_called_once()
    
    @patch('builtins.input')
    @patch('sys.stdout', new_callable=StringIO)
    def test_run_history_command(self, mock_stdout, mock_input):
        """Test history command in interactive session."""
        mock_input.side_effect = ["history", "quit"]
        
        self.session.run()
        
        output = mock_stdout.getvalue()
        self.assertIn("No search history", output)
    
    @patch('builtins.input')
    @patch('sys.stdout', new_callable=StringIO)
    def test_run_export_command(self, mock_stdout, mock_input):
        """Test export command in interactive session."""
        mock_input.side_effect = ["export test.json", "quit"]
        
        with patch.object(self.session, 'export_last_results') as mock_export:
            self.session.run()
            mock_export.assert_called_once_with("test.json")
    
    @patch('builtins.input')
    @patch('src.interactive.get_cve_data')
    def test_run_search_cve_command(self, mock_get_cve, mock_input):
        """Test search cve command in interactive session."""
        mock_input.side_effect = ["search cve CVE-2021-44228", "quit"]
        mock_get_cve.return_value = {
            "cve_id": "CVE-2021-44228",
            "summary": "Test vulnerability"
        }
        
        with patch('src.interactive.colorize_output'):
            self.session.run()
            
            mock_get_cve.assert_called_once_with("CVE-2021-44228")
    
    @patch('builtins.input')
    @patch('src.interactive.get_cves_data')
    def test_run_search_product_command(self, mock_get_cves, mock_input):
        """Test search product command in interactive session."""
        mock_input.side_effect = ["search product apache", "quit"]
        mock_get_cves.return_value = {
            "cves": [{"cve_id": "CVE-2021-44228"}],
            "total": 1
        }
        
        with patch('src.interactive.colorize_output'):
            self.session.run()
            
            mock_get_cves.assert_called_once_with(product="apache", limit=10)
    
    @patch('builtins.input')
    @patch('sys.stdout', new_callable=StringIO)
    def test_run_unknown_command(self, mock_stdout, mock_input):
        """Test unknown command in interactive session."""
        mock_input.side_effect = ["unknown command", "quit"]
        
        self.session.run()
        
        output = mock_stdout.getvalue()
        self.assertIn("Unknown command", output)
    
    @patch('builtins.input')
    @patch('sys.stdout', new_callable=StringIO)
    def test_run_keyboard_interrupt(self, mock_stdout, mock_input):
        """Test keyboard interrupt handling."""
        mock_input.side_effect = [KeyboardInterrupt(), "quit"]
        
        self.session.run()
        
        output = mock_stdout.getvalue()
        self.assertIn("Use 'quit' to exit", output)
    
    @patch('builtins.input')
    @patch('sys.stdout', new_callable=StringIO)
    def test_run_eof_error(self, mock_stdout, mock_input):
        """Test EOF error handling."""
        mock_input.side_effect = EOFError()
        
        self.session.run()
        
        output = mock_stdout.getvalue()
        self.assertIn("Goodbye", output)


if __name__ == '__main__':
    unittest.main()