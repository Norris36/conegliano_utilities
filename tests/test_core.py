import unittest
import ast
import inspect
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from conegliano_utilities.core import get_functions_dataframe, hygin, find_files, get_file_creation_time, get_file_modified_time
from conegliano_utilities.data_utils import get_columns, humanise_df, rename_columns
import conegliano_utilities.core as core_module


class TestCore(unittest.TestCase):
    
    def setUp(self):
        self.core_functions = [
            get_functions_dataframe,
            hygin, 
            find_files,
            get_file_creation_time,
            get_file_modified_time
        ]
        self.data_functions = [
            get_columns,
            humanise_df,
            rename_columns
        ]
        self.all_functions = self.core_functions + self.data_functions
    
    def test_documentation_standard_compliance(self):
        """
        Test that all functions adhere to the enhanced documentation standard.
        
        1. Validates summary one-liner
        2. Checks for numbered steps describing the process
        3. Validates Args section with proper formatting
        4. Ensures Returns section with variable (type) - description format
        
        Returns type: None (NoneType) - assertion-based test with no return value
        """
        for func in self.all_functions:
            with self.subTest(function=func.__name__):
                self._validate_function_documentation(func)
    
    def _validate_function_documentation(self, func):
        """
        Validates a single function's documentation format with enhanced standard.
        
        1. Extracts and parses function docstring
        2. Checks for summary one-liner
        3. Validates numbered steps section
        4. Checks Args and Returns sections
        
        Returns type: None (NoneType) - raises AssertionError if validation fails
        """
        docstring = inspect.getdoc(func)
        self.assertIsNotNone(docstring, f"Function {func.__name__} has no docstring")
        
        lines = [line.strip() for line in docstring.split('\n') if line.strip()]
        
        # Check minimum structure requirements
        self.assertGreaterEqual(len(lines), 4, 
                              f"Function {func.__name__} docstring too short for standard format")
        
        # Find key sections
        args_idx = None
        returns_idx = None
        numbered_steps_start = None
        
        for i, line in enumerate(lines):
            if line.lower().startswith('args:'):
                args_idx = i
            elif line.lower().startswith('returns:') or line.lower().startswith('returns type:'):
                returns_idx = i
            elif line.strip().startswith('1.') and numbered_steps_start is None:
                numbered_steps_start = i
        
        # 1. Check for summary (first line should be non-empty)
        self.assertTrue(len(lines[0]) > 0, 
                       f"Function {func.__name__} missing summary line")
        
        # 2. Check for numbered steps
        if numbered_steps_start is not None:
            # Validate that we have numbered steps
            steps_found = []
            current_idx = numbered_steps_start
            
            while current_idx < len(lines) and current_idx < (args_idx or len(lines)):
                line = lines[current_idx]
                if line.strip() and (line.strip()[0].isdigit() and line.strip()[1:3] == '. '):
                    steps_found.append(line)
                elif line.lower().startswith('args:') or line.lower().startswith('returns'):
                    break
                current_idx += 1
            
            self.assertGreater(len(steps_found), 0,
                             f"Function {func.__name__} should have numbered steps (1. 2. 3. etc.)")
        
        # 3. Check Args section exists if function has parameters
        if hasattr(func, '__code__') and func.__code__.co_argcount > 0:
            # Skip 'self' parameter for methods
            param_count = func.__code__.co_argcount
            if func.__code__.co_varnames[0] == 'self':
                param_count -= 1
            
            if param_count > 0:
                self.assertIsNotNone(args_idx, 
                                   f"Function {func.__name__} has parameters but no Args section")
        
        # 4. Check Returns section format
        if returns_idx is not None:
            returns_line = lines[returns_idx]
            if returns_line.lower().startswith('returns type:'):
                # Check enhanced format: variable_name (datatype) - description
                returns_content = returns_line.split('Returns type:', 1)[1].strip()
                self.assertIn('(', returns_content, 
                             f"Function {func.__name__} returns line missing datatype in parentheses: '{returns_line}'")
                self.assertIn(')', returns_content,
                             f"Function {func.__name__} returns line missing closing parenthesis: '{returns_line}'")
                self.assertIn(' - ', returns_content,
                             f"Function {func.__name__} returns line missing ' - ' separator: '{returns_line}'")
    
    def test_core_function_imports(self):
        """
        Test that core functions can be imported successfully.
        
        ~~~
        " Validates all expected functions are available
        " Checks function callability
        " Ensures no import errors
        ~~~
        
        Returns type: None (NoneType) - assertion-based test with no return value
        """
        expected_functions = [
            'get_functions_dataframe',
            'hygin',
            'find_files', 
            'get_file_creation_time',
            'get_file_modified_time'
        ]
        
        for func_name in expected_functions:
            self.assertTrue(hasattr(core_module, func_name),
                          f"Function {func_name} not found in core module")
            func = getattr(core_module, func_name)
            self.assertTrue(callable(func),
                          f"Function {func_name} is not callable")
    
    def test_get_functions_dataframe_basic(self):
        """
        Test basic functionality of get_functions_dataframe.
        
        ~~~
        " Creates a test Python file with function
        " Calls get_functions_dataframe on test file
        " Validates returned DataFrame structure
        ~~~
        
        Returns type: None (NoneType) - assertion-based test with no return value
        """
        # Create a temporary test file
        test_file_path = '/tmp/test_functions.py'
        test_content = '''
def test_func(x: int, y: str) -> bool:
    """Test function for documentation testing.
    
    ~~~
    " Takes integer and string inputs
    " Returns boolean result
    ~~~
    
    Returns type: bool - test result
    """
    return True
'''
        
        with open(test_file_path, 'w') as f:
            f.write(test_content)
        
        try:
            df = get_functions_dataframe(test_file_path)
            self.assertEqual(len(df), 1)
            self.assertIn('Function', df.columns)
            self.assertIn('Description', df.columns)
            self.assertIn('Input Types', df.columns)
            self.assertIn('Output Type', df.columns)
            self.assertEqual(df.iloc[0]['Function'], 'test_func')
        finally:
            # Clean up
            if os.path.exists(test_file_path):
                os.remove(test_file_path)
    
    def test_hygin_basic_functionality(self):
        """
        Test basic functionality of hygin search function.
        
        ~~~
        " Tests search in current directory
        " Validates return type is list
        " Checks error handling for invalid paths
        ~~~
        
        Returns type: None (NoneType) - assertion-based test with no return value
        """
        # Test with current directory
        result = hygin('.', 'test_core.py')
        self.assertIsInstance(result, list)
        
        # Test error handling for invalid path
        with self.assertRaises(ValueError):
            hygin('/nonexistent/path', 'test')


if __name__ == '__main__':
    unittest.main()