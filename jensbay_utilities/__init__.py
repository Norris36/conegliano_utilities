"""
Jensbay Utilities - Personal utility functions for data science and development tasks
"""

__version__ = "1.0.0"

# Import main functions to make them available at package level
from .core import *
from .data_utils import *
from .web_utils import *

# Define what gets imported with "from jensbay_utilities import *"
__all__ = [
    # Core utilities
    'get_functions_dataframe',
    'hygin',
    'find_files',
    'get_file_creation_time',
    'get_file_modified_time',
    
    # Data utilities
    'get_columns',
    'humanise_df',
    'rename_columns',
    
    # Web utilities
    'find_all_links',
]