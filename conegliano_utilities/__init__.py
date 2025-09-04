"""
Conegliano Utilities - Personal utility functions for data science and development tasks
"""

import warnings
import requests
import json
from packaging import version

__version__ = "1.1.1"

def check_for_updates():
    """
    Check if a newer version is available on GitHub.
    
    1. Gets current version from package
    2. Fetches latest release info from GitHub API
    3. Compares versions and shows warning if outdated
    4. Provides upgrade command if update available
    
    Returns type: None (NoneType) - prints update information or warnings
    """
    try:
        # GitHub API endpoint for latest release
        url = "https://api.github.com/repos/Norris36/conegliano_utilities/releases/latest"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            latest_info = response.json()
            latest_version = latest_info['tag_name'].lstrip('v')
            current_version = __version__
            
            if version.parse(latest_version) > version.parse(current_version):
                warnings.warn(
                    f"\n🔔 UPDATE AVAILABLE 🔔\n"
                    f"Current version: {current_version}\n"
                    f"Latest version: {latest_version}\n"
                    f"Run: pip install --upgrade git+https://github.com/Norris36/conegliano_utilities.git\n",
                    UserWarning,
                    stacklevel=2
                )
            
    except Exception:
        # Silently fail - don't disrupt normal usage if check fails
        pass

# Check for updates on import (optional - can be disabled)
try:
    check_for_updates()
except Exception:
    pass

# Import main functions to make them available at package level
from .core import *
from .data_utils import *
from .web_utils import *
from .workout import *

# Define what gets imported with "from conegliano_utilities import *"
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
    
    # Workout utilities
    'WorkoutGenerator',
    'create_workout_from_dataframe',
    'create_workout_from_github',
    'load_exercise_data_from_github',
    'load_latest_workout_from_github',
]