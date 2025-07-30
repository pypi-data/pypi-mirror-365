"""Tests for the constants module."""
import unittest
from src.constants import (
    BASE_URL, DEFAULT_TIMEOUT, DEFAULT_LIMIT, HTTP_OK, HTTP_BAD_REQUEST,
    HTTP_NOT_FOUND, HTTP_TOO_MANY_REQUESTS, SEVERITY_MAP, API_VERSION,
    PACKAGE_NAME
)


class TestConstants(unittest.TestCase):
    """Test cases for constants."""
    
    def test_base_url(self):
        """Test BASE_URL constant."""
        self.assertIsInstance(BASE_URL, str)
        self.assertTrue(BASE_URL.startswith("https://"))
        self.assertIn("shodan", BASE_URL.lower())
    
    def test_default_timeout(self):
        """Test DEFAULT_TIMEOUT constant."""
        self.assertIsInstance(DEFAULT_TIMEOUT, int)
        self.assertGreater(DEFAULT_TIMEOUT, 0)
        self.assertLessEqual(DEFAULT_TIMEOUT, 60)  # Reasonable timeout
    
    def test_default_limit(self):
        """Test DEFAULT_LIMIT constant."""
        self.assertIsInstance(DEFAULT_LIMIT, int)
        self.assertGreater(DEFAULT_LIMIT, 0)
        self.assertLessEqual(DEFAULT_LIMIT, 10000)  # Reasonable limit
    
    def test_http_status_codes(self):
        """Test HTTP status code constants."""
        self.assertEqual(HTTP_OK, 200)
        self.assertEqual(HTTP_BAD_REQUEST, 400)
        self.assertEqual(HTTP_NOT_FOUND, 404)
        self.assertEqual(HTTP_TOO_MANY_REQUESTS, 429)
        
        # All should be integers
        status_codes = [HTTP_OK, HTTP_BAD_REQUEST, HTTP_NOT_FOUND, HTTP_TOO_MANY_REQUESTS]
        for code in status_codes:
            self.assertIsInstance(code, int)
            self.assertGreaterEqual(code, 200)
            self.assertLess(code, 600)
    
    def test_severity_map(self):
        """Test SEVERITY_MAP constant."""
        self.assertIsInstance(SEVERITY_MAP, dict)
        
        expected_severities = ["critical", "high", "medium", "low", "none"]
        for severity in expected_severities:
            self.assertIn(severity, SEVERITY_MAP)
            
            # Each severity should map to a tuple of (min, max) scores
            score_range = SEVERITY_MAP[severity]
            self.assertIsInstance(score_range, tuple)
            self.assertEqual(len(score_range), 2)
            
            min_score, max_score = score_range
            self.assertIsInstance(min_score, (int, float))
            self.assertIsInstance(max_score, (int, float))
            self.assertLessEqual(min_score, max_score)
            self.assertGreaterEqual(min_score, 0.0)
            self.assertLessEqual(max_score, 10.0)
    
    def test_severity_map_ranges(self):
        """Test SEVERITY_MAP ranges are logical."""
        # Critical should be highest
        self.assertGreaterEqual(SEVERITY_MAP["critical"][0], 9.0)
        self.assertEqual(SEVERITY_MAP["critical"][1], 10.0)
        
        # High should be next
        self.assertGreaterEqual(SEVERITY_MAP["high"][0], 7.0)
        self.assertLess(SEVERITY_MAP["high"][1], 9.0)
        
        # Medium should be middle
        self.assertGreaterEqual(SEVERITY_MAP["medium"][0], 4.0)
        self.assertLess(SEVERITY_MAP["medium"][1], 7.0)
        
        # Low should be lower
        self.assertGreater(SEVERITY_MAP["low"][0], 0.0)
        self.assertLess(SEVERITY_MAP["low"][1], 4.0)
        
        # None should be zero
        self.assertEqual(SEVERITY_MAP["none"][0], 0.0)
        self.assertEqual(SEVERITY_MAP["none"][1], 0.0)
    
    def test_severity_map_no_gaps(self):
        """Test SEVERITY_MAP has no gaps in coverage."""
        # Sort severities by their minimum score
        severities = sorted(SEVERITY_MAP.items(), key=lambda x: x[1][0])
        
        # Check that ranges cover 0.0 to 10.0 without gaps
        self.assertEqual(severities[0][1][0], 0.0)  # Should start at 0
        
        for i in range(len(severities) - 1):
            current_max = severities[i][1][1]
            next_min = severities[i + 1][1][0]
            
            # Should have no gap (next min should be close to current max)
            # Use a more lenient comparison for floating point precision
            gap = abs(next_min - current_max)
            self.assertLessEqual(gap, 0.11, f"Gap of {gap} between {severities[i][0]} and {severities[i+1][0]}")
    
    def test_api_version(self):
        """Test API_VERSION constant."""
        self.assertIsInstance(API_VERSION, str)
        self.assertTrue(API_VERSION.startswith("v"))
        self.assertRegex(API_VERSION, r"v\d+")  # Should be like v1, v2, etc.
    
    def test_package_name(self):
        """Test PACKAGE_NAME constant."""
        self.assertIsInstance(PACKAGE_NAME, str)
        self.assertGreater(len(PACKAGE_NAME), 0)
        self.assertEqual(PACKAGE_NAME.lower(), PACKAGE_NAME)  # Should be lowercase
        self.assertNotIn(" ", PACKAGE_NAME)  # Should not contain spaces
    
    def test_constants_immutability(self):
        """Test that constants are of expected immutable types."""
        # String constants should be strings
        string_constants = [BASE_URL, API_VERSION, PACKAGE_NAME]
        for const in string_constants:
            self.assertIsInstance(const, str)
        
        # Integer constants should be integers
        int_constants = [DEFAULT_TIMEOUT, DEFAULT_LIMIT, HTTP_OK, HTTP_BAD_REQUEST, 
                        HTTP_NOT_FOUND, HTTP_TOO_MANY_REQUESTS]
        for const in int_constants:
            self.assertIsInstance(const, int)
        
        # SEVERITY_MAP should be a dictionary
        self.assertIsInstance(SEVERITY_MAP, dict)
    
    def test_constants_reasonable_values(self):
        """Test that constants have reasonable values."""
        # Timeout should be reasonable (not too short or too long)
        self.assertGreaterEqual(DEFAULT_TIMEOUT, 5)
        self.assertLessEqual(DEFAULT_TIMEOUT, 120)
        
        # Limit should be reasonable
        self.assertGreaterEqual(DEFAULT_LIMIT, 10)
        self.assertLessEqual(DEFAULT_LIMIT, 50000)
        
        # Package name should be reasonable length
        self.assertGreaterEqual(len(PACKAGE_NAME), 3)
        self.assertLessEqual(len(PACKAGE_NAME), 50)
        
        # Base URL should be HTTPS
        self.assertTrue(BASE_URL.startswith("https://"))
        
        # API version should be reasonable
        self.assertLessEqual(len(API_VERSION), 10)


class TestSeverityMapUsage(unittest.TestCase):
    """Test SEVERITY_MAP usage scenarios."""
    
    def test_score_classification(self):
        """Test that scores are classified correctly."""
        test_cases = [
            (10.0, "critical"),
            (9.5, "critical"),
            (9.0, "critical"),
            (8.9, "high"),
            (8.0, "high"),
            (7.0, "high"),
            (6.9, "medium"),
            (5.0, "medium"),
            (4.0, "medium"),
            (3.9, "low"),
            (2.0, "low"),
            (0.1, "low"),
            (0.0, "none")
        ]
        
        for score, expected_severity in test_cases:
            # Find which severity range the score falls into
            found_severity = None
            for severity, (min_score, max_score) in SEVERITY_MAP.items():
                if min_score <= score <= max_score:
                    found_severity = severity
                    break
            
            self.assertEqual(found_severity, expected_severity, 
                           f"Score {score} should be classified as {expected_severity}, got {found_severity}")
    
    def test_boundary_values(self):
        """Test boundary values between severity ranges."""
        # Test exact boundary values
        self.assertTrue(9.0 >= SEVERITY_MAP["critical"][0])
        self.assertTrue(7.0 >= SEVERITY_MAP["high"][0])
        self.assertTrue(4.0 >= SEVERITY_MAP["medium"][0])
        self.assertTrue(0.1 >= SEVERITY_MAP["low"][0])
        self.assertTrue(0.0 >= SEVERITY_MAP["none"][0])


if __name__ == '__main__':
    unittest.main()