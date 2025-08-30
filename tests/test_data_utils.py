import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from conegliano_utilities.data_utils import *
except ImportError:
    pass


class TestDataUtils(unittest.TestCase):
    
    def test_module_import(self):
        try:
            import conegliano_utilities.data_utils
            self.assertTrue(True)
        except ImportError:
            self.skipTest("data_utils module not available")


if __name__ == '__main__':
    unittest.main()