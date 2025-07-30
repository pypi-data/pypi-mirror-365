"""Tests for the formatting module."""
import pytest
import unittest
from unittest.mock import patch, Mock
from io import StringIO
import sys
from src.formatting import (
    OutputFormatter, format_cve_output, format_cve_list_output
)


class TestOutputFormatter(unittest.TestCase):
    """Test cases for OutputFormatter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_cve = {
            "cve_id": "CVE-2021-44228",
            "summary": "Apache Log4j2 JNDI features vulnerability allowing remote code execution",
            "cvss_v3": {
                "baseScore": 10.0,
                "baseSeverity": "Critical",
                "vectorString": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H"
            },
            "published": "2021-12-10T00:00:00Z",
            "modified": "2021-12-15T00:00:00Z",
            "kev": True,
            "epss": 0.95,
            "references": [
                "https://nvd.nist.gov/vuln/detail/CVE-2021-44228",
                "https://logging.apache.org/log4j/2.x/security.html"
            ],
            "cwe": "CWE-502: Deserialization of Untrusted Data"
        }
        
        self.sample_cves = [
            self.sample_cve,
            {
                "cve_id": "CVE-2021-44229",
                "summary": "Apache Log4j2 DoS vulnerability",
                "cvss_v3": {"baseScore": 7.5, "baseSeverity": "High"},
                "published": "2021-12-11T00:00:00Z",
                "kev": False,
                "epss": 0.25
            }
        ]
    
    def test_formatter_initialization(self):
        """Test OutputFormatter initialization."""
        formatter = OutputFormatter("table")
        self.assertEqual(formatter.format_type, "table")
        
        # Default format
        formatter_default = OutputFormatter()
        self.assertEqual(formatter_default.format_type, "default")
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_format_default(self, mock_stdout):
        """Test default formatting."""
        formatter = OutputFormatter("default")
        formatter.format_cve_data(self.sample_cve)
        
        output = mock_stdout.getvalue()
        self.assertIn("CVE-2021-44228", output)
        self.assertIn("Apache Log4j2", output)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_format_compact(self, mock_stdout):
        """Test compact formatting."""
        formatter = OutputFormatter("compact")
        formatter.format_cve_data(self.sample_cve)
        
        output = mock_stdout.getvalue()
        self.assertIn("CVE-2021-44228", output)
        self.assertIn("KEV", output)  # Should show KEV indicator
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_format_detailed(self, mock_stdout):
        """Test detailed formatting."""
        formatter = OutputFormatter("detailed")
        formatter.format_cve_data(self.sample_cve)
        
        output = mock_stdout.getvalue()
        self.assertIn("CVE Details", output)
        self.assertIn("SUMMARY", output)
        self.assertIn("SEVERITY & SCORING", output)
        self.assertIn("TIMELINE", output)
        self.assertIn("KNOWN EXPLOITED VULNERABILITY", output)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_format_table(self, mock_stdout):
        """Test table formatting."""
        formatter = OutputFormatter("table")
        formatter.format_cve_list(self.sample_cves)
        
        output = mock_stdout.getvalue()
        self.assertIn("CVE ID", output)
        self.assertIn("Severity", output)
        self.assertIn("CVSS", output)
        self.assertIn("┌", output)  # Table borders
        self.assertIn("│", output)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_format_summary(self, mock_stdout):
        """Test summary formatting."""
        formatter = OutputFormatter("summary")
        formatter.format_cve_list(self.sample_cves)
        
        output = mock_stdout.getvalue()
        self.assertIn("CVE SUMMARY", output)
        self.assertIn("Total CVEs", output)
        self.assertIn("Severity Distribution", output)
        self.assertIn("Critical", output)
        self.assertIn("High", output)
    
    def test_get_severity_level(self):
        """Test severity level extraction."""
        formatter = OutputFormatter()
        
        # Test CVSS v3 severity
        cve_with_v3 = {
            "cvss_v3": {"baseSeverity": "Critical"}
        }
        self.assertEqual(formatter._get_severity_level(cve_with_v3), "critical")
        
        # Test CVSS score calculation
        cve_with_score = {
            "cvss_v3": {"baseScore": 8.5}
        }
        self.assertEqual(formatter._get_severity_level(cve_with_score), "high")
        
        # Test CVSS v2 fallback
        cve_with_v2 = {
            "cvss": {"score": 6.5}
        }
        self.assertEqual(formatter._get_severity_level(cve_with_v2), "medium")
    
    def test_get_cvss_score(self):
        """Test CVSS score extraction."""
        formatter = OutputFormatter()
        
        # Test CVSS v3
        cve_with_v3 = {
            "cvss_v3": {"baseScore": 9.8}
        }
        self.assertEqual(formatter._get_cvss_score(cve_with_v3), "9.8")
        
        # Test CVSS v2 fallback
        cve_with_v2 = {
            "cvss": {"score": 7.5}
        }
        self.assertEqual(formatter._get_cvss_score(cve_with_v2), "7.5")
        
        # Test no score available
        cve_no_score = {}
        self.assertEqual(formatter._get_cvss_score(cve_no_score), "N/A")
    
    def test_colorize_cve_id(self):
        """Test CVE ID colorization."""
        formatter = OutputFormatter()
        result = formatter._colorize_cve_id("CVE-2021-44228")
        
        # Should contain the CVE ID and color codes
        self.assertIn("CVE-2021-44228", result)
    
    def test_truncate(self):
        """Test text truncation."""
        formatter = OutputFormatter()
        
        # Text shorter than limit
        short_text = "Short text"
        self.assertEqual(formatter._truncate(short_text, 20), short_text)
        
        # Text longer than limit
        long_text = "This is a very long text that should be truncated"
        truncated = formatter._truncate(long_text, 20)
        self.assertEqual(len(truncated), 20)
        self.assertTrue(truncated.endswith("..."))
    
    def test_format_date_value(self):
        """Test date formatting."""
        formatter = OutputFormatter()
        
        # ISO date format
        iso_date = "2021-12-10T00:00:00Z"
        formatted = formatter._format_date_value(iso_date)
        self.assertIn("2021-12-10", formatted)
        self.assertIn("UTC", formatted)
        
        # Invalid date format
        invalid_date = "invalid-date"
        formatted_invalid = formatter._format_date_value(invalid_date)
        self.assertEqual(formatted_invalid, invalid_date)
    
    def test_format_dict_value(self):
        """Test dictionary value formatting."""
        formatter = OutputFormatter()
        
        # CVSS data
        cvss_dict = {"baseScore": 9.8, "baseSeverity": "Critical"}
        formatted = formatter._format_dict_value(cvss_dict)
        self.assertIn("9.8", formatted)
        self.assertIn("Critical", formatted)
        
        # Other dictionary
        other_dict = {"key": "value"}
        formatted_other = formatter._format_dict_value(other_dict)
        self.assertIn("key", formatted_other)
        self.assertIn("value", formatted_other)
    
    def test_format_list_value(self):
        """Test list value formatting."""
        formatter = OutputFormatter()
        
        # Short list
        short_list = ["item1", "item2"]
        formatted = formatter._format_list_value(short_list)
        self.assertEqual(formatted, "item1, item2")
        
        # Long list
        long_list = ["item1", "item2", "item3", "item4", "item5"]
        formatted_long = formatter._format_list_value(long_list)
        self.assertIn("item1, item2, item3", formatted_long)
        self.assertIn("more", formatted_long)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_format_cve_list_empty(self, mock_stdout):
        """Test formatting empty CVE list."""
        formatter = OutputFormatter()
        formatter.format_cve_list([])
        
        output = mock_stdout.getvalue()
        self.assertIn("No CVEs found", output)
    
    def test_get_severity_color(self):
        """Test severity color mapping."""
        formatter = OutputFormatter()
        
        # Test all severity levels
        colors = {
            "critical": formatter._get_severity_color("critical"),
            "high": formatter._get_severity_color("high"),
            "medium": formatter._get_severity_color("medium"),
            "low": formatter._get_severity_color("low"),
            "none": formatter._get_severity_color("none")
        }
        
        # All should return color codes (non-empty strings)
        for severity, color in colors.items():
            self.assertIsInstance(color, str)
            self.assertGreater(len(color), 0)
    
    def test_get_severity_score(self):
        """Test severity score calculation for sorting."""
        formatter = OutputFormatter()
        
        scores = {
            "critical": formatter._get_severity_score("critical"),
            "high": formatter._get_severity_score("high"),
            "medium": formatter._get_severity_score("medium"),
            "low": formatter._get_severity_score("low"),
            "none": formatter._get_severity_score("none")
        }
        
        # Critical should have highest score
        self.assertGreater(scores["critical"], scores["high"])
        self.assertGreater(scores["high"], scores["medium"])
        self.assertGreater(scores["medium"], scores["low"])
        self.assertGreater(scores["low"], scores["none"])


class TestFormattingFunctions(unittest.TestCase):
    """Test standalone formatting functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_cve = {
            "cve_id": "CVE-2021-44228",
            "summary": "Test vulnerability",
            "cvss_v3": {"baseScore": 9.8, "baseSeverity": "Critical"}
        }
    
    @patch('src.formatting.OutputFormatter')
    def test_format_cve_output(self, mock_formatter_class):
        """Test format_cve_output function."""
        mock_formatter = Mock()
        mock_formatter_class.return_value = mock_formatter
        
        format_cve_output(self.sample_cve, "table", ["cve_id", "summary"])
        
        mock_formatter_class.assert_called_once_with("table")
        mock_formatter.format_cve_data.assert_called_once_with(
            self.sample_cve, ["cve_id", "summary"]
        )
    
    @patch('src.formatting.OutputFormatter')
    def test_format_cve_list_output(self, mock_formatter_class):
        """Test format_cve_list_output function."""
        mock_formatter = Mock()
        mock_formatter_class.return_value = mock_formatter
        
        cves = [self.sample_cve]
        format_cve_list_output(cves, "compact", ["cve_id"])
        
        mock_formatter_class.assert_called_once_with("compact")
        mock_formatter.format_cve_list.assert_called_once_with(
            cves, ["cve_id"]
        )


if __name__ == '__main__':
    unittest.main()