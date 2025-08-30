import unittest
import ast
import inspect
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from jensbay_utilities.core import get_functions_dataframe, hygin, find_files, get_file_creation_time, get_file_modified_time
import jensbay_utilities.core as core_module


class TestCore(unittest.TestCase):
    
    def setUp(self):
        self.core_functions = [
            get_functions_dataframe,
            hygin, 
            find_files,
            get_file_creation_time,
            get_file_modified_time
        ]
    
    def test_documentation_standard_compliance(self):
        """
        Test that all functions adhere to the documentation standard.
        
        ~~~
        • Checks for summary one-liner followed by ~~~
        • Validates bulleted list of operations
        • Ensures ~~~ followed by returns type description
        ~~~
        
        Returns type: None (NoneType) - assertion-based test with no return value
        """
        for func in self.core_functions:
            with self.subTest(function=func.__name__):
                self._validate_function_documentation(func)
    
    def _validate_function_documentation(self, func):
        """
        Validates a single function's documentation format.
        
        ~~~
        • Extracts and parses function docstring
        • Checks for required documentation components
        • Validates structure matches standard format
        ~~~
        
        Returns type: None (NoneType) - raises AssertionError if validation fails
        """
        docstring = inspect.getdoc(func)
        self.assertIsNotNone(docstring, f"Function {func.__name__} has no docstring")
        
        lines = [line.strip() for line in docstring.split('\n') if line.strip()]
        
        # Check minimum structure requirements
        self.assertGreaterEqual(len(lines), 4, 
                              f"Function {func.__name__} docstring too short for standard format")
        
        # Find the ~~~ delimiters
        first_delimiter_idx = None
        second_delimiter_idx = None
        
        for i, line in enumerate(lines):
            if line == '~~~':
                if first_delimiter_idx is None:
                    first_delimiter_idx = i
                elif second_delimiter_idx is None:
                    second_delimiter_idx = i
                    break
        
        self.assertIsNotNone(first_delimiter_idx, 
                           f"Function {func.__name__} missing first ~~~ delimiter")
        self.assertIsNotNone(second_delimiter_idx, 
                           f"Function {func.__name__} missing second ~~~ delimiter")
        
        # Validate structure
        # 1. Summary one-liner should be before first ~~~
        self.assertGreater(first_delimiter_idx, 0,
                         f"Function {func.__name__} missing summary before first ~~~")
        
        # 2. Bulleted operations should be between ~~~ delimiters
        operations_section = lines[first_delimiter_idx + 1:second_delimiter_idx]
        self.assertGreater(len(operations_section), 0,
                         f"Function {func.__name__} missing operations between ~~~ delimiters")
        
        # Check that operations are bulleted
        for i, op_line in enumerate(operations_section):
            self.assertTrue(op_line.startswith('•') or op_line.startswith('-') or op_line.startswith('*'),
                          f"Function {func.__name__} operation line {i+1} not properly bulleted: '{op_line}'")
        
        # 3. Returns type should follow second ~~~
        returns_section = lines[second_delimiter_idx + 1:]
        self.assertGreater(len(returns_section), 0,
                         f"Function {func.__name__} missing returns section after second ~~~")
        
        # Check returns format: should be "Returns type: variable_name (datatype) - description"
        returns_line = returns_section[0]
        self.assertTrue(returns_line.lower().startswith('returns type:'),
                       f"Function {func.__name__} returns line doesn't start with 'Returns type:': '{returns_line}'")
        
        # Check that it follows format: variable_name (datatype) - description
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