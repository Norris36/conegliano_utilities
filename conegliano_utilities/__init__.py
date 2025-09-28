"""
Conegliano Utilities - Personal utility functions for data science and development tasks
"""

import warnings
import requests
from packaging import version

__version__ = "1.1.19"


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
        url = (
            "https://api.github.com/repos/Norris36/conegliano_utilities/releases/latest"
        )
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            latest_info = response.json()
            latest_version = latest_info["tag_name"].lstrip("v")
            current_version = __version__

            if version.parse(latest_version) > version.parse(current_version):
                warnings.warn(
                    f"\n🔔 UPDATE AVAILABLE 🔔\n"
                    f"Current version: {current_version}\n"
                    f"Latest version: {latest_version}\n"
                    "Run: pip install --upgrade "
                    "git+https://github.com/Norris36/conegliano_utilities.git\n",
                    UserWarning,
                    stacklevel=2,
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
from .issue_logger import *
from .issue_config import *
from .local_issue_store import *
from .email_issue_reporter import *
from .global_issue_logger import *
from .code_extractor import *
from .issue_solver import *

# Print version info on import
print_version_info()

# Define what gets imported with "from conegliano_utilities import *"
__all__ = [
    # Core utilities
    "get_functions_dataframe",
    "hygin",
    "find_files",
    "get_file_creation_time",
    "get_file_modified_time",
    "get_folder_sizes",
    "create_dataframe_from_folder_sizes",
    "get_filesize_dataframe",
    # Data utilities
    "get_columns",
    "humanise_df",
    "rename_columns",
    # Web utilities
    "find_all_links",
    # Workout utilities
    "WorkoutGenerator",
    "create_workout_from_dataframe",
    "create_workout_from_github",
    "load_exercise_data_from_github",
    "load_latest_workout_from_github",
    # Issue logging utilities
    "create_github_issue",
    "create_debug_issue",
    "log_error_and_create_issue",
    "quick_issue",
    "smart_issue",
    "format_system_info",
    "format_stack_trace",
    # Issue configuration
    "get_github_token",
    "setup_token_config",
    "set_hardcoded_token",
    # Local issue storage
    "store_issue_locally",
    "list_local_issues",
    "sync_local_issues_to_github",
    "create_local_debug_issue",
    # Email issue reporting
    "send_issue_email",
    "create_mailto_link",
    "print_email_issue",
    # Global issue logging (works from anywhere)
    "global_issue",
    "quick_global_issue",
    "list_repo_issues",
    "global_issue_context",
    "issue",  # Short alias for global_issue
    # Code extraction utilities
    "extract_function_code",
    "copy_function_to_clipboard",
    "search_function_in_directory",
    "find_function_in_file",
    "list_functions_in_file",
    "quick_function_copy",
    "copy_func",  # Alias
    "find_func",  # Alias
    "get_code",   # Alias
    # Issue solving with code integration
    "issue_solved",
    "get_open_issues",
    "display_open_issues",
    "add_comment_to_issue",
    "close_issue",
    "quick_solve",
    "solve",       # Alias
    "quick_solution",  # Alias
    "list_issues", # Alias
]
