"""Tests for the __version__ module."""
import unittest
import re
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from __version__ import __version__


class TestVersion(unittest.TestCase):
    """Test cases for version information."""
    
    def test_version_exists(self):
        """Test that version is defined."""
        self.assertIsNotNone(__version__)
        self.assertIsInstance(__version__, str)
        self.assertTrue(len(__version__) > 0)
    
    def test_version_format(self):
        """Test that version follows semantic versioning format."""
        # Should match pattern like "1.0.4" or "1.0.4-beta.1"
        version_pattern = r'^\d+\.\d+\.\d+(?:-[a-zA-Z0-9.-]+)?$'
        self.assertRegex(__version__, version_pattern)
    
    def test_version_components(self):
        """Test version components are valid."""
        # Split version into components
        base_version = __version__.split('-')[0]  # Remove pre-release suffix if any
        parts = base_version.split('.')
        
        # Should have exactly 3 parts (major.minor.patch)
        self.assertEqual(len(parts), 3)
        
        # Each part should be a valid integer
        for part in parts:
            self.assertTrue(part.isdigit())
            self.assertGreaterEqual(int(part), 0)
    
    def test_current_version_value(self):
        """Test current version value."""
        # This test ensures the version is what we expect
        self.assertEqual(__version__, "1.0.5")


if __name__ == '__main__':
    unittest.main()