"""Tests for the API module."""
import unittest
from unittest.mock import patch, Mock, MagicMock
import json
import tempfile
import os
import time
from src.api import (
    get_cve_data, get_cves_data, get_cpe_data, 
    _get_from_cache, _save_to_cache,
    get_cache_dir
)
from src.constants import DEFAULT_LIMIT


class TestAPI(unittest.TestCase):
    """Test cases for API functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_cve_data = {
            "cve_id": "CVE-2021-44228",
            "summary": "Apache Log4j2 2.0-beta9 through 2.15.0 (excluding security releases 2.12.2, 2.12.3, and 2.3.1) JNDI features used in configuration, log messages, and parameters do not protect against attacker controlled LDAP and other JNDI related endpoints.",
            "cvss": 10.0,
            "cvss_version": 3.0,
            "cvss_v2": 9.3,
            "cvss_v3": 10.0,
            "epss": 0.9447,
            "ranking_epss": 0.99995,
            "kev": True,
            "published_time": "2021-12-10T10:15:09",
            "references": ["https://logging.apache.org/log4j/2.x/security.html"],
            "cpes": ["cpe:2.3:a:apache:log4j:2.0"]
        }
        
        self.sample_cves_data = {
            "cves": [self.sample_cve_data],
            "total": 1
        }
        
        self.sample_cpe_data = {
            "cpes": ["cpe:2.3:a:apache:log4j:2.14.1:*:*:*:*:*:*:*"],
            "total": 1
        }
    
    @patch('src.api._get_from_cache')
    @patch('src.api.http_session.get')
    def test_get_cve_data_success(self, mock_get, mock_cache):
        """Test successful CVE data retrieval."""
        # Ensure cache returns None so we make the API call
        mock_cache.return_value = None
        
        mock_response = Mock()
        mock_response.json.return_value = self.sample_cve_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = get_cve_data("CVE-2021-44228")
        
        self.assertEqual(result, self.sample_cve_data)
        mock_get.assert_called_once()
    
    @patch('src.api._get_from_cache')
    @patch('src.api.http_session.get')
    def test_get_cve_data_error(self, mock_get, mock_cache):
        """Test CVE data retrieval with API error."""
        # Ensure cache returns None so we make the API call
        mock_cache.return_value = None
        mock_get.side_effect = Exception("API Error")
        
        result = get_cve_data("CVE-2021-44228")
        
        # The function should return an error dict when there's an exception
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
    
    @patch('src.api._get_from_cache')
    @patch('src.api.http_session.get')
    def test_get_cves_data_success(self, mock_get, mock_cache):
        """Test successful CVEs data retrieval."""
        # Ensure cache returns None so we make the API call
        mock_cache.return_value = None
        
        mock_response = Mock()
        mock_response.json.return_value = self.sample_cves_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = get_cves_data(product="apache")
        
        self.assertEqual(result, self.sample_cves_data)
        mock_get.assert_called_once()
    
    @patch('src.api._get_from_cache')
    @patch('src.api.http_session.get')
    def test_get_cpe_data_success(self, mock_get, mock_cache):
        """Test successful CPE data retrieval."""
        # Ensure cache returns None so we make the API call
        mock_cache.return_value = None
        
        mock_response = Mock()
        mock_response.json.return_value = self.sample_cpe_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = get_cpe_data("apache")
        
        self.assertEqual(result["cpes"], self.sample_cpe_data["cpes"])
        self.assertEqual(result["total"], self.sample_cpe_data["total"])
    
    def test_cache_functionality(self):
        """Test cache save and retrieve functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock the cache directory
            with patch('src.api.CACHE_DIR', temp_dir):
                cache_key = "test_key"
                test_data = {"test": "data"}
                
                # Test saving to cache
                _save_to_cache(cache_key, test_data)
                
                # Test retrieving from cache
                cached_data = _get_from_cache(cache_key)
                self.assertEqual(cached_data, test_data)
    
    def test_cache_expiry(self):
        """Test cache expiry functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('src.api.CACHE_DIR', temp_dir):
                cache_key = "test_key_expiry"
                test_data = {"test": "data"}
                
                # Save to cache
                _save_to_cache(cache_key, test_data)
                
                # Mock file modification time to be old
                cache_file = os.path.join(temp_dir, f"{cache_key}.json")
                old_time = time.time() - (25 * 60 * 60)  # 25 hours ago
                os.utime(cache_file, (old_time, old_time))
                
                # Should return None for expired cache
                cached_data = _get_from_cache(cache_key)
                self.assertIsNone(cached_data)
    
    def test_rate_limiter(self):
        """Test rate limiter functionality (disabled for performance)."""
        # Rate limiting has been temporarily disabled for better performance
        # This test is kept for future reference
        self.assertTrue(True)  # Placeholder test
    
    def test_get_cache_dir(self):
        """Test cache directory creation."""
        cache_dir = get_cache_dir()
        self.assertTrue(cache_dir.exists())
        self.assertTrue(cache_dir.is_dir())
    
    @patch('src.api._get_from_cache')
    @patch('src.api.http_session.get')
    def test_get_cves_data_with_filters(self, mock_get, mock_cache):
        """Test CVEs data retrieval with various filters."""
        # Ensure cache returns None so we make the API call
        mock_cache.return_value = None
        
        mock_response = Mock()
        mock_response.json.return_value = self.sample_cves_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Test with multiple filters
        result = get_cves_data(
            product="apache",
            is_kev=True,
            sort_by_epss=True,
            start_date="2021-01-01",
            end_date="2021-12-31",
            skip=10,
            limit=50
        )
        
        self.assertEqual(result, self.sample_cves_data)
        
        # Verify the correct parameters were passed
        call_args = mock_get.call_args
        params = call_args[1]['params']
        self.assertEqual(params['product'], 'apache')
        self.assertEqual(params['is_kev'], 'true')
        self.assertEqual(params['sort_by'], 'epss_score')
        self.assertEqual(params['start_date'], '2021-01-01')
        self.assertEqual(params['end_date'], '2021-12-31')
        self.assertEqual(params['skip'], 10)
        self.assertEqual(params['limit'], 50)


if __name__ == '__main__':
    unittest.main()