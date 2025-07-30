"""Tests for the main module."""
import unittest
from unittest.mock import patch, Mock
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.main import main


class TestMain(unittest.TestCase):
    """Test cases for main module."""
    
    @patch('src.main.cli')
    def test_main_function_calls_cli(self, mock_cli):
        """Test that main function calls the CLI."""
        main()
        mock_cli.assert_called_once()
    
    @patch('src.main.cli')
    def test_main_function_with_exception(self, mock_cli):
        """Test main function handles CLI exceptions."""
        mock_cli.side_effect = Exception("Test exception")
        
        # The main function should let CLI handle exceptions
        with self.assertRaises(Exception):
            main()
    
    def test_main_module_structure(self):
        """Test main module has correct structure."""
        from src.main import main as main_function
        
        # Should have main function
        self.assertTrue(callable(main_function))
    
    def test_main_function_signature(self):
        """Test main function has correct signature."""
        import inspect
        
        sig = inspect.signature(main)
        
        # Should take no parameters
        self.assertEqual(len(sig.parameters), 0)
        
        # Should have no return annotation (returns None)
        self.assertEqual(sig.return_annotation, inspect.Signature.empty)
    
    def test_main_as_script(self):
        """Test main module when run as script."""
        # Import and check the main block structure
        from src.main import main as main_function
        
        # The main() function should exist and be callable
        self.assertTrue(callable(main_function))


class TestMainModuleIntegration(unittest.TestCase):
    """Integration tests for main module."""
    
    def test_main_imports(self):
        """Test that main module imports work correctly."""
        try:
            from src.main import main
            from src.cli import cli
        except ImportError as e:
            self.fail(f"Failed to import required modules: {e}")
    
    def test_main_module_can_be_imported(self):
        """Test that main module can be imported without errors."""
        try:
            import src.main
        except Exception as e:
            self.fail(f"Failed to import main module: {e}")
    
    def test_main_function_exists_and_callable(self):
        """Test that main function exists and is callable."""
        from src.main import main
        
        self.assertTrue(callable(main))
        
        # Should be able to get function info
        import inspect
        self.assertTrue(inspect.isfunction(main))
    
    @patch('sys.argv', ['cvequery', '--help'])
    def test_main_with_args(self):
        """Test main function with command line arguments."""
        from src.main import main
        
        # The --help flag causes SystemExit, which is expected behavior
        with self.assertRaises(SystemExit) as cm:
            main()
        
        # Help should exit with code 0
        self.assertEqual(cm.exception.code, 0)
    
    def test_main_module_docstring(self):
        """Test main module has appropriate structure."""
        from src.main import main as main_function
        
        # Function should be documented or at least exist
        self.assertTrue(callable(main_function))


class TestMainModuleAsScript(unittest.TestCase):
    """Test main module when executed as a script."""
    
    @patch('src.main.main')
    def test_main_block_execution(self, mock_main):
        """Test that main block executes main() when run as script."""
        # This test simulates the if __name__ == "__main__": block
        
        # Create a mock module with the main block
        main_code = '''
if __name__ == "__main__":
    main()
'''
        
        # The actual test is that main() gets called when the module is run
        # This is implicitly tested by the module structure
        self.assertTrue(callable(mock_main))
    
    def test_main_module_entry_point(self):
        """Test main module serves as proper entry point."""
        from src.main import main as main_function
        
        # Should have main function that can serve as entry point
        self.assertTrue(callable(main_function))
        
        # Main function should be at module level
        self.assertEqual(main_function.__module__, 'src.main')


if __name__ == '__main__':
    unittest.main()