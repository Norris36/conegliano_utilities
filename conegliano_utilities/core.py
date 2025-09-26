## File: jensbay_utilities/core.py
import os
import ast
import re
import datetime
from typing import List, get_type_hints
import pandas as pd
from tqdm import tqdm


def print_version_info() -> None:
    """
    Print current package version and last update timestamp.

    ~~~
    • Imports version from package __init__.py
    • Gets current timestamp for load time
    • Displays formatted version information
    • Shows when module was last loaded
    • Provides visual separator for clarity
    ~~~

    Returns type: None (NoneType) - prints version information to console
    """
    try:
        from . import __version__
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"\n{'='*50}")
        print(f"🚀 Conegliano Utilities v{__version__}")
        print(f"📅 Loaded at: {current_time}")
        print(f"{'='*50}\n")
    except ImportError:
        print("⚠️  Version information not available")
    except Exception as e:
        print(f"⚠️  Error loading version: {e}")


def get_functions_dataframe(filename: str = 'conegliano_utilities.py') -> pd.DataFrame:
    """
    Extracts function names, docstrings, input and output variable types from a Python file.

    1. Reads Python source code from specified file
    2. Parses source code using AST module  
    3. Extracts function definitions with type hints and docstrings
    4. Creates structured DataFrame with function metadata
    5. Handles cases with missing type annotations gracefully

    Args:
        filename (str): The path to the Python file

    Returns type: df (pd.DataFrame) - structured data with columns "Function", "Description", "Input Types", "Output Type"
    """
    with open(filename, 'r') as file:
        source_code = file.read()

    tree = ast.parse(source_code)
    functions_data = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            function_name = node.name
            docstring = ast.get_docstring(node)

            # Handle cases where type hints are not present
            input_types = []
            output_type = 'None'
            
            if node.args.args:
                # Extract input parameter types from annotations
                for arg in node.args.args:
                    if arg.annotation:
                        # Get the annotation as string
                        if hasattr(arg.annotation, 'id'):
                            type_name = arg.annotation.id
                        else:
                            type_name = str(arg.annotation)
                        input_types.append(f"{arg.arg}: {type_name}")
                    else:
                        input_types.append(f"{arg.arg}: Any")
            
            # Extract return type from annotation
            if node.returns:
                if hasattr(node.returns, 'id'):
                    output_type = node.returns.id
                else:
                    output_type = str(node.returns)
            
            # If no return annotation, try to extract from docstring
            if output_type == 'None' and docstring:
                if 'Returns:' in docstring or 'Returns' in docstring:
                    try:
                        returns_section = docstring.split('Returns')[1].split(':')[1].split('.')[0].strip()
                        output_type = returns_section
                    except:
                        output_type = 'Unknown'

            # Get first line of docstring for description
            description = docstring.split('\n')[0] if docstring else "No docstring found."
            
            functions_data.append({
                "Function": function_name,
                "Description": description,
                "Input Types": ", ".join(input_types) if input_types else "None",
                "Output Type": output_type
            })

    df = pd.DataFrame(functions_data)
    pd.set_option('display.max_colwidth', 200)
    return df


def hygin(path: str, query: str, extensions=None) -> list:
    """
    Searches for files that match the given query within the specified path.

    1. Validates input path exists and is directory
    2. Normalizes extensions parameter to list format
    3. Recursively walks through directory structure
    4. Filters files by query pattern and extensions
    5. Displays progress using tqdm progress bar

    Args:
        path (str): The path to start the search from
        query (str): The file name or pattern to search for
        extensions (str or list, optional): File extension(s) to filter by

    Returns type: matching_files (list) - file paths that match query and extension criteria
    """
    if not os.path.isdir(path):
        raise ValueError(f"{path} is not a directory")

    # Normalize extensions to a list if it's a single string
    if isinstance(extensions, str):
        extensions = [extensions]

    # List all directories and files in the provided path
    top_paths = os.listdir(path) + [path]
    matching_files = []

    with tqdm(total=len(top_paths), desc="Initializing search") as pbar:
        for top_dir in top_paths:
            full_top_path = os.path.join(path, top_dir)
            pbar.set_description(f"Searching in {top_dir}")

            if os.path.isdir(full_top_path):
                # Count the number of subdirectories to update the total
                dirs_to_search = []
                for root, dirs, _ in os.walk(full_top_path):
                    dirs_to_search.extend(dirs)

                # Update the total iterations in the progress bar
                pbar.total += len(dirs_to_search)

                # Traverse the directory
                for root, dirs, files in os.walk(full_top_path):
                    for f in files:
                        if query in f:
                            if extensions:
                                if any(f.endswith(ext) for ext in extensions):
                                    matching_files.append(os.path.join(root, f))
                            else:
                                matching_files.append(os.path.join(root, f))

                    # Update the progress bar description with remaining folders
                    remaining_folders = len(dirs_to_search) - len([d for d in dirs_to_search if d in root])
                    pbar.set_description(f"Searching in {root} | Folders left: {remaining_folders}")

                    # Update the progress bar
                    pbar.update(1)

            pbar.update(1)

            
            
    return matching_files


def find_files(paths: List[str], target_date: str = '2025-02-11', days: int = 14) -> pd.DataFrame:
    """
    Find and filter files based on modification date within a specified date range.
    
    1. Creates DataFrame from input file paths
    2. Validates target date format and converts to datetime
    3. Extracts file metadata including modification times
    4. Calculates date range window around target date
    5. Filters files within specified date range window
    
    Args:
        paths (List[str]): A list of file paths to be analyzed
        target_date (str): The center date for filtering in 'YYYY-MM-DD' format
        days (int): The total number of days in the date range window (default: 14)
    
    Returns type: filtered_working_dataframe (pd.DataFrame) - filtered files with metadata including path, filename, modification date, and folder name
    """
    working_dataframe = pd.DataFrame(paths, columns=['path'])
    
    # Validate date format
    assert isinstance(target_date, str) and re.match(r'^\d{4}-\d{2}-\d{2}$', target_date), \
           "target_date must be a string in format 'YYYY-MM-DD'"
    
    target_date = datetime.datetime.strptime(target_date, '%Y-%m-%d')
    
    # Extract filename from path
    working_dataframe['file_name'] = working_dataframe['path'].apply(
        lambda x: os.path.basename(x)
    )
    
    # Get file modification time (fixed the reference to external 'my' module)
    working_dataframe['file_modified_date'] = working_dataframe['path'].apply(
        lambda x: os.path.getmtime(x) if os.path.exists(x) else None
    )

    # Convert timestamps to datetime
    working_dataframe['file_modified_date'] = pd.to_datetime(
        working_dataframe['file_modified_date'], unit='s', errors='coerce'
    )

    # Extract folder name
    working_dataframe['folder_name'] = working_dataframe['path'].apply(
        lambda x: os.path.basename(os.path.dirname(x))
    )

    # Calculate date range
    min_date = target_date - datetime.timedelta(days=days/2)
    max_date = target_date + datetime.timedelta(days=days/2)
    
    # Filter files within date range
    filtered_working_dataframe = working_dataframe[
        (working_dataframe['file_modified_date'] >= min_date) & 
        (working_dataframe['file_modified_date'] <= max_date)
    ]

    return filtered_working_dataframe


def get_file_creation_time(file_path: str) -> str:
    """
    Returns the creation time of the file at the given path.

    1. Gets file creation timestamp using os.getctime
    2. Converts timestamp to human-readable format
    3. Handles file not found and OS errors gracefully
    4. Returns formatted time string or error message

    Args:
        file_path (str): The path to the file

    Returns type: readable_time (str) - creation time in 'YYYY-MM-DD HH:MM:SS' format or error message
    """
    try:
        creation_time = os.path.getctime(file_path)
        readable_time = datetime.datetime.fromtimestamp(creation_time).strftime('%Y-%m-%d %H:%M:%S')
        return readable_time
    except (FileNotFoundError, OSError) as e:
        return f"Error: {str(e)}"


def get_file_modified_time(file_path: str) -> str:
    """
    Get the modified time of a file.

    1. Gets file modification timestamp using os.getmtime
    2. Converts timestamp to human-readable format  
    3. Handles file not found and OS errors gracefully
    4. Returns formatted time string or error message

    Args:
        file_path (str): The path to the file

    Returns type: readable_time (str) - modification time in 'YYYY-MM-DD HH:MM:SS' format or error message
    """
    try:
        modified_time = os.path.getmtime(file_path)
        readable_time = datetime.datetime.fromtimestamp(modified_time).strftime('%Y-%m-%d %H:%M:%S')
        return readable_time
    except FileNotFoundError:
        return "File not found"
    except OSError as e:
        return f"Error: {str(e)}"


def get_folder_sizes(root_folder: str) -> dict:
    """
    Calculate the size of all immediate subdirectories within a root folder.

    ~~~
    • Lists all immediate subdirectories in root folder
    • Walks through each subdirectory recursively
    • Calculates total size by summing all file sizes
    • Handles permission errors and inaccessible files gracefully
    • Returns dictionary mapping folder paths to sizes in bytes
    ~~~

    Args:
        root_folder (str): The root directory path to analyze

    Returns type: folder_sizes (dict) - mapping of folder paths to their total sizes in bytes
    """
    folder_sizes = {}

    # Get only immediate subdirectories (not files)
    for item in os.listdir(root_folder):
        item_path = os.path.join(root_folder, item)
        if os.path.isdir(item_path):
            dir_size = 0
            for dirpath, dirnames, filenames in os.walk(item_path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        dir_size += os.path.getsize(filepath)
                    except (OSError, PermissionError):
                        continue  # Skip inaccessible files
            folder_sizes[item_path] = dir_size

    return folder_sizes


def create_dataframe_from_folder_sizes(folder_sizes: dict) -> pd.DataFrame:
    """
    Create a structured DataFrame from folder size data with analytics.

    ~~~
    • Creates DataFrame with folder paths and sizes in GB
    • Sorts folders by size in descending order
    • Calculates cumulative size totals
    • Computes percentage and cumulative percentage of total
    • Adds basename column for folder names
    • Rounds all numeric values to 2 decimal places
    ~~~

    Args:
        folder_sizes (dict): Dictionary mapping folder paths to sizes in bytes

    Returns type: df (pd.DataFrame) - structured data with columns for path, size, cumulative metrics, and percentages
    """
    df = pd.DataFrame({
        "path": list(folder_sizes.keys()),
        "size (GB)": [size / (1024 ** 3) for size in folder_sizes.values()]
    })
    df["size (GB)"] = df["size (GB)"].round(2)  # Round to 2 decimal places
    df.sort_values(by="size (GB)", ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)
    # now lets get the cummulative size
    df["cum (size)"] = df["size (GB)"].cumsum().round(2)
    # and the percentage of total size
    df['percentage(size)'] = (df["size (GB)"] / df["size (GB)"].sum() * 100).round(2)
    # and the cumulative percentage of total size
    df['cum percentage (size)'] = (df['cum (size)'] / df["size (GB)"].sum() * 100).round(2)
    df["basename"] = df["path"].apply(os.path.basename)
    return df


def get_filesize_dataframe(folder_path: str) -> pd.DataFrame:
    """
    Analyze folder sizes and return comprehensive analytics DataFrame.

    ~~~
    • Validates input path is a valid directory
    • Calculates sizes of all immediate subdirectories
    • Creates structured DataFrame with size analytics
    • Sorts results by size in descending order
    • Returns complete folder size analysis
    ~~~

    Args:
        folder_path (str): The directory path to analyze

    Returns type: df (pd.DataFrame) - complete folder size analysis with metrics and rankings
    """
    folder_path = folder_path.strip()
    if not os.path.isdir(folder_path):
        raise ValueError("The provided path is not a valid directory.")
    folder_sizes = get_folder_sizes(folder_path)
    df = create_dataframe_from_folder_sizes(folder_sizes)
    df.sort_values(by="size (GB)", ascending=False, inplace=True)
    return df
