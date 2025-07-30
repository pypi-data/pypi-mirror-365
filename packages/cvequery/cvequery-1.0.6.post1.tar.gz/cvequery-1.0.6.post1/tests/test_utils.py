"""Tests for the utils module."""
import unittest
from unittest.mock import patch, mock_open
import json
import tempfile
import os
from datetime import datetime
from src.utils import (
    save_to_json, validate_date, get_cvss_severity, filter_by_severity,
    colorize_output, sort_by_epss_score, create_cache_key
)


class TestUtils(unittest.TestCase):
    """Test cases for utility functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_cve = {
            "cve_id": "CVE-2021-44228",
            "summary": "Apache Log4j2 vulnerability",
            "cvss_v3": {"baseScore": 10.0, "baseSeverity": "Critical"},
            "cvss": {"score": 9.5},
            "epss": 0.95,
            "published": "2021-12-10T00:00:00Z"
        }
        
        self.sample_cves_data = {
            "cves": [
                {
                    "cve_id": "CVE-2021-44228",
                    "cvss_v3": {"baseScore": 10.0},
                    "epss": 0.95
                },
                {
                    "cve_id": "CVE-2021-44229", 
                    "cvss_v3": {"baseScore": 7.5},
                    "epss": 0.25
                },
                {
                    "cve_id": "CVE-2021-44230",
                    "cvss_v3": {"baseScore": 4.5},
                    "epss": 0.10
                }
            ],
            "total": 3
        }
    
    def test_save_to_json(self):
        """Test JSON file saving."""
        test_data = {"test": "data", "number": 123}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json_file = f.name
        
        try:
            save_to_json(test_data, json_file)
            
            # Verify file was created and contains correct data
            self.assertTrue(os.path.exists(json_file))
            with open(json_file, 'r') as f:
                loaded_data = json.load(f)
                self.assertEqual(loaded_data, test_data)
        finally:
            if os.path.exists(json_file):
                os.unlink(json_file)
    
    def test_validate_date_valid(self):
        """Test date validation with valid dates."""
        valid_dates = [
            "2021-01-01",
            "2023-12-31", 
            "2022-06-15"
        ]
        
        for date_str in valid_dates:
            self.assertTrue(validate_date(date_str))
    
    def test_validate_date_invalid(self):
        """Test date validation with invalid dates."""
        invalid_dates = [
            "2021-13-01",  # Invalid month
            "2021-01-32",  # Invalid day
            "21-01-01",    # Wrong format
            "2021/01/01",  # Wrong separator
            "invalid",     # Not a date
            ""             # Empty string
        ]
        
        for date_str in invalid_dates:
            self.assertFalse(validate_date(date_str))
    
    def test_get_cvss_severity(self):
        """Test CVSS severity calculation."""
        test_cases = [
            (10.0, "critical"),
            (9.5, "critical"),
            (8.5, "high"),
            (7.0, "high"),
            (6.5, "medium"),
            (4.0, "medium"),
            (3.5, "low"),
            (0.1, "low"),
            (0.0, "none")
        ]
        
        for score, expected_severity in test_cases:
            self.assertEqual(get_cvss_severity(score), expected_severity)
    
    def test_filter_by_severity_critical(self):
        """Test filtering by critical severity."""
        result = filter_by_severity(self.sample_cves_data, ["critical"])
        
        self.assertEqual(len(result["cves"]), 1)
        self.assertEqual(result["cves"][0]["cve_id"], "CVE-2021-44228")
        self.assertEqual(result["total"], 1)
    
    def test_filter_by_severity_multiple(self):
        """Test filtering by multiple severity levels."""
        result = filter_by_severity(self.sample_cves_data, ["critical", "high"])
        
        self.assertEqual(len(result["cves"]), 2)
        self.assertEqual(result["total"], 2)
        
        # Should be sorted by score (highest first)
        self.assertEqual(result["cves"][0]["cve_id"], "CVE-2021-44228")
        self.assertEqual(result["cves"][1]["cve_id"], "CVE-2021-44229")
    
    def test_filter_by_severity_no_matches(self):
        """Test filtering with no matches."""
        result = filter_by_severity(self.sample_cves_data, ["none"])
        
        self.assertEqual(len(result["cves"]), 0)
        self.assertEqual(result["total"], 0)
    
    def test_filter_by_severity_empty_data(self):
        """Test filtering with empty data."""
        empty_data = {"cves": [], "total": 0}
        result = filter_by_severity(empty_data, ["critical"])
        
        self.assertEqual(result, empty_data)
    
    def test_filter_by_severity_no_levels(self):
        """Test filtering with no severity levels specified."""
        result = filter_by_severity(self.sample_cves_data, [])
        
        self.assertEqual(result, self.sample_cves_data)
    
    def test_sort_by_epss_score(self):
        """Test sorting by EPSS score."""
        result = sort_by_epss_score(self.sample_cves_data)
        
        # Should be sorted by EPSS score (highest first)
        epss_scores = [cve.get("epss", 0) for cve in result["cves"]]
        self.assertEqual(epss_scores, [0.95, 0.25, 0.10])
    
    def test_sort_by_epss_score_empty(self):
        """Test sorting empty data."""
        empty_data = {"cves": []}
        result = sort_by_epss_score(empty_data)
        
        self.assertEqual(result, empty_data)
    
    def test_sort_by_epss_score_missing_epss(self):
        """Test sorting with missing EPSS scores."""
        data_with_missing = {
            "cves": [
                {"cve_id": "CVE-1", "epss": 0.5},
                {"cve_id": "CVE-2"},  # Missing EPSS
                {"cve_id": "CVE-3", "epss": 0.8}
            ]
        }
        
        result = sort_by_epss_score(data_with_missing)
        
        # Should handle missing EPSS scores (treat as 0.0)
        self.assertEqual(len(result["cves"]), 3)
        self.assertEqual(result["cves"][0]["epss"], 0.8)
        self.assertEqual(result["cves"][1]["epss"], 0.5)
    
    def test_create_cache_key(self):
        """Test cache key creation."""
        # Test with simple arguments
        key1 = create_cache_key("test", arg1="value1", arg2="value2")
        key2 = create_cache_key("test", arg1="value1", arg2="value2")
        key3 = create_cache_key("test", arg1="different", arg2="value2")
        
        # Same arguments should produce same key
        self.assertEqual(key1, key2)
        
        # Different arguments should produce different keys
        self.assertNotEqual(key1, key3)
        
        # Keys should be consistent regardless of argument order
        key4 = create_cache_key("test", arg2="value2", arg1="value1")
        self.assertEqual(key1, key4)
    
    def test_create_cache_key_with_none_values(self):
        """Test cache key creation with None values."""
        key1 = create_cache_key("test", arg1="value1", arg2=None)
        key2 = create_cache_key("test", arg1="value1", arg2=None)
        
        self.assertEqual(key1, key2)
    
    @patch('builtins.print')
    def test_colorize_output(self, mock_print):
        """Test colorized output function."""
        fields_to_display = ["cve_id", "summary", "cvss_v3"]
        
        colorize_output(self.sample_cve, fields_to_display)
        
        # Should have called print for each field
        self.assertEqual(mock_print.call_count, len(fields_to_display))
    
    @patch('builtins.print')
    def test_colorize_output_with_dict_values(self, mock_print):
        """Test colorized output with dictionary values."""
        fields_to_display = ["cvss_v3"]
        
        colorize_output(self.sample_cve, fields_to_display)
        
        # Should handle dictionary values
        mock_print.assert_called()
    
    @patch('builtins.print')
    def test_colorize_output_with_list_values(self, mock_print):
        """Test colorized output with list values."""
        cve_with_list = {
            "cve_id": "CVE-2021-44228",
            "references": ["https://example.com/1", "https://example.com/2"]
        }
        
        colorize_output(cve_with_list, ["references"])
        
        mock_print.assert_called()
    
    def test_filter_by_severity_with_different_cvss_formats(self):
        """Test severity filtering with different CVSS formats."""
        mixed_format_data = {
            "cves": [
                {
                    "cve_id": "CVE-1",
                    "cvss_v3": {"baseScore": 9.0}  # Dict format
                },
                {
                    "cve_id": "CVE-2", 
                    "cvss_v3": 7.5  # Direct number format
                },
                {
                    "cve_id": "CVE-3",
                    "cvss": {"score": 8.5}  # CVSS v2 format
                },
                {
                    "cve_id": "CVE-4",
                    "cvss": 6.0  # Direct CVSS v2 number
                }
            ],
            "total": 4
        }
        
        result = filter_by_severity(mixed_format_data, ["critical", "high"])
        
        # Should find CVEs with scores >= 7.0
        self.assertEqual(len(result["cves"]), 3)
        
        # Should be sorted by score
        scores = []
        for cve in result["cves"]:
            if "cvss_v3" in cve:
                if isinstance(cve["cvss_v3"], dict):
                    scores.append(cve["cvss_v3"]["baseScore"])
                else:
                    scores.append(cve["cvss_v3"])
            elif "cvss" in cve:
                if isinstance(cve["cvss"], dict):
                    scores.append(cve["cvss"]["score"])
                else:
                    scores.append(cve["cvss"])
        
        # Should be in descending order
        self.assertEqual(scores, sorted(scores, reverse=True))


if __name__ == '__main__':
    unittest.main()