## File: jensbay_utilities/core.py
import os
import ast
import re
import datetime
from typing import List, get_type_hints
import pandas as pd
from tqdm import tqdm


def get_functions_dataframe(filename: str = 'jensbay_utilities.py') -> pd.DataFrame:
    """
    Extracts function names, docstrings, input and output variable types from a Python file.

    Args:
        filename (str): The path to the Python file.

    Returns:
        pd.DataFrame: A DataFrame with columns "Function", "Description", "Input Types", "Output Type"
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

    Args:
        path (str): The path to start the search from.
        query (str): The file name or pattern to search for.
        extensions (str or list, optional): File extension(s) to filter by.

    Returns:
        list: A list of files that match the query and specified extensions.
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
            pbar.set_description(f"Searching in {top_dir}")
            full_top_path = os.path.join(path, top_dir)
            
            if os.path.isdir(full_top_path):
                for root, dirs, files in os.walk(full_top_path):
                    for f in files:
                        if query in f:
                            if extensions:
                                if any(f.endswith(ext) for ext in extensions):
                                    matching_files.append(os.path.join(root, f))
                            else:
                                matching_files.append(os.path.join(root, f))
            pbar.update(1)
            
    return matching_files


def find_files(paths: List[str], target_date: str = '2025-02-11', days: int = 14) -> pd.DataFrame:
    """
    Find and filter files based on modification date within a specified date range.
    
    Args:
        paths (List[str]): A list of file paths to be analyzed
        target_date (str): The center date for filtering in 'YYYY-MM-DD' format
        days (int): The total number of days in the date range window (default: 14)
    
    Returns:
        pd.DataFrame: A DataFrame with filtered files and metadata
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

    Args:
        file_path (str): The path to the file.

    Returns:
        str: The creation time of the file in a readable format.
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

    Args:
        file_path (str): The path to the file.

    Returns:
        str: The modified time of the file in a human-readable format.
    """
    try:
        modified_time = os.path.getmtime(file_path)
        readable_time = datetime.datetime.fromtimestamp(modified_time).strftime('%Y-%m-%d %H:%M:%S')
        return readable_time
    except FileNotFoundError:
        return "File not found"
    except OSError as e:
        return f"Error: {str(e)}"
