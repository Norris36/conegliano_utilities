"""
Code Extractor - Extract and manage function code globally

This module provides utilities for:
1. Extracting function source code from any Python file
2. Copying function code to clipboard
3. Finding functions across codebases
4. Managing code snippets for issue resolution
"""

import ast
import inspect
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime
import importlib.util


def find_function_in_file(file_path: str, function_name: str) -> Optional[Dict[str, Any]]:
    """
    Find a specific function in a Python file and extract its details.

    ~~~
    • Parses Python file using AST
    • Locates function definition by name
    • Extracts source code, line numbers, and metadata
    • Handles both regular functions and methods
    ~~~

    Args:
        file_path (str): Path to Python file
        function_name (str): Name of function to find

    Returns type: function_info (Optional[Dict[str, Any]]) - function details or None if not found
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.splitlines()

        # Parse the file with AST
        tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name == function_name:
                    # Extract function source code
                    start_line = node.lineno - 1  # AST uses 1-based indexing
                    end_line = node.end_lineno if hasattr(node, 'end_lineno') else len(lines)

                    # Get the actual source code
                    function_lines = lines[start_line:end_line]
                    source_code = '\n'.join(function_lines)

                    # Get function signature and docstring
                    signature_parts = [f"def {node.name}("]
                    for i, arg in enumerate(node.args.args):
                        if i > 0:
                            signature_parts.append(", ")
                        signature_parts.append(arg.arg)
                        if arg.annotation:
                            signature_parts.append(f": {ast.unparse(arg.annotation)}")
                    signature_parts.append(")")

                    if node.returns:
                        signature_parts.append(f" -> {ast.unparse(node.returns)}")

                    signature = ''.join(signature_parts)

                    # Extract docstring
                    docstring = None
                    if (node.body and isinstance(node.body[0], ast.Expr) and
                        isinstance(node.body[0].value, ast.Constant) and
                        isinstance(node.body[0].value.value, str)):
                        docstring = node.body[0].value.value

                    return {
                        "name": function_name,
                        "file_path": file_path,
                        "source_code": source_code,
                        "signature": signature,
                        "docstring": docstring,
                        "start_line": start_line + 1,  # Return 1-based line numbers
                        "end_line": end_line,
                        "is_async": isinstance(node, ast.AsyncFunctionDef),
                        "lines_count": end_line - start_line
                    }

        return None  # Function not found

    except Exception as e:
        print(f"❌ Error parsing {file_path}: {e}")
        return None


def search_function_in_directory(directory: str, function_name: str, extensions: List[str] = None) -> List[Dict[str, Any]]:
    """
    Search for a function across all Python files in a directory.

    ~~~
    • Recursively searches through directory tree
    • Finds all occurrences of function name
    • Returns detailed information for each match
    • Supports filtering by file extensions
    ~~~

    Args:
        directory (str): Directory to search in
        function_name (str): Function name to find
        extensions (List[str], optional): File extensions to search (default: ['.py'])

    Returns type: matches (List[Dict[str, Any]]) - list of function matches with details
    """
    if extensions is None:
        extensions = ['.py']

    matches = []
    directory_path = Path(directory)

    try:
        for file_path in directory_path.rglob('*'):
            if file_path.suffix in extensions and file_path.is_file():
                try:
                    function_info = find_function_in_file(str(file_path), function_name)
                    if function_info:
                        # Add relative path for better display
                        function_info['relative_path'] = str(file_path.relative_to(directory_path))
                        matches.append(function_info)
                except Exception as e:
                    # Skip files that can't be parsed
                    continue

        return matches

    except Exception as e:
        print(f"❌ Error searching directory {directory}: {e}")
        return []


def extract_function_code(function_name: str, search_paths: List[str] = None) -> Dict[str, Any]:
    """
    Extract function code with automatic search across common locations.

    ~~~
    • Searches current directory and common Python paths
    • Returns first match with detailed metadata
    • Includes context about where function was found
    • Provides ready-to-copy source code
    ~~~

    Args:
        function_name (str): Name of function to extract
        search_paths (List[str], optional): Custom search paths

    Returns type: extraction_result (Dict[str, Any]) - function code and metadata
    """
    if search_paths is None:
        search_paths = [
            os.getcwd(),  # Current directory
            os.path.expanduser("~"),  # Home directory
        ]

        # Add common Python locations if they exist
        common_paths = [
            "/usr/local/lib/python*",
            os.path.expanduser("~/Documents"),
            os.path.expanduser("~/Projects"),
            os.path.expanduser("~/Code"),
        ]
        search_paths.extend([p for p in common_paths if os.path.exists(p)])

    print(f"🔍 Searching for function '{function_name}'...")

    all_matches = []
    for search_path in search_paths:
        if os.path.exists(search_path):
            matches = search_function_in_directory(search_path, function_name)
            all_matches.extend(matches)

    if not all_matches:
        return {
            "success": False,
            "function_name": function_name,
            "error": "Function not found in any search paths",
            "searched_paths": search_paths
        }

    # Return the first match (you can modify this logic)
    best_match = all_matches[0]

    return {
        "success": True,
        "function_name": function_name,
        "source_code": best_match["source_code"],
        "file_path": best_match["file_path"],
        "relative_path": best_match.get("relative_path", ""),
        "signature": best_match["signature"],
        "docstring": best_match["docstring"],
        "start_line": best_match["start_line"],
        "end_line": best_match["end_line"],
        "total_matches": len(all_matches),
        "all_matches": all_matches
    }


def copy_function_to_clipboard(function_name: str, include_metadata: bool = True) -> Dict[str, Any]:
    """
    Extract function code and copy to clipboard with optional metadata.

    ~~~
    • Finds and extracts function source code
    • Copies to system clipboard automatically
    • Optionally includes file location and metadata
    • Returns extraction results for confirmation
    ~~~

    Args:
        function_name (str): Function name to copy
        include_metadata (bool): Include metadata comments in copied code

    Returns type: copy_result (Dict[str, Any]) - copy operation result and function details
    """
    # Extract the function
    extraction_result = extract_function_code(function_name)

    if not extraction_result.get("success"):
        return extraction_result

    # Prepare code for clipboard
    source_code = extraction_result["source_code"]

    if include_metadata:
        metadata_header = f"""# Function: {function_name}
# Source: {extraction_result.get('relative_path', extraction_result['file_path'])}
# Lines: {extraction_result['start_line']}-{extraction_result['end_line']}
# Extracted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""
        clipboard_content = metadata_header + source_code
    else:
        clipboard_content = source_code

    # Copy to clipboard
    try:
        # Try different clipboard methods
        copy_success = False

        # Method 1: pbcopy (macOS)
        try:
            subprocess.run(['pbcopy'], input=clipboard_content.encode(), check=True)
            copy_success = True
            print("📋 Copied to clipboard using pbcopy")
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        # Method 2: xclip (Linux)
        if not copy_success:
            try:
                subprocess.run(['xclip', '-selection', 'clipboard'],
                             input=clipboard_content.encode(), check=True)
                copy_success = True
                print("📋 Copied to clipboard using xclip")
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass

        # Method 3: Windows clip
        if not copy_success:
            try:
                subprocess.run(['clip'], input=clipboard_content.encode(), check=True)
                copy_success = True
                print("📋 Copied to clipboard using clip")
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass

        if not copy_success:
            print("⚠️  Could not copy to clipboard automatically")
            print("📝 Code is available in the returned result")

        extraction_result.update({
            "clipboard_content": clipboard_content,
            "copied_to_clipboard": copy_success,
            "include_metadata": include_metadata
        })

        print(f"✅ Function '{function_name}' extracted successfully")
        if extraction_result.get("total_matches", 0) > 1:
            print(f"💡 Found {extraction_result['total_matches']} matches, used first one")

        return extraction_result

    except Exception as e:
        extraction_result.update({
            "clipboard_error": str(e),
            "copied_to_clipboard": False
        })
        return extraction_result


def list_functions_in_file(file_path: str) -> List[Dict[str, Any]]:
    """
    List all functions defined in a Python file.

    ~~~
    • Parses file to find all function definitions
    • Extracts basic metadata for each function
    • Handles both regular and async functions
    • Returns organized list for browsing
    ~~~

    Args:
        file_path (str): Path to Python file

    Returns type: functions_list (List[Dict[str, Any]]) - list of function metadata
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        tree = ast.parse(content)
        functions = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Extract basic info
                function_info = {
                    "name": node.name,
                    "line_number": node.lineno,
                    "is_async": isinstance(node, ast.AsyncFunctionDef),
                    "args_count": len(node.args.args),
                    "has_docstring": False
                }

                # Check for docstring
                if (node.body and isinstance(node.body[0], ast.Expr) and
                    isinstance(node.body[0].value, ast.Constant) and
                    isinstance(node.body[0].value.value, str)):
                    function_info["has_docstring"] = True
                    function_info["docstring_preview"] = node.body[0].value.value[:100] + "..." if len(node.body[0].value.value) > 100 else node.body[0].value.value

                functions.append(function_info)

        return sorted(functions, key=lambda x: x["line_number"])

    except Exception as e:
        print(f"❌ Error parsing {file_path}: {e}")
        return []


def quick_function_copy(function_name: str) -> None:
    """
    Quick function to copy function code to clipboard with minimal output.

    ~~~
    • Simplified interface for rapid function copying
    • Automatically copies to clipboard
    • Prints only essential information
    • Perfect for workflow integration
    ~~~

    Args:
        function_name (str): Function name to copy

    Returns type: None (NoneType) - prints results to console
    """
    print(f"📄 Copying function '{function_name}'...")

    result = copy_function_to_clipboard(function_name, include_metadata=True)

    if result.get("success"):
        file_location = result.get("relative_path", result.get("file_path", "unknown"))
        print(f"✅ Copied from: {file_location}:{result.get('start_line', '?')}")
        if result.get("copied_to_clipboard"):
            print("📋 Ready to paste!")
    else:
        print(f"❌ Not found: {result.get('error', 'Unknown error')}")


# Convenience aliases
copy_func = copy_function_to_clipboard
find_func = extract_function_code
get_code = quick_function_copy